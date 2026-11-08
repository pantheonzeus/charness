#!/usr/bin/env python3
"""
Pre-Publish Audit — deterministic scorer for the "will the algorithm carry it"
gate (see references/rubric.md, Scorecard B). No judge calls: every sub-metric
is computed from the text with documented heuristics for the two soft parts
(curiosity-gap, CTA genuineness).

Usage: prepublish_audit.py <path-to-post.md>
Exit 0 iff composite >= 85 (the framework's own "Viral Potential" band).
Prints one JSON line (machine-readable) then one human summary line.

Weights: Hook 30% · Readability 20% · Spacing 20% · AI-Fluff 30%.

Also reports three post-hoc viral/quality signals (added 2026-07-19, see
references/viral-metrics.md #8-10): Sovereignty/EU-Framing, Save-Worthiness,
Conversation-Trigger. These are REPORTED ONLY — they never enter `composite`
and never affect the exit code. They exist so a draft can see these signals
before publishing, without disturbing the three-gate ship criteria.
"""

import json
import re
import statistics
import sys

# --- Canonical phrase lists (single source of truth; kept in sync with the
# banned-phrase list in references/rubric.md used by the mutator step). ---
FLUFF_OPENERS = [
    "i wanted to share", "in my experience", "reflecting on",
    "in today's", "in todays", "i'm excited to", "im excited to",
    "thoughts on", "excited to announce", "thrilled to share",
]

# Added 2026-07-19, from the analytics read (see references/rubric.md,
# "Pitch-opener penalty"): both 2026-07 flops opened on a generalising
# capability claim with no first-person voice — a pitch, not a lived
# moment — and both cleared the old Hook metric while landing near-zero
# engagement. This is a deliberately modest mechanical pre-signal; the
# real enforcement is Scorecard C's P2 (Story-over-Pitch) judge.
PITCH_OPENER_SUBJECTS_RE = re.compile(
    r"\b(most|every|nobody|manufacturers|factories|companies|businesses)\b",
    re.IGNORECASE,
)
PITCH_ANNOUNCEMENT_RE = re.compile(
    r"\bas-a-service\b.{0,30}\b(changes|flips|means)\b", re.IGNORECASE
)
PERSONAL_MARKER_RE = re.compile(
    r"\b(I|my|we|our|ich|mich|mir|mein\w*|wir|uns|unser\w*)\b", re.IGNORECASE
)

AI_FLUFF_PHRASES = [
    "moreover", "furthermore", "in conclusion", "delve", "testament",
    "thrilled to share", "excited to announce", "game-changer", "game changer",
    "unlock the power of", "ever-evolving", "ever evolving", "leverage",
    "synergy", "seamless", "cutting-edge", "cutting edge", "paradigm shift",
    "landscape", "in today's fast-paced", "in todays fast-paced",
]

# Engagement-bait closes. Expanded 2026-08-18: LinkedIn's own 2026 feed release
# names "engagement bait" and "comment to agree" prompts as downranked, and both
# notebook sources independently call generic closes momentum-killers. The old
# three-string list let "What's your take?" and "Let's continue the conversation
# in the comments" score a *perfect* CTA — the exact shapes now penalised.
CTA_BAIT = [
    "agree?", "thoughts?", "right?", "am i wrong", "who else",
    "comment below", "comment yes", "comment 'yes'", "drop a comment",
    "tag someone", "tag a friend", "let me know in the comments",
    "what's your take", "whats your take", "what do you think?",
    "let's continue the conversation", "lets continue the conversation",
    "thoughts below", "sound off", "repost if", "share if you agree",
    "who agrees", "raise your hand",
]

TENSION_MARKERS = [
    "everyone", "nobody", "wrong", "stop", "myth", "don't", "dont",
    "nearly", "never",
]

# --- Family B post-hoc signals (added 2026-07-19, see references/viral-metrics.md).
# Reported only — not part of `composite`, do not gate the exit code. ---

# Sovereignty/EU-Framing: this account's highest-converting, most under-used
# axis per engagement-learnings.md Rule 3. Four independent categories; hitting
# more of them (not just repeating one) is what the score rewards.
# EN + DE terms, same precedent as score_ai_fluff's personal-marker regex —
# without the DE terms the highest-converting post in the whole corpus
# (Finnish Independence Day, entirely in German) scores 0 here by omission,
# not because the framing is actually absent.
SOVEREIGNTY_CATEGORIES = {
    "sovereignty": [r"sovereign\w*", r"souver[äa]n\w*", r"own(?:ing)? (?:the|our) data",
                     r"hyperscaler"],
    "eu_institutional": [r"\beu\b", r"european union", r"europ[äa]ische union",
                          r"horizon", r"consortium", r"konsortium",
                          r"brussels", r"\bga review\b", r"grant \d"],
    "resilience_capacity": [r"resilien\w*", r"\bcapacity\b", r"kapazit[äa]t\w*",
                             r"supply chain", r"lieferkette"],
    "defense_security": [r"defen[cs]e", r"\bsecurity\b", r"sicherheit\w*",
                          r"verteidigung\w*", r"milit[äa]r\w*", r"govtech", r"\bnato\b"],
}
SOVEREIGNTY_CATEGORIES_RE = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
    for cat, pats in SOVEREIGNTY_CATEGORIES.items()
}

# --- Buyer-Dialect Density (Family B #11, added 2026-08-18) ---------------
# Why this exists: LinkedIn's 2026 retrieval layer embeds members and posts into
# one semantic space, and a member's vector is built from their profile, skills,
# work history and the posts they have engaged with (Tier-1; see
# references/ranking-model-2026.md M4). So the *vocabulary* a post uses is part
# of what decides which audience it is retrieved to. This account's measured
# Rule 5 gap — on-theme manufacturing content, but IT-services/consulting
# viewers — is consistent with posts being written in consultant dialect.
#
# This is a LEXICAL proxy for a SEMANTIC mechanism, and deliberately a modest
# one: it counts words, it cannot judge whether the post is genuinely about the
# buyer's problem. It is reported, never gating. Scorecard C's P1 judge remains
# the real enforcement of buyer resonance.
#
# Note on the overlap: "servitization"/"digitalization" are consultant-dialect
# words AND names of this account's own positioning pillars. A low score does
# NOT mean "stop writing about servitization" — it means the concept arrived
# without the buyer's own words next to it. Pair the pillar word with plant
# words; don't delete the pillar.
BUYER_DIALECT_TERMS = [
    r"\boee\b", r"unplanned downtime", r"\bdowntime\b", r"\bchangeover\b",
    r"r[üu]stzeit\w*", r"umr[üu]st\w*", r"\bretooling\b", r"cycle time",
    r"taktzeit\w*", r"\btakt\b", r"scrap rate", r"\bausschuss\b",
    r"first[- ]pass yield", r"\byield\b", r"\bshift\b", r"\bschicht\w*",
    r"production line", r"\bshop floor\b", r"werkshalle", r"maintenance window",
    r"wartungsfenster", r"spare parts?", r"ersatzteil\w*", r"lead time",
    r"lieferzeit\w*", r"\bthroughput\b", r"\bdurchsatz\b", r"\bbottleneck\b",
    r"\bengpass\b", r"\bcommissioning\b", r"inbetriebnahme", r"ramp[- ]up",
    r"machine hours?", r"maschinenstunde\w*", r"\bspindle\b", r"\bplc\b",
    r"\bsps\b", r"opc ?ua", r"\bscada\b", r"\bmes\b", r"\bhistorian\b",
    r"\bbrownfield\b", r"\bretrofit\w*", r"\bplant\b", r"\bwerk\b",
    r"\boperator\b", r"\bbediener\b", r"pay[- ]per[- ]part", r"asset onboarding",
    r"iec ?62443", r"\bnis2\b", r"air[- ]gapped", r"network segmentation",
    r"\btooling\b", r"\bfixture\b", r"second shift", r"\bmtbf\b",
    r"predictive maintenance", r"\bcapex\b", r"\bopex\b",
    # DE parity (added 2026-08-18). Same rationale as score_sovereignty's DE
    # terms: this account posts in German, and its highest-converting post is
    # entirely in German — without these, a German plant-floor post scores 0
    # here by omission rather than because the dialect is absent.
    r"\bstillstand\w*", r"\banlage\b", r"\banlagen\w*", r"instandhaltung\w*",
    r"\bwartung\w*", r"produktionslinie\w*", r"fertigungslinie\w*",
    r"\bst[öo]rung\w*", r"nachr[üu]st\w*", r"bestandsanlage\w*",
    r"\bfertigung\b", r"\bmaschinenpark\b", r"\bschichtbetrieb\b",
]
CONSULTANT_DIALECT_TERMS = [
    r"digital transformation", r"transformation journey", r"servitis?ation",
    r"servitiz\w*", r"business model transformation", r"value proposition",
    r"\benablement\b", r"end[- ]to[- ]end", r"\bholistic\w*\b",
    r"ecosystem play", r"\broadmap\b", r"maturity model", r"best practices?",
    r"\bframework\b", r"thought leadership", r"stakeholder alignment",
    r"change management", r"cent(?:er|re) of excellence", r"operating model",
    r"digitali[sz]ation", r"data[- ]driven", r"unlock(?:ing)? value",
    r"capability building", r"north star", r"\bplaybook\b",
    r"operational excellence", r"value[- ]based pricing",
]
BUYER_DIALECT_RE = [re.compile(p, re.IGNORECASE) for p in BUYER_DIALECT_TERMS]
CONSULTANT_DIALECT_RE = [re.compile(p, re.IGNORECASE) for p in CONSULTANT_DIALECT_TERMS]

# Save-Worthiness: cues that the post is a reusable reference, not a one-read
# take. Uses text-level enumeration cues rather than markdown list syntax,
# since the archived vault posts (fetched from the live rendering) carry no
# preserved line breaks — this must work on a single-paragraph body too.
ENUMERATION_RE = re.compile(
    r"\b(firstly?,|secondly?,|thirdly?,|two things|three things|four things|"
    r"two reasons|three reasons|two questions|the breakdown|here's why|"
    r"here's the|\(1\)|\b1\)|\b1\.\s)",
    re.IGNORECASE,
)
# A repeated Title-Case term (2-4 words, hyphens allowed) is the mechanical
# proxy for "a named, reusable framework" (e.g. "Manufacturing-as-a-Service",
# "Revenue Bridge") — one mention is incidental capitalization, two is a coined term.
NAMED_PHRASE_RE = re.compile(
    r"\b(?:[A-Z][\w'-]*\s+){1,3}[A-Z][\w'-]*\b"
)

# Conversation-Trigger: a genuine open question anywhere in the body (not just
# the Spacing metric's last-line CTA check) + a stakeable contrast, e.g.
# "X, not Y" / "instead of" / a direct second-person stake.
NAMED_TENSION_RE = re.compile(
    r"\b(instead of|rather than|\bvs\.?\b|\bversus\b|not \w+, ?\w+|"
    r"what's your|what would you|would your)\b",
    re.IGNORECASE,
)

# Same detection approach as scripts/hygiene_check.sh, restated here in
# Python so this scorer is self-contained (not shelling out).
LINK_RE = re.compile(r'(https?://|www\.)[^\s)"\']+')
HASHTAG_RE = re.compile(r'(?:^|[^\w#])(#[A-Za-z][A-Za-z0-9_]*)')
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]"
)


def sentences_of(text):
    """Naive sentence split on ./!/? followed by whitespace or end-of-text."""
    body = LINK_RE.sub(" ", text)  # don't let a URL's dots count as sentence breaks
    parts = re.split(r'(?<=[.!?])\s+', body.strip())
    return [p.strip() for p in parts if p.strip()]


def words_of(text_no_tags_no_links):
    return [w for w in re.findall(r"[A-Za-z']+", text_no_tags_no_links) if w]


def score_hook(lines):
    content_lines = [l for l in lines if l.strip()]
    if not content_lines:
        return 0, "empty post"

    # The "hook" is the opening block before the first blank line (the actual
    # pre-"...see more" preview on mobile) — not strictly the first physical
    # line. A staccato hook split across two consecutive lines with no blank
    # line between them ("Everyone's chasing X.\nWe nearly did too.") reads as
    # one hook and must be measured as one; only a blank line ends the block.
    hook_block = []
    for l in lines:
        if not l.strip():
            if hook_block:
                break
            continue
        hook_block.append(l.strip())
        if len(hook_block) == 2:
            break
    hook_text = " ".join(hook_block)
    len1 = len(hook_text)

    if 70 <= len1 <= 140:
        base = 95
    elif 50 <= len1 <= 69:
        base = 80
    elif 141 <= len1 <= 180:
        base = 78
    elif 30 <= len1 <= 49:
        base = 70
    elif 181 <= len1 <= 220:
        base = 55
    elif len1 < 30:
        base = 60
    else:  # > 220 chars before the first break — a wall, no early break
        base = 30

    opener_lower = hook_text.lower()
    if any(opener_lower.startswith(p) or p in opener_lower[:60] for p in FLUFF_OPENERS):
        base = min(base, 40)

    is_pitch_opener = (
        not PERSONAL_MARKER_RE.search(hook_text)
        and (
            bool(PITCH_OPENER_SUBJECTS_RE.match(hook_text.strip()))
            or bool(PITCH_ANNOUNCEMENT_RE.search(hook_text))
        )
    )
    if is_pitch_opener:
        base = min(base, 55)

    has_digit = bool(re.search(r'\d|%|€|\$', opener_lower))
    has_tension = any(m in opener_lower for m in TENSION_MARKERS)
    curiosity_present = has_digit or has_tension

    if curiosity_present:
        base = min(base + 5, 100)
    else:
        base = min(base, 82)  # good length but no hook payoff

    return max(0, min(100, base)), f"hook_block_len={len1} curiosity={curiosity_present} pitch_opener={is_pitch_opener}"


def score_readability(text):
    no_links = LINK_RE.sub(" ", text)
    no_tags = HASHTAG_RE.sub(" ", no_links)
    wc = len(words_of(no_tags))

    if 60 <= wc <= 220:
        word_score = 100
    elif 40 <= wc <= 280:
        word_score = 70
    else:
        word_score = 40

    sents = sentences_of(no_tags)
    lens = [len(words_of(s)) for s in sents if words_of(s)]
    avg_len = statistics.mean(lens) if lens else 0

    if avg_len < 15:
        avg_score = 100
    elif avg_len <= 20:
        avg_score = 80
    elif avg_len <= 25:
        avg_score = 60
    else:
        avg_score = 35

    stdev = statistics.pstdev(lens) if len(lens) > 1 else 0
    if stdev >= 6:
        var_score = 100
    elif stdev >= 3:
        var_score = 75
    else:
        var_score = 55

    score = 0.4 * word_score + 0.4 * avg_score + 0.2 * var_score
    return round(score, 1), {"wordcount": wc, "avg_sentence_len": round(avg_len, 1), "sentence_len_stdev": round(stdev, 2)}, lens


def score_spacing(text, lines, sents_count):
    links = LINK_RE.findall(text)
    tags = HASHTAG_RE.findall(text)

    if len(links) > 0:
        return 20.0, {"reason": "outbound link in body", "links": len(links), "hashtags": len(tags)}
    if len(tags) > 3:
        return 35.0, {"reason": ">3 hashtags", "links": len(links), "hashtags": len(tags)}

    # drop hashtag-only lines (e.g. a trailing "#Foo #Bar" line) from the content-line count
    content_lines = [
        l for l in lines
        if l.strip() and not re.fullmatch(r'(\s*#[A-Za-z0-9_]+\s*)+', l.strip())
    ]

    ratio = len(content_lines) / max(1, sents_count)
    if ratio >= 0.7:
        one_idea = 100
    elif ratio >= 0.4:
        one_idea = 75
    else:
        one_idea = 45

    blank_blocks = len(re.findall(r'\n[ \t]*\n', text))
    if blank_blocks >= 4:
        whitespace = 100
    elif blank_blocks >= 2:
        whitespace = 80
    else:
        whitespace = 50

    emoji_count = len(EMOJI_RE.findall(text))
    emoji_score = 100 if emoji_count <= 5 else 60

    non_tag_lines = [l.strip() for l in content_lines if l.strip()]
    last_line = non_tag_lines[-1] if non_tag_lines else ""
    last_lower = last_line.lower()
    # CTA scoring rebalanced 2026-08-18. Previously a question-shaped close was
    # the ONLY route to a full score (100) and any declarative close was capped
    # at 70 — the scorer structurally pushed every post toward "What do you
    # think?". A question and a strong declarative close are now scored equally;
    # bait is a real penalty rather than a mild one.
    if any(b in last_lower for b in CTA_BAIT):
        cta = 35
    elif len(words_of(last_line)) > 4:
        # Substantive close, question or statement — both are legitimate endings.
        cta = 90
    else:
        # Trailing fragment / one-liner sign-off: weak either way.
        cta = 65

    score = 0.35 * one_idea + 0.25 * whitespace + 0.15 * emoji_score + 0.25 * cta
    return round(score, 1), {
        "links": len(links), "hashtags": len(tags), "one_idea_per_line": one_idea,
        "whitespace": whitespace, "emoji_count": emoji_count, "cta": cta,
    }


def hard_anchor_count(text):
    """Digit anchors + mid-sentence capitalized words (proper-noun proxy).

    Extracted from score_ai_fluff so score_saveworthiness (Family B #9) can
    reuse the identical count instead of re-implementing it."""
    digit_anchors = len(re.findall(r'\d+', text))
    # mid-sentence capitalized words as a proper-noun proxy (skip each sentence's first word)
    proper_noun_anchors = 0
    for s in sentences_of(text):
        toks = s.split()
        for t in toks[1:]:
            w = t.strip(".,!?\"'()")
            if w and w[0].isupper() and w.lower() not in ("i",):
                proper_noun_anchors += 1
    return digit_anchors + proper_noun_anchors


def score_ai_fluff(text, sent_lens):
    score = 100
    lower = text.lower()
    hits = []
    for phrase in AI_FLUFF_PHRASES:
        n = lower.count(phrase)
        if n:
            hits.append((phrase, n))
            score -= 12 * n

    # First-person markers, EN + DE (ich/mich/mir, mein*, wir, uns, unser*) — a
    # German post has a strong personal voice the EN-only pattern read as zero,
    # flooring AI-Fluff at 70; the DE terms let it score honestly.
    personal = len(re.findall(
        r"\b(I|my|we|our|ich|mich|mir|mein\w*|wir|uns|unser\w*)\b",
        text, flags=re.IGNORECASE))
    if personal == 0:
        score -= 30
    elif personal < 2:
        score -= 10

    anchors = hard_anchor_count(text)
    if anchors == 0:
        score -= 25
    elif anchors < 3:
        score -= 10

    stdev = statistics.pstdev(sent_lens) if len(sent_lens) > 1 else 0
    if stdev < 2:
        score -= 10

    score = max(0, min(100, score))
    return score, {"phrase_hits": hits, "personal_markers": personal, "hard_anchors": anchors, "sentence_len_stdev": round(stdev, 2)}


def score_sovereignty(text):
    """Family B #8 — Sovereignty/EU-Framing Signal. 25pt per distinct category
    hit (cap 100) + 15pt bonus if any hit lands in the first ~180 chars (the
    hook region — a char-prefix, not a line count, so it works whether or not
    the source preserves line breaks; see viral-metrics.md)."""
    hook_region = text[:180]
    hits = {}
    hook_hit = False
    for cat, patterns in SOVEREIGNTY_CATEGORIES_RE.items():
        cat_hit = any(p.search(text) for p in patterns)
        hits[cat] = cat_hit
        if cat_hit and any(p.search(hook_region) for p in patterns):
            hook_hit = True
    n_categories = sum(1 for v in hits.values() if v)
    base = min(100, 25 * n_categories)
    bonus = 15 if hook_hit else 0
    score = min(100, base + bonus)
    return score, {"categories_hit": sorted(c for c, v in hits.items() if v), "hook_bonus": bonus}


def score_saveworthiness(text):
    """Family B #9 — Save-Worthiness (Reference Value): predicts Save Rate.
    30pt hard-anchor density (cap at 10 anchors) + 30pt enumeration cue +
    40pt a repeated (>=2x) Title-Case phrase, i.e. a named, reusable concept."""
    anchors = hard_anchor_count(text)
    anchor_score = min(30, anchors * 3)

    enum_hit = bool(ENUMERATION_RE.search(text))
    enum_score = 30 if enum_hit else 0

    phrases = NAMED_PHRASE_RE.findall(text)
    counts = {}
    for p in phrases:
        counts[p] = counts.get(p, 0) + 1
    repeated = sorted(p for p, c in counts.items() if c >= 2)
    framework_score = 40 if repeated else 0

    score = max(0, min(100, anchor_score + enum_score + framework_score))
    return score, {"hard_anchors": anchors, "enumeration_cue": enum_hit, "repeated_phrases": repeated[:3]}


def score_conversation_trigger(text):
    """Family B #10 — Conversation-Trigger Score: predicts Conversation Density.
    40pt a genuine open question anywhere in the body (>4 words, not CTA-bait —
    distinct from Spacing's last-line-only CTA check) + 30pt a contrarian/
    stakeable claim (TENSION_MARKERS) + 30pt a named, specific contrast."""
    sents = sentences_of(text)
    question_sents = [s for s in sents if s.strip().endswith("?")]
    genuine_q = any(
        len(words_of(s)) > 4 and not any(b in s.lower() for b in CTA_BAIT)
        for s in question_sents
    )
    if genuine_q:
        question_score = 40
    elif question_sents:
        question_score = 15
    else:
        question_score = 0

    lower = text.lower()
    tension_hits = sum(1 for m in TENSION_MARKERS if m in lower)
    contrarian_score = min(30, tension_hits * 10)

    named_tension = bool(NAMED_TENSION_RE.search(text))
    named_score = 30 if named_tension else 0

    score = max(0, min(100, question_score + contrarian_score + named_score))
    return score, {
        "genuine_question": genuine_q, "tension_hits": tension_hits,
        "named_tension": named_tension,
    }


def _readable(pattern):
    """Strip regex furniture so the audit's detail output names terms, not patterns."""
    out = pattern.replace(r"\b", "").replace(r"\w*", "").replace("?", "")
    out = out.replace("[- ]", " ").replace("(?:er|re)", "er")
    out = re.sub(r"\(\?:[^)]*\)", "", out)
    return out.strip()


def score_buyer_dialect(text):
    """Family B #11 — Buyer-Dialect Density: predicts Family A #6
    (Decision-Maker Density / manufacturing-viewer share), NOT engagement rate.

    60pt for distinct buyer-dialect terms present (10 each, capped at 6 terms)
    + 20pt if at least one lands in the first ~180 chars (the hook region — same
    char-prefix convention as score_sovereignty, so it survives the archive's
    line-break-stripped bodies) + 20pt dominance bonus when buyer terms
    outnumber consultant-dialect terms (10pt if tied and both present).

    Reported, non-gating. A lexical proxy for a semantic mechanism — see the
    term-bank comment above, and references/ranking-model-2026.md M4.
    """
    hook_region = text[:180]
    buyer_hits = sorted({_readable(m.pattern) for m in BUYER_DIALECT_RE if m.search(text)})
    consultant_hits = sorted({_readable(m.pattern) for m in CONSULTANT_DIALECT_RE if m.search(text)})
    hook_hit = any(m.search(hook_region) for m in BUYER_DIALECT_RE)

    term_score = min(60, 10 * len(buyer_hits))
    hook_bonus = 20 if hook_hit else 0
    if buyer_hits and len(buyer_hits) > len(consultant_hits):
        dominance = 20
    elif buyer_hits and len(buyer_hits) == len(consultant_hits):
        dominance = 10
    else:
        dominance = 0

    score = min(100, term_score + hook_bonus + dominance)
    return score, {
        "buyer_terms": len(buyer_hits),
        "consultant_terms": len(consultant_hits),
        "buyer_matched": buyer_hits,
        "consultant_matched": consultant_hits,
        "hook_bonus": hook_bonus,
        "dominance": dominance,
    }


def band_for(composite):
    if composite >= 85:
        return "Viral Potential"
    if composite >= 50:
        return "Standard Reach"
    return "Fluffed / Suppressed"


def main():
    if len(sys.argv) != 2:
        print("usage: prepublish_audit.py <path-to-post.md>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    lines = text.split("\n")
    sents = sentences_of(text)

    hook_score, hook_detail = score_hook(lines)
    readability_score, readability_detail, sent_lens = score_readability(text)
    spacing_score, spacing_detail = score_spacing(text, lines, max(1, len(sents)))
    aifluff_score, aifluff_detail = score_ai_fluff(text, sent_lens)

    composite = round(
        0.30 * hook_score + 0.20 * readability_score + 0.20 * spacing_score + 0.30 * aifluff_score,
        1,
    )
    band = band_for(composite)

    # Family B post-hoc signals (references/viral-metrics.md #8-10) — reported
    # only, never enter `composite`, never affect the exit code below.
    sovereignty_score, sovereignty_detail = score_sovereignty(text)
    saveworthiness_score, saveworthiness_detail = score_saveworthiness(text)
    convo_score, convo_detail = score_conversation_trigger(text)
    dialect_score, dialect_detail = score_buyer_dialect(text)

    result = {
        "hook": hook_score,
        "readability": readability_score,
        "spacing": spacing_score,
        "aifluff": aifluff_score,
        "composite": composite,
        "band": band,
        "sovereignty": sovereignty_score,
        "saveworthiness": saveworthiness_score,
        "conversation_trigger": convo_score,
        "buyer_dialect": dialect_score,
        "detail": {
            "hook": hook_detail,
            "readability": readability_detail,
            "spacing": spacing_detail,
            "aifluff": aifluff_detail,
            "sovereignty": sovereignty_detail,
            "saveworthiness": saveworthiness_detail,
            "conversation_trigger": convo_detail,
            "buyer_dialect": dialect_detail,
        },
    }
    print(json.dumps(result))
    print(
        f"hook={hook_score} readability={readability_score} spacing={spacing_score} "
        f"aifluff={aifluff_score} composite={composite} band=\"{band}\" | "
        f"sovereignty={sovereignty_score} saveworthiness={saveworthiness_score} "
        f"conversation_trigger={convo_score} buyer_dialect={dialect_score} "
        f"(reported, non-gating)"
    )

    sys.exit(0 if composite >= 85 else 1)


if __name__ == "__main__":
    main()
