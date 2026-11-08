# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["mlx-audio", "misaki[en]", "soundfile", "numpy", "markdown"]
# ///
"""Render a deliverable in output/ into a PDF or an MP3, next to the source (same stem).

  uv run scripts/render.py pdf   output/plans/<file>.html|.md    headless Chrome -> <file>.pdf
  uv run scripts/render.py audio output/plans/<file>.md          on-device voices -> <file>.mp3

pdf:   an .md with a same-stem .html prints the .html (it carries the designed layout);
       otherwise the markdown is converted to plain print HTML first.
audio: lines like **MAYA:** / **BEN:** become a two-host podcast; [bracketed] reviewer tags and
       anything outside a speaker turn are not voiced. A file without speaker turns is narrated
       by one voice. Voices are the briefing podcast's (daily-intel-briefing/scripts/podcast.py).
Used by the console (webapp/tasks.py) and by the researcher / plan-runner agents.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
sys.path.insert(0, str(REPO / "resources/skills/workflow-ops/daily-intel-briefing/scripts"))

PRINT_CSS = """body{font:11pt/1.55 Georgia,serif;max-width:46em;margin:0 auto;color:#111}
h1,h2,h3{font-family:-apple-system,Helvetica,sans-serif;line-height:1.25}h1{font-size:20pt}
table{border-collapse:collapse;font-size:9.5pt}td,th{border:1px solid #bbb;padding:4px 6px;vertical-align:top}
code{font-size:9.5pt}blockquote{border-left:3px solid #bbb;margin-left:0;padding-left:1em;color:#444}
@page{margin:18mm 16mm}"""


def source(arg, suffixes):
    path = (REPO / arg).resolve()
    if not str(path).startswith(str(OUTPUT) + "/") or path.suffix not in suffixes or not path.is_file():
        sys.exit(f"not a {'/'.join(suffixes)} file under output/: {arg}")
    return path


def pdf(arg):
    import markdown

    src = source(arg, (".html", ".md"))
    html = src.with_suffix(".html")
    tmp = None
    if src.suffix == ".md" and not html.is_file():
        body = markdown.markdown(src.read_text(), extensions=["tables", "fenced_code", "sane_lists"])
        tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False)
        tmp.write(f"<!doctype html><meta charset=utf-8><title>{src.stem}</title><style>{PRINT_CSS}</style>{body}")
        tmp.close()
        html = Path(tmp.name)
    out = src.with_suffix(".pdf")
    try:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", html.as_uri()], check=True, capture_output=True, timeout=120)
    finally:
        if tmp:
            Path(tmp.name).unlink(missing_ok=True)
    print("OK", out.relative_to(REPO))


def clean(text):
    text = re.sub(r"\[[^\]]*\]", "", text)                       # [verified], [likely, range] …
    text = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", text)  # wikilinks
    text = re.sub(r"\(https?://[^)]*\)", "", text)
    text = re.sub(r"[*_`#>|]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def turns_of(md):
    """[(speaker, text)] from **NAME:** turns; [] when the file has none."""
    turns, cur = [], None
    for line in md.splitlines():
        m = re.match(r"\s*\*\*([A-Z][A-Za-z .'-]{0,30}):\*\*\s*(.*)", line)
        if m:
            cur = [m.group(1).strip().title(), m.group(2)]
            turns.append(cur)
        elif cur and line.strip() and not line.lstrip().startswith(("#", "---")):
            cur[1] += " " + line.strip()
        else:
            cur = None
    return [(s, clean(t)) for s, t in turns if clean(t)]


def narration_of(md):
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)         # frontmatter
    paras = [clean(p) for p in re.split(r"\n\s*\n", md)]
    return [("Narrator", p) for p in paras if p and not re.fullmatch(r"[-=: ]*", p)]


def audio(arg):
    import numpy as np
    from mlx_audio.tts.utils import load_model
    from podcast import HOSTS, TTS_MODEL, RATE, SPEED, GAP_SWITCH, GAP_SAME, GAP_SEGMENT

    src = source(arg, (".md",))
    md = src.read_text()
    turns = turns_of(md) or narration_of(md)
    if not turns:
        sys.exit("nothing to voice")
    named = {name.title(): voice for name, voice in HOSTS.values()}   # Maya, Ben
    pool, voices = list(named.values()), {}
    for s, _ in turns:
        voices.setdefault(s, named.get(s) or pool[len(voices) % len(pool)])
    model = load_model(TTS_MODEL)
    silence = lambda s: np.zeros(int(RATE * s), dtype=np.float32)
    out, last = [], None
    for speaker, text in turns:
        if last is not None:
            out.append(silence(GAP_SEGMENT if speaker == "Narrator" else GAP_SWITCH if speaker != last else GAP_SAME))
        out += [np.array(r.audio, dtype=np.float32) for r in model.generate(text=text, voice=voices[speaker], speed=SPEED)]
        last = speaker
    wav = np.concatenate(out)
    mp3 = src.with_suffix(".mp3")
    title = next((l.lstrip("# ").strip() for l in md.splitlines() if l.startswith("# ")), src.stem)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(RATE), "-ac", "1", "-i", "-",
                    "-codec:a", "libmp3lame", "-b:a", "96k", "-metadata", f"title={title}",
                    "-metadata", "artist=cbrain", str(mp3)], input=wav.tobytes(), check=True)
    print("OK %s (%d:%02d)" % (mp3.relative_to(REPO), len(wav) // RATE // 60, len(wav) // RATE % 60))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("pdf", "audio"):
        {"pdf": pdf, "audio": audio}[sys.argv[1]](sys.argv[2])
    else:
        sys.exit(__doc__)
