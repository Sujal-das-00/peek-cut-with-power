"""Many channels: each with its own upload times, in groups, fed by creators, and one click that puts every ready
clip on them. YouTube is a stand-in: nothing leaves this machine."""
import os, sys, tempfile, time
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-channels-")
os.environ.update(DATABASE_URL="", PEAKCUT_ACCOUNTS="0", PEAKCUT_PUBLIC_URL="http://127.0.0.1:8765")
sys.path.insert(0, ".")
from pathlib import Path
from fastapi.testclient import TestClient
from studio import accounts, auth, creators, ctx, db, jobs, posting, server
db.init()
fails = []
def check(n, got, want=True):
    ok = want(got) if callable(want) else got == want
    print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"   got {got!r}")); ok or fails.append(n)

BASE = "http://127.0.0.1:8765"
H = {"Origin": BASE}
c = TestClient(server.app, base_url=BASE, follow_redirects=False)
uid = auth.local_user().id
hhmm = lambda t: time.strftime("%H:%M", time.localtime(t))   # noqa: E731
day = lambda t: time.strftime("%Y-%m-%d", time.localtime(t))   # noqa: E731

with ctx.as_user(uid):
    for aid, pf, name in (("yt_A", "youtube", "Alpha Clips"), ("yt_B", "youtube", "Beta Shorts"), ("tt_C", "tiktok", "@gamma")):
        accounts._put({"id": aid, "platform": pf, "name": name, "added": time.time(), "access_token": "secret-tok", "expires": time.time() + 3600})

cid = c.post("/api/creators", json={"name": "Streamer"}, headers=H).json()["id"]
check("a creator can post to two channels", c.put(f"/api/creators/{cid}", json={"accounts": ["yt_A", "yt_B"]}, headers=H).status_code, 200)

# a finished video with five clips, scores 50..90
with ctx.as_user(uid):
    d = creators.root(cid) / "videos" / "job1"
    (d / "clips").mkdir(parents=True, exist_ok=True)
    job = {"id": "job1", "user": uid, "kind": "video", "creator": cid, "dir": str(d), "created": time.time(), "source": {},
           "options": {}, "status": "done", "clips": [{"id": f"k{i}", "status": "done", "score": 50 + 10 * i, "title": f"Clip {i}",
                                                     "file": f"k{i}.mp4", "made_at": time.time()} for i in range(5)]}
    jobs._jobs["job1"] = job
    jobs._by_user.setdefault(uid, {})["job1"] = job

# ---- a channel's own upload times
r = c.put("/api/accounts/yt_A", json={"schedule_on": True, "times": "10:00, 8:00, 09:00"}, headers=H)
check("a channel's times are saved", r.status_code, 200)
check("a bad time is refused with a reason", (c.put("/api/accounts/yt_A", json={"times": "8am"}, headers=H).status_code), 400)
check("a channel that isn't connected is refused", c.put("/api/accounts/yt_Z", json={"schedule_on": True}, headers=H).status_code, 404)
accs = {a["id"]: a for a in c.get("/api/accounts").json()}
check("the page sees the tidy times", accs["yt_A"]["schedule"], {"on": True, "times": ["08:00", "09:00", "10:00"], "own": True, "ahead": True})
check("a channel without its own times has no schedule", accs["yt_B"]["schedule"]["on"], False)
check("tokens never reach the page", "secret-tok" in c.get("/api/accounts").text, False)

# ---- groups
r = c.post("/api/groups", json={"name": "Gaming", "accounts": ["yt_A", "yt_B"]}, headers=H)
gid = r.json()["id"]
check("a group is made with its channels", [a["group"] for a in c.get("/api/accounts").json() if a["id"] != "tt_C"], [gid, gid])
check("two groups can't share a name", c.post("/api/groups", json={"name": "gaming"}, headers=H).status_code, 400)
check("a group can be renamed", (c.put(f"/api/groups/{gid}", json={"name": "Games"}, headers=H).status_code, c.get("/api/channels").json()["groups"][0]["name"]), (200, "Games"))
r = c.put(f"/api/groups/{gid}", json={"schedule_on": True, "times": ["08:00", "09:00", "10:00"]}, headers=H)
check("one schedule for the whole group", {a["id"]: a["schedule"]["times"] for a in c.get("/api/accounts").json() if a["group"] == gid},
      {"yt_A": ["08:00", "09:00", "10:00"], "yt_B": ["08:00", "09:00", "10:00"]})

# ---- one click: a preview first, then for real
r = c.post("/api/posts/plan", json={"group": gid, "dry": True}, headers=H).json()
check("the preview counts every clip for every channel", (r["queued"], [x["queued"] for x in r["channels"]]), (10, [5, 5]))
with ctx.as_user(uid):
    check("the preview keeps nothing", len(posting._mine()), 0)
r = c.post("/api/posts/plan", json={"group": gid}, headers=H).json()
check("one click queues them all", r["queued"], 10)
check("doing it again adds nothing", c.post("/api/posts/plan", json={"group": gid}, headers=H).json()["queued"], 0)
with ctx.as_user(uid):
    a_posts = sorted((p for p in posting._mine() if p["account"] == "yt_A"), key=lambda p: p["publish_at"])
    check("each goes live on one of the channel's times", all(hhmm(p["publish_at"]) in ("08:00", "09:00", "10:00") for p in a_posts))
    check("no two share a time", len({p["publish_at"] for p in a_posts}), 5)
    per_day = {}
    for p in a_posts:
        per_day[day(p["publish_at"])] = per_day.get(day(p["publish_at"]), 0) + 1
    check("three times a day means three a day, whatever the creator's cap", max(per_day.values()), 3)
    check("the best clip goes first", [p["clip"] for p in a_posts], ["k4", "k3", "k2", "k1", "k0"])
    check("uploads go out up to a day ahead, not all at once",
          all(abs(p["due_at"] - max(time.time(), p["publish_at"] - posting.AHEAD)) < 5 for p in a_posts))

# ---- the channel's settings survive connecting it again (a fresh record is written then)
with ctx.as_user(uid):
    accounts._put({"id": "yt_A", "platform": "youtube", "name": "Alpha Clips", "added": time.time(), "access_token": "new"})
a = next(x for x in c.get("/api/accounts").json() if x["id"] == "yt_A")
check("connecting again keeps the group and times", (a["group"], a["schedule"]["times"]), (gid, ["08:00", "09:00", "10:00"]))

# ---- PeakCut posts at the time instead (the computer must be on then)
r = c.put("/api/accounts/yt_A", json={"ahead": False}, headers=H).json()
check("changing how it posts moves the waiting clips", r["moved"], 5)
with ctx.as_user(uid):
    a_posts = [p for p in posting._mine() if p["account"] == "yt_A"]
    check("then they wait for their time, with no YouTube schedule",
          all("publish_at" not in p and hhmm(p["due_at"]) in ("08:00", "09:00", "10:00") for p in a_posts))
c.put("/api/accounts/yt_A", json={"ahead": True}, headers=H)

# ---- uploading: YouTube's own schedule, and its daily limit
sent = []
def fake_upload(acc, path, title, desc, tags, privacy, publish_at=None):
    sent.append(publish_at)
    if len(sent) == 1:
        raise accounts.LimitReached("YouTube's daily upload allowance for this server's Google project is used up.")
    return "vid" + str(len(sent)), "https://www.youtube.com/shorts/x"
accounts.youtube_upload = fake_upload
with ctx.as_user(uid):
    p = min((p for p in posting._mine() if p["account"] == "yt_B"), key=lambda p: p["publish_at"])
    posting._post(p)
    check("the daily limit is not a failure and uses no try", (p["status"], p["tries"]), ("scheduled", 0))
    check("it waits until after the limit resets", p["due_at"] >= posting._after_limit_reset() - 1 and posting._blocked.get("yt") == p["due_at"])
    posting._blocked.clear()
    posting._post(p)
    check("the upload asks YouTube to publish at the slot", (p["status"], sent[-1]), ("posted", p["publish_at"]))
    ch = {x["id"]: x for x in posting.channels_overview()["channels"]}
    check("an uploaded-ahead clip counts as waiting on YouTube, not as posted", (ch["yt_B"]["on_youtube"], ch["yt_B"]["posted_total"]), (1, 0))
    late = min((p for p in posting._mine() if p["account"] == "yt_B" and p["status"] == "scheduled"), key=lambda p: p["publish_at"])
    late["publish_at"], n = time.time() + 30, len(sent)
    posting._post(late)
    check("a clip that missed its time takes the next free one, not a public post now",
          (len(sent), late["status"], hhmm(late["publish_at"]) in ("08:00", "09:00", "10:00"), late["publish_at"] > time.time() + 600), (n, "scheduled", True, True))
    late.update(publish_at=time.time() + 30, manual=True)
    posting._post(late)
    check("a late clip sent with Post now or Retry uploads straight away", (len(sent), sent[-1], "publish_at" in late, late["status"]), (n + 1, None, False, "posted"))
    check("the channels list carries feeds and what's next", (ch["yt_A"]["feeds"][0]["name"], len(ch["yt_A"]["next"]) > 0), ("Streamer", True))

# ---- which creators feed a channel, from the channel's side; TikTok never uploads ahead
check("a creator is set to feed a channel", c.put("/api/accounts/tt_C", json={"feeds": [cid], "schedule_on": True, "times": "12:00"}, headers=H).status_code, 200)
check("...and the creator now posts there", "tt_C" in c.get("/api/creators").json()[0]["accounts"])
with ctx.as_user(uid):
    check("only YouTube schedules on its own side", (accounts.uploads_ahead("tt_C"), accounts.uploads_ahead("yt_A")), (False, True))
r = c.post("/api/posts/plan", json={"creator": cid, "accounts": ["tt_C"]}, headers=H).json()
check("one click for one creator on one channel", (r["queued"], r["channels"][0]["ahead"]), (5, False))
check("no channels picked is refused", c.post("/api/posts/plan", json={"accounts": []}, headers=H).status_code, 400)

# ---- deleting a group keeps its channels
check("a group can be deleted", c.delete(f"/api/groups/{gid}", headers=H).status_code, 200)
check("its channels stay, ungrouped", [a["group"] for a in c.get("/api/accounts").json()], ["", "", ""])

print("ALL PASSED" if not fails else "FAILED: " + ", ".join(fails))
sys.exit(1 if fails else 0)
