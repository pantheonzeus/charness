"""Meeting shield: is it OK to speak or listen right now? (JARVIS spec v1, §1)

Signals, all in RAM (never written anywhere):
  CAL    a calendar event now: not all-day, not declined, at least one other attendee (events.json)
  CALL   a call app using the mic (Zoom, Teams, Slack huddle, FaceTime, Webex)
  BMIC   a browser using the mic (Chrome/Safari/…): the console captures natively, so this is someone's call
  MEET   a meet.google.com room tab is open (weak: a left-open tab must not shield all afternoon)
  UNK    any other process holding the mic for ≥ 10 s
  SHIELD the principal's manual shield ("I'm with someone"), up to 2 h
Fast into the shield, slow out of it (60 s of no strong signal). When unsure, stay quiet.
The native helper (native/presence.swift) reports facts; this module decides.
"""
import json
import os
import re
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
HELPER_SRC = HERE / "native" / "presence.swift"
HELPER = HERE / "native" / "bin" / "presence"
EVENTS = REPO / "output" / "meetings" / "events.json"
MEETINGS = REPO / "output" / "meetings" / "meetings.json"

CALL_APPS = re.compile(r"^(us\.zoom|com\.microsoft\.teams|com\.tinyspeck\.slackmacgap|com\.cisco\.webex|com\.apple\.FaceTime"
                       r"|com\.apple\.avconferenced|com\.apple\.TelephonyUtilities|com\.hnc\.Discord|com\.skype)", re.I)
BROWSERS = re.compile(r"^(com\.google\.Chrome|com\.apple\.Safari|com\.apple\.WebKit|company\.thebrowser|org\.mozilla"
                      r"|com\.microsoft\.edgemac|com\.brave\.Browser|com\.operasoftware)", re.I)
IGNORE = re.compile(r"^(com\.apple\.(CoreSpeech|accessibility\.heard|SpeechRecognitionCore|corespeechd|siri))", re.I)
MEET_SCRIPT = '''if application "Google Chrome" is not running then return "no"
set urls to {}
tell application "Google Chrome"
  repeat with w in windows
    try
      if mode of w is not "incognito" then set urls to urls & (get URL of tabs of w)
    end try
  end repeat
end tell
repeat with u in urls
  set s to (u as text)
  if s contains "meet.google.com/" then
    set p to text ((offset of "meet.google.com/" in s) + 16) thru -1 of s
    if (length of p) ≥ 12 and character 4 of p is "-" and character 9 of p is "-" then return "yes"
  end if
end repeat
return "no"'''

UNK_HOLD, EXIT_HOLD, PRE_MIN, POST_MIN = 10, 60, 5, 10
STALE_S, DEAD_S, HEARTBEAT_S, SETTLE_S = 20 * 60, 2 * 3600, 15, 60


class Presence:
    def __init__(self, self_pids=()):
        self.self_pids = set(self_pids) | {os.getpid()}
        self.inputs, self.output = [], {}
        self.meet = False
        self.meet_ok = True               # AppleScript usable (permission, Chrome scriptable)
        self.beat = 0.0                   # last helper message
        self.helper_ok = False
        self.hotkey_ok = None
        self.woke = 0.0
        self.unk_since = {}               # pid -> first seen holding input
        self.shield_until = 0.0
        self.overrides = set()            # calendar uids the principal said "I'm not in this one"
        self.last_strong = 0.0
        self.in_meeting_since = None
        self.post_until = 0.0
        self.listeners = []               # callables(state dict) on every state change
        self.hotkey_listeners = []        # callables(down: bool, cancel: bool)
        self._last = None
        self._files = {}                  # path -> (mtime, parsed json)
        self.proc = None

    # ---------- signals ----------
    def _json(self, path):
        """Parsed once per change of the file: state() runs every second and per spoken sentence, and
        meetings.json is ~170 KB, so re-parsing it each time competed with the speaker thread."""
        mtime = path.stat().st_mtime
        hit = self._files.get(path)
        if hit is None or hit[0] != mtime:
            hit = self._files[path] = (mtime, json.loads(path.read_text()))
        return hit[1]

    def calendar(self, now=None):
        """(current event or None, next event start or None, age of the sync in seconds)."""
        now = now or time.time()
        try:
            synced = datetime.fromisoformat(self._json(MEETINGS)["synced_at"]).timestamp()
        except (OSError, ValueError, KeyError, TypeError):
            synced = 0
        try:
            events = self._json(EVENTS).get("events") or []
        except (OSError, ValueError):
            events = []
        cur, nxt = None, None
        for e in events:
            if e.get("all_day") or e.get("declined") or e.get("uid") in self.overrides:
                continue
            if not any(not a.get("is_current_user") for a in e.get("attendees") or []):
                continue                  # a solo block (focus time) is not a meeting
            try:
                s, t = datetime.fromisoformat(e["start"]).timestamp(), datetime.fromisoformat(e["end"]).timestamp()
            except (KeyError, ValueError):
                continue
            if s <= now < t:
                cur = cur or {"uid": e["uid"], "title": e.get("title", ""), "end": t}
            elif s > now and (nxt is None or s < nxt):
                nxt = s
        return cur, nxt, (now - synced) if synced else None

    def strong(self, now):
        sig = []
        for p in self.inputs:
            pid, b = p.get("pid"), p.get("bundle") or ""
            if pid in self.self_pids or IGNORE.match(b):
                continue
            if CALL_APPS.match(b):
                sig.append("huddle" if "slack" in b.lower() else "call")
            elif BROWSERS.match(b):
                sig.append("meet" if self.meet else "browser-call")
            else:
                first = self.unk_since.setdefault(pid, now)
                if now - first >= UNK_HOLD:
                    sig.append(f"mic:{b or pid}")
        live = {p.get("pid") for p in self.inputs}
        self.unk_since = {k: v for k, v in self.unk_since.items() if k in live}
        return sig

    # ---------- the state ----------
    def state(self, now=None):
        now = now or time.time()
        cur, nxt, age = self.calendar(now)
        sig = self.strong(now)
        if cur:
            sig.append("calendar")
        if self.shield_until > now:
            sig.append("manual")
        if sig:
            self.last_strong = now
            if self.in_meeting_since is None:
                self.in_meeting_since = now
        elif self.in_meeting_since is not None and now - self.last_strong >= EXIT_HOLD:
            self.in_meeting_since = None
            self.post_until = now + POST_MIN * 60
        pre = nxt is not None and nxt - now <= PRE_MIN * 60
        headset = bool(self.output.get("headphones"))
        reasons = sorted(set(sig))
        if not self.helper_ok or now - self.beat > HEARTBEAT_S:
            st = "UNKNOWN"
        elif now - self.woke < SETTLE_S:
            st = "SETTLING"
        elif self.in_meeting_since is not None:
            st = "IN-MEETING"
        elif pre:
            st = "PRE"
        elif age is None or age > DEAD_S:
            st = "DEAD-CAL"
        elif age > STALE_S:
            st = "STALE"
        elif self.meet:
            st = "QUIET"                  # a Meet tab is open but nobody uses the mic: no proactive speech
        elif now < self.post_until:
            st = "POST"
        else:
            st = "FREE"
        # Audio is the default. Nothing detected (a call, the calendar, a stale helper) silences the console:
        # it only says what it sees. Quiet happens only when you say so (the manual shield, by voice or a tap).
        quiet = self.shield_until > now
        free = not quiet
        seen = {"IN-MEETING": " · IN A CALL" if any(r != "calendar" for r in reasons) else " · MEETING ON THE CALENDAR",
                "PRE": " · MEETING SOON", "UNKNOWN": " · NO PRESENCE HELPER", "DEAD-CAL": " · CALENDAR OFFLINE"}.get(st, "")
        word = "QUIET · YOU SAID SO" if quiet else "ON AIR" + seen
        return {
            "state": st, "word": word, "reasons": reasons,
            "call": st == "IN-MEETING" and any(r != "calendar" for r in reasons),   # a real call, not just the calendar
            "speak": free,                                    # replies may be spoken
            "listen": True,                                   # the mic stays yours, even when quiet: so you can say "talk again"
            "proactive": free,                                # the crew may knock
            "blank": False,                                   # the screen is never blanked on its own
            "room": "PRIVATE" if headset and free else "OPEN",
            "headset": headset, "output": self.output.get("name", ""),
            "meeting_end": cur["end"] if cur else None, "meeting_uid": cur["uid"] if cur else None, "next_start": nxt, "calendar_age": age,
            "shield_until": self.shield_until if self.shield_until > now else None,
            "hotkey": self.hotkey_ok, "meet_detect": self.meet_ok,
        }

    def _changed(self):
        s = self.state()
        key = (s["state"], s["word"], s["room"], tuple(s["reasons"]), s["shield_until"])
        if key != self._last:
            self._last = key
            for f in list(self.listeners):
                try:
                    f(s)
                except Exception:
                    pass

    # ---------- inputs ----------
    def shield(self, minutes):
        m = max(0, min(int(minutes), 600))
        self.shield_until = time.time() + m * 60 if m else 0      # 0 = "talk again": quiet ends now
        self._changed()

    def override(self, uid):
        self.overrides.add(uid)
        self._changed()

    def on_message(self, m):
        self.beat, self.helper_ok = time.time(), True
        t = m.get("t")
        if t == "audio":
            self.inputs, self.output = m.get("inputs") or [], m.get("output") or {}
        elif t == "wake":
            self.woke = time.time()
        elif t == "hotkey":
            self.hotkey_ok = True
            for f in list(self.hotkey_listeners):
                f(bool(m.get("down")), bool(m.get("cancel")))
        elif t == "hotkey_unavailable":
            self.hotkey_ok = False
        elif t == "hotkey_ready":
            self.hotkey_ok = True
        self._changed()

    # ---------- runtime ----------
    def _build(self):
        if HELPER.exists() and HELPER.stat().st_mtime >= HELPER_SRC.stat().st_mtime:
            return True
        HELPER.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["swiftc", "-O", str(HELPER_SRC), "-o", str(HELPER)], capture_output=True, text=True)
        if r.returncode:
            print(f"presence helper did not build: {r.stderr[-400:]}", flush=True)
        return r.returncode == 0

    def _read(self):
        while True:
            if not self._build():
                return
            self.proc = subprocess.Popen([str(HELPER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            for line in self.proc.stdout:
                try:
                    self.on_message(json.loads(line))
                except ValueError:
                    pass
            self.helper_ok = False
            self._changed()
            time.sleep(2)                 # the helper died: restart it, stay quiet meanwhile (UNKNOWN)

    def _meet_loop(self):
        while True:
            try:
                r = subprocess.run(["osascript", "-e", MEET_SCRIPT], capture_output=True, text=True, timeout=2)
                self.meet_ok = r.returncode == 0
                self.meet = self.meet_ok and r.stdout.strip() == "yes"
            except subprocess.TimeoutExpired:
                self.meet_ok = False
            self._changed()
            time.sleep(3)

    def _tick(self):
        while True:                       # time-based transitions (exit hold, PRE, POST, staleness)
            time.sleep(1)
            self._changed()

    def start(self):
        for f in (self._read, self._meet_loop, self._tick):
            threading.Thread(target=f, daemon=True).start()
        return self


presence = Presence()
