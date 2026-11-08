"""Knock to the phone: when you're away from the Mac, a knock also goes out as an iMessage to yourself.

The gateway idea from Hermes Agent, cut down to what the knock needs. Three rules:
  content  count and kind only ("Jarvis: 2 need you — 1 urgent. Mail, Plan"). Never a title, a name or a summary:
           titles carry client names, and employer content doesn't leave the Mac (your call, 2026-10-27).
           One exception: daily-intel learn_podcasts.py sends its episode titles (public research, your call
           2026-10-31), gated by outbound_gate.
  when     only on a knock (so the knock budget caps it: 2 an hour, 8 a day), and only when the keyboard and mouse
           have been idle for AWAY_S. At the desk the spoken knock is enough.
  where    Messages.app on this Mac, to the handle in ~/.config/cbrain/imessage-to (your own phone number or Apple
           ID, one line). No file, no push. End-to-end encrypted; no bot, no token, no third-party server.
Test: uv run webapp/push.py test   (sends one fixed test message, idle or not)
"""
import subprocess
import sys
from pathlib import Path

HANDLE_F = Path.home() / ".config" / "cbrain" / "imessage-to"
AWAY_S = 600
KINDS = {"mail": "Mail", "ready": "Ready", "plan": "Plan", "research": "Research", "meeting": "Meeting",
         "briefing": "Briefing", "idea": "Idea", "role": "Role"}
SEND = ['on run argv',
        'tell application "Messages" to send (item 1 of argv) to participant (item 2 of argv) of '
        '(1st account whose service type = iMessage)',
        'end run']


def handle():
    try:
        return HANDLE_F.read_text().strip()
    except OSError:
        return ""


def idle_s():
    """Seconds since the last keyboard or mouse input (IOHIDSystem), 0 if unreadable (counts as present)."""
    try:
        out = subprocess.run(["ioreg", "-c", "IOHIDSystem"], capture_output=True, text=True, timeout=5).stdout
        return next(int(line.split("=")[-1]) // 10**9 for line in out.splitlines() if "HIDIdleTime" in line)
    except Exception:
        return 0


def text(kinds, urgent):
    """The whole message: a count, the urgent count, and the kinds. Nothing from the items themselves."""
    seen = list(dict.fromkeys(KINDS.get(k, "Item") for k in kinds))
    head = f"Jarvis: {len(kinds)} need{'s' if len(kinds) == 1 else ''} you"
    return f"{head}{f' — {urgent} urgent' if urgent else ''}. {', '.join(seen)}"


def send(msg):
    to = handle()
    if not to:
        return False
    subprocess.Popen(["osascript", *sum((["-e", line] for line in SEND), []), msg, to],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


def knock(kinds, urgent):
    """Called by jarvis.knock: pushes only when you're away."""
    if idle_s() >= AWAY_S:
        send(text(kinds, urgent))


if __name__ == "__main__" and sys.argv[1:] == ["test"]:
    if not handle():
        sys.exit(f"no handle: put your phone number or Apple ID in {HANDLE_F}")
    r = subprocess.run(["osascript", *sum((["-e", line] for line in SEND), []), "Jarvis: test push from the Mac.", handle()],
                       capture_output=True, text=True)
    print(r.stderr.strip() or f"sent to {handle()} (idle now: {idle_s()} s)")
