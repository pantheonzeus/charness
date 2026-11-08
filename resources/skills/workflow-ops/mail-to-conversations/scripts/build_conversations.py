#!/usr/bin/env python3
"""Turn fetched Gmail (JSON from fetch_gmail.py) into vault artefacts:

- one note per email       -> Mail/msgs/<YYYYMMDD>-<subject>-<id8>.md
- one conversation index   -> Mail/Conversations.md  (grouped by thread, newest first)
- sender contacts linked   -> Clients/<Name>.md gets a `## Mail` section of its threads

Append-only on existing contact notes. Idempotent (existing msg notes skipped).

  python3 build_conversations.py --sources /tmp/mail.json --vault cbrain \
    --domain-map employers/<active>/mail-to-conversations/domain_map.yaml [--dry-run]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def default_self_email():
    """Your own address, kept out of the repo: $CHARNESS_SELF_EMAIL, else this clone's
    `git config charness.selfEmail` (.git/config is never committed)."""
    if os.environ.get("CHARNESS_SELF_EMAIL"):
        return os.environ["CHARNESS_SELF_EMAIL"]
    try:
        return subprocess.run(["git", "config", "--get", "charness.selfEmail"], cwd=Path(__file__).parent,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""

PERSONAL = {"gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "icloud.com", "me.com", "yahoo.com"}


def safe_filename(t):
    t = re.sub(r'[/:*?"<>|]', "-", t or ""); t = re.sub(r"\s+", " ", t).strip()
    return t[:110].rstrip(" -")


def slugify(t):
    s = re.sub(r"[^A-Za-z0-9]+", "-", t or "").strip("-")
    return (s[:60].rstrip("-")) or "mail"


def clean_subject(s):
    return re.sub(r"^((re|aw|fwd|wg|fw|antw)\s*:\s*)+", "", (s or "").strip(), flags=re.I) or "(no subject)"


def load_domain_map(path):
    m = {}
    if path and Path(path).exists():
        for line in Path(path).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" in line:
                k, v = line.split(":", 1)
                k, v = k.strip().strip('"').lower(), v.strip().strip('"')
                if k and v:
                    m[k] = v
    return m


def company(domain, dmap):
    if not domain:
        return ""
    if domain in dmap:
        return dmap[domain]
    if domain in PERSONAL:
        return ""
    parts = domain.split(".")
    label = parts[-2] if len(parts) >= 2 else parts[0]
    return label.replace("-", " ").title()


def disp(name, email):
    n = (name or "").strip()
    # Gmail on-behalf / mailing-list senders arrive as "'Real Name' via listhandle"
    # (e.g. "'Example Corp' via purchase-orders.acme"). Keep the real display name;
    # drop the ' via <handle>' annotation and the stray surrounding quotes.
    n = re.sub(r"\s+via\s+.*$", "", n, flags=re.I).strip().strip("'\"").strip()
    if n and "@" not in n:
        # '/' and '\' are illegal in filenames and break [[wikilink]] resolution
        # (Obsidian reads '/' as a path separator) — keep link text == filename.
        return n.strip('"').replace("/", "-").replace("\\", "-")
    if email:
        return re.sub(r"[._-]+", " ", email.split("@")[0]).title()
    return n or "Unknown"


def msg_body(m):
    """Prefer a full body if the fetch captured one, else fall back to the snippet.
    fetch_gmail.py / mcp_gmail_to_sources.py emit `snippet` today; when they are extended
    to carry the parsed plaintext body (`body_text`/`body`), notes fill in automatically."""
    return (m.get("body_text") or m.get("body") or m.get("snippet") or "").strip()


def index_existing_contacts(clients_dir):
    by_email = {}
    if clients_dir.exists():
        for f in clients_dir.glob("*.md"):
            try:
                txt = f.read_text()
            except Exception:
                continue
            for mt in re.finditer(r"\*\*Email:\*\*\s*(\S+@\S+)", txt):
                by_email[mt.group(1).strip().lower()] = f
    return by_email


def first_recipient(to):
    if not to:
        return ""
    first = to.split(",")[0]
    m = re.search(r"<([^>]+)>", first)
    return (m.group(1) if m else first).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--vault", default=".")
    ap.add_argument("--domain-map")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--exclude-noise", action="store_true",
                    help="drop calendar-notification emails + automated/no-reply senders")
    ap.add_argument("--exclude-senders", default="",
                    help="extra comma-separated sender addresses to drop entirely")
    ap.add_argument("--self-email", default=default_self_email(),
                    help="your address — kept in threads, but not made into a contact "
                         "(default: $CHARNESS_SELF_EMAIL or git config charness.selfEmail)")
    args = ap.parse_args()
    self_email = args.self_email.strip().lower()

    _CAL = re.compile(r"^(invitation|accepted|declined|tentative|tentatively accepted|"
                      r"updated invitation|cancell?ed|canceled|new event|reminder|"
                      r"proposed new time|new updates|automatic reply|out of office)\b", re.I)
    # Functional / distribution-list / no-reply local-parts. Matched on a leading token
    # (prefix + separator/end) so 'purchase-orders.acme' and 'team-acme' are caught
    # while real names ('jane.doe') are not. Used both to drop noise messages
    # (--exclude-noise) and, always-on, to keep functional senders out of Clients/.
    _AUTO_LOCAL = re.compile(
        r"^(no-?reply|noreply|do-?not-?reply|invoicing|invoice|billing|info|info-de|"
        r"notifications?|mailer|mailer-daemon|postmaster|bounce|purchase-?orders?|"
        r"accounts-?payable|calendar|events?|team|teams|support|helpdesk|newsletter|"
        r"mailing|group|marketing|supervisors?|developers?|staff|department|"
        r"calendar-notification)([._-]|$)|-admin-group$", re.I)

    def _functional(email):
        e = (email or "").lower()
        # local-part functional token, or a *.onmicrosoft.com tenant routing / list address
        return bool(_AUTO_LOCAL.match(e.split("@")[0])) or e.split("@")[-1].endswith(".onmicrosoft.com")
    extra_drop = {s.strip().lower() for s in args.exclude_senders.split(",") if s.strip()}

    def is_noise(m):
        if _CAL.match(m.get("subject", "")):
            return True
        em = (m.get("from_email") or "").lower()
        if em in extra_drop:
            return True
        local = em.split("@")[0]
        return bool(_AUTO_LOCAL.match(local))

    vault = Path(args.vault)
    mail_dir = vault / "Mail"
    msgs_dir = mail_dir / "msgs"
    clients_dir = vault / "Clients"
    dmap = load_domain_map(args.domain_map) if args.domain_map else {}
    if not args.dry_run:
        msgs_dir.mkdir(parents=True, exist_ok=True)
        clients_dir.mkdir(parents=True, exist_ok=True)

    data = json.load(open(args.sources))
    messages = data.get("messages", [])
    if args.exclude_noise:
        before = len(messages)
        messages = [m for m in messages if not is_noise(m)]
        sys.stderr.write("Noise filter: dropped %d of %d messages (calendar/automated)\n"
                         % (before - len(messages), before))
    existing = index_existing_contacts(clients_dir)
    existing_name = {em: p.stem for em, p in existing.items()}   # email -> canonical contact name

    def person_link(email, raw_name):
        """Render a sender/participant as a link that resolves to the real contact file."""
        e = (email or "").strip().lower()
        if e == self_email:
            return "you"
        if e in existing_name:                      # reuse the contact that already exists
            return f"[[{existing_name[e]}]]"
        if _functional(e):                          # functional/list sender — plain text, not a contact
            return disp(raw_name, email)
        return f"[[{disp(raw_name, email)}]]"

    run_contacts = {}                 # email -> (path, display name)
    actions = []
    msg_created = msg_skipped = new_contacts = 0

    # group by thread
    threads = defaultdict(list)
    for m in messages:
        threads[m["thread_id"]].append(m)
    for tid in threads:
        threads[tid].sort(key=lambda x: x["internal_ms"])
    # order threads by most-recent message desc
    thread_order = sorted(threads, key=lambda t: max(x["internal_ms"] for x in threads[t]), reverse=True)

    # msg id -> note basename (for linking); thread -> subject label + participants
    msg_note = {}
    thread_subject = {}
    thread_people = defaultdict(set)   # tid -> set of (email, name)

    # ---- pass 1: per-email notes + resolve/append sender contacts ----
    for m in messages:
        email = (m["from_email"] or "").lower()
        name = disp(m["from_name"], m["from_email"])
        comp = company(m["from_domain"], dmap)
        date_iso = (m["date"] or "")[:10]
        ymd = date_iso.replace("-", "")
        subj = m["subject"]
        base = f"{ymd}-{slugify(clean_subject(subj))}-{m['id'][:8]}"
        msg_note[m["id"]] = base
        thread_people[m["thread_id"]].add((email, name))

        note_path = msgs_dir / f"{base}.md"
        if note_path.exists():
            msg_skipped += 1
        else:
            fm = (
                "---\ntype: mail\nprovenance: untrusted-ingest\n"
                f'date: {date_iso}\nfrom: "{m["from_email"]}"\n'
                f'subject: "{subj.replace(chr(34), chr(39))}"\n'
                f'thread_id: "{m["thread_id"]}"\nmessage_id: "{m["message_id"]}"\n---\n\n'
            )
            slink = person_link(email, m["from_name"])
            body = (
                f"# ✉ {subj}\n\n"
                f"**From:** {slink} <{m['from_email']}>" + (f" · {comp}" if comp else "") + "\n"
                f"**To:** {m['to']}\n" + (f"**Cc:** {m['cc']}\n" if m['cc'] else "") +
                f"**Date:** {m['date']}\n"
                f"**Conversation:** [[Conversations#{clean_subject(subj)}]]\n\n"
                f"> {msg_body(m)}\n\n"
                f"## Links\n- Conversation: [[Conversations#{clean_subject(subj)}]]\n- Sender: {slink}\n"
            )
            actions.append(f"  CREATE  Mail/msgs/{note_path.name}")
            if not args.dry_run:
                note_path.write_text(fm + body)
            msg_created += 1

        # resolve sender contact (dedup by email; never make a contact of yourself or a
        # functional/distribution-list sender)
        if email and email != self_email and not _functional(email) and email not in run_contacts:
            if email in existing:
                target = existing[email]
            else:
                target = clients_dir / f"{safe_filename(name)}.md"
            run_contacts[email] = (target, name, comp)

    # thread subject label = cleaned subject of latest msg
    for tid in threads:
        latest = threads[tid][-1]
        thread_subject[tid] = clean_subject(latest["subject"])

    # ---- pass 2: Conversations index ----
    lines = ["---\ntype: index\nstatus: active\ntags: [index, mail]\n---",
             f"# Conversations\n",
             f"*{len(messages)} messages · {len(threads)} conversations · from {data.get('query','')}*\n"]
    # map email->display name for participant links
    email_name = {e: n for (e, n) in {p for s in thread_people.values() for p in s}}
    for tid in thread_order:
        msgs = threads[tid]
        subj = thread_subject[tid]
        parts = sorted({person_link(e, n) for (e, n) in thread_people[tid] if e})
        lines.append(f"## {subj}")
        lines.append(f"*{len(msgs)} message(s)* · Participants: " + ", ".join(parts))
        for mm in reversed(msgs):   # newest first within a thread
            sender = disp(mm["from_name"], mm["from_email"])
            to1 = first_recipient(mm["to"])
            snip = msg_body(mm)[:140]
            lines.append(f"- {(mm['date'] or '')[:16].replace('T',' ')} · **{sender}** → {to1} · "
                         f"[[{msg_note[mm['id']]}|open]] — {snip}")
        lines.append("")
    conv_md = "\n".join(lines)
    conv_path = mail_dir / "Conversations.md"
    actions.append(f"  WRITE   Mail/Conversations.md ({len(threads)} conversations)")
    if not args.dry_run:
        conv_path.write_text(conv_md)

    # ---- pass 3: link each sender contact to its threads (clean, bidirectional) ----
    sender_threads = defaultdict(set)   # email -> set(tid)
    for m in messages:
        if m["from_email"]:
            sender_threads[m["from_email"].lower()].add(m["thread_id"])

    for email, (target, name, comp) in run_contacts.items():
        tids = sorted(sender_threads.get(email, []),
                      key=lambda t: max(x["internal_ms"] for x in threads[t]), reverse=True)
        mail_links = [f"- [[Conversations#{thread_subject[t]}]] ({len(threads[t])} msg)" for t in tids]
        mail_block = "## Mail\n" + "\n".join(mail_links) + "\n"
        if target.exists():
            txt = target.read_text()
            # append only links not already present
            new_links = [l for l in mail_links if l.split("]]")[0] not in txt]
            if new_links:
                if "## Mail" in txt:
                    txt = re.sub(r"(## Mail\s*\n)", r"\1" + "\n".join(new_links) + "\n", txt, count=1)
                else:
                    txt = txt.rstrip() + "\n\n" + "## Mail\n" + "\n".join(new_links) + "\n"
                actions.append(f"  APPEND  Clients/{target.name}  (+{len(new_links)} mail link)")
                if not args.dry_run:
                    target.write_text(txt)
        else:
            fm = ["---", "type: person", "status: new"]
            if comp:
                fm.append(f'company: "{comp}"')
            fm += ["---", ""]
            fields = list(fm) + [f"# {name}", ""]
            if comp:
                fields.append(f"**Company:** {comp}")
            fields.append(f"**Email:** {email}")
            fields.append("**Status:** New (from email)")
            body = "\n".join(fields) + "\n\n## Notes\n\n" + mail_block
            actions.append(f"  CREATE  Clients/{target.name}")
            if not args.dry_run:
                target.write_text(body)
            new_contacts += 1

    hdr = "DRY RUN — no files written\n" if args.dry_run else ""
    sys.stdout.write(hdr + "\n".join(actions) + "\n")
    sys.stdout.write("\nSummary: %d messages · %d conversations · %d msg notes created (%d existed) · %d new contacts\n"
                     % (len(messages), len(threads), msg_created, msg_skipped, new_contacts))


if __name__ == "__main__":
    main()
