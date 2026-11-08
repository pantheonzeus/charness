# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["mlx-audio", "misaki[en]", "soundfile", "numpy"]
# ///
"""Deterministic half of the briefing podcast: validate the two-host script, then voice it.

  uv run podcast.py check  output/briefings/<date>.podcast.json   validate; prints OK or the errors (exit 1)
  uv run podcast.py render <date>                                  voice the script -> output/briefings/<date>.mp3

Voices run on-device (Kokoro-82M via MLX, same model as the console's voice.py); the MP3 is
served to the phone by the console (webapp/server.py, /api/briefings/<date>/podcast).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
BRIEFINGS = REPO / "output" / "briefings"
TTS_MODEL = "mlx-community/Kokoro-82M-bf16"
HOSTS = {"A": ("Maya", "af_heart"), "B": ("Ben", "am_michael")}
SPEED = 1.0
MIN_WORDS, MAX_WORDS = 1500, 4000          # ~10-25 minutes spoken
RATE = 24000
GAP_SWITCH, GAP_SAME, GAP_SEGMENT = 0.32, 0.15, 0.8   # seconds of silence


def check(path):
    errors = []
    try:
        p = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return ["cannot read JSON: %s" % e]
    date = p.get("date", "")
    if not Path(path).name == "%s.podcast.json" % date:
        errors.append("date %r does not match filename %s" % (date, Path(path).name))
    try:
        brief = json.loads((BRIEFINGS / f"{date}.json").read_text())
    except (OSError, ValueError):
        return errors + ["no readable briefing output/briefings/%s.json to ground the script in" % date]
    items = {it["id"]: it for s in brief["sections"] for it in s["items"]}
    allowed = {x["url"] for it in items.values() for x in it.get("sources", [])}
    allowed |= {x["source"] for s in brief["sections"] for x in s.get("indicators", [])}
    allowed |= {str(u) for u in p.get("extra_sources", [])}
    if not str(p.get("title", "")).strip():
        errors.append("missing title")
    segs = p.get("segments") or []
    if not segs:
        errors.append("no segments")
    words, covered = 0, set()
    for n, seg in enumerate(segs):
        item = seg.get("item")
        if item is not None and item not in items:
            errors.append("segment %d: item %r is not in the briefing" % (n, item))
        covered.add(item)
        turns = seg.get("turns") or []
        if not turns:
            errors.append("segment %d: no turns" % n)
        for t, turn in enumerate(turns):
            where = "segment %d turn %d" % (n, t)
            text = str(turn.get("text", ""))
            words += len(text.split())
            if turn.get("speaker") not in HOSTS:
                errors.append("%s: speaker must be one of %s" % (where, list(HOSTS)))
            if not text.strip():
                errors.append("%s: empty text" % where)
            if re.search(r"https?://|www\.|\[\[|[*_#`|]", text):
                errors.append("%s: URL, wikilink or markdown in spoken text" % where)
            src = turn.get("src") or []
            for u in src:
                if u not in allowed:
                    errors.append("%s: src %s is neither a briefing source nor in extra_sources" % (where, u))
            # Numbers are where a script goes wrong; every turn that states one must cite it.
            if re.search(r"\d", text) and not src:
                errors.append("%s: states a number but has no src" % where)
    missing = [i for i in items if i not in covered]
    if missing:
        errors.append("briefing items never discussed: %s" % ", ".join(missing))
    if not MIN_WORDS <= words <= MAX_WORDS:
        errors.append("%d spoken words; keep it between %d and %d" % (words, MIN_WORDS, MAX_WORDS))
    return errors


def render(date):
    import numpy as np
    from mlx_audio.tts.utils import load_model

    src = BRIEFINGS / f"{date}.podcast.json"
    errors = check(src)
    if errors:
        sys.exit("script fails check — fix it first:\n  " + "\n  ".join(errors))
    p = json.loads(src.read_text())
    model = load_model(TTS_MODEL)
    silence = lambda s: np.zeros(int(RATE * s), dtype=np.float32)
    out, last = [], None
    for n, seg in enumerate(p["segments"]):
        if n:
            out.append(silence(GAP_SEGMENT))
        for turn in seg["turns"]:
            if last is not None:
                out.append(silence(GAP_SWITCH if turn["speaker"] != last else GAP_SAME))
            voice = HOSTS[turn["speaker"]][1]
            out += [np.array(r.audio, dtype=np.float32) for r in model.generate(text=turn["text"], voice=voice, speed=SPEED)]
            last = turn["speaker"]
    audio = np.concatenate(out)
    mp3 = BRIEFINGS / f"{date}.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(RATE), "-ac", "1", "-i", "-",
                    "-codec:a", "libmp3lame", "-b:a", "96k",
                    "-metadata", f"title={p['title']}", "-metadata", "artist=cbrain briefing",
                    "-metadata", f"date={date}", str(mp3)],
                   input=audio.tobytes(), check=True)
    print("OK %s (%d:%02d)" % (mp3.relative_to(REPO), len(audio) // RATE // 60, len(audio) // RATE % 60))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        errs = check(sys.argv[2])
        print("OK" if not errs else "\n".join(errs))
        sys.exit(1 if errs else 0)
    if len(sys.argv) == 3 and sys.argv[1] == "render":
        render(sys.argv[2])
    else:
        sys.exit(__doc__)
