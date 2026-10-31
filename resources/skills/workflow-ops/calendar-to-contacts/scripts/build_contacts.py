#!/usr/bin/env python3
"""Turn a week of calendar events (JSON from fetch_week_events.py) into vault notes.

Creates one contact note per attendee (Clients/<Name>.md) and one meeting note per
event (notes/<YYYYMMDD>-<slug>.md), bi-directionally linked. Append-only on existing
contact notes — never rewrites fields you've already annotated.

  python3 build_contacts.py --sources /tmp/week-events.json \
    --vault cbrain [--dry-run] [--self-email a@b.com]
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def default_self_email():
    """Your own address, kept out of the repo: $CHARNESS_SELF_EMAIL, else this clone's
    `git config charness.selfEmail` (.git/config is never committed)."""
    if os.environ.get("CHARNESS_SELF_EMAIL"):
        return os.environ["CHARNESS_SELF_EMAIL"]
    try:
        return subprocess.run(["git", "config", "--get", "charness.selfEmail"], cwd=Path(__file__).parent,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""

PERSONAL_DOMAINS = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com",
    "icloud.com", "me.com", "yahoo.com", "gmx.de", "gmx.net", "web.de", "proton.me",
}

# Common multi-label public suffixes (ccSLDs). Without these, domain.split(".")[-2]
# grabs the TLD tier, not the org: warwick.ac.uk -> "ac", acme.co.uk -> "co".
_MULTI_SUFFIX = {
    "ac.uk", "co.uk", "org.uk", "gov.uk", "me.uk", "ac.at", "co.at", "or.at",
    "ac.il", "co.il", "com.au", "edu.au", "gov.au", "org.au", "co.jp", "or.jp",
    "co.nz", "co.za", "com.br", "com.mx", "co.in", "ac.in", "com.tr", "edu.tr",
    "ac.be", "com.es", "edu.es", "com.cn", "edu.cn", "com.sg", "com.hk",
}
# Free/personal mail providers keyed by their org label (ccTLD-agnostic), so
# outlook.es / gmail.co.uk / yahoo.de all resolve to "personal" -> blank company.
_PERSONAL_LABELS = {
    "gmail", "googlemail", "outlook", "hotmail", "live", "icloud", "me", "yahoo",
    "gmx", "web", "proton", "protonmail", "aol", "mail", "yandex", "t-online",
}
# A "name" that is really an email local-part (jane.doe, first.last) — never a
# real display name, must not become the note filename verbatim.
_LOCALPART_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)+$")
_COMPANY_SUFFIXES = {"inc", "ltd", "llc", "gmbh", "ag", "plc", "co", "corp", "sa", "bv", "oy", "ab", "se"}

# Distribution lists, shared calendars, and functional mailboxes get invited to meetings
# but are NOT people — minting a contact note for them produces junk like
# `Team Germany.md` / `Germany Calendar.md` / `'BMW Group' via purchase-orders.germany.md`.
# Match functional tokens on a local-part word boundary so real names ('christoph', 'steam')
# are never caught (token must start the local-part or follow a . _ - separator).
_FUNCTIONAL_LOCAL_RE = re.compile(
    r"(^|[._-])(no-?reply|do-?not-?reply|noreply|mailer|mailer-daemon|postmaster|bounce|"
    r"notifications?|purchase-?orders?|invoicing|invoice|billing|accounts-?payable|"
    r"calendar|events?|team|teams|support|helpdesk|info|admin|newsletter|mailing|"
    r"group|all-?staff|staff|everyone|marketing|supervisors?|developers?|department)([._-]|$)", re.I)


def _is_list_domain(email):
    """`*.onmicrosoft.com` addresses are Microsoft 365 tenant routing / distribution lists,
    never a person's real identity (e.g. projectteam@…onmicrosoft.com)."""
    dom = (email or "").split("@", 1)[-1].lower()
    return dom.endswith(".onmicrosoft.com")


def _humanize_local(local):
    return re.sub(r"[._-]+", " ", local).title()


def _org_label(domain):
    """Registrable org label, TLD-tier aware.
    warwick.ac.uk -> 'warwick'; tuwien.ac.at -> 'tuwien'; acme.com -> 'acme'."""
    parts = domain.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in _MULTI_SUFFIX:
        return parts[-3]
    return parts[-2] if len(parts) >= 2 else parts[0]


def safe_filename(title):
    title = re.sub(r'[/:*?"<>|]', "-", title or "")
    title = re.sub(r"\s+", " ", title).strip()
    return title[:120].rstrip(" -")


def slugify(title):
    s = re.sub(r"[^A-Za-z0-9]+", "-", title or "").strip("-")
    return (s[:60].rstrip("-")) or "event"


# --- calendar description ("notes") cleaning: strip HTML + join/dial-in boilerplate ---
_BOILER = re.compile(
    r"(microsoft teams|teams\.microsoft|join from pc|zoom\.us|webinar id|besprechungs-id|"
    r"meeting id|passcode|passwort|einwählen|phone one-tap|need help|benötigen sie hilfe|"
    r"systemreferenz|meetingoptions|join via audio|international numbers|aka\.ms|find a local|"
    r"lokale rufnummer|________|beitreten|riverside\.com|us02web|für organisatoren|"
    r"view group files|leave group|learn more about|reply all to this message|"
    r"datenschutz und sicherheit|zurücksetzen der einwahl|suchen einer lokalen|"
    r"telefonkonferenz|phone conference|get up-to-date information|"
    r"join the meeting now|dial in by phone|for organizers|reset dial-in|meeting options|"
    r"dieser besprechung beitreten|per telefon)", re.I)
_NOTICE = re.compile(r"(transkribiert|transkription dient|falls sie fragen oder einwände|"
                     r"daten werden nur lokal|🔒)", re.I)
_PHONE = re.compile(r"^\+?\d[\d()\s,*#-]{7,}")


def clean_description(desc):
    """Strip HTML and dial-in/boilerplate lines from a calendar event description."""
    if not desc:
        return ""
    t = re.sub(r"<br\s*/?>", "\n", desc, flags=re.I)
    t = re.sub(r"</p>", "\n", t, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    out = []
    for line in t.splitlines():
        s = line.strip()
        if not s or _BOILER.search(s) or _NOTICE.search(s) or _PHONE.match(s):
            continue
        if re.fullmatch(r"[-_=*·•\s]{3,}", s):
            continue
        out.append(s)
    dedup = []
    for s in out:
        if not dedup or dedup[-1] != s:
            dedup.append(s)
    return "\n".join(dedup)


def load_domain_map(path):
    m = {}
    if path and Path(path).exists():
        for line in Path(path).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip().strip('"').lower(), v.strip().strip('"')
            if k and v:
                m[k] = v
    return m


def company_from_email(email, domain_map):
    if not email or "@" not in email:
        return ""
    domain = email.split("@", 1)[1].lower()
    if domain in domain_map:
        return domain_map[domain]
    if domain in PERSONAL_DOMAINS:
        return ""
    label = _org_label(domain)
    if label in _PERSONAL_LABELS:   # outlook.es, gmail.co.uk, … personal regardless of ccTLD
        return ""
    return label.replace("-", " ").title()


def display_name(att):
    name = (att.get("name") or "").strip()
    email = (att.get("email") or "").strip()
    if name and "@" not in name:
        # A calendar-supplied "name" that is really an email local-part
        # (e.g. 'jane.doe') must be humanized, not used verbatim as the filename.
        if _LOCALPART_RE.match(name):
            return _humanize_local(name)
        # Outlook-style "Surname, Given" -> "Given Surname", so the link matches the person note.
        # Company forms ("Acme, Inc.") are left alone.
        m = re.fullmatch(r"([^,\d]+?),\s*([^,\d]+)", name)
        if m and m.group(2).strip().rstrip(".").lower() not in _COMPANY_SUFFIXES:
            return f"{m.group(2).strip()} {m.group(1).strip()}"
        return name
    if email:
        return _humanize_local(email.split("@", 1)[0])
    return name or "Unknown"


def index_existing_contacts(clients_dir):
    """Map lowercase email -> existing Clients/*.md path, to avoid near-duplicates."""
    by_email = {}
    if not clients_dir.exists():
        return by_email
    for f in clients_dir.glob("*.md"):
        try:
            txt = f.read_text()
        except Exception:
            continue
        for m in re.finditer(r"\*\*Email:\*\*\s*(\S+@\S+)", txt):
            by_email[m.group(1).strip().lower()] = f
    return by_email


def ensure_meetings_link(path, link, dry, actions):
    """Append `- [[link]]` under a `## Meetings` section in an existing contact note."""
    txt = path.read_text()
    if f"[[{link}]]" in txt:
        return
    if "## Meetings" in txt:
        new = re.sub(r"(## Meetings\s*\n)", r"\1- [[%s]]\n" % link, txt, count=1)
    else:
        new = txt.rstrip() + f"\n\n## Meetings\n- [[{link}]]\n"
    actions.append(f"  APPEND  {path.name}  += [[{link}]]")
    if not dry:
        path.write_text(new)


def create_contact(path, name, email, company, headline, date, link, dry, actions):
    fm = ["---", "type: person", "status: new"]
    if company:
        fm.append(f'company: "{company}"')
    fm += [f"date: {date}", "---", ""]
    fields = list(fm) + [f"# {name}", ""]
    if company:
        fields.append(f"**Company:** {company}")
    if email:
        fields.append(f"**Email:** {email}")
    fields.append(f"**Headline:** {headline}")
    fields.append("**Status:** New (from calendar)")
    fields.append(f"**First seen:** {date}")
    body = "\n".join(fields) + "\n\n## Notes\n\n## Meetings\n- [[%s]]\n" % link
    actions.append(f"  CREATE  Clients/{path.name}")
    if not dry:
        path.write_text(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, help="JSON from fetch_week_events.py")
    ap.add_argument("--vault", default=".", help="vault root (default cwd)")
    ap.add_argument("--self-email", default=default_self_email(),
                    help="your address, excluded from contacts (default: $CHARNESS_SELF_EMAIL or git config charness.selfEmail)")
    ap.add_argument("--domain-map", help="path to domain_map.yaml (optional)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    vault = Path(args.vault)
    clients_dir = vault / "Clients"
    notes_dir = vault / "notes"
    if not args.dry_run:
        clients_dir.mkdir(parents=True, exist_ok=True)
        notes_dir.mkdir(parents=True, exist_ok=True)

    data = json.load(open(args.sources))
    events = data.get("events", [])
    self_email = args.self_email.lower()
    domain_map = load_domain_map(args.domain_map) if args.domain_map else {}

    existing = index_existing_contacts(clients_dir)   # email -> path (pre-run)
    run_contacts = {}   # email(lower) -> path (created/resolved this run)
    actions = []
    new_contacts = existing_hits = mtg_created = mtg_skipped = 0

    def kept(att):
        email = (att.get("email") or "").strip().lower()
        if not email or email == self_email or att.get("is_current_user"):
            return False
        if att.get("type") in ("room", "resource"):
            return False
        if _FUNCTIONAL_LOCAL_RE.search(email.split("@", 1)[0]) or _is_list_domain(email):
            return False  # distribution list / shared calendar / functional mailbox — not a person
        return True

    for ev in events:
        people = [a for a in ev.get("attendees", []) if kept(a)]
        cdesc = clean_description(ev.get("description", ""))
        if not people and not cdesc:
            continue  # pure solo block, no notes -> not a meeting worth recording
        date_iso = (ev.get("start") or "")[:10]
        yyyymmdd = date_iso.replace("-", "")
        title = ev.get("title") or "(untitled)"
        mtg_link = f"{yyyymmdd}-{slugify(title)}"
        mtg_path = notes_dir / f"{mtg_link}.md"

        attendee_links = []
        for att in people:
            email = att["email"].strip()
            el = email.lower()
            name = display_name(att)
            attendee_links.append(f"[[{name}]]")

            # resolve target contact file: run cache -> existing-by-email -> new by name
            if el in run_contacts:
                target = run_contacts[el]
                existing_hit = True
            elif el in existing:
                target = existing[el]
                existing_hit = True
            else:
                target = clients_dir / f"{safe_filename(name)}.md"
                existing_hit = target.exists()

            if existing_hit or el in run_contacts:
                if target.exists():
                    ensure_meetings_link(target, mtg_link, args.dry_run, actions)
                else:
                    # first sighting this run of an already-name-collided file we haven't made
                    pass
                if el not in run_contacts and (el in existing):
                    existing_hits += 1
            if not target.exists() and el not in run_contacts:
                company = company_from_email(email, domain_map)
                headline = f'Met in "{title}" ({date_iso})' + (f" · {company}" if company else "")
                create_contact(target, name, email, company, headline, date_iso, mtg_link,
                               args.dry_run, actions)
                new_contacts += 1
            run_contacts[el] = target

        # meeting note (idempotent)
        if mtg_path.exists():
            mtg_skipped += 1
        else:
            when = ev.get("start", "")[11:16]
            loc = ev.get("location", "")
            locline = f"**Location:** {loc[:90]}\n" if loc and "http" not in loc.lower() else ""
            att_block = "\n".join(f"- {l}" for l in attendee_links) or "- (none listed)"
            notes_section = f"## Notes\n{cdesc}\n\n" if cdesc else "## Notes\n\n"
            body = (
                "---\n"
                "type: meeting\n"
                f"date: {date_iso}\n"
                "---\n\n"
                f"# Meeting — {title}\n\n"
                f"**Date:** {date_iso}\n"
                f"**Time:** {when}\n"
                f"**Source:** Google Calendar\n"
                f"**Event:** {title}\n"
                f"{locline}\n"
                # No empty '## TL;DR' stub at creation — a calendar event has no content to
                # summarize yet, and an empty heading renders blank on transclusion (the
                # progressive-disclosure silent-failure trap). The distill/backfill pass adds
                # ## TL;DR only once the meeting has real notes.
                "## Attendees\n" + att_block + "\n\n"
                + notes_section
                + "## My Notes\n\n## Next Steps\n\n"
                f"## Links\n- Daily report: [[{yyyymmdd}]]\n"
            )
            tag = f"{len(people)} attendees" + ("" if cdesc else ", no description")
            actions.append(f"  CREATE  notes/{mtg_path.name}  ({tag})")
            if not args.dry_run:
                mtg_path.write_text(body)
            mtg_created += 1

    hdr = "DRY RUN — no files written\n" if args.dry_run else ""
    sys.stdout.write(hdr + "\n".join(actions) + ("\n" if actions else ""))
    sys.stdout.write(
        "\nSummary: %d events processed · %d new contacts, %d existing · "
        "%d meeting notes created, %d already existed\n"
        % (len(events), new_contacts, existing_hits, mtg_created, mtg_skipped)
    )


if __name__ == "__main__":
    main()
