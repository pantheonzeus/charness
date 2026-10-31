"""Native microphone for the console (JARVIS spec v1, §2): capture happens here, not in the browser.

Why: Chrome routes every tab's audio through one process, so a mic opened by the console would look
exactly like a Meet call to the meeting shield. Here the mic belongs to the server process, which
presence.py excludes by PID, and any browser mic use left over is someone's call.

  push-to-talk   hold Right Option (native helper) or the console's mic button; audio only while held
  follow-up      5 s after a reply to a turn YOU started; only your verified voice counts
  voiceprint     enrolled once (3 phrases), kept at ~/.config/cbrain/voiceprint.npy (0600), on-device only
Audio is never written to disk. The built-in mic is used by name, never a Bluetooth input (AirPods
would drop to call quality).
"""
import io
import os
import threading
import time
from pathlib import Path

import numpy as np
import soundfile as sf

RATE = 16000
VOICEPRINT = Path.home() / ".config" / "cbrain" / "voiceprint.npy"
SPK_MODEL = ("Wespeaker/wespeaker-voxceleb-resnet34-LM", "voxceleb_resnet34_LM.onnx")
MAX_SECS, FOLLOWUP_SECS, END_SILENCE = 60, 5, 0.9
MIN_RUN_S = 0.3   # a mic stream runs at least this long before it is stopped


def wav(audio):
    buf = io.BytesIO()
    sf.write(buf, audio, RATE, format="WAV", subtype="PCM_16")
    return buf.getvalue()


class Speaker:
    """On-device speaker verification: ResNet34 embeddings (ONNX), cosine against your enrolled print."""

    def __init__(self):
        self.sess, self.opts, self.lock = None, None, threading.Lock()
        self.print, self.threshold = None, 0.55
        if VOICEPRINT.exists():
            d = np.load(VOICEPRINT, allow_pickle=False)
            self.print, self.threshold = d[:-1], float(d[-1])

    def _load(self):
        if self.sess is None:
            import kaldi_native_fbank as knf
            import onnxruntime as ort
            from huggingface_hub import hf_hub_download
            self.sess = ort.InferenceSession(hf_hub_download(*SPK_MODEL))
            o = knf.FbankOptions()
            o.frame_opts.dither, o.frame_opts.samp_freq, o.mel_opts.num_bins = 0, RATE, 80
            self.opts, self.knf = o, knf

    def embed(self, audio):
        with self.lock:
            self._load()
            f = self.knf.OnlineFbank(self.opts)
            f.accept_waveform(RATE, (audio * 32768).tolist())
            f.input_finished()
            m = np.stack([f.get_frame(i) for i in range(f.num_frames_ready)])
            e = self.sess.run(None, {self.sess.get_inputs()[0].name: (m - m.mean(0))[None].astype(np.float32)})[0][0]
            return e / np.linalg.norm(e)

    def enroll(self, samples):
        embs = [self.embed(s) for s in samples]
        mean = np.mean(embs, axis=0)
        mean /= np.linalg.norm(mean)
        mutual = min(float(a @ b) for i, a in enumerate(embs) for b in embs[i + 1:])
        self.print, self.threshold = mean, float(np.clip(mutual - 0.12, 0.40, 0.70))
        VOICEPRINT.parent.mkdir(parents=True, exist_ok=True)
        with open(VOICEPRINT, "wb") as fh:
            np.save(fh, np.append(mean, self.threshold))
        os.chmod(VOICEPRINT, 0o600)
        return {"threshold": round(self.threshold, 2), "consistency": round(mutual, 2)}

    def reset(self):
        VOICEPRINT.unlink(missing_ok=True)
        self.print = None

    def verify(self, audio):
        if self.print is None:
            return False, 0.0
        score = float(self.embed(audio) @ self.print)
        return score >= self.threshold, score


class Capture:
    def __init__(self):
        self.device, self.stream, self.frames, self.gen, self.started = None, None, [], 0, 0.0
        self.lock = threading.Lock()
        self.speaker = Speaker()
        self.enrolling = None             # list of samples while enrolling
        try:
            import sounddevice as sd
            self.sd = sd
            ins = [(i, d["name"]) for i, d in enumerate(sd.query_devices()) if d["max_input_channels"] > 0]
            self.device = next((i for i, n in ins if "macbook" in n.lower() or "built-in" in n.lower()), None)
            self.device_name = next((n for i, n in ins if i == self.device), None)
        except Exception as e:            # no PortAudio / no devices: the console falls back to browser capture
            self.sd, self.device_name, self.error = None, None, str(e)

    @property
    def available(self):
        return self.sd is not None and self.device is not None

    def info(self):
        return {"available": self.available, "device": self.device_name, "enrolled": self.speaker.print is not None,
                "enrolling": None if self.enrolling is None else len(self.enrolling), "recording": self.stream is not None}

    # ---------- push-to-talk ----------
    def start(self, take=False):
        """Open the mic. take: a take already running (the follow-up window) becomes a fresh one on the same
        stream. Never stop and restart the device here: CoreAudio deadlocks PortAudio when a stream stops while a
        start/stop notification is in flight (seen 2026-10-29: the mic stuck open, the presence thread frozen)."""
        with self.lock:
            if not self.available or (self.stream is not None and not take):
                return False
            self.gen += 1                 # a follow-up window that sees this stops: the mic is no longer its own
            self.frames = []
            if self.stream is None:
                self.stream = self.sd.InputStream(device=self.device, channels=1, samplerate=RATE, dtype="float32",
                                                  callback=lambda x, n, t, s: self.frames.append(x[:, 0].copy()))
                self.stream.start()
                self.started = time.time()
            return True

    def stop(self, gen=None):
        """Close the mic; return the take as float32 audio (None if nothing usable).
        gen: only if it is still that take (push-to-talk may have taken the mic over)."""
        settle = self.started + MIN_RUN_S - time.time()
        if settle > 0:                    # the same deadlock: a stop right after the start is when it strikes
            time.sleep(settle)
        with self.lock:
            if self.stream is None or (gen is not None and gen != self.gen):
                return None
            self.stream.stop()
            self.stream.close()
            self.stream = None
            audio = np.concatenate(self.frames) if self.frames else np.zeros(0, np.float32)
            self.frames = []
        audio = audio[: MAX_SECS * RATE]
        return audio if len(audio) > 0.35 * RATE else None

    def abort(self):
        self.stop()

    # ---------- follow-up window ----------
    def followup(self, allowed, on_open=None, secs=FOLLOWUP_SECS):
        """Listen up to `secs` (5 s by default) for your voice; return (audio, score) or (None, reason).
        `allowed()` is re-checked every frame: if the shield goes up, the mic closes at once."""
        if not self.available or self.speaker.print is None or not self.start():
            return None, "unavailable"
        gen = self.gen
        on_open and on_open()
        t0, noise, voiced, started, silent = time.time(), None, 0, None, 0.0
        seen = 0
        try:
            while True:
                time.sleep(0.05)
                if not allowed():
                    self.stop(gen)
                    return None, "shielded"
                with self.lock:
                    if self.gen != gen:   # push-to-talk took the mic over
                        return None, "push-to-talk"
                    new = self.frames[seen:]
                    seen = len(self.frames)
                for fr in new:
                    rms = float(np.sqrt(np.mean(fr * fr))) if len(fr) else 0.0
                    if noise is None:
                        noise = rms
                    if started is None:
                        voiced = voiced + 1 if rms > max(0.012, noise * 3) else 0
                        noise = noise if voiced else noise * 0.9 + rms * 0.1
                        if voiced >= 4:
                            started = time.time()
                    else:
                        silent = 0.0 if rms > max(0.01, noise * 2.5) else silent + len(fr) / RATE
                if started is None and time.time() - t0 > secs:
                    self.stop(gen)
                    return None, "timeout"
                if started and (silent >= END_SILENCE or time.time() - started > 20):
                    break
        except Exception:
            self.stop(gen)
            raise
        audio = self.stop(gen)
        if audio is None:
            return None, "short"
        ok, score = self.speaker.verify(audio)
        return (audio, score) if ok else (None, f"not your voice ({score:.2f})")


capture = Capture()
