"""Play a learning podcast on the Mac from a text: the reply to the morning list Jarvis sends (learn_podcasts.py).

  "play 2" (or just "2" on the day of the list)   the second episode in that list (learn packs with a downloaded .m4a)
  "play humanoids"           the episode whose topic or title shares the most words with the request
  "stop" / "pause"           stops the episode, only while one is playing (otherwise the text goes to Jarvis)
Handled before the language model: deterministic, instant, no agent cost. Plays through afplay like Jarvis's
speech, and not while the meeting shield has speech off.
"""
import json
import re
import subprocess
from datetime import date
from pathlib import Path

BRIEFINGS = Path(__file__).resolve().parents[1] / "output" / "briefings"
P = {"player": None, "title": ""}


def episodes():
    """(date, [(label, file)]) for the newest briefing that has learning podcasts, in the order the iMessage listed them."""
    for f in sorted(BRIEFINGS.glob("????-??-??.json"), reverse=True):
        learn = BRIEFINGS / f.stem / "learn"
        if not learn.is_dir():
            continue
        b = json.loads(f.read_text())
        titles = {s["id"]: s["title"] for s in b["sections"]}
        out = [(f"{titles.get(p['section'], p['section'])}: {p['title']}", learn / f"{p['section']}.m4a")
               for p in b.get("learn") or [] if (learn / f"{p['section']}.m4a").exists()]
        if out:
            return f.stem, out
    return "", []


def playing():
    return P["player"] is not None and P["player"].poll() is None


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3}


def handle(text, speak_ok, send):
    """True if the text was a podcast command (and is answered here); False lets it go on to Jarvis."""
    t = text.strip().lower().rstrip(".!")
    if re.fullmatch(r"(stop|pause|stopp)( it| the podcast)?", t):
        if not playing():
            return False
        P["player"].kill()
        send("Jarvis: stopped.")
        return True
    m = re.fullmatch(r"(?:play|listen to|spiel)\s+(?:#|no\.?|number|nr\.?)?\s*(.+)", t)
    day, eps = episodes()
    if not m and re.fullmatch(r"\d{1,2}", t) and day == date.today().isoformat():   # a bare number answers today's list
        m = re.fullmatch(r"(\d{1,2})", t)
    if not m:
        return False
    if not eps:
        send("Jarvis: no learning podcasts downloaded yet.")
        return True
    want = m.group(1)
    if want.isdigit():
        pick = eps[int(want) - 1] if 1 <= int(want) <= len(eps) else None
    else:
        score, best = max(((len(words(want) & words(label)), (label, f)) for label, f in eps), key=lambda x: x[0])
        pick = best if score else None
    if not pick:
        send(f"Jarvis: no episode matches. Reply with a number, 1 to {len(eps)}.")
        return True
    if not speak_ok:
        send("Jarvis: speech is off on the Mac (meeting shield). Not playing.")
        return True
    if playing():
        P["player"].kill()
    P["player"], P["title"] = subprocess.Popen(["afplay", str(pick[1])]), pick[0]
    send(f"Jarvis: playing {pick[0]}. Text stop to end it.")
    return True
