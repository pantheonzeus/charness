#!/usr/bin/env python3
"""
Bridge output/ deliverables and input/ artifacts into the second brain.

Charter §4 keeps two zones: finished deliverables live in output/ (the working
artifact area), the knowledge graph lives in cbrain/. This script closes the gap the
principal asked for — every deliverable gets a linked index note under
cbrain/notes/Deliverables/, and every input artifact one under cbrain/notes/Inputs/, so
both are discoverable from the vault, while the files themselves stay where they are
(nothing is moved, no scheduler path breaks).

WHAT IT INDEXES — output/ (type: deliverable):
  - .md / .html anywhere under output/     (reports, decks, briefs, dossiers, profiles, drafts)
  - .docx / .pptx / .pdf / .xlsx            (documents; folded into a same-stem .md/.html note
                                             as an extra format, else get their own note)
  - .png / .svg                             (renders/diagrams; folded into a same-stem note,
                                             else bundled into ONE "<folder> images" note per dir)
  - .mp3                                    (rendered audio, scripts/render.py; folded into a same-stem
                                             note only — a loose MP3, e.g. briefing audio, is skipped)
WHAT IT INDEXES — input/ (type: input): every file, one note each.

WHAT IT DELIBERATELY SKIPS (and says so — no silent truncation, Charter budget rule):
  - output/podcasts/**  and  *.summary.md  → already bridged by `notebooklm-daily-audio`
                                             (nlm-*.base + NotebookLM sources). Re-indexing
                                             would duplicate what the vault already records.
  - output/morning-briefing/**             → ephemeral, regenerated daily.
  - output/.runs/**                        → run state (control spines), not deliverables.
  - output/tasks/**                        → console task packets/answers (webapp/tasks.py); the report in output/research/ is the deliverable.
  - hidden files (.build-*.html, .gitignore), Office lock files (~$*), *.bak*, *.log,
    .DS_Store, and code/data (.py .sh .json .jsonl .tsv .m4a …) → build intermediates,
    temp files, source code. A project folder's README.md is its index entry.
  - artifacts already claimed by a hand-authored note (generated != deliverable-index)
    via its `artifact:` field or a ../../../output/… link — never duplicated, never overwritten.

Each index note carries Base-queryable YAML and auto-detected [[wikilinks]] to any existing
person/topic note whose name appears in the artifact's path — so the artifact is wired into
the graph, not left an island (Charter §6).

IDEMPOTENT: index notes are fully generated (marked `generated: deliverable-index` /
`input-index`) and overwritten on each run — like a Base. Re-running never duplicates. Notes
whose artifact no longer exists are pruned (default on). Hand-authored notes are never touched.

Usage:  python3 index_deliverables.py [--vault /path/to/cbrain] [--dry-run] [--no-prune]
"""
import os, re, sys, glob, argparse, datetime, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))

INDEX_DIR_NAME = "notes/Deliverables"          # under the vault
GEN_MARK = "deliverable-index"                 # frontmatter `generated:` value
INPUT_DIR_NAME = "notes/Inputs"
INPUT_GEN_MARK = "input-index"
# Work outside this repo: documents in sibling repos under ~/GitHub (and loose files there).
WORK_DIR_NAME = "notes/Work"
WORK_GEN_MARK = "work-index"
WORK_SKIP_REPOS = {os.path.basename(REPO)}
WORK_SKIP_DIRS = {"node_modules", "venv", "env", "my_env", "mlx-env", "site-packages", "__pycache__",
                  "dist", "build", "target", "vendor"}            # plus every hidden dir (.git, .venv, …)
WORK_SKIP_NAMES = {"claude.md", "agents.md", "license.md", "changelog.md", "code_of_conduct.md"}
WORK_MAX_BYTES = 50 * 1024 * 1024

# --- scope policy (documented in the module docstring) -----------------------
TEXT_EXT = {".md", ".html"}
DOC_EXT = {".docx", ".pptx", ".pdf", ".xlsx"}
IMG_EXT = {".png", ".svg"}
AUDIO_EXT = {".mp3"}
PRIMARY_ORDER = [".md", ".html", ".docx", ".pptx", ".pdf", ".xlsx", ".png", ".svg", ".mp3"]
SKIP_DIRS = {".runs", "podcasts", "morning-briefing", "tasks"}   # first path segment under output/
SKIP_NAME_RX = re.compile(r"(\.summary\.md$)|(\.log$)|(^\.)|(^~\$)|(\.bak)", re.I)
CLAIM_RX = re.compile(r'artifact:\s*"output/([^"]+)"|\]\(\.\./\.\./\.\./output/([^)]+)\)')


def title_of(path):
    """First markdown H1, else a prettified filename stem."""
    if path.endswith(".md"):
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"#\s+(.+)", line.strip())
                    if m:
                        return m.group(1).strip()
                    if line.strip() and not line.startswith("---"):
                        break
        except OSError:
            pass
    stem = unicodedata.normalize("NFC", os.path.splitext(os.path.basename(path))[0])
    return re.sub(r"[-_]+", " ", stem).strip().title()


def first_para(path):
    """First real paragraph of a markdown file, for a TL;DR line (skips YAML/headings)."""
    if not path.endswith(".md"):
        return ""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return ""
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)   # strip frontmatter
    for block in text.split("\n\n"):
        block = block.strip()
        if block and not block.startswith("#") and not block.startswith("!["):
            return re.sub(r"\s+", " ", block)[:280]
    return ""


def vault_entities(vault):
    """Map first-significant-token -> canonical [[note name]] for people + topics."""
    ents = {}
    for sub in ("projects", "Clients"):
        for f in glob.glob(os.path.join(vault, sub, "*.md")):
            name = os.path.splitext(os.path.basename(f))[0]
            tok = re.split(r"[\s_-]+", name.lower())[0]
            if len(tok) >= 5:                       # avoid noise from short/common tokens
                ents.setdefault(tok, name)
    return ents


def detect_links(rel_output_path, ents):
    hay = rel_output_path.lower()
    # whole-token match: "chris" must not hit inside "christoph"
    hits = [name for tok, name in ents.items()
            if re.search(rf"(?<![a-z0-9]){re.escape(tok)}(?![a-z0-9])", hay)]
    # stable, de-duplicated
    seen, out = set(), []
    for n in sorted(hits):
        if n not in seen:
            seen.add(n); out.append(n)
    return out


def slug_for(rel):
    """output/-relative path -> flat, collision-free index-note stem."""
    stem = os.path.splitext(rel)[0]
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def link_to(root_name, rel, index_dir_name):
    """Filesystem-relative link from the index note to the artifact (outside the vault)."""
    return os.path.relpath(os.path.join(REPO, root_name, rel),
                           os.path.join(REPO, "cbrain", index_dir_name))


def manual_claims(index_dir):
    """output/-relative paths already covered by hand-authored notes in the index dir."""
    claimed = set()
    for f in glob.glob(os.path.join(index_dir, "*.md")):
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        if f"generated: {GEN_MARK}" in text[:600]:
            continue
        for a, b in CLAIM_RX.findall(text):
            claimed.add(a or b)
    return claimed


def iter_files(root, skip_dirs=()):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        top = "" if rel_dir == "." else rel_dir.split(os.sep)[0]
        if top in skip_dirs:
            dirnames[:] = []                        # prune the walk
            continue
        for fn in filenames:
            if SKIP_NAME_RX.search(fn):
                continue
            full = os.path.join(dirpath, fn)
            yield full, os.path.relpath(full, root)


def plan_deliverables(output_root, claimed):
    """Group same-stem files; return ([(primary_rel, [sibling_rel..])], {dir: [image_rel..]})."""
    groups = {}
    for full, rel in iter_files(output_root, SKIP_DIRS):
        ext = os.path.splitext(rel)[1].lower()
        if ext not in TEXT_EXT | DOC_EXT | IMG_EXT | AUDIO_EXT or rel in claimed:
            continue
        groups.setdefault(os.path.splitext(rel)[0].lower(), []).append(rel)   # slug is lowercase too
    notes, bundles = [], {}
    for stem, rels in sorted(groups.items()):
        rels.sort(key=lambda r: PRIMARY_ORDER.index(os.path.splitext(r)[1].lower()))
        if os.path.splitext(rels[0])[1].lower() in AUDIO_EXT:
            continue                     # audio only ever rides on a document's note
        if os.path.splitext(rels[0])[1].lower() in IMG_EXT:
            bundles.setdefault(os.path.dirname(rels[0]), []).extend(rels)
        else:
            notes.append((rels[0], rels[1:]))
    return notes, bundles


def plan_work(github_root):
    """Documents in sibling repos (+ loose files in ~/GitHub itself), as ../<repo>/<path> rels.
    Never code, envs, hidden dirs, media, or keys: only TEXT_EXT | DOC_EXT."""
    out = []
    for dirpath, dirnames, filenames in os.walk(github_root):
        rel_dir = os.path.relpath(dirpath, github_root)
        top = "" if rel_dir == "." else rel_dir.split(os.sep)[0]
        if top in WORK_SKIP_REPOS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in WORK_SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXT | DOC_EXT or SKIP_NAME_RX.search(fn) or fn.lower() in WORK_SKIP_NAMES:
                continue
            full = os.path.join(dirpath, fn)
            if os.path.getsize(full) > WORK_MAX_BYTES:
                continue
            rel = os.path.relpath(full, github_root)
            out.append((full, rel if top else "_loose/" + rel))
    return sorted(out, key=lambda x: x[1])


def build_note(full, rel, ents, siblings=(), root_name="output", index_dir_name=INDEX_DIR_NAME,
               note_type="deliverable", gen_mark=GEN_MARK, default_cat="report"):
    st = os.stat(full)
    date = datetime.date.fromtimestamp(st.st_mtime).isoformat()
    kb = max(1, round(st.st_size / 1024))
    parts = rel.split("/")
    cat = parts[0] if len(parts) > 1 else default_cat
    links = detect_links(rel, ents)
    artifact = f"{root_name}/{rel}"
    fm = [
        "---",
        f"type: {note_type}",
        "status: active",
        f"date: {date}",
        f"tags: [{note_type}{', ' + cat if cat != note_type else ''}]",
        f"artifact: \"{artifact}\"",
        f"kind: {os.path.splitext(rel)[1].lstrip('.').lower()}",
        f"size_kb: {kb}",
        f"generated: {gen_mark}",
        "---",
    ]
    label = {"deliverable": "Deliverable artifact", "work": "Work document"}.get(note_type, "Input artifact")
    body = [f"# {title_of(full)}", ""]
    body.append(f"> {label} — lives in [`{artifact}`]({link_to(root_name, rel, index_dir_name)}). "
                f"This note is the vault index entry (auto-generated).")
    if siblings:
        body += ["", "## Other formats",
                 *[f"- [`{root_name}/{s}`]({link_to(root_name, s, index_dir_name)})" for s in siblings]]
    tl = first_para(full)
    if tl:
        body += ["", "## TL;DR", tl]
    if links:
        body += ["", "## Related", *[f"- [[{n}]]" for n in links]]
    body += ["", f"_Generated by `deliverable-index`; edits here are overwritten. "
                 f"Category: **{cat}** · {kb} KB._", ""]
    return "\n".join(fm) + "\n\n" + "\n".join(body)


def build_bundle(output_root, rel_dir, images, ents):
    """One note listing every orphan image (no same-stem document) in a directory."""
    fulls = [os.path.join(output_root, r) for r in images]
    date = datetime.date.fromtimestamp(max(os.stat(f).st_mtime for f in fulls)).isoformat()
    kb = max(1, round(sum(os.stat(f).st_size for f in fulls) / 1024))
    where = rel_dir or "output (top level)"
    cat = rel_dir.split("/")[0] if rel_dir else "report"
    links = detect_links(" ".join(images), ents)
    fm = [
        "---",
        "type: deliverable",
        "status: active",
        f"date: {date}",
        f"tags: [deliverable, {cat}]",
        f"artifact: \"output/{rel_dir + '/' if rel_dir else ''}\"",
        "kind: images",
        f"size_kb: {kb}",
        f"generated: {GEN_MARK}",
        "---",
    ]
    body = [f"# Images — {where}", "",
            f"> {len(images)} rendered images/diagrams with no same-name document beside them. "
            f"This note is the vault index entry (auto-generated).", "", "## Files",
            *[f"- [`output/{r}`]({link_to('output', r, INDEX_DIR_NAME)})" for r in sorted(images)]]
    if links:
        body += ["", "## Related", *[f"- [[{n}]]" for n in links]]
    body += ["", f"_Generated by `deliverable-index`; edits here are overwritten. "
                 f"Category: **{cat}** · {kb} KB._", ""]
    return "\n".join(fm) + "\n\n" + "\n".join(body)


def sync(index_dir, gen_mark, wanted, dry_run, prune):
    """Write changed notes, prune stale generated ones; never touch hand-authored notes."""
    if not dry_run:
        os.makedirs(index_dir, exist_ok=True)
    written = conflicts = pruned = 0
    for fn, content in wanted.items():
        dest = os.path.join(index_dir, fn)
        old = None
        if os.path.exists(dest):
            with open(dest, encoding="utf-8") as fh:
                old = fh.read()
            if f"generated: {gen_mark}" not in old[:600]:
                conflicts += 1
                print(f"  ! kept hand-authored note, not overwritten: {fn}", file=sys.stderr)
                continue
        if old != content:
            written += 1
            if not dry_run:
                with open(dest, "w", encoding="utf-8") as fh:
                    fh.write(content)
    if prune and os.path.isdir(index_dir):
        for existing in glob.glob(os.path.join(index_dir, "*.md")):
            if os.path.basename(existing) in wanted:
                continue
            # only prune notes WE generated
            with open(existing, encoding="utf-8") as fh:
                head = fh.read(600)
            if f"generated: {gen_mark}" in head:
                pruned += 1
                if not dry_run:
                    os.remove(existing)
    return written, conflicts, pruned


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=os.path.join(REPO, "cbrain"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-prune", action="store_true")
    args = ap.parse_args()

    output_root = os.path.join(REPO, "output")
    input_root = os.path.join(REPO, "input")
    index_dir = os.path.join(args.vault, INDEX_DIR_NAME)
    input_dir = os.path.join(args.vault, INPUT_DIR_NAME)
    ents = vault_entities(args.vault)
    tag = "[dry-run] would index" if args.dry_run else "indexed"

    claimed = manual_claims(index_dir)
    notes, bundles = plan_deliverables(output_root, claimed)
    wanted = {}     # note filename -> content
    for rel, siblings in notes:
        wanted[slug_for(rel) + ".md"] = build_note(os.path.join(output_root, rel), rel, ents, siblings)
    for rel_dir, images in sorted(bundles.items()):
        wanted[slug_for(rel_dir or "output") + "-images.md"] = build_bundle(output_root, rel_dir, images, ents)
    w, c, p = sync(index_dir, GEN_MARK, wanted, args.dry_run, not args.no_prune)
    print(f"{tag} {len(notes)} deliverables + {len(bundles)} image bundles into cbrain/{INDEX_DIR_NAME} "
          f"({w} new/changed, {p} pruned, {c} hand-authored kept, {len(claimed)} artifacts claimed by "
          f"hand-authored notes). Skipped by policy: podcasts/, *.summary.md, morning-briefing/, .runs/, tasks/, "
          f"hidden/lock/.bak files, code & data files.")

    wanted = {}
    if os.path.isdir(input_root):
        for full, rel in sorted(iter_files(input_root)):
            wanted[slug_for(rel) + ".md"] = build_note(
                full, rel, ents, root_name="input", index_dir_name=INPUT_DIR_NAME,
                note_type="input", gen_mark=INPUT_GEN_MARK, default_cat="input")
    w, c, p = sync(input_dir, INPUT_GEN_MARK, wanted, args.dry_run, not args.no_prune)
    print(f"{tag} {len(wanted)} input artifacts into cbrain/{INPUT_DIR_NAME} "
          f"({w} new/changed, {p} pruned, {c} hand-authored kept).")

    wanted = {}
    github_root = os.path.dirname(REPO)
    for full, rel in plan_work(github_root):
        note = build_note(full, rel, ents, root_name="..", index_dir_name=WORK_DIR_NAME,
                          note_type="work", gen_mark=WORK_GEN_MARK, default_cat="loose")
        if rel.startswith("_loose/"):   # artifact points at the real file, not the _loose/ label
            note = note.replace(rel, rel[7:])
        wanted[slug_for(rel) + ".md"] = note
    w, c, p = sync(os.path.join(args.vault, WORK_DIR_NAME), WORK_GEN_MARK, wanted, args.dry_run, not args.no_prune)
    print(f"{tag} {len(wanted)} work documents from sibling repos in {github_root} into cbrain/{WORK_DIR_NAME} "
          f"({w} new/changed, {p} pruned, {c} hand-authored kept). Skipped: code, envs, hidden dirs, media, keys.")


if __name__ == "__main__":
    main()
