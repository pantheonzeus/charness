#!/usr/bin/env python3
"""Agent Skills spec export — converts house-schema frontmatter to the open standard (agentskills.io/specification).

The spec allows six top-level keys: name, description, license, compatibility, metadata, allowed-tools. Anthropic's
quick_validate.py and the reference skills-ref validator both reject any other top-level key, and quick_validate
also rejects '<' or '>' anywhere in the description. The mapping:
  id                → name (the slug; must equal the folder)
  description       → description, with the triggers folded in ("Use when: …") while it stays ≤ 1024 chars
  environment       → compatibility (when ≤ 500 chars, else it stays in metadata)
  allowed-tools     → stays top level
  name (title), every other key → metadata, original key names and order (comments are lost)
The body and every bundled file are copied unchanged.

  python3 spec_export.py check                     lint rule: every skill converts to valid spec frontmatter; exit 0 iff errors=0
  python3 spec_export.py export SLUG… --out DIR    write DIR/<slug>/ (whole skill folder, converted SKILL.md); never touches the source
"""
import argparse, pathlib, re, shutil, sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
ALLOWED = ["name", "description", "license", "compatibility", "metadata", "allowed-tools"]
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
# Common angle forms rewritten to their typographic equivalents; any other '<' or '>' is an error to fix by hand.
ANGLES = [(">=", "≥"), ("<=", "≤"), ("->", "→"), ("<-", "←")]


def skills():
    return {p.parent.name: p for p in sorted(ROOT.glob("*/*/SKILL.md")) if not p.parts[-3].startswith("_")}


def clean(text):
    for a, b in ANGLES:
        text = text.replace(a, b)
    return re.sub(r"<([^<>\s]+)>", r"{\1}", text)


def convert(path):
    """Return (frontmatter dict, body, errors) for one SKILL.md."""
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    if not m:
        return None, text, ["no frontmatter block"]
    src, body = yaml.safe_load(m.group(1)) or {}, text[m.end():]
    desc = clean(" ".join(str(src.get("description", "")).split()))
    triggers = [clean(str(t).strip()) for t in src.get("triggers") or []]
    new = [t for t in triggers if t.lower() not in desc.lower()]
    dropped = 0
    if new:
        lead = desc.rstrip(".") + ". Use when: "
        fit = []
        for t in new:
            if len(lead + ", ".join(fit + [t]) + ".") > 1024:
                break
            fit.append(t)
        if fit:
            desc = lead + ", ".join(fit) + "."
        dropped = len(new) - len(fit)
    out = {"name": src.get("id"), "description": desc}
    env = src.get("environment")
    if env and len(str(env)) <= 500:
        out["compatibility"] = str(env)
    if "allowed-tools" in src:
        out["allowed-tools"] = src["allowed-tools"]
    meta = {"title": src["name"]} if "name" in src else {}
    for k, v in src.items():
        if k in ("id", "name", "description", "allowed-tools") or (k == "environment" and "compatibility" in out):
            continue
        meta[k] = v
    out["metadata"] = meta
    errors = validate(render(out, body), path.parent.name)
    if dropped and len(desc) <= 1024:
        errors.append(f"warn: {dropped} of {len(new)} triggers did not fit in 1024 chars")
    return out, body, errors


def validate(text, folder):
    """The checks of Anthropic's quick_validate.py and skills-ref, run on the rendered file as it would ship."""
    fm = yaml.safe_load(FM.match(text).group(1))
    errors = [f"unexpected top-level key `{k}`" for k in fm if k not in ALLOWED]
    name, desc, compat = fm.get("name"), fm.get("description"), fm.get("compatibility")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"name `{name}` is not a valid spec slug")
    elif name != folder:
        errors.append(f"name `{name}` != folder `{folder}`")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("description is empty")
    elif len(desc) > 1024:
        errors.append(f"description is {len(desc)} chars (max 1024): rewrite it by hand")
    elif re.search(r"[<>]", desc):
        errors.append(f"description keeps '<' or '>': {re.findall(r'.{0,10}[<>].{0,10}', desc)[:2]}")
    if compat is not None and (not isinstance(compat, str) or len(compat) > 500):
        errors.append("compatibility must be a string of at most 500 chars")
    return errors


def render(fm, body):
    head = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10**6)
    return f"---\n{head}---\n{body}"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    ex = sub.add_parser("export")
    ex.add_argument("slugs", nargs="+")
    ex.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()

    found, total, warns = skills(), 0, 0
    if a.cmd == "check":
        for slug, p in found.items():
            _, _, errs = convert(p)
            for e in errs:
                print(f"{p.relative_to(ROOT)}: {e}")
            total += sum(not e.startswith("warn:") for e in errs)
            warns += sum(e.startswith("warn:") for e in errs)
        print(f"skills={len(found)} errors={total} warnings={warns}")
        return 0 if not total else 1
    for slug in a.slugs:
        if slug not in found:
            print(f"{slug}: no such skill")
            total += 1
            continue
        fm, body, errs = convert(found[slug])
        dest = a.out / slug
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(found[slug].parent, dest, ignore=shutil.ignore_patterns("__pycache__"))
        (dest / "SKILL.md").write_text(render(fm, body), encoding="utf-8")
        hard = [e for e in errs if not e.startswith("warn:")]
        for e in errs:
            print(f"{slug}: {e}")
        total += len(hard)
        print(f"{slug}: exported → {dest}{' (with errors)' if hard else ''}")
    return 0 if not total else 1


if __name__ == "__main__":
    sys.exit(main())
