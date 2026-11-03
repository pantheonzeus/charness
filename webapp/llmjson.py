"""The JSON a model answered with, read the way Anthropic's Sonnet 5.5 prompting guide says to.

A model asked for "JSON only" sometimes works the problem out in prose first, or writes a draft before its
final JSON. Taking everything from the first `{` to the last `}` then spans both and fails to parse. Instead,
try a parse at each `{` or `[`, skip past every value that parses (so values nested inside it don't count on
their own), and keep the last one.
"""
import json

_dec = json.JSONDecoder()


def last_json(text):
    """The last top-level JSON object or array in text. ValueError when there is none."""
    found, i = None, 0
    while True:
        starts = [j for j in (text.find("{", i), text.find("[", i)) if j != -1]
        if not starts:
            break
        i = min(starts)
        try:
            found, i = _dec.raw_decode(text, i)
        except ValueError:
            i += 1
    if found is None:
        raise ValueError("no JSON value in the model's answer")
    return found
