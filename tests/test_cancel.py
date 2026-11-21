"""Cancelling: a video that is waiting or being made, and a single clip that is being made. Whatever was already
finished is kept, whatever was not is gone, running programs are stopped, and the queue carries on.

Runs against the code directly with its own data folder. The AI and the voice reader are replaced."""
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, ".")


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def wait(cond, seconds=60):
    end = time.time() + seconds
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.1)
    return False


def make_video(path, seconds=60):
    third = seconds // 3
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=red:s=320x240:d={third}:r=25",
                    "-f", "lavfi", "-i", f"color=c=blue:s=320x240:d={third}:r=25", "-f", "lavfi", "-i", f"color=c=green:s=320x240:d={third}:r=25",
                    "-filter_complex", "[0][1][2]concat=n=3:v=1:a=0[v]", "-map", "[v]", "-pix_fmt", "yuv420p", str(path)], check=True)


def main(data):
    os.environ.update(PEAKCUT_DATA=data, DATABASE_URL="", PEAKCUT_ACCOUNTS="0", PEAKCUT_AI_KEY="", PEAKCUT_AI_KEY_FILE="")
    from fastapi import HTTPException

    from studio import ai, auth, brain, ctx, db, jobs, media, render, server
    db.init()
    work = Path(data) / "work"
    work.mkdir()
    video = work / "long.mp4"
    make_video(video)
    user = auth.local_user().id

    # ---- a running program is stopped, quickly
    flag = {"stop": False}
    threading.Timer(1.0, lambda: flag.update(stop=True)).start()
    t0 = time.time()
    try:
        media.run_cancellable(["sleep", "30"], cancel=lambda: flag["stop"])
        ok = False
    except media.Cancelled:
        ok = time.time() - t0 < 4
    check("a long ffmpeg-style program is killed within a moment of Cancel", ok)
    check("a program left alone finishes normally", media.run_cancellable(["echo", "hi"]).stdout.strip() == "hi")

    stub_state = {"enter": threading.Event(), "go": threading.Event(), "calls": 0}

    def stub(prompt, images, schema, purpose="", timeout=None):
        stub_state["calls"] += 1
        n = stub_state["calls"]
        if n == 2:                                  # the second part waits here until the test says go
            stub_state["enter"].set()
            stub_state["go"].wait(30)
        a = 0 if n == 1 else 30
        return [{"start": a + 0.4, "end": a + 6.2, "score": 70, "hook": f"moment {n}", "title": f"Moment {n}"}], "stub", 100

    with ctx.as_user(user), patch.object(brain, "ask_vision", stub), patch.object(ai, "ready", return_value=True):
        # ---- a video that is waiting its turn stops at once, and the queue does not stall
        waiting = jobs.create({"type": "file", "path": str(video), "name": "Waiting"}, {"vision": True}, enqueue=False)
        jobs.cancel(waiting)
        check("a waiting video is cancelled at once", waiting["status"] == "done" and waiting["stage"] == "Cancelled by you" and waiting["clips"] == [])
        try:
            jobs.cancel(waiting)
            ok = False
        except ValueError:
            ok = True
        check("a video that is not being made cannot be cancelled again", ok)

        # ---- a video in the middle: the first part's clip is finished and kept, the second part never happens
        threading.Thread(target=jobs._worker, daemon=True).start()
        job = jobs.create({"type": "file", "path": str(video), "name": "Middle"},
                          {"vision": True, "parts": 2, "max_clips": 2, "min_len": 5, "max_len": 10}, enqueue=True)
        check("the second part is reached", stub_state["enter"].wait(60))
        check("the first part's clip finishes while the second is being asked about", wait(lambda: any(c["status"] == "done" for c in job["clips"])))
        jobs.cancel(job)
        check("cancelling shows it is stopping", job["stage"] == "Cancelling…" and job["status"] == "running")
        stub_state["go"].set()
        check("the video stops", wait(lambda: job["status"] == "done"))
        check("it says who stopped it", job["stage"] == "Cancelled by you" and job.get("cancelled_at"))
        check("the finished clip is kept and nothing from the second part appears", len(job["clips"]) == 1 and job["clips"][0]["status"] == "done"
              and (Path(job["dir"]) / "clips" / job["clips"][0]["file"]).is_file())
        check("the AI was not asked about a third thing", stub_state["calls"] == 2)
        check("the picture work folder is cleaned up", not (Path(job["dir"]) / "frames").exists())
        check("the line moves on afterwards", wait(lambda: jobs.running_now() == 0))
        pub = jobs.public(job)
        check("the page can tell it was cancelled", pub["cancelled_at"] and "_prev" not in str(pub["clips"]))

        # ---- the next video still works after a cancel
        stub_state.update(enter=threading.Event(), go=threading.Event(), calls=10)
        stub_state["go"].set()
        after = jobs.create({"type": "file", "path": str(video), "name": "After"}, {"vision": True, "parts": 1, "max_clips": 1, "min_len": 5, "max_len": 10}, enqueue=True)
        check("a video made after a cancel finishes normally", wait(lambda: after["status"] == "done") and len(after["clips"]) == 1 and after["clips"][0]["status"] == "done")

        # ---- one clip, cancelled while it is being made for the first time: it disappears
        gate = {"started": threading.Event(), "go": threading.Event()}

        def slow(src, out_dir, name, clip, words, w, h, voiceover=None, cancel=None):
            gate["started"].set()
            while not cancel():
                time.sleep(0.05)
            raise media.Cancelled()

        j2 = jobs.create({"type": "file", "path": str(video), "name": "One clip"}, {}, enqueue=False)
        j2.update(status="done", duration=60.0, width=320, height=240, source_path=str(video))
        new = {"id": "clip01", "start": 1.0, "end": 9.0, "status": "queued", "hook": "NEW", "title": "t", "description": "", "hashtags": [],
               "score": 50, "version": 0, "queued_at": time.time()}
        j2["clips"] = [new]
        (Path(j2["dir"]) / "clips").mkdir(exist_ok=True)
        (Path(j2["dir"]) / "clips" / "clip01.ass").write_text("x")
        with patch.object(render, "render_clip", slow):
            t = threading.Thread(target=jobs.render_one, args=(j2, new, []))
            t.start()
            check("the clip is being made", gate["started"].wait(10) and new["status"] == "rendering")
            jobs.cancel_clip(j2, new)
            t.join(10)
        check("a clip cancelled while it is first made is removed", j2["clips"] == [] and not t.is_alive())
        check("its leftover files are removed", not (Path(j2["dir"]) / "clips" / "clip01.ass").exists())

        # ---- a waiting clip with nothing made yet disappears at once
        q = {"id": "clip02", "start": 1.0, "end": 9.0, "status": "queued", "hook": "Q", "title": "", "description": "", "hashtags": [], "score": 1, "version": 0}
        j2["clips"] = [q]
        jobs.cancel_clip(j2, q)
        check("a waiting clip cancelled before it starts is gone at once", j2["clips"] == [])
        render_calls = []
        with patch.object(render, "render_clip", lambda *a, **k: render_calls.append(1) or {}):
            jobs.render_one(j2, q, [])
        check("and if its turn comes anyway, nothing is made", render_calls == [])

        # ---- a clip being made again: cancelling puts it back as it was
        clips_dir = Path(j2["dir"]) / "clips"
        (clips_dir / "clip03.mp4").write_bytes(b"old video")
        old = {"id": "clip03", "start": 2.0, "end": 12.0, "status": "done", "hook": "OLD HOOK", "title": "Old title", "description": "", "hashtags": ["a"],
               "score": 60, "version": 1, "file": "clip03.mp4", "cover": "clip03.jpg", "layout": "blur", "style": "bounce"}
        j2["clips"] = [old]
        jobs._jobs[j2["id"]] = j2
        with patch.object(jobs._q, "put"):
            jobs.request_render(j2["id"], "clip03", {"hook": "NEW HOOK", "start": 3.0, "end": 14.0})
        check("a re-make changes the clip and remembers how it was", old["hook"] == "NEW HOOK" and old["status"] == "queued" and old["_prev"]["hook"] == "OLD HOOK")
        gate["started"].clear()
        with patch.object(render, "render_clip", slow):
            t = threading.Thread(target=jobs.render_one, args=(j2, old, []))
            t.start()
            gate["started"].wait(10)
            jobs.cancel_clip(j2, old)
            t.join(10)
        check("a re-make that is cancelled goes back to the video it had", old["status"] == "done" and old["hook"] == "OLD HOOK"
              and old["start"] == 2.0 and old["end"] == 12.0 and "_prev" not in old and "cancel" not in old and (clips_dir / "clip03.mp4").read_bytes() == b"old video")

        # ---- the checks in front of the buttons
        done_job = after
        for name, call in (("cancelling a finished video", lambda: server.cancel_job(done_job["id"])),
                           ("cancelling a finished clip", lambda: server.cancel_clip(done_job["id"], done_job["clips"][0]["id"]))):
            try:
                call()
                ok = False
            except HTTPException as e:
                ok = e.status_code == 409
            check(f"{name} is refused", ok)
        try:
            server.cancel_job("nonexistent-id")
            ok = False
        except HTTPException as e:
            ok = e.status_code == 404
        check("cancelling a video that is not there says so", ok)

        # ---- cancelled before the server stopped: it stays cancelled when the server is back
        jobs._jobs.pop(waiting["id"], None)
        j3 = jobs.create({"type": "file", "path": str(video), "name": "Restart"}, {}, enqueue=False)
        j3.update(status="running", cancelled_at=time.time())
        jobs.save(j3)
        jobs._jobs.pop(j3["id"], None)
        jobs._by_user.get(user, {}).pop(j3["id"], None)
        jobs._load_file(Path(j3["dir"]) / "job.json", user)
        back = jobs._jobs[j3["id"]]
        check("a cancel is not forgotten by a restart", back["status"] == "done" and back["stage"] == "Cancelled by you" and not back.get("resume"))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="pc-cancel-") as d:
        main(d)
