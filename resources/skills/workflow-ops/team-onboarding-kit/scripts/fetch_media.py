#!/usr/bin/env python3
"""Poll a notebook, rename each finished studio artifact, download it. Run it in the background.

Usage (from the repo root):
  python3 fetch_media.py --run-dir output/.runs/<slug> --notebook <id> --out output/<slug>-media [--profile default] [--max-minutes 90]

Reads and updates <run-dir>/artifacts.json; a finished item gets "done": <path>. Re-runs skip finished items.
Gotcha: `nlm download` has no --profile flag; it uses the default profile. Quiz/flashcards download as JSON.
"""
import argparse, json, pathlib, re, subprocess, time

EXT = {"audio": "m4a", "video": "mp4", "infographic": "png", "slides": "pdf", "quiz": "json", "flashcards": "json"}
DL = {"slides": "slide-deck"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--notebook", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile", default="default")
    ap.add_argument("--max-minutes", type=int, default=90)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run_dir), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    arts_path = run / "artifacts.json"
    arts = json.loads(arts_path.read_text())

    def nlm(*args, prof=True):
        return subprocess.run(["nlm", *args, *(["--profile", a.profile] if prof else [])], capture_output=True, text=True)

    def slug(s):
        return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

    deadline = time.time() + a.max_minutes * 60
    while time.time() < deadline:
        st = {x["artifact_id"]: x["status"] for x in json.loads(nlm("studio", "status", a.notebook, "--json").stdout or "[]")}
        pending = 0
        for key, art in sorted(arts.items()):
            if art.get("done") or art.get("failed") or not art.get("artifact_id"):
                continue
            s = st.get(art["artifact_id"], "unknown")
            if s in ("completed", "ready", "done"):
                nlm("studio", "rename", art["artifact_id"], art["title"])
                path = out / f"{key}-{slug(art['title'])}.{EXT[art['kind']]}"
                extra = ["--format", "json"] if art["kind"] in ("quiz", "flashcards") else ["--no-progress"]
                r = nlm("download", DL.get(art["kind"], art["kind"]), a.notebook, "--id", art["artifact_id"],
                        "--output", str(path), *extra, prof=False)
                if path.exists() and path.stat().st_size > 0:
                    art["done"] = str(path)
                    print(f"{key} downloaded → {path}", flush=True)
                else:
                    print(f"{key} download failed: {(r.stdout + r.stderr)[-200:]}", flush=True)
                    pending += 1
            elif s in ("failed", "error"):
                art["failed"] = s
                print(f"{key} FAILED in NotebookLM", flush=True)
            else:
                pending += 1
        arts_path.write_text(json.dumps(arts, indent=1))
        if pending == 0:
            break
        time.sleep(60)
    left = [k for k, v in arts.items() if not v.get("done")]
    print(f"FINISHED: {len(arts) - len(left)}/{len(arts)} downloaded; not done: {left}", flush=True)


if __name__ == "__main__":
    main()
