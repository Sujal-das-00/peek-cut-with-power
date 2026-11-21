"""Voices that read a voice-over aloud, on this computer: Kokoro, run by sherpa-onnx (already part of PeakCut, so
nothing extra is installed). The voices are downloaded once, from Settings, Voices, and nothing about a voice-over
is ever sent to an outside service.

The download is unpacked next to where it will live and moved into place only when it is whole, the same as the
speech models (see fetch_model.py). Only the English voices are offered: the model's other languages are not
supported by the reader PeakCut uses, and a voice that mangles the words is worse than no voice.

    PEAKCUT_TTS_MODEL_URL      a mirror of the download (it must be the same file)
    PEAKCUT_TTS_MODEL_SHA256   the file's fingerprint, checked before anything is unpacked (empty: not checked)
"""
import hashlib
import os
import re
import shutil
import tarfile
import threading
import urllib.request
from pathlib import Path

import numpy as np

from . import config, safe
from .fetch_model import WAIT, WrongFile

NAME = "kokoro-multi-lang-v1_0"
URL = config.env("PEAKCUT_TTS_MODEL_URL") or f"https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/{NAME}.tar.bz2"
SHA256 = (config.env("PEAKCUT_TTS_MODEL_SHA256") or "").strip().lower()
SIZE_MB = 330
CREDIT = "Kokoro 82M by hexgrad (Apache-2.0), packaged for sherpa-onnx"
SAMPLE_TEXT = "Hi, I'm {name}. This is how your voice-over will sound on your clips."

# speaker number -> name, as listed by the model's own documentation. Only the English ones (0 to 27).
_NAMES = ("af_alloy af_aoede af_bella af_heart af_jessica af_kore af_nicole af_nova af_river af_sarah af_sky "
          "am_adam am_echo am_eric am_fenrir am_liam am_michael am_onyx am_puck am_santa "
          "bf_alice bf_emma bf_isabella bf_lily bm_daniel bm_fable bm_george bm_lewis").split()
VOICES = [{"id": i, "name": n[3:].capitalize(), "accent": "US" if n[0] == "a" else "UK",
           "gender": "female" if n[1] == "f" else "male", "code": n} for i, n in enumerate(_NAMES)]
DEFAULT_VOICE = 3          # Heart: the model's best-liked voice

state = {"doing": False, "percent": 0, "error": ""}
_lock = threading.Lock()             # one download at a time
_engine_lock = threading.Lock()      # building the reader
_say_lock = threading.Lock()         # the reader says one thing at a time
_engine = None


def folder() -> Path:
    return config.MODELS_DIR / NAME


def previews() -> Path:
    return config.MODELS_DIR / "kokoro-previews"


def ready() -> bool:
    d = folder()
    return all((d / f).is_file() for f in ("model.onnx", "voices.bin", "tokens.txt", "lexicon-us-en.txt")) and (d / "espeak-ng-data").is_dir()


def status() -> str:
    return "ready" if ready() else "downloading" if state["doing"] else "missing"


def valid(sid) -> bool:
    return isinstance(sid, int) and not isinstance(sid, bool) and 0 <= sid < len(VOICES)


def brief() -> dict:
    return {"state": status(), "size_mb": SIZE_MB, "percent": state["percent"], "error": state["error"], "credit": CREDIT,
            "default": DEFAULT_VOICE, "voices": VOICES}


# ---------------------------------------------------------------- downloading
def _save(dest) -> str:
    digest = hashlib.sha256()
    with urllib.request.urlopen(URL, timeout=WAIT) as r, open(dest, "wb") as f:
        total, got = int(r.headers.get("Content-Length") or 0), 0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            digest.update(chunk)
            got += len(chunk)
            if total > 0:
                state["percent"] = min(99, got * 100 // total)
    return digest.hexdigest()


def _fetch():
    state.update(doing=True, percent=0, error="")
    print(f"\n  Downloading the Kokoro voices (one time, about {SIZE_MB} MB)...\n", flush=True)
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    tmp, part = config.MODELS_DIR / "voices-model.tar.bz2", config.MODELS_DIR / "voices-model.unpacking"
    try:
        got_sha = _save(tmp)
        if SHA256 and got_sha != SHA256:
            raise WrongFile(f"its fingerprint (SHA-256) is {got_sha}, but PeakCut expects {SHA256}")
        shutil.rmtree(part, ignore_errors=True)
        part.mkdir()
        with tarfile.open(tmp, "r:bz2") as t:
            for m in t.getmembers():         # only plain files and folders that stay inside the unpacking folder
                if (m.isfile() or m.isdir()) and not m.name.startswith(("/", "..")) and ".." not in m.name.split("/"):
                    t.extract(m, part)
        got = part / NAME
        if not got.is_dir():
            raise OSError("the download did not contain the voices")
        shutil.rmtree(folder(), ignore_errors=True)
        got.rename(folder())
        if not ready():
            shutil.rmtree(folder(), ignore_errors=True)
            raise OSError("the download is missing some of the voice files")
        state["percent"] = 100
        print("  Kokoro voices ready.\n", flush=True)
    except WrongFile as e:
        state["error"] = f"The downloaded file is not the expected one: {e}."
        raise RuntimeError("PeakCut downloaded the voices, but the file is not the one it expects, so it was not used. "
                           f"Nothing was unpacked. Try again later. Details: {e}.") from e
    except Exception as e:  # noqa: BLE001
        state["error"] = safe.friendly(e, 200)
        raise RuntimeError(f"PeakCut couldn't download the voices (about {SIZE_MB} MB, needed once). Check the internet "
                           f"connection and free disk space, then try again. What it reported: {state['error']}") from e
    finally:
        state["doing"] = False
        tmp.unlink(missing_ok=True)
        shutil.rmtree(part, ignore_errors=True)


def start():
    """Begin downloading in the background (from the pages); progress is in `state`."""
    if ready() or state["doing"]:
        return
    state.update(doing=True, percent=0, error="")

    def run():
        try:
            with _lock:
                if not ready():
                    _fetch()
        except Exception:  # noqa: BLE001 - the reason is kept in state["error"]
            pass
        finally:
            state["doing"] = False
    threading.Thread(target=run, daemon=True, name="fetch-voices").start()


def remove():
    """Delete the voices to free the space. A voice-over can't be made until they are downloaded again."""
    global _engine
    with _lock:
        if state["doing"]:
            raise RuntimeError("The voices are still downloading.")
        with _engine_lock, _say_lock:
            _engine = None
        shutil.rmtree(folder(), ignore_errors=True)
        shutil.rmtree(previews(), ignore_errors=True)
        state.update(percent=0, error="")


# ---------------------------------------------------------------- speaking
def _reader():
    global _engine
    with _engine_lock:
        if _engine is None:
            if not ready():
                raise RuntimeError("The voices aren't on this computer yet. Download them in Settings, Voices "
                                   "(an admin can do this), then try again.")
            import sherpa_onnx as so
            d = folder()
            k = so.OfflineTtsKokoroModelConfig(model=str(d / "model.onnx"), voices=str(d / "voices.bin"), tokens=str(d / "tokens.txt"),
                                               data_dir=str(d / "espeak-ng-data"), dict_dir=str(d / "dict") if (d / "dict").is_dir() else "",
                                               lexicon=",".join(str(d / f) for f in ("lexicon-us-en.txt", "lexicon-zh.txt") if (d / f).is_file()))
            cfg = so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=k, num_threads=max(1, min(4, (os.cpu_count() or 2) // 2)), provider="cpu"),
                                      max_num_sentences=1)
            _engine = so.OfflineTts(cfg)
        return _engine


def say(text: str, sid: int, speed: float = 1.0):
    """The sound of `text` in one voice: (float samples, sample rate)."""
    if not valid(sid):
        raise ValueError("Choose one of the voices in the list.")
    eng = _reader()
    with _say_lock:
        out = eng.generate(text, sid=sid, speed=max(0.5, min(2.0, float(speed))))
    return np.asarray(out.samples, dtype=np.float32), int(out.sample_rate)


def sentences(text: str) -> list:
    """The text in sentences, so each can be timed on its own."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", str(text or "")).strip()) if p.strip()]
    return parts[:40]


def spread(text: str, start: float, end: float) -> list:
    """The words of a sentence placed along the time it takes to say it, longer words taking longer."""
    words = text.split()
    if not words:
        return []
    weights = [len(w) + 1 for w in words]
    total, t, out = sum(weights), start, []
    for w, wt in zip(words, weights):
        e = t + (end - start) * wt / total
        out.append({"w": w, "s": round(t, 2), "e": round(e, 2)})
        t = e
    return out


GAP = 0.15          # seconds of quiet between two sentences


def narrate(text: str, sid: int, out: Path, max_seconds: float | None = None) -> dict:
    """Read a voice-over into a WAV file. When it would run longer than `max_seconds` (the clip), it is read once
    more, faster (at most 1.4 times), so it ends with the clip. Returns {"seconds", "words", "speed"}: the words
    carry their own times, counted from the start of the file, for the captions."""
    import soundfile as sf
    sents = sentences(text)
    if not sents:
        raise ValueError("There is nothing to read.")
    speed = 1.0
    for attempt in range(2):
        pieces, words, t, rate = [], [], 0.0, 24000
        for s in sents:
            a, rate = say(s, sid, speed)
            d = len(a) / rate
            words += spread(s, t, t + d)
            pieces += [a, np.zeros(int(rate * GAP), dtype=np.float32)]
            t += d + GAP
        t -= GAP
        if not max_seconds or t <= max_seconds or attempt == 1:
            break
        speed = min(1.4, speed * t / max_seconds * 1.03)
    audio = np.concatenate(pieces[:-1])
    if max_seconds and len(audio) / rate > max_seconds:
        audio = audio[:int(max_seconds * rate)]
        words = [w for w in words if w["s"] < max_seconds]
    sf.write(str(out), audio, rate)
    return {"seconds": round(len(audio) / rate, 2), "words": words, "speed": round(speed, 2)}


def preview(sid: int) -> Path:
    """A few seconds of one voice, made the first time it is asked for and kept."""
    if not valid(sid):
        raise ValueError("Choose one of the voices in the list.")
    f = previews() / f"{sid}.wav"
    if not f.is_file():
        previews().mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp.wav")
        narrate(SAMPLE_TEXT.format(name=VOICES[sid]["name"]), sid, tmp)
        tmp.replace(f)
    return f
