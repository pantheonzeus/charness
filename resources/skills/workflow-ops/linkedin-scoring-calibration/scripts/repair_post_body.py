#!/usr/bin/env python3
"""
Repair LinkedIn post notes whose `## Post` body lost its line breaks on ingest.

WHY THIS EXISTS
---------------
Found 2026-08-18: 34 of 57 notes in cbrain/notes/LinkedIn-Posts/ store the post
body as one unbroken paragraph. A real LinkedIn post always carries line breaks,
so a single-line body is an ingest artifact, not an authorial choice.

It silently corrupts the two heaviest-weighted scorer features. build_dataset.py
splits the body on "\n" and hands it to score_hook()/score_spacing() — Hook is
30% of the composite and Spacing 20%. With one line, the "hook block" becomes the
entire post (1051 chars on one sample, against a 70-140 optimal band) and
one-idea-per-line collapses.

Measured over the 51 scorable posts:

    breaks lost   n=28  hook 43.2  composite 70.8  passing >=85:  0/28
    breaks intact n=23  hook 55.4  composite 74.4  passing >=85:  6/23

Every post that clears the ship gate is one whose formatting survived. Intersect
formatting-intact with has-demographics and only 7 of 57 posts are usable
calibration rows. Everything downstream is fitting an artifact until this is
repaired.

WHY IT IS NOT AUTOMATIC
-----------------------
The bodies must come from LinkedIn, and LinkedIn's `/feed/update/...` URLs return
a sign-in wall to any unauthenticated fetch (verified 2026-08-18, same constraint
`linkedin-post-discovery` documents for search). Only a logged-in human can copy
the original text. This script does everything either side of that step.

Reconstructing line breaks by guessing is NOT an option — that would invent the
author's formatting and then score it as if it were real. Paste the original.

USAGE
-----
    # 1. what needs fixing, with the URL to open for each
    python3 repair_post_body.py --list

    # 2. copy the post text from LinkedIn into a file, then:
    python3 repair_post_body.py --repair 20251130-the-kill-list.md --from body.txt

    #    or pipe it straight in:
    pbpaste | python3 repair_post_body.py --repair 20251130-the-kill-list.md --from -

    # 3. confirm
    python3 repair_post_body.py --verify

Only the `## Post` section is touched. Everything else in the note — frontmatter,
Performance table, Audience snapshot — is preserved byte-for-byte. A .bak copy is
written before any change.
"""

import argparse
import os
import re
import shutil
import sys

DEFAULT_POSTS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..",
                 "cbrain", "notes", "LinkedIn-Posts")
)

POST_RE = re.compile(r"(^## Post\s*\n)(.*?)(?=^## )", re.DOTALL | re.MULTILINE)


def read_body(text):
    m = POST_RE.search(text)
    return m.group(2).strip() if m else None


def is_damaged(body):
    """Mirror of build_dataset.formatting_intact() — keep the two in step."""
    return len([l for l in body.split("\n") if l.strip()]) <= 2


def frontmatter_url(text):
    m = re.search(r"^url:\s*(\S+)", text, re.MULTILINE)
    return m.group(1) if m else ""


def scan(posts_dir):
    out = []
    for name in sorted(os.listdir(posts_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(posts_dir, name)
        text = open(path, encoding="utf-8").read()
        body = read_body(text)
        if body is None or len(body) < 80:
            continue
        out.append((name, path, body, frontmatter_url(text)))
    return out


def cmd_list(posts_dir):
    rows = scan(posts_dir)
    damaged = [r for r in rows if is_damaged(r[2])]
    print(f"{len(damaged)} of {len(rows)} posts need repair\n")
    for i, (name, _, body, url) in enumerate(damaged, 1):
        print(f"{i:2}. {name}")
        print(f"    {url or '!! no url: in frontmatter — recover manually'}")
        print(f"    {len(body)} chars on one line, starts: {body[:70]!r}")
    if damaged:
        print("\nFor each: open the URL, copy the post text with its line breaks, then")
        print("  python3 repair_post_body.py --repair <file> --from <textfile|->")
    return 0


def cmd_repair(posts_dir, name, source, force=False):
    path = os.path.join(posts_dir, name)
    if not os.path.isfile(path):
        sys.exit(f"error: no such note: {path}")

    new_body = (sys.stdin.read() if source == "-"
                else open(source, encoding="utf-8").read()).strip()
    if not new_body:
        sys.exit("error: replacement body is empty — nothing written")
    if is_damaged(new_body):
        sys.exit("error: the replacement is itself a single block. Copy the post "
                 "from LinkedIn with its line breaks intact; do not retype it as "
                 "one paragraph. Nothing written.")

    text = open(path, encoding="utf-8").read()
    old_body = read_body(text)
    if old_body is None:
        sys.exit(f"error: no '## Post' section in {name} — nothing written")

    # Guard against pasting the wrong post: the words should mostly match.
    def words(s):
        return set(re.findall(r"[a-zA-ZäöüßÄÖÜ]{4,}", s.lower()))
    a, b = words(old_body), words(new_body)
    overlap = len(a & b) / max(1, len(a))
    if overlap < 0.5 and not force:
        sys.exit(f"error: the pasted text shares only {overlap:.0%} of the stored "
                 f"post's words — either a different post, or a partial copy that "
                 f"would silently truncate the body. Nothing written. Re-check the "
                 f"URL and copy the whole post; pass --force only if you are sure "
                 f"the stored text was wrong.")

    shutil.copy2(path, path + ".bak")
    repaired = POST_RE.sub(lambda m: m.group(1) + new_body + "\n\n", text, count=1)
    open(path, "w", encoding="utf-8").write(repaired)

    lines = len([l for l in new_body.split("\n") if l.strip()])
    print(f"repaired {name}: 1 line -> {lines} lines ({overlap:.0%} word overlap "
          f"with the stored text). Backup at {os.path.basename(path)}.bak")
    return 0


def cmd_verify(posts_dir):
    rows = scan(posts_dir)
    damaged = [r[0] for r in rows if is_damaged(r[2])]
    intact = len(rows) - len(damaged)
    print(f"formatting intact: {intact}/{len(rows)}")
    if damaged:
        print(f"still damaged ({len(damaged)}):")
        for n in damaged:
            print("  ", n)
        return 1
    print("all post bodies carry line breaks — rebuild the dataset and recalibrate.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--posts", default=DEFAULT_POSTS)
    ap.add_argument("--list", action="store_true", help="show the repair worklist")
    ap.add_argument("--verify", action="store_true", help="re-check every note")
    ap.add_argument("--repair", metavar="NOTE.md", help="note to repair")
    ap.add_argument("--from", dest="source", metavar="FILE",
                    help="file holding the correct body, or - for stdin")
    ap.add_argument("--force", action="store_true",
                    help="skip the word-overlap safety check (use only when the "
                         "stored text itself was wrong)")
    args = ap.parse_args()

    if not os.path.isdir(args.posts):
        sys.exit(f"error: posts dir not found: {args.posts}")
    if args.list:
        return cmd_list(args.posts)
    if args.verify:
        return cmd_verify(args.posts)
    if args.repair:
        if not args.source:
            sys.exit("error: --repair needs --from <file|->")
        return cmd_repair(args.posts, args.repair, args.source, args.force)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
