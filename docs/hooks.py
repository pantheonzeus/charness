"""MkDocs build hook: the pages that come from the repo itself, so the site can't drift from it.

- reference/skills.md is generated from resources/skills/INDEX.md and each category's _category.md
  scope. The skills HIDDEN matches are left off the site (principal's call, 2026-11-08).
- Charter, Soul, the HarnessCard and the changelog are published from the root files. Their relative
  links point at the matching site page, or at the file on GitHub.
- In any page, `](gh:path)` links that path on GitHub, and {{ skills_count }}, {{ categories_count }},
  {{ jobs_count }} and {{ hook_suites_count }} are filled in from the repo at build time.
"""
import posixpath
import re
from pathlib import Path

from mkdocs.structure.files import File

ROOT = Path(__file__).resolve().parent.parent
GH = "https://github.com/pantheonzeus/charness"
HIDDEN = re.compile(r"^(linkedin-.*|career-campaign-review|campaign-week|role-scout)$")

# root file → site page it is published as
ROOT_PAGES = {
    "Charter.md": "reference/charter.md",
    "Soul.md": "reference/soul.md",
    "HARNESSCARD.md": "governance/harnesscard.md",
    "CHANGELOG.md": "reference/changelog.md",
}

LINK = re.compile(r"\]\(([^)\s]+)\)")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def gh_url(path: str) -> str:
    kind = "tree" if path.endswith("/") else "blob"
    return f"{GH}/{kind}/main/{path.rstrip('/')}"


def parse_index() -> list[dict]:
    """INDEX.md rows as {category, name, description, path, slug}."""
    skills, category = [], None
    for line in (ROOT / "resources/skills/INDEX.md").read_text().splitlines():
        if line.startswith("## "):
            category = line[3:].strip()
            continue
        if not (category and line.startswith("|")):
            continue
        cells = [c.strip() for c in CELL_SPLIT.split(line.strip().strip("|"))]
        path = cells[-1].strip("`")
        if len(cells) < 4 or not path.endswith("/SKILL.md"):   # header, separator, _shared modules
            continue
        skills.append({
            "category": category,
            "name": cells[0],
            "description": cells[2].replace("\\|", "|"),
            "path": path,
            "slug": path.split("/")[-2] if path.count("/") >= 2 else path,
        })
    return [s for s in skills if not HIDDEN.match(s["slug"])]


def category_scope(category: str) -> str:
    f = ROOT / "resources/skills" / category / "_category.md"
    if f.exists():
        m = re.search(r"\*\*Scope:\*\*\s*(.+)", f.read_text())
        if m:
            return m.group(1).strip()
    return ""


def catalog(skills: list[dict]) -> str:
    out = [
        "# Skill catalog",
        "",
        f"{len(skills)} skills in {len({s['category'] for s in skills})} categories, generated from "
        f"[`resources/skills/INDEX.md`]({gh_url('resources/skills/INDEX.md')}) at build time. Each skill is "
        "one Markdown policy document: the agent matches a task against the triggers, then opens only that "
        "skill's `SKILL.md`. How that works: [Skills](../concepts/skills.md).",
        "",
        "Some personal-workflow skills are in the repo but not listed here.",
        "",
    ]
    for category in dict.fromkeys(s["category"] for s in skills):
        rows = [s for s in skills if s["category"] == category]
        out += [f"## {category}", ""]
        if scope := category_scope(category):
            out += [f"*{scope}*", ""]
        out += ["| Skill | What it does |", "|---|---|"]
        for s in rows:
            desc = s["description"].replace("\n", " ")
            out.append(f"| [{s['name']}]({gh_url('resources/skills/' + s['path'])}) | {desc} |")
        out.append("")
    return "\n".join(out)


def rewrite_root_links(markdown: str, page_uri: str) -> str:
    """Relative links in a root file: to the site page it is published as, else to GitHub."""
    def fix(m):
        target = m.group(1)
        if re.match(r"^(https?:|mailto:|#)", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        path = posixpath.normpath(path)
        if path in ROOT_PAGES:
            rel = posixpath.relpath(ROOT_PAGES[path], posixpath.dirname(page_uri))
            return f"]({rel}{'#' + anchor if anchor else ''})"
        return f"]({gh_url(path)}{'#' + anchor if anchor else ''})"
    return LINK.sub(fix, markdown)


def counts(skills: list[dict]) -> dict:
    return {
        "skills_count": len(skills),
        "categories_count": len({s["category"] for s in skills}),
        "jobs_count": len(list((ROOT / ".claude/agents").glob("*.md"))),
        "hook_suites_count": len(list((ROOT / ".claude/hooks/tests").glob("*.test.sh"))),
    }


_skills: list[dict] = []
_sources: dict[str, str] = {}   # generated page → repo path it came from (for the edit link)


def on_files(files, config):
    _skills[:] = parse_index()
    files.append(File.generated(config, "reference/skills.md", content=catalog(_skills)))
    _sources["reference/skills.md"] = "resources/skills/INDEX.md"
    for src, uri in ROOT_PAGES.items():
        text = rewrite_root_links((ROOT / src).read_text(), uri)
        files.append(File.generated(config, uri, content=text))
        _sources[uri] = src
    return files


def on_page_markdown(markdown, page, config, files):
    markdown = re.sub(r"\]\(gh:([^)\s]+)\)", lambda m: f"]({gh_url(m.group(1))})", markdown)
    for key, value in counts(_skills).items():
        markdown = markdown.replace("{{ " + key + " }}", str(value))
    if page.file.src_uri in _sources:
        page.edit_url = f"{GH}/edit/main/{_sources[page.file.src_uri]}"
    return markdown
