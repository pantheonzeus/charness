#!/usr/bin/env python3
"""Queue NotebookLM studio artifacts from a jobs file and record their ids.

Usage (from the repo root):
  python3 create_artifacts.py --run-dir output/.runs/<slug> --notebook <id> --jobs <run-dir>/jobs.json [--only K1,K2] [--profile default]

jobs.json: [{"key", "kind": audio|video|infographic|slides|quiz|flashcards, "title", "opts": [...cli flags],
             "src": [source ids], "prompt": "..."}]
Writes/updates <run-dir>/artifacts.json: {key: {artifact_id, kind, title}}. A re-run with --only regenerates those keys.
"""
import argparse, json, pathlib, subprocess, time

LANG_KINDS = ("audio", "video", "infographic", "slides")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--notebook", required=True)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--profile", default="default")
    ap.add_argument("--language", default="en")
    a = ap.parse_args()
    run = pathlib.Path(a.run_dir)
    out = run / "artifacts.json"
    arts = json.loads(out.read_text()) if out.exists() else {}
    only = set(filter(None, a.only.split(",")))
    for j in json.loads(pathlib.Path(a.jobs).read_text()):
        if only and j["key"] not in only:
            continue
        cmd = ["nlm", j["kind"], "create", a.notebook, *j.get("opts", []), "--focus", j["prompt"],
               "--source-ids", ",".join(j["src"]), "-y", "--json", "--profile", a.profile]
        if j["kind"] in LANG_KINDS:
            cmd += ["--language", a.language]
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            res = json.loads(r.stdout)
            arts[j["key"]] = {"artifact_id": res["artifact_id"], "kind": j["kind"], "title": j["title"]}
            print(j["key"], res.get("status"), flush=True)
        except (json.JSONDecodeError, KeyError):
            print(j["key"], "ERROR", (r.stdout + r.stderr)[-300:], flush=True)
        out.write_text(json.dumps(arts, indent=1))
        time.sleep(3)


if __name__ == "__main__":
    main()
