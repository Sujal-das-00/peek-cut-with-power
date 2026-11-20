"""The upload schedule: posts take the next free upload time, failed posts wait for a manual tap. No network."""
import os, sys, tempfile, time
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-sched-")
os.environ.update(DATABASE_URL="", PEAKCUT_ACCOUNTS="0")
sys.path.insert(0, ".")
from studio import accounts, ctx, posting

fails = []
def check(n, got, want=True):
    ok = want(got) if callable(want) else got == want
    print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"   got {got!r}")); ok or fails.append(n)

with ctx.as_user("u_sched"):
    # ---- the times are checked and tidied
    check("times are sorted and tidied", accounts.parse_times("18:00, 9:00 ,13:30,09:00"), ["09:00", "13:30", "18:00"])
    for bad in ("25:00", "9am", "12:60"):
        try:
            accounts.parse_times(bad); ok = False
        except ValueError:
            ok = True
        check(f"{bad!r} is refused", ok)
    try:
        accounts.parse_times(", ".join(f"{h:02d}:00" for h in range(13))); ok = False
    except ValueError:
        ok = True
    check("more than 12 times is refused", ok)
    try:
        accounts.save_settings({"schedule_on": True, "schedule_times": " , "}); ok = False
    except ValueError:
        ok = True
    check("a schedule with no times cannot be turned on", ok)
    s = accounts.save_settings({"schedule_on": True, "schedule_times": "18:00,9:00"})
    check("settings keep the tidy form", (s["schedule_on"], s["schedule_times"]), (True, "09:00, 18:00"))

    # ---- slots: each post takes the next free time on its account
    def post(pid, acct, due, status="scheduled", **kw):
        p = {"id": pid, "user": "u_sched", "job": "j", "clip": pid, "creator": None, "account": acct, "account_name": acct,
             "platform": "youtube", "status": status, "due_at": due, "created": 0, "title": pid, "score": 0, "tries": 0,
             "url": "", "remote_id": "", "error": None, "views": None, **kw}
        posting._posts.append(p)
        return p
    t = [posting._next_slot("A", 45, 6)]
    check("first post lands on a scheduled time", time.strftime("%H:%M", time.localtime(t[0])) in ("09:00", "18:00"))
    post("p1", "A", t[0])
    t.append(posting._next_slot("A", 45, 6))
    check("the next one takes the next time, not the same", (t[1] > t[0], time.strftime("%H:%M", time.localtime(t[1])) in ("09:00", "18:00")), (True, True))
    check("another account is not held up by it", posting._next_slot("B", 45, 6), t[0])
    post("p2", "A", t[1])
    check("a failed post gives its time back", (posting._posts.__setitem__(0, dict(posting._posts[0], status="failed")), posting._next_slot("A", 45, 6))[1], t[0])
    posting._posts[0]["status"] = "scheduled"
    posting._posts.clear()
    one = post("c1", "A", t[0])
    nxt = posting._next_slot("A", 45, 1)
    check("the daily cap still holds", time.strftime("%Y-%m-%d", time.localtime(nxt)) != time.strftime("%Y-%m-%d", time.localtime(t[0])))

    # ---- re-spreading leaves hand-sent and tried posts alone, and keeps the order
    posting._posts.clear()
    a = post("a", "A", time.time() + 7 * 86400)
    b = post("b", "A", time.time() + 8 * 86400)
    m = post("m", "A", time.time(), manual=True)
    tried = post("t", "A", time.time() + 9 * 86400, tries=1)
    moved = posting.reschedule()
    first = posting._next_slot("A", 45, 6, {x["id"] for x in (a, b)})
    check("two waiting posts were moved", moved, 2)
    check("they keep their order and take different times", 0 < a["due_at"] < b["due_at"] and a["due_at"] != b["due_at"])
    check("both are on schedule times", all(time.strftime("%H:%M", time.localtime(x["due_at"])) in ("09:00", "18:00") for x in (a, b)))
    check("they moved up, not further away", b["due_at"] < time.time() + 8 * 86400 and a["due_at"] == first)
    check("post-now and tried posts stayed put", (m["due_at"] < time.time() + 5, tried["due_at"] > time.time() + 8.5 * 86400), (True, True))

    # ---- the failed list: one tap retries everything, or a post is removed
    posting._posts.clear()
    f1, f2 = post("f1", "A", 1, status="failed", error="x"), post("f2", "A", 2, status="failed", error="y")
    ov = posting.overview()
    check("failed posts have their own list", ([p["id"] for p in ov["failed"]], [p["id"] for p in ov["posts"]]), (["f2", "f1"], []))
    check("overview carries the schedule", ov["schedule"], {"on": True, "times": "09:00, 18:00"})
    posting.dismiss("f2")
    check("removing drops it", [p["id"] for p in posting._posts], ["f1"])
    check("retry all sends the rest now", (posting.retry_failed(), f1["status"], f1["tries"], f1["due_at"] <= time.time()), (1, "scheduled", 0, True))
    try:
        posting.dismiss("f1"); ok = False
    except ValueError:
        ok = True
    check("a waiting post cannot be removed as failed", ok)

print("ALL PASSED" if not fails else "FAILED: " + ", ".join(fails))
sys.exit(1 if fails else 0)
