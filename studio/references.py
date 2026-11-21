"""References: a video (or just some words) that shows how the finished clips should look.

A reference can be a silent video, a video with a voice, or only a text description, and it can carry a note of
the person's own. When one is added it is studied once, here, and boiled down to a few lines (how often it cuts,
how it looks, how fast and in what words the voice speaks). Only those few lines are ever sent to the AI, with each
part of a video, so a reference costs almost nothing to use again and again. The reference's own video is deleted
once it has been studied; only a small cover picture stays, for the list.

Each person's references are kept in their own folder: users/<id>/references/<reference id>/ref.json."""
import json
import re
import shutil
import threading
import time
import uuid
from pathlib import Path

from . import brain, config, ctx, media, safe, vision

ID = re.compile(r"[0-9a-f]{12}")
MAX_REFERENCES = 30
MAX_MB = 400                 # the biggest reference video accepted
_lock = threading.RLock()


def _root() -> Path:
    return config.user_dir(ctx.uid()) / "references"


def _dir(rid: str) -> Path:
    return _root() / rid


def _read(rid: str):
    try:
        return json.loads((_dir(rid) / "ref.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write(ref: dict):
    d = _dir(ref["id"])
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / "ref.json.tmp"
    tmp.write_text(json.dumps(ref, indent=1), encoding="utf-8")
    tmp.replace(d / "ref.json")
    ctx.bump()


def get(rid) -> dict | None:
    """The reference, only if it belongs to whoever this runs for."""
    return _read(rid) if isinstance(rid, str) and ID.fullmatch(rid) else None


def public(ref: dict) -> dict:
    """What the page may see: no files, no paths."""
    p = ref.get("profile") or {}
    return {"id": ref["id"], "name": ref["name"], "note": ref.get("note", ""), "status": ref["status"], "stage": ref.get("stage", ""),
            "error": ref.get("error", ""), "created": ref["created"], "kind": p.get("kind", ""), "seconds": p.get("seconds", 0),
            "audio": bool(p.get("audio")), "pace": p.get("pace", ""), "shot": p.get("shot", 0), "look": p.get("look", ""),
            "wps": p.get("wps", 0), "voice_sample": p.get("voice_sample", ""), "cover": bool(ref.get("cover"))}


def list_all() -> list:
    out = []
    root = _root()
    for f in root.glob("*/ref.json") if root.is_dir() else []:
        try:
            ref = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if ref.get("status") == "analyzing" and time.time() - ref.get("created", 0) > 1800:
            ref.update(status="error", error="The study of this reference was interrupted. Add it again.")
        out.append(public(ref))
    return sorted(out, key=lambda r: -r["created"])


def profile(rid) -> dict | None:
    """The reference's boiled-down text, for a job. None when it is gone or not finished."""
    ref = get(rid)
    return ref.get("profile") if ref and ref.get("status") == "ready" else None


def clean_name(v) -> str:
    return " ".join(str(v or "").split())[:60] or "Reference"


def create(name: str, note: str, video: Path | None) -> dict:
    """Start studying a reference. `video` is a file already saved on this computer (or None for text only); it is
    moved into the reference's folder and deleted when the study ends. Returns at once; the study runs behind."""
    note = brain._safe(note, 500)
    if not video and not note:
        raise ValueError("Add a reference video, or describe in words how the clips should look.")
    with _lock:
        if len(list(_root().glob("*/ref.json"))) >= MAX_REFERENCES if _root().is_dir() else False:
            raise ValueError(f"You can keep {MAX_REFERENCES} references. Delete one first.")
        rid = uuid.uuid4().hex[:12]
        ref = {"id": rid, "name": clean_name(name), "note": note, "status": "analyzing", "stage": "Waiting", "created": time.time(),
               "error": "", "profile": None, "cover": False}
        _dir(rid).mkdir(parents=True)
        src = None
        if video:
            src = _dir(rid) / ("source" + Path(video).suffix.lower())
            shutil.move(str(video), src)
        _write(ref)
    threading.Thread(target=ctx.bind(_study), args=(rid, src), daemon=True, name="study-" + rid).start()
    return ref


def _study(rid: str, src: Path | None):
    ref = _read(rid)
    if not ref:
        return

    def stage(text):
        ref["stage"] = text
        _write(ref)
    try:
        if src and src.is_file():
            stage("Studying the video")
            try:
                if media.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", str(src), "-frames:v", "1", "-vf", "scale=320:-2",
                              "-q:v", "5", str(_dir(rid) / "cover.jpg")]) is not None and (_dir(rid) / "cover.jpg").is_file():
                    ref["cover"] = True
            except Exception:  # noqa: BLE001 - a list without a picture is fine
                pass
        ref["profile"] = vision.build_profile(src if src and src.is_file() else None, ref.get("note", ""), stage)
        ref.update(status="ready", stage="Ready", error="")
    except Exception as e:  # noqa: BLE001
        ref.update(status="error", error=safe.friendly(e, 300), stage="")
    finally:
        if src:
            src.unlink(missing_ok=True)        # only the few lines about it are kept
    _write(ref)


def delete(rid: str) -> bool:
    ref = get(rid)
    if not ref:
        return False
    shutil.rmtree(_dir(rid), ignore_errors=True)
    ctx.bump()
    return True


def cover_path(rid: str):
    ref = get(rid)
    f = _dir(rid) / "cover.jpg" if ref else None
    return f if f and f.is_file() else None
