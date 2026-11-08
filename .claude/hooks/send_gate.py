#!/usr/bin/env python3
"""PreToolUse send gate (G7 + G1b): no message leaves without a human "send" and a clean outbound scan.

The send rules used to be prose ("call send only when the user's very next message approves that exact
mail"), and the change log said so: nothing mechanically stopped a send. Prompts are one injection away
from being ignored; this check is not (arXiv:2607.08028: harness-enforced contracts blocked every
violation that prompt-only rules let through).

Decision, on any tool whose name contains "send" on an MCP server (mail, chat):
  1. Who may send. A headless job may not, except plan-runner (living-plan's email deliverable).
  2. Approval, from the transcript, never from tool output (injected text arrives as tool results, so it
     can't approve). Interactive/console: the latest human message is a short, explicit yes ("send it",
     "yes", "schick"), and the assistant's turn before it named every recipient (the read-back).
     plan-runner: the resumed prompt carries the checkpoint answer "Send it".
  3. Outbound scan (scripts/outbound_gate.py, send mode): another client's name, a third company's
     contact, an internal channel. A finding blocks unless the human wrote "send anyway".
FAIL-CLOSED: a send is irreversible, so anything unparsable denies. Every decision is traced to
output/.runs/_forensics/hooks.jsonl. Test: bash .claude/hooks/tests/send-gate.test.sh
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
APPROVE = re.compile(r"\b(send( it| that| now)?|yes|yep|yeah|ja|jep|schick( sie| es| ab)?|abschicken|senden|approved?|go ahead|passt|los)\b", re.I)
REFUSE = re.compile(r"\b(don'?t|do not|not yet|nicht|no|nein|draft|entwurf|wait|warte|stop|change|ändere?)\b", re.I)


def human_text(entry):
    """The words the person actually wrote in one user transcript entry ("" for tool results)."""
    content = entry.get("message", {}).get("content")
    items = [{"type": "text", "text": content}] if isinstance(content, str) else (content or [])
    if any(i.get("type") == "tool_result" for i in items if isinstance(i, dict)):
        return ""
    parts = []
    for i in items:
        if not isinstance(i, dict) or i.get("type") != "text":
            continue
        t = i.get("text", "")
        if t.lstrip().startswith(("<context refreshed", "<system-reminder>", "<command-", "<local-command")):
            continue
        if "<task-notification>" in t or "SYSTEM NOTIFICATION" in t or "<agent-message" in t:
            continue   # system events and subagent reports are not the person's words
        t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S)
        t = re.sub(r"^\s*<on-stage>.*?</on-stage>\s*", "", t, flags=re.S)
        parts.append(t.strip())
    return "\n".join(p for p in parts if p)


def last_turns(transcript):
    """(latest human message, the assistant text between the human message before it and it)."""
    entries = []
    with open(transcript, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    human_idx = [i for i, e in enumerate(entries) if e.get("type") == "user" and human_text(e)]
    if not human_idx:
        return "", ""
    last = human_idx[-1]
    prev = human_idx[-2] if len(human_idx) > 1 else -1
    said = []
    for e in entries[prev + 1:last]:
        if e.get("type") == "assistant":
            for i in e.get("message", {}).get("content") or []:
                if isinstance(i, dict) and i.get("type") == "text":
                    said.append(i.get("text", ""))
    return human_text(entries[last]), "\n".join(said)


def recipients(tool_input):
    out = []
    for k in ("to", "cc", "bcc"):
        v = tool_input.get(k)
        if isinstance(v, list):
            v = ",".join(map(str, v))
        out += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", v or "")
    return out


def decide(event, job):
    tool, ti = event.get("tool_name", ""), event.get("tool_input") or {}
    if job and job != "plan-runner":
        return f"headless job '{job}' may not send messages; only plan-runner may, after a 'Send it' checkpoint"
    transcript = event.get("transcript_path")
    if not transcript or not Path(transcript).is_file():
        return "no transcript to verify the approval against"
    human, readback = last_turns(transcript)
    to = recipients(ti)
    is_mail = "mail" in tool.lower() or bool(to)
    if job == "plan-runner":
        if not ("answered your question" in human and re.search(r"\bSend it\b", human)
                and not re.search(r"Don'?t send|Save as (a )?Gmail draft", human, re.I)):
            return "plan-runner sends only after the checkpoint answer 'Send it'"
    else:
        if not human or len(human) > 300 or not APPROVE.search(human) or REFUSE.search(human):
            return ("no explicit approval: the latest message from the person must be a short yes "
                    "('send it') to the read-back, with no change requested")
        missing = [r for r in to if r.lower() not in readback.lower()]
        if missing:
            return f"the read-back before the approval did not name {', '.join(missing)}: read the mail back in full first"
    if is_mail:
        sys.path.insert(0, str(REPO / "scripts"))
        import outbound_gate
        text = f"{ti.get('subject', '')}\n{ti.get('body', '')}"
        findings = outbound_gate.scan(text, to)
        if findings and "send anyway" not in human.lower():
            return "outbound scan: " + "; ".join(findings) + ". Fix the mail, or the person says 'send anyway'"
    return None


def trace(event, job, decision, reason):
    log = REPO / "output" / ".runs" / "_forensics" / "hooks.jsonl"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a") as f:
            f.write(json.dumps({"ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "session_id": event.get("session_id"), "hook": "send-gate", "decision": decision,
                                "tool": event.get("tool_name"), "why": reason, "job": job or None}) + "\n")
    except OSError:
        pass


def main():
    job = os.environ.get("CBRAIN_JOB", "")
    try:
        event = json.loads(sys.stdin.read() or "{}")
        reason = decide(event, job)
    except Exception as e:   # fail closed
        event, reason = {}, f"send gate could not verify ({type(e).__name__}); not sending"
    trace(event, job, "deny" if reason else "allow", reason)
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": f"send gate: {reason}."}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
