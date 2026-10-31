#!/usr/bin/env python3
"""Generate NotebookLM audio overviews for notebooks touched today, then download them.

Extends the `notebooklm` skill: finds every notebook whose `updated_at` falls on
the target date (local) and that does NOT already have an audio overview, then
triggers `nlm audio create` for each. Idempotent — re-running skips notebooks
that already have (or are generating) an audio overview.

Second phase: for each matched notebook, wait until an audio overview finishes
generating, then download the `.m4a` into `output/podcasts/` (repo root).
Idempotent by filename — a file that already exists is never re-downloaded.

Third phase: for each matched notebook, fetch NotebookLM's auto-generated text
summary (`nlm describe notebook`) and write it next to the audio as
`<YYYYMMDD>-<slug>.summary.md`. Idempotent by filename. This is the raw handoff
queue the `distill-to-vault` workflow consumes to build linked vault notes.

Usage:
  python3 daily_audio.py                      # today: create + download + summarize
  python3 daily_audio.py --dry-run            # show targets, change nothing
  python3 daily_audio.py --date 2026-07-07    # a specific local date
  python3 daily_audio.py --format brief --length short --language de
  python3 daily_audio.py --no-download        # only create overviews, skip download
  python3 daily_audio.py --no-summary         # skip the summary phase
  python3 daily_audio.py --wait-timeout 0     # download only overviews already completed
  python3 daily_audio.py --podcast-dir /some/where   # override output dir

Requires the `nlm` CLI (notebooklm-mcp-cli) on PATH and valid Google auth.
Exits non-zero if any create or download fails, so a scheduler surfaces it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Repo root, resolved from this file's location so it works under launchd (cwd = /):
# <repo>/resources/skills/workflow-ops/notebooklm-daily-audio/scripts/daily_audio.py
REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_PODCAST_DIR = REPO_ROOT / "output" / "podcasts"


def run_nlm(args: list[str]) -> subprocess.CompletedProcess:
    """Run an `nlm ...` command, capturing output."""
    return subprocess.run(["nlm", *args], capture_output=True, text=True)


def local_date_of(updated_at: str):
    """Convert a NotebookLM `updated_at` (UTC ISO, e.g. 2026-07-07T06:57:53Z)
    to a local date. Returns None if it can't be parsed."""
    if not updated_at:
        return None
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().date()
    except ValueError:
        return None


def slugify(title: str) -> str:
    """Filesystem-safe slug from a notebook title."""
    s = re.sub(r"[^\w\s-]", "", (title or "").lower()).strip()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60] or "untitled"


def audio_artifacts(notebook_id: str) -> list[dict]:
    """All audio-type studio artifacts for a notebook (any status)."""
    proc = run_nlm(["studio", "status", notebook_id, "--json"])
    if proc.returncode != 0:
        print(f"  ! studio status failed for {notebook_id}: {(proc.stderr.strip() or proc.stdout.strip())}",
              file=sys.stderr)
        return []
    try:
        artifacts = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return []
    out = []
    for art in artifacts:
        if not isinstance(art, dict):
            continue
        blob = " ".join(
            str(art.get(k, "")) for k in ("type", "artifact_type", "name", "title", "kind")
        ).lower()
        if "audio" in blob or "overview" in blob:
            out.append(art)
    return out


def has_audio_overview(notebook_id: str) -> bool:
    """True if the notebook already has (or is generating) an audio overview.

    Used as the create gate: an in-progress overview counts, so a re-run won't
    re-trigger while generation is underway.
    """
    return bool(audio_artifacts(notebook_id))


def wait_for_completed_audio(notebook_id: str, timeout: int, interval: int) -> bool:
    """Poll until at least one audio artifact reports `completed`, or timeout.
    timeout <= 0 means: check once, don't wait."""
    deadline = time.monotonic() + max(timeout, 0)
    while True:
        arts = audio_artifacts(notebook_id)
        if any(str(a.get("status", "")).lower() == "completed" for a in arts):
            return True
        if timeout <= 0 or time.monotonic() >= deadline:
            return False
        time.sleep(interval)


def download_audio(notebook_id: str, dest: Path) -> subprocess.CompletedProcess:
    dest.parent.mkdir(parents=True, exist_ok=True)
    return run_nlm(["download", "audio", notebook_id, "-o", str(dest), "--no-progress"])


def fetch_summary(notebook_id: str) -> dict | None:
    """NotebookLM's AI-generated notebook summary + suggested topics.
    Returns the parsed JSON dict, or None if the call/parse fails."""
    proc = run_nlm(["describe", "notebook", notebook_id, "--json"])
    if proc.returncode != 0:
        print(f"  ! describe notebook failed for {notebook_id}: {(proc.stderr.strip() or proc.stdout.strip())}",
              file=sys.stderr)
        return None
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def write_summary_file(dest: Path, notebook_id: str, title: str, date_str: str,
                       audio_name: str, data: dict) -> None:
    """Write the raw notebook summary as a self-describing handoff artifact
    that the distill-to-vault workflow consumes. Frontmatter carries the
    idempotency key (notebook_id) and `distilled: false` queue flag."""
    # `nlm describe notebook` returns `summary` as a list of paragraph strings
    # (sometimes a single string); normalize either shape to text.
    raw = data.get("summary") or ""
    if isinstance(raw, list):
        summary = "\n\n".join(str(p).strip() for p in raw if str(p).strip())
    else:
        summary = str(raw).strip()
    topics = data.get("topics") or data.get("suggested_topics") or []
    if isinstance(topics, str):
        topics = [topics]
    topics_yaml = "[" + ", ".join(str(t) for t in topics) + "]"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        f"---\n"
        f"type: notebook-summary\n"
        f"notebook_id: {notebook_id}\n"
        f"notebook_title: {title}\n"
        f"date: {date_str}\n"
        f"topics: {topics_yaml}\n"
        f"audio: {audio_name}\n"
        f"distilled: false\n"
        f"---\n\n"
        f"# {title} — NotebookLM summary\n\n"
        f"{summary or '_(no summary returned by NotebookLM)_'}\n",
        encoding="utf-8",
    )


def list_notebooks() -> list[dict]:
    proc = run_nlm(["notebook", "list", "--json"])
    if proc.returncode != 0:
        print(f"ERROR: `nlm notebook list` failed: {(proc.stderr.strip() or proc.stdout.strip())}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as e:
        print(f"ERROR: could not parse notebook list JSON: {e}", file=sys.stderr)
        sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser(description="Daily NotebookLM audio overviews + download.")
    ap.add_argument("--date", help="Local target date YYYY-MM-DD (default: today).")
    ap.add_argument("--format", default="deep_dive",
                    help="Overview format: deep_dive|brief|critique|debate (default: deep_dive).")
    ap.add_argument("--length", default="default",
                    help="Length: short|default|long (default: default).")
    ap.add_argument("--language", default="en", help="BCP-47 language code (default: en).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would be created/downloaded, but change nothing.")
    ap.add_argument("--no-download", action="store_true",
                    help="Only create overviews; skip the download phase.")
    ap.add_argument("--no-summary", action="store_true",
                    help="Skip the summary phase (don't fetch/write .summary.md files).")
    ap.add_argument("--podcast-dir", default=str(DEFAULT_PODCAST_DIR),
                    help=f"Where to save .m4a files (default: {DEFAULT_PODCAST_DIR}).")
    ap.add_argument("--wait-timeout", type=int, default=900,
                    help="Max seconds to wait for a freshly-created overview to finish "
                         "before downloading (default: 900; 0 = download only completed).")
    ap.add_argument("--poll-interval", type=int, default=15,
                    help="Seconds between studio-status polls while waiting (default: 15).")
    args = ap.parse_args()

    if args.date:
        try:
            target = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"ERROR: --date must be YYYY-MM-DD, got {args.date!r}", file=sys.stderr)
            return 2
    else:
        target = datetime.now().astimezone().date()

    podcast_dir = Path(args.podcast_dir).expanduser()

    notebooks = list_notebooks()
    # "Idea · " notebooks belong to idea-engine/scripts/podcast.py, "Daily Intel · " ones to
    # daily-intel-briefing/scripts/learn_podcasts.py and "Research · " ones to notebooklm/scripts/task_media.py;
    # all download their own audio
    matched = [nb for nb in notebooks if local_date_of(nb.get("updated_at")) == target
               and not str(nb.get("title", "")).startswith(("Idea · ", "Daily Intel · ", "Research · "))]
    print(f"Target date {target}: {len(matched)} notebook(s) touched.", file=sys.stderr)

    # ---- Phase 1: create overviews for notebooks that have none ----
    skipped, created, would_create, errors = 0, 0, 0, 0
    for nb in matched:
        nid, title = nb.get("id"), nb.get("title", "(untitled)")
        if has_audio_overview(nid):
            print(f"  = SKIP create (already has audio): {title}", file=sys.stderr)
            skipped += 1
            continue
        if args.dry_run:
            print(f"  + WOULD CREATE: {title}  [{nid}]", file=sys.stderr)
            would_create += 1
            continue
        proc = run_nlm([
            "audio", "create", nid,
            "-f", args.format, "-l", args.length,
            "--language", args.language, "-y",
        ])
        if proc.returncode == 0:
            print(f"  + CREATED: {title}", file=sys.stderr)
            created += 1
        else:
            print(f"  ! FAILED create: {title}: {(proc.stderr.strip() or proc.stdout.strip())}", file=sys.stderr)
            errors += 1

    # ---- Phase 2: download completed overviews into output/podcasts ----
    downloaded, on_disk, would_download, pending, dl_errors = 0, 0, 0, 0, 0
    if not args.no_download:
        print(f"\nDownload phase → {podcast_dir}", file=sys.stderr)
        for nb in matched:
            nid, title = nb.get("id"), nb.get("title", "(untitled)")
            dest = podcast_dir / f"{target:%Y%m%d}-{slugify(title)}.m4a"
            if dest.exists():
                print(f"  = ON DISK: {dest.name}", file=sys.stderr)
                on_disk += 1
                continue
            if args.dry_run:
                print(f"  + WOULD DOWNLOAD: {dest.name}  [{nid}]", file=sys.stderr)
                would_download += 1
                continue
            if not wait_for_completed_audio(nid, args.wait_timeout, args.poll_interval):
                print(f"  … PENDING (no completed audio within {args.wait_timeout}s): {title}",
                      file=sys.stderr)
                pending += 1
                continue
            proc = download_audio(nid, dest)
            if proc.returncode == 0:
                print(f"  ↓ DOWNLOADED: {dest.name}", file=sys.stderr)
                downloaded += 1
            else:
                print(f"  ! FAILED download: {title}: {(proc.stderr.strip() or proc.stdout.strip())}", file=sys.stderr)
                dl_errors += 1

    # ---- Phase 3: fetch + write text summaries (the distiller's queue) ----
    summarized, sum_on_disk, would_summarize, sum_errors = 0, 0, 0, 0
    if not args.no_summary:
        print(f"\nSummary phase → {podcast_dir}", file=sys.stderr)
        for nb in matched:
            nid, title = nb.get("id"), nb.get("title", "(untitled)")
            stem = f"{target:%Y%m%d}-{slugify(title)}"
            sdest = podcast_dir / f"{stem}.summary.md"
            if sdest.exists():
                print(f"  = ON DISK: {sdest.name}", file=sys.stderr)
                sum_on_disk += 1
                continue
            if args.dry_run:
                print(f"  + WOULD SUMMARIZE: {sdest.name}  [{nid}]", file=sys.stderr)
                would_summarize += 1
                continue
            data = fetch_summary(nid)
            if data is None:
                sum_errors += 1
                continue
            write_summary_file(sdest, nid, title, f"{target:%Y-%m-%d}",
                               f"{stem}.m4a", data)
            print(f"  ✎ SUMMARIZED: {sdest.name}", file=sys.stderr)
            summarized += 1

    if args.dry_run:
        summary = (f"would-create {would_create} · skipped {skipped} · "
                   f"would-download {would_download} · on-disk {on_disk} · "
                   f"would-summarize {would_summarize}")
    else:
        summary = (f"created {created} · skipped {skipped} · downloaded {downloaded} · "
                   f"on-disk {on_disk} · pending {pending} · "
                   f"summarized {summarized} · summary-on-disk {sum_on_disk}")
    print(f"\nDone: matched {len(matched)} · {summary} · "
          f"errors {errors + dl_errors + sum_errors}", file=sys.stderr)
    return 1 if (errors or dl_errors or sum_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
