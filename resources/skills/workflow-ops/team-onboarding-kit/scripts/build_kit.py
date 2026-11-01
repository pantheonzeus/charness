#!/usr/bin/env python3
"""Build one personal onboarding page per team member, plus a shared media folder.

Usage (from the repo root):
  python3 build_kit.py --run-dir output/.runs/<slug> --config output/.runs/<slug>/kit.py --out output/<slug>-onboarding-kit

--run-dir holds artifacts.json (written by create_artifacts.py, completed by fetch_media.py).
--config is a copy of kit.example.py filled in for this engagement (ENGAGEMENT, PEOPLE, MEDIA_DESC, ORDER, DATES).
Writes <out>/onboarding-<person>.html, <out>/media/, <out>/README.txt; copies ENGAGEMENT["playbook"] if set.
"""
import argparse, importlib.util, json, pathlib, re, shutil, subprocess

HERE = pathlib.Path(__file__).resolve().parent


def load_config(path):
    spec = importlib.util.spec_from_file_location("kit_config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def duration_min(p):
    out = subprocess.run(["afinfo", str(p)], capture_output=True, text=True).stdout  # macOS; None elsewhere
    m = re.search(r"estimated duration:\s*([\d.]+)", out)
    return round(float(m.group(1)) / 60, 1) if m else None


def norm_quiz(raw):
    """NotebookLM quiz JSON mixes four types; keep all of them.

    multiple_choice / multiple_select -> {type:"choice", q, options:[{t, ok, why}], multi}
    fill_in_the_blank / short_answer  -> {type:"open", q, answer, also, why, hint}
    """
    out = []
    for it in (raw.get("questions", []) if isinstance(raw, dict) else raw) or []:
        q = it.get("question", "")
        if it.get("answerOptions"):
            opts = [dict(t=o.get("text", ""), ok=bool(o.get("isCorrect")), why=o.get("rationale", "")) for o in it["answerOptions"]]
            if q and any(o["ok"] for o in opts):
                out.append(dict(type="choice", q=q, options=opts, multi=sum(o["ok"] for o in opts) > 1))
        else:
            grading = it.get("grading") or {}
            ans = it.get("bestAnswer") or grading.get("modelAnswer") or ""
            if q and ans:
                out.append(dict(type="open", q=q, answer=ans, also=it.get("acceptableAnswers", []),
                                why=it.get("rationale") or grading.get("rationale", ""), hint=it.get("hint", "")))
    return out


def card_text(side):
    """A flashcard side is a string or {"flashcardContentBlock": [{"type": "text", "content": ...}]}."""
    if isinstance(side, dict):
        return " ".join(b.get("content", "") for b in side.get("flashcardContentBlock", []) if b.get("type") == "text").strip()
    return side


def norm_cards(raw):
    out = []
    for c in (raw.get("cards", []) if isinstance(raw, dict) else raw) or []:
        f, b = card_text(c.get("front")), card_text(c.get("back"))
        if f and b:
            out.append(dict(f=f, b=b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = load_config(a.config)
    run, kit = pathlib.Path(a.run_dir), pathlib.Path(a.out)
    media_dir = kit / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    media, quizzes, cards = {}, {}, []
    for key, art in json.loads((run / "artifacts.json").read_text()).items():
        src = pathlib.Path(art.get("done", ""))
        if not art.get("done") or not src.exists():
            continue
        if art["kind"] == "quiz":
            quizzes[key] = norm_quiz(json.loads(src.read_text()))
            continue
        if art["kind"] == "flashcards":
            cards = norm_cards(json.loads(src.read_text()))
            continue
        dst = media_dir / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
        media[key] = dict(key=key, kind=art["kind"],
                          title=re.sub(r"^(\d+ · |Video · |Infographic · )| \(v\d+\)$", "", art["title"]),
                          file=f"media/{src.name}", desc=cfg.MEDIA_DESC.get(key, ""),
                          min=duration_min(dst) if art["kind"] in ("audio", "video") else None)

    eng = dict(cfg.ENGAGEMENT)
    if eng.get("playbook"):
        pb = pathlib.Path(eng["playbook"])
        shutil.copy2(pb, kit / pb.name)
        eng["playbook"] = pb.name
    tpl = (HERE / "template.html").read_text()
    for slug, person in cfg.PEOPLE.items():
        p = dict(person)
        p["week"] = [dict(w, date=cfg.DATES.get(w["day"], "")) for w in p["week"]]
        p["sprint"] = [dict(day=d, date=cfg.DATES.get(d, ""), text=t) for d, t in p["sprint"].items()]
        p["quizItems"] = quizzes.get(p.get("quiz"), [])
        data = dict(slug=slug, person=p, engagement=eng, media=media, order=cfg.ORDER, cards=cards, notebook=cfg.NOTEBOOK_URL)
        html = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__NAME__", p["name"])
        (kit / f"onboarding-{slug}.html").write_text(html)
        missing = sorted({k for w in p["week"] for k in w["media"]} - media.keys())
        print(f"{slug}: {len(p['quizItems'])} quiz items, {len(cards)} cards, missing media: {missing or 'none'}")
    pages = " / ".join(f"onboarding-{s}.html" for s in cfg.PEOPLE)
    (kit / "README.txt").write_text(
        f"{eng['title']}: team onboarding kit ({eng.get('banner', 'confidential')})\n\n"
        "1. Download this whole folder (the pages need the media/ folder next to them).\n"
        f"2. Open your own page in Chrome, Safari or Edge:\n     {pages}\n"
        "3. Start with 'Start here', then 'My prep week'.\n\n"
        "Your ticks, ratings and quiz answers are saved only in your own browser.\n")
    print(f"media in kit: {len(media)}")


if __name__ == "__main__":
    main()
