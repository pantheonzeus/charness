"""Local speech for the console — both directions run on-device via MLX (Apple Silicon).

  speech → text : Whisper large-v3-turbo   (~0.7s for a spoken question on an M5)
  text → speech : Qwen3-TTS 1.7B CustomVoice, 6-bit  (warm: first audio ~0.2s, ~2.3× faster than real time on an M5)

The voice carries emotion: each sentence is said in a tone (TONES) the Chief of Staff picks with a
[[tone: …]] directive (server.py). Audio never leaves the machine; only the transcript goes to Claude.
Models download once on first use (~1.6 GB + ~2 GB) into the Hugging Face cache.
"""
import io
import re
import threading

import numpy as np
import soundfile as sf

STT_MODEL = "mlx-community/whisper-large-v3-turbo"
TTS_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-6bit"
VOICE = "serena"    # the principal's pick by ear (2026-10-19), over Kokoro bf_emma: it can carry emotion
ACCENT = "Refined British RP accent."   # none of the model's voices is British; the instruction supplies it
# The tones the Chief of Staff may pick ([[tone: …]]); anything else is said calm.
TONES = {
    "calm": "Calm, clear and confident, like a trusted assistant giving a briefing.",
    "warm": "Warm and friendly, genuinely glad to help.",
    "dry": "Dry, understated British humour, a slight smile in the voice.",
    "pleased": "Bright and genuinely pleased, sharing good news.",
    "concerned": "Concerned and serious, a little lower and slower.",
    "urgent": "Urgent and focused, brisk but never panicked.",
    "gentle": "Gentle and reassuring, soft and unhurried.",
}
_lock = threading.Lock()  # one MLX job at a time; the GPU is shared
_tts = None

# Whisper's stock output on silence or noise — never a real question.
HALLUCINATIONS = {"", "you", "thank you", "thank you.", "thanks for watching!", "bye.", ".", "okay."}


def _model():
    global _tts
    if _tts is None:
        from mlx_audio.tts.utils import load_model
        _tts = load_model(TTS_MODEL)
    return _tts


def warm():
    """Load both models and run each once, so the first real turn isn't a cold start."""
    speak("Ready.")
    transcribe(_wav(np.zeros(16000, dtype=np.float32), 16000))


def transcribe(wav_bytes: bytes, vocabulary: str = "") -> str:
    """German or English, detected per turn; vault names as a vocabulary hint so they come out right."""
    import mlx_whisper
    audio, rate = sf.read(io.BytesIO(wav_bytes), dtype="float32")
    if rate != 16000:
        raise ValueError(f"expected 16 kHz audio, got {rate}")
    with _lock:
        text = mlx_whisper.transcribe(audio, path_or_hf_repo=STT_MODEL, language=None,
                                      initial_prompt=(f"Names: {vocabulary}." if vocabulary else None),
                                      condition_on_previous_text=False)["text"].strip()
    # Whisper's output on silence: stock phrases, or punctuation with no words at all.
    return "" if text.lower() in HALLUCINATIONS or len(re.findall(r"\w", text)) < 2 else text


def _cap(text: str) -> int:
    """Most tokens a sentence may take (12.5 per second of audio): twice a slow reading (~7 chars/s, serena runs
    ~14) plus 3 s. The library's default, 4096, is 5.5 minutes: a sentence whose end the model misses would
    babble on that long, holding the GPU lock while everything else waits."""
    return int(12.5 * (len(text) / 7 + 3))


def _capped(secs: float, text: str):
    if secs >= _cap(text) / 12.5 - 1:
        print(f"speech: a sentence hit the length cap ({secs:.0f}s of audio for {len(text)} chars)", flush=True)


def speak(text: str, tone: str = "calm") -> bytes:
    instruct = f"{ACCENT} {TONES.get(tone, TONES['calm'])}"
    with _lock:
        chunks = [np.array(r.audio) for r in _model().generate(text=text, voice=VOICE, instruct=instruct, lang_code="auto",
                                                               max_tokens=_cap(text))]
    audio = np.concatenate(chunks) if chunks else np.zeros(2400, dtype=np.float32)
    _capped(len(audio) / 24000, text)
    return _wav(audio, 24000)


def stream(text: str, tone: str = "calm"):
    """The same, ~0.3 s at a time as it is generated (float32, 24 kHz), so playback can start at once.
    Holds the GPU lock until the sentence is done or the caller stops iterating."""
    instruct = f"{ACCENT} {TONES.get(tone, TONES['calm'])}"
    secs = 0.0
    with _lock:
        for r in _model().generate(text=text, voice=VOICE, instruct=instruct, lang_code="auto",
                                   stream=True, streaming_interval=0.32, max_tokens=_cap(text)):
            chunk = np.asarray(r.audio, dtype=np.float32)
            secs += len(chunk) / 24000
            yield chunk
    _capped(secs, text)


def _wav(audio, rate) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def speakable(text: str) -> str:
    """Markdown → something worth saying out loud. Code, tables and URLs are skipped."""
    text = re.sub(r"```.*?(```|$)", " ", text, flags=re.S)
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|"))
    text = re.sub(r"\[\[([^\]|]+)(\|([^\]]+))?\]\]", lambda m: m.group(3) or m.group(1), text)  # [[Note|alias]]
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)                                        # [label](url)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^\s*(#+|[-*•]|\d+\.)\s+", "", text, flags=re.M)
    text = re.sub(r"[*_~>#]", "", text)
    return re.sub(r"\s+", " ", text).strip()


class Sentences:
    """Cuts a token stream into sentences so speech can start before the reply is finished."""

    def __init__(self):
        self.buf, self.first = "", True

    def feed(self, delta: str) -> list[str]:
        self.buf += delta
        out = []
        while True:
            m = re.search(r"(?<=[.!?;:])\s+|\n\s*\n|\n(?=\s*[-*•\d])", self.buf)
            if not m:
                return out
            piece, rest = self.buf[:m.end()], self.buf[m.end():]
            # The first sentence goes out at once (latency); later ones get merged until
            # they're long enough that synthesis overhead doesn't chop the rhythm.
            if not self.first and len(speakable(piece)) < 40 and rest.strip():
                nxt = re.search(r"(?<=[.!?;:])\s+|\n\s*\n", rest)
                if not nxt:
                    return out
                piece, rest = piece + rest[:nxt.end()], rest[nxt.end():]
            self.buf, self.first = rest, False
            if speakable(piece):
                out.append(speakable(piece))

    def flush(self) -> list[str]:
        piece, self.buf = speakable(self.buf), ""
        return [piece] if piece else []
