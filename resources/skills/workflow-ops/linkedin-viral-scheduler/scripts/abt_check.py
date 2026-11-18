"""ABT guard for LinkedIn drafts (added 2026-11-18).

Tight ABT (Randy Olson's And, But, Therefore): one setup, one dominant turn,
one consequence. Beats connect by therefore/but, never by "and then".
Mechanical proxy only; the arc itself is the writer's job
(content/linkedin-authentic-storytelling §2).

Usage: python3 abt_check.py <post.md>
Prints one line; exit 0 = pass, 1 = fail, 2 = usage error.
Pass iff: 90-200 words (hashtags excluded), zero "and then",
1-3 turn words (but/except/however/yet), >= 1 consequence word
(so/therefore/that's why/which means).
"""
import re
import sys

if len(sys.argv) != 2:
    print("usage: abt_check.py <post.md>", file=sys.stderr)
    sys.exit(2)
text = open(sys.argv[1], encoding="utf-8").read()
text = text.split("\n---\n")[0]  # ignore a FIRST COMMENT block after a --- rule
body = re.sub(r"#\w+", "", text).lower()
words = len(re.findall(r"[\w']+", body))
and_then = len(re.findall(r"\band then\b", body))
turns = len(re.findall(r"\b(but|except|however|yet)\b", body))
cons = len(re.findall(r"\b(so|therefore|that's why|which means)\b", body))
ok = 90 <= words <= 200 and and_then == 0 and 1 <= turns <= 3 and cons >= 1
print(f"abt words={words} and_then={and_then} turns={turns} consequences={cons} verdict={'pass' if ok else 'fail'}")
sys.exit(0 if ok else 1)
