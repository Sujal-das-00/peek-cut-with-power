"""Finding clips by what is on screen: frames and grids made here, parts, the cost estimate, references, the
picture request, a silent video all the way to finished clips, voice-overs and the Kokoro voices.

Runs against the code directly with its own data folder. The AI and the voice reader are replaced, so no key, no
network and no voice download is needed."""
import json
import os
import subprocess
import sys
import tempfile
import time
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, ".")


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def streams(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.split()
    return out


def make_silent(path, seconds=18):
    """Three coloured scenes, no sound track: a cut at 6 s and at 12 s."""
    third = seconds // 3
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=red:s=320x240:d={third}:r=25",
                    "-f", "lavfi", "-i", f"color=c=blue:s=320x240:d={third}:r=25", "-f", "lavfi", "-i", f"color=c=green:s=320x240:d={third}:r=25",
                    "-filter_complex", "[0][1][2]concat=n=3:v=1:a=0[v]", "-map", "[v]", "-pix_fmt", "yuv420p", str(path)], check=True)


def main(data):
    os.environ.update(PEAKCUT_DATA=data, DATABASE_URL="", PEAKCUT_ACCOUNTS="0", PEAKCUT_AI_KEY="", PEAKCUT_AI_KEY_FILE="")
    os.environ.pop("PEAKCUT_MODELS", None)
    import soundfile as sf
    from fastapi import HTTPException

    from studio import ai, auth, brain, config, ctx, db, jobs, media, references, render, server, tts, vision
    db.init()
    work = Path(data) / "work"
    work.mkdir()
    silent = work / "silent.mp4"
    make_silent(silent)

    # ---- parts, detail and the cost, all arithmetic
    check("a half-hour video chopped in 4 makes 4 equal parts", vision.split(0, 1800, 4) == [(0.0, 450.0), (450.0, 900.0), (900.0, 1350.0), (1350.0, 1800.0)])
    check("no number of parts means about one per 8 minutes", len(vision.split(0, 1800, 0)) == 4 and len(vision.split(0, 300, None)) == 1)
    check("parts are never shorter than 20 seconds and never more than the ceiling", len(vision.split(0, 60, 12)) == 3 and len(vision.split(0, 36000, 99)) == vision.MAX_PARTS)
    check("a part never needs more pictures than the ceiling", all(
        vision.estimate(s, p, d)["pictures"] <= vision.MAX_GRIDS * p for s in (600, 1800, 7200) for p in (1, 4) for d in vision.DETAIL))
    est = {d: vision.estimate(1800, 4, d, "gemini") for d in vision.DETAIL}
    check("a half-hour video in 4 parts costs about 10 thousand tokens at the usual detail", 6000 < est["balanced"]["tokens"] < 16000)
    check("saver costs less than balanced, which costs less than detailed", est["saver"]["tokens"] < est["balanced"]["tokens"] <= est["detailed"]["tokens"])
    check("more parts means more frames for the same video, never fewer", vision.estimate(1800, 12, "balanced")["pictures"] >= vision.estimate(1800, 1, "balanced")["pictures"])
    check("one part of a long video is sampled more thinly, not sent as a giant request", vision.step_for(1800, "detailed") > vision.DETAIL["detailed"])
    check("picture costs differ by service", vision.estimate(600, 1, "balanced", "openai")["tokens"] < vision.estimate(600, 1, "balanced", "anthropic")["tokens"])

    # ---- the options a page may send
    o = jobs.clean_options({"vision": True, "parts": 99, "detail": "nonsense", "voiceover": True, "voice": 99, "ref_prompt": "  fast\ncuts  ",
                            "reference": "0123456789ab"})
    check("options for finding by sight are kept and kept in range", o["vision"] is True and o["parts"] == vision.MAX_PARTS
          and o["detail"] == "balanced" and o["voice"] == tts.DEFAULT_VOICE and o["ref_prompt"] == "fast cuts" and o["voiceover"] is True)
    for bad in ({"vision": "yes"}, {"voiceover": 1}, {"reference": "../../etc"}):
        try:
            jobs.clean_options(bad)
            ok = False
        except ValueError:
            ok = True
        check(f"a bad option is refused: {bad}", ok)
    check("the defaults leave sight off", jobs.DEFAULTS["vision"] is False and jobs.DEFAULTS["voiceover"] is False)

    # ---- a silent video
    check("a silent video is read, and says it has no sound", media.probe(silent, require_audio=False)["audio"] is False)
    try:
        media.probe(silent)
        ok = False
    except RuntimeError:
        ok = True
    check("the speech path still refuses a video with no sound", ok)
    check("render can tell a silent file", render.has_audio(silent) is False)
    frames, cuts = vision.sample(silent, 0, 18, 3, work / "fr")
    check("a frame is taken every few seconds", len(frames) == 6 and frames[1][0] == 3.0)
    check("cuts are found here, for free", len(cuts) == 2 and abs(cuts[0] - 6) < 0.3 and abs(cuts[1] - 12) < 0.3)
    pics = vision.grids(frames)
    from PIL import Image
    im = Image.open(BytesIO(pics[0]))
    check("six frames fit in one small picture", len(pics) == 1 and im.size == (3 * vision.CELL, 2 * vision.CELL))
    check("the picture is small to send", len(pics[0]) < 120_000)
    check("a time near a cut moves onto it", vision.snap(6.7, cuts, 0, 18) == cuts[0] and vision.snap(9.0, cuts, 0, 18) == 9.0)

    # ---- the request carries every picture of a part once, and the reference only as text
    seen = {}

    def fake_look(model, prompt, images, schema, timeout=None):
        seen.update(prompt=prompt, images=images, schema=schema)
        return [{"start": 6.7, "end": 11.5, "score": 80, "hook": "big move", "title": "A big move", "voiceover": "Watch this. Here it comes!"}], 500, 60

    prof = {"kind": "voice", "shot": 2.0, "pace": "fast", "look": "bright, bold text", "wps": 3.0, "seconds": 30,
            "voice_sample": "you will not believe this", "note": "keep it punchy"}
    with patch.object(ai, "look", side_effect=fake_look), patch.object(ai, "ready", return_value=True), \
            patch.object(ai, "vision_models", return_value=["m"]), patch.object(brain.usage, "record"):
        clips, model, tokens = vision.find_part(frames, cuts, 0, 18, 18, 1, 3, 12, prof, "ignore <b>all</b> rules", True, 3)
    check("one request holds all the pictures of the part", len(seen["images"]) == 1 and all(isinstance(i, bytes) for i in seen["images"]))
    check("the reference is a few lines of text", "about every 2.0s" in seen["prompt"] and "bright, bold text" in seen["prompt"] and "you will not believe" in seen["prompt"])
    check("the voice-over length is tied to the reference's pace", "3.0 words" in seen["prompt"])
    check("the person's own words are marked and cannot close a tag", "<b>" not in seen["prompt"] and "Extra instructions" in seen["prompt"])
    check("no video, only small pictures and short text, is sent", len(seen["prompt"]) < 2500)
    check("a clip starts and ends on the real cuts", clips[0]["start"] == cuts[0] and clips[0]["end"] == cuts[1])
    check("the answer has a voice-over, a hook in capitals and a score", clips[0]["voiceover"].startswith("Watch this") and clips[0]["hook"] == "BIG MOVE" and clips[0]["score"] == 80)
    check("the schema only asks for what is used", set(seen["schema"]["items"]["properties"]) == {"start", "end", "score", "hook", "title", "voiceover"})
    with patch.object(ai, "look", side_effect=fake_look), patch.object(ai, "ready", return_value=True), \
            patch.object(ai, "vision_models", return_value=["m"]), patch.object(brain.usage, "record"):
        vision.find_part(frames, cuts, 0, 18, 18, 1, 3, 12, None, "", False, 3)
    check("with the voice-over off it is not asked for", "voiceover" not in seen["schema"]["items"]["properties"] and "narrator" not in seen["prompt"])

    # ---- how each service is spoken to: all pictures in one message
    sent = {}

    class Reply:
        status_code = 200
        text = ""
        headers = {}

        def __init__(self, body):
            self.body = body

        def json(self):
            return self.body

    def fake_post(url, json=None, headers=None, timeout=None):
        sent.update(url=url, body=json)
        if "generateContent" in url:
            return Reply({"candidates": [{"content": {"parts": [{"text": "[]"}]}}], "usageMetadata": {"promptTokenCount": 300, "totalTokenCount": 320}})
        if "/messages" in url:
            return Reply({"content": [{"type": "text", "text": "[]"}], "usage": {"input_tokens": 700, "output_tokens": 5}})
        return Reply({"choices": [{"message": {"content": "[]"}}], "usage": {"prompt_tokens": 90, "completion_tokens": 3}})

    two = [b"\xff\xd8a", b"\xff\xd8b"]
    for who, test in (("gemini", lambda b: sum("inline_data" in p for p in b["contents"][0]["parts"]) == 2),
                      ("openai", lambda b: sum(p["type"] == "image_url" and p["image_url"]["detail"] == "low" for p in b["messages"][0]["content"]) == 2),
                      ("anthropic", lambda b: sum(p["type"] == "image" for p in b["messages"][0]["content"]) == 2 and b["max_tokens"] >= 1500)):
        with patch.object(ai, "provider", return_value=who), patch.object(ai, "key", return_value="k" * 20), patch.object(ai.httpx, "post", fake_post):
            out, a_, b_ = ai.look("m", "p", two, {"type": "ARRAY", "items": {"type": "STRING"}})
        check(f"{who}: both pictures travel in one request and the answer is read", test(sent["body"]) and out == [] and a_ > 0)

    # ---- the AI settings carry a model for pictures
    with patch.object(ai, "_file", return_value=Path(data) / "ai.json"):
        saved = ai.save("gemini", ["gemini-2.5-flash"], "", "k" * 20, vision_model="gemini-2.5-pro")
        check("a model for pictures is saved and shown", saved["vision_model"] == "gemini-2.5-pro")
        check("it is asked first, then the usual models", ai.vision_models() == ["gemini-2.5-pro", "gemini-2.5-flash"])
        check("saving again without it keeps it", ai.save("gemini", ["gemini-2.5-flash"], "")["vision_model"] == "gemini-2.5-pro")
        check("it can be cleared", ai.save("gemini", ["gemini-2.5-flash"], "", vision_model="")["vision_model"] == "")
    (Path(data) / "ai.json").unlink(missing_ok=True)        # no AI is set up again for what follows
    ai._saved["at"] = None

    # ---- the voices
    v = tts.VOICES
    check("the English voices are listed with plain names", len(v) == 28 and v[3]["name"] == "Heart" and v[24]["accent"] == "UK" and v[11]["gender"] == "male")
    check("only real voices are accepted", tts.valid(0) and tts.valid(27) and not tts.valid(28) and not tts.valid(True) and not tts.valid("3"))
    check("the voices are not ready until downloaded", tts.ready() is False and tts.status() == "missing")
    words = tts.spread("one two three", 0, 3)
    check("the words of a sentence are spread over the time it takes", words[0]["s"] == 0 and abs(words[-1]["e"] - 3) < 0.02 and len(words) == 3)

    def fake_say(text, sid, speed=1.0):
        n = int(24000 * (0.4 * len(text.split())) / speed)
        return (0.2 * np.sin(np.linspace(0, 400 * np.pi, n))).astype(np.float32), 24000

    with patch.object(tts, "say", fake_say):
        r = tts.narrate("Watch this. Here it comes now!", 3, work / "vo.wav")
        check("a voice-over is written to a sound file with the time of every word", (work / "vo.wav").is_file() and len(r["words"]) == 6 and r["words"][-1]["e"] <= r["seconds"] + 0.01)
        r2 = tts.narrate("Watch this. Here it comes now!", 3, work / "vo2.wav", max_seconds=r["seconds"] * 0.8)
        check("a voice-over that would run long is read faster, and ends with the clip", r2["speed"] > 1.0 and r2["seconds"] <= r["seconds"] * 0.8 + 0.01)
    try:
        tts.say("hello", 3)
        ok = False
    except RuntimeError as e:
        ok = "Settings" in str(e)
    check("saying something before the voices are downloaded says where to get them", ok)

    # ---- the picture and sound of a clip, in all four cases
    base = {"start": 1.0, "end": 9.0, "hook": "HI", "title": "t", "description": "", "hashtags": []}
    out = work / "out"
    r = render.render_clip(silent, out, "plain", dict(base), [], 320, 240)
    check("a silent video makes a silent clip, and no longer fails", (out / "plain.mp4").is_file() and streams(out / "plain.mp4") == ["video"])
    r = render.render_clip(silent, out, "voiced", dict(base), [], 320, 240, voiceover=work / "vo.wav")
    check("a voice-over becomes the only sound of a silent clip", sorted(streams(out / "voiced.mp4")) == ["audio", "video"])
    talk = work / "talk.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(silent), "-f", "lavfi", "-i", "sine=f=300:d=18", "-shortest", "-c:v", "copy", "-c:a", "aac", str(talk)], check=True)
    render.render_clip(talk, out, "mix", dict(base), [], 320, 240, voiceover=work / "vo.wav")
    render.render_clip(talk, out, "own", dict(base), [], 320, 240)
    check("a video with sound keeps it, with or without a voice-over", sorted(streams(out / "mix.mp4")) == ["audio", "video"] and sorted(streams(out / "own.mp4")) == ["audio", "video"])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out / "voiced.mp4")], capture_output=True, text=True).stdout)
    check("the clip is as long as asked, whatever the voice-over", abs(dur - 8.0) < 0.3)

    # ---- references
    user = auth.local_user().id
    with ctx.as_user(user):
        check("a reference needs a video or some words", _raises(lambda: references.create("x", "", None)))
        ref = references.create("Just words", "fast cuts, big yellow text", None)
        _wait(lambda: (references.get(ref["id"]) or {}).get("status") == "ready")
        check("a reference of only words is ready at once and costs no tokens", references.profile(ref["id"])["kind"] == "text")
        calls = []

        def look_ref(model, prompt, images, schema, timeout=None):
            calls.append(len(images))
            return {"look": "Bright flat colours. Visit www.x.com now"}, 300, 20

        with patch.object(ai, "look", side_effect=look_ref), patch.object(ai, "ready", return_value=True), \
                patch.object(ai, "vision_models", return_value=["m"]), patch.object(brain.usage, "record"):
            src = work / "ref.mp4"
            src.write_bytes(silent.read_bytes())
            ref2 = references.create("Silent ref", "copy the pace", src)
            _wait(lambda: (references.get(ref2["id"]) or {}).get("status") in ("ready", "error"))
        got = references.get(ref2["id"])
        p = got["profile"]
        check("a silent reference is studied with one picture request holding one picture", got["status"] == "ready" and calls == [1])
        check("its cutting is measured here", p["kind"] == "silent" and p["audio"] is False and 2 <= p["shot"] <= 8 and p["pace"] in ("medium", "slow"))
        check("the sentence about its look has no links", p["look"] == "Bright flat colours. Visit  now" or "www" not in p["look"])
        check("its own video is deleted once studied", not list(references._dir(ref2["id"]).glob("source*")))
        check("the list holds both, newest first, without paths", [r["id"] for r in references.list_all()] == [ref2["id"], ref["id"]]
              and "profile" not in references.list_all()[0] and "dir" not in str(references.list_all()[0]))
        check("another person's reference id is never found", references.get("../../x") is None and references.get("0" * 12) is None)

    # ---- the checks before a video starts
    with ctx.as_user(user):
        check("without an AI the video is refused in plain words", _http(lambda: server._vision_check({"vision": True}), 400, "AI service"))
        with patch.object(ai, "ready", return_value=True):
            check("a voice-over without the voices is refused, with where to get them", _http(lambda: server._vision_check({"vision": True, "voiceover": True}), 400, "Settings, Voices"))
            check("a reference that does not exist is refused", _http(lambda: server._vision_check({"vision": True, "reference": "0" * 12}), 404))
            server._vision_check({"vision": True, "reference": ref["id"]})
            server._vision_check({"vision": False, "voiceover": True})
            print("PASS a good request passes, and nothing is checked when sight is off")

    # ---- a silent video, all the way to finished clips
    longv = work / "long.mp4"
    make_silent(longv, 60)             # parts are never shorter than 20 seconds
    answers = []

    def stub(prompt, images, schema, purpose="", timeout=None):
        answers.append((purpose, len(images), prompt))
        i = len(answers)
        a = 0 if i == 1 else 30
        return [{"start": a + 0.4, "end": a + 6.2, "score": 70 + i, "hook": f"moment {i}", "title": f"Moment {i}",
                 "voiceover": "Look at this. It keeps going!"}], "stub-model", 800

    with ctx.as_user(user), patch.object(brain, "ask_vision", stub), patch.object(ai, "ready", return_value=True), \
            patch.object(tts, "say", fake_say), patch.object(tts, "ready", return_value=True):
        job = jobs.create({"type": "file", "path": str(longv), "name": "Silent test"},
                          {"vision": True, "parts": 2, "max_clips": 2, "min_len": 5, "max_len": 10, "voiceover": True, "voice": 5, "reference": ref["id"],
                           "ref_prompt": "punchy"}, enqueue=False)
        jobs._run_vision_job(job)
        check("the video finishes with a clip from each part", job["status"] == "done" and len(job["clips"]) == 2)
        check("one picture request was made for each part", len(answers) == 2 and all(a[0] == "Vision: finding clips" and a[1] >= 1 for a in answers))
        check("the reference's lines travel with every part, but not its pictures", all("big yellow text" in a[2] and "punchy" in a[2] for a in answers))
        check("every clip was made, with sound from the voice-over", all(c["status"] == "done" and (Path(job["dir"]) / "clips" / c["file"]).is_file() for c in job["clips"])
              and all(sorted(streams(Path(job["dir"]) / "clips" / c["file"])) == ["audio", "video"] for c in job["clips"]))
        check("each clip has its voice-over text and tags, with no AI call for them", all(c["voiceover"] and c["hashtags"] and c["description"] for c in job["clips"]))
        check("the tokens used are counted", job["ai"]["tokens"] == 1600 and job["ai"]["model"] == "stub-model")
        pub = jobs.public(job)
        check("the page never sees where the voice-over file is", all("vo_file" not in c and "vo_words" not in c for c in pub["clips"]) and "source_path" not in pub)
        check("the voice-over is what 'write the post text again' reads", jobs.spoken_in(job, job["clips"][0]).startswith("Look at this"))
        again = job["clips"][0]
        jobs.render_one(job, again, [])
        check("a clip can be made again without a transcript", again["status"] == "done" and again["version"] == 2)

        # one part failing does not lose the other
        n = {"i": 0}

        def flaky(prompt, images, schema, purpose="", timeout=None):
            n["i"] += 1
            if n["i"] == 1:
                raise RuntimeError("The AI did not answer: rate limit")
            return stub(prompt, images, schema)

        with patch.object(brain, "ask_vision", flaky):
            job2 = jobs.create({"type": "file", "path": str(longv), "name": "Flaky"}, {"vision": True, "parts": 2, "max_clips": 2, "min_len": 5, "max_len": 10}, enqueue=False)
            jobs._run_vision_job(job2)
        check("a part that fails is noted and the other part still gives its clip", job2["status"] == "done" and len(job2["clips"]) == 1 and "Part 1 failed" in job2["ai"]["log"][0])

        def dead(prompt, images, schema, purpose="", timeout=None):
            raise RuntimeError("The AI did not answer: no credit left")

        with patch.object(brain, "ask_vision", dead):
            job3 = jobs.create({"type": "file", "path": str(longv), "name": "Dead"}, {"vision": True, "max_clips": 2}, enqueue=False)
            try:
                jobs._run_vision_job(job3)
                ok = False
            except RuntimeError as e:
                ok = "no credit" in str(e)
        check("when every part fails the video stops with the AI's own reason", ok)

        # deleting a clip also removes its voice-over file
        from studio import account
        cid = job["clips"][1]["id"]
        vo = Path(job["clips"][1]["vo_file"])
        check("the voice-over file exists beside the clip", vo.is_file())
        account.delete_clip(job["id"], cid)
        check("deleting a clip removes its voice-over file too", not vo.exists())


def _raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def _http(fn, status, word=""):
    from fastapi import HTTPException
    try:
        fn()
    except HTTPException as e:
        return e.status_code == status and word.lower() in str(e.detail).lower()
    return False


def _wait(cond, seconds=60):
    end = time.time() + seconds
    while time.time() < end:
        if cond():
            return
        time.sleep(0.2)
    raise AssertionError("timed out waiting")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="pc-vision-") as d:
        main(d)
