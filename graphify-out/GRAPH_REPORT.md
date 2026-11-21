# Graph Report - PeakCut  (2026-11-21)

## Corpus Check
- 86 files · ~152,754 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ttf 3, .example 1)

## Summary
- 1701 nodes · 4621 edges · 86 communities (68 shown, 18 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 122 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ab3cf616`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- live.py
- media.py
- server.py
- app
- os
- save
- accounts.py
- jobs.py
- PeakCut
- render.py
- posting.py
- creators.py
- delete_creator
- post
- Request
- post
- admin.py
- narrate
- create_from_link
- profiles.py
- _write
- _run_job
- json
- test_tools.py
- brain.py
- ready
- auth.py
- references.py
- time
- vision.py
- ctx.py
- asr
- numpy
- main
- roman.py
- ask_ai
- storage.py
- os
- fetch_model.py
- config.py
- re
- zip_clips
- transcribe.py
- refresh
- test_hardening.py
- test_speech.py
- studio/__init__.py
- mailer.py
- main
- main
- user_dir
- .__call__
- test_captions.py
- make
- status
- _fetch_piece
- Gaming mode
- test_ai.py
- proxy
- build_profile
- Reply
- _FairQueue
- _trim_names
- test_connect.py
- StuckProc
- auth.py
- shutil
- test_retry.py
- test_robustness.py
- test_roman.py
- google_client
- LimitReached
- threading
- PeakAscii
- AIError
- _Quiet
- Compress
- GradientASCII

## God Nodes (most connected - your core abstractions)
1. `uid()` - 55 edges
2. `main()` - 52 edges
3. `_run_job()` - 43 edges
4. `save()` - 34 edges
5. `_run_vision_job()` - 31 edges
6. `_admin()` - 30 edges
7. `Session` - 29 edges
8. `main()` - 23 edges
9. `get()` - 21 edges
10. `ask_ai()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Rules worth knowing` --references--> `_safe()`  [INFERRED]
  AGENTS.md → studio/brain.py
- `Rules worth knowing` --references--> `_text()`  [INFERRED]
  AGENTS.md → studio/brain.py
- `1. It knows which game it is` --references--> `_tidy()`  [INFERRED]
  GAMING.md → studio/brain.py
- `Rules worth knowing` --references--> `ask_ai()`  [INFERRED]
  AGENTS.md → studio/brain.py
- `Rules worth knowing` --references--> `ask_vision()`  [INFERRED]
  AGENTS.md → studio/brain.py

## Import Cycles
- 2-file cycle: `studio/fetch_model.py -> studio/transcribe.py -> studio/fetch_model.py`
- 2-file cycle: `studio/ai.py -> studio/config.py -> studio/ai.py`

## Communities (86 total, 18 thin omitted)

### Community 0 - "live.py"
Cohesion: 0.12
Nodes (19): user_ids(), as_user(), active(), active_for(), active_mine(), check_now(), run(), _clip_span() (+11 more)

### Community 1 - "media.py"
Cohesion: 0.11
Nodes (17): _biggest(), _caption_words(), check_youtube(), cookie_opts(), download(), download_audio(), hook(), download_section() (+9 more)

### Community 2 - "server.py"
Cohesion: 0.08
Nodes (37): public_settings(), admin_page(), ai_usage(), app_page(), asset(), auth_page(), _back(), brand() (+29 more)

### Community 3 - "app"
Cohesion: 0.04
Nodes (47): build, cpu_shares, cpus, depends_on, env_file, environment, mem_limit, memswap_limit (+39 more)

### Community 4 - "os"
Cohesion: 0.08
Nodes (4): make_video(), _session(), busy_for(), session()

### Community 5 - "save"
Cohesion: 0.07
Nodes (8): bind(), submit_live(), media_safe(), recover(), cleanup(), Session, cleanup(), work()

### Community 6 - "accounts.py"
Cohesion: 0.09
Nodes (41): add_group(), app_keys(), _apps_file(), apps_public(), _apps_saved(), can_connect(), _check(), clip_link() (+33 more)

### Community 7 - "jobs.py"
Cohesion: 0.08
Nodes (28): all_jobs(), cancel_clip(), _caption_words(), clean_hashtags(), _drop_clip(), _english_part(), enqueue(), _f() (+20 more)

### Community 8 - "PeakCut"
Cohesion: 0.05
Nodes (39): Installing or updating PeakCut for someone, Run and test, Where things are, Working on PeakCut, Channels: connect many, schedule everything in one click, How it fits together, Part 1: register PeakCut with Google (once per PeakCut install), Part 2: connect each channel (+31 more)

### Community 9 - "render.py"
Cohesion: 0.05
Nodes (27): init(), build_ass(), _clean(), _filter(), _Font, geometry(), _groups(), has_audio() (+19 more)

### Community 10 - "posting.py"
Cohesion: 0.12
Nodes (25): get(), _add(), _after_limit_reset(), cancel(), _caption(), digest_text(), dismiss(), enqueue() (+17 more)

### Community 11 - "creators.py"
Cohesion: 0.13
Nodes (21): all_creators(), _clean(), clean_description(), clean_hook(), create(), _fix(), forget(), get() (+13 more)

### Community 12 - "delete_creator"
Cohesion: 0.10
Nodes (17): Busy, _busy(), delete_clip(), delete_creator(), delete_many(), delete(), get(), add_posts() (+9 more)

### Community 13 - "post"
Cohesion: 0.09
Nodes (21): mine(), read_all(), _ai_error(), ai_models(), ai_test(), cancel_clip(), _channel_ok(), clip_now() (+13 more)

### Community 14 - "Request"
Cohesion: 0.13
Nodes (30): bump(), _admin(), admin_delete_user(), admin_disable(), admin_feedback(), admin_feedback_status(), admin_overview(), admin_user() (+22 more)

### Community 15 - "post"
Cohesion: 0.10
Nodes (27): cookie_args(), google_ready(), is_verified(), public(), throttle(), ready(), site_allowed(), change_password() (+19 more)

### Community 16 - "admin.py"
Cohesion: 0.06
Nodes (29): _cli(), _day(), _log(), overview(), Refused, set_admin(), set_disabled(), user_detail() (+21 more)

### Community 17 - "narrate"
Cohesion: 0.19
Nodes (7): narrate(), preview(), previews(), say(), sentences(), spread(), valid()

### Community 18 - "create_from_link"
Cohesion: 0.10
Nodes (28): NoUser, uid(), version(), busy_count(), job_dir(), public(), queue_epoch(), disk_full() (+20 more)

### Community 19 - "profiles.py"
Cohesion: 0.13
Nodes (17): _clean_name(), fetch(), _fetch(), _get(), live_now(), live_shared(), _meta(), _no_date() (+9 more)

### Community 20 - "_write"
Cohesion: 0.11
Nodes (18): _all(), _channels(), delete_group(), groups(), in_group(), list_accounts(), parse_times(), prefs() (+10 more)

### Community 21 - "_run_job"
Cohesion: 0.09
Nodes (25): log(), detect(), apply(), _cancelled(), _check(), _covers(), _facecam(), _run_job() (+17 more)

### Community 22 - "json"
Cohesion: 0.12
Nodes (29): _anthropic(), base_url(), call(), current(), _fail(), _file(), _from_dashboard(), _from_events() (+21 more)

### Community 23 - "test_tools.py"
Cohesion: 0.19
Nodes (3): fake_open(), model_bytes(), Stream

### Community 24 - "brain.py"
Cohesion: 0.10
Nodes (23): 1. It knows which game it is, fallback_by_loudness(), find_clips(), find_live_clips(), _fmt(), _game_rules(), judge_transcript(), loud_zscore() (+15 more)

### Community 25 - "ready"
Cohesion: 0.25
Nodes (9): _fetch(), folder(), _reader(), ready(), remove(), _save(), start(), run() (+1 more)

### Community 26 - "auth.py"
Cohesion: 0.21
Nodes (11): delete_account(), AuthError, change_password(), _check_password_rules(), forget(), get_user(), hash_password(), login() (+3 more)

### Community 27 - "references.py"
Cohesion: 0.19
Nodes (14): clean_name(), cover_path(), create(), delete(), _dir(), get(), list_all(), profile() (+6 more)

### Community 28 - "time"
Cohesion: 0.22
Nodes (10): now(), channels_overview(), _day(), _live(), _next_slot(), overview(), _slots(), _upcoming() (+2 more)

### Community 29 - "vision.py"
Cohesion: 0.15
Nodes (9): estimate(), find_part(), grids(), part_count(), profile_text(), _schema(), snap(), split() (+1 more)

### Community 31 - "asr"
Cohesion: 0.11
Nodes (18): build, deploy, environment, ports, restart, volumes, context, dockerfile (+10 more)

### Community 32 - "numpy"
Cohesion: 0.09
Nodes (20): _asked(), _best(), _corner(), detect(), _duration(), _finish(), _frame_jpeg(), _frames() (+12 more)

### Community 33 - "main"
Cohesion: 0.13
Nodes (9): check(), _http(), main(), fake_look(), flaky(), stub(), _raises(), test_picture_limit_pieces() (+1 more)

### Community 34 - "roman.py"
Cohesion: 0.14
Nodes (13): english_captions(), fix_caption_words(), _fix_caption_words(), needs_translation(), has_hindi(), _korean(), _letters(), needs_roman() (+5 more)

### Community 35 - "ask_ai"
Cohesion: 0.15
Nodes (11): clear_problem(), explain(), note_problem(), vision_models(), ask_ai(), ask_vision(), look_for_facecam(), _look_in_pieces() (+3 more)

### Community 36 - "storage.py"
Cohesion: 0.18
Nodes (10): cancel_change(), change(), drive_of(), full_message(), info(), pending(), pick_folder(), shutil_free() (+2 more)

### Community 37 - "os"
Cohesion: 0.09
Nodes (9): motion_map(), static_ranges(), open_folder(), make(), cli(), client(), signup(), make_silent() (+1 more)

### Community 38 - "fetch_model.py"
Cohesion: 0.14
Nodes (11): ensure(), _fetch(), folder(), label(), main(), ready(), remove(), _save() (+3 more)

### Community 39 - "config.py"
Cohesion: 0.14
Nodes (8): ai_key(), _keep(), _read_secret(), _secret(), smtp_password(), work(), burn(), worker()

### Community 40 - "re"
Cohesion: 0.12
Nodes (7): read_clip_link(), asked_wait(), _picture_limit(), events(), make(), shown_together(), talk()

### Community 41 - "zip_clips"
Cohesion: 0.20
Nodes (5): clip_title_name(), zip_clips(), bulk_delete(), clips_zip(), _pairs()

### Community 42 - "transcribe.py"
Cohesion: 0.05
Nodes (30): decode(), work(), healthz(), main(), _chunks(), decode_pieces(), _decode_remote(), _give_back() (+22 more)

### Community 43 - "refresh"
Cohesion: 0.29
Nodes (5): read_log(), needs_refresh(), refresh(), _creator_rows(), _sync_unchanged()

### Community 44 - "test_hardening.py"
Cohesion: 0.25
Nodes (3): google(), Req, Resp

### Community 45 - "test_speech.py"
Cohesion: 0.29
Nodes (3): Answer, archive(), fake_open()

### Community 46 - "studio/__init__.py"
Cohesion: 0.08
Nodes (4): _fast_sqlite(), fake_get(), R, refs()

### Community 48 - "main"
Cohesion: 0.25
Nodes (6): describe(), _first(), post_text(), check(), fails_with(), main()

### Community 49 - "main"
Cohesion: 0.19
Nodes (9): Rules worth knowing, cancel(), running_now(), Cancelled, hook(), run_cancellable(), check(), main() (+1 more)

### Community 50 - "user_dir"
Cohesion: 0.14
Nodes (11): _create(), google_finish(), local_user(), mark_verified(), save_photo(), _use_link(), verify_link(), _data_folder() (+3 more)

### Community 51 - ".__call__"
Cohesion: 0.18
Nodes (6): seen_recently(), _from_here(), Gate, deny(), receive(), _own_address()

### Community 52 - "test_captions.py"
Cohesion: 0.53
Nodes (4): check(), has_dialogue(), main(), rejects_caption_value()

### Community 53 - "make"
Cohesion: 0.24
Nodes (6): channel_tag(), keywords(), make(), add(), numbered(), _tag()

### Community 54 - "status"
Cohesion: 0.29
Nodes (4): status(), _speech_brief(), status(), latest()

### Community 55 - "_fetch_piece"
Cohesion: 0.18
Nodes (7): _fetch_piece(), _plain(), extract_audio(), find_offset(), load_audio(), loudness_per_second(), _try_one()

### Community 56 - "Gaming mode"
Cohesion: 0.20
Nodes (8): 2. The crowd is counted as people, 3. The facecam is found, and the game fills the screen, 4. Ad breaks and static screens, Gaming mode, Settings for launch night, The tests, What it does not do, judge_signals()

### Community 57 - "test_ai.py"
Cohesion: 0.24
Nodes (3): fake_gemma_post(), fake_post(), Reply

### Community 58 - "proxy"
Cohesion: 0.22
Nodes (8): labels, networks, networks, proxy, external, name, services, app

### Community 59 - "build_profile"
Cohesion: 0.31
Nodes (4): _text(), build_profile(), _listen(), sample()

### Community 63 - "test_connect.py"
Cohesion: 0.14
Nodes (6): get(), post(), R, fake_get(), fake_post(), Reply

### Community 64 - "StuckProc"
Cohesion: 0.22
Nodes (3): one_shot_popen(), StuckProc, _Out

### Community 66 - "auth.py"
Cohesion: 0.16
Nodes (11): end_session(), forgot(), _h(), _make_link(), photo(), _photo_stamp(), send_verify(), start_session() (+3 more)

### Community 68 - "shutil"
Cohesion: 0.14
Nodes (5): explain(), missing(), _places(), setup(), main()

### Community 69 - "test_retry.py"
Cohesion: 0.32
Nodes (3): daily_then_ok(), failure(), Resp

### Community 72 - "google_client"
Cohesion: 0.40
Nodes (3): google_url(), google_client(), _read_google_client()

### Community 76 - "LimitReached"
Cohesion: 0.33
Nodes (3): LimitReached, _yt_limits(), fake_upload()

### Community 77 - "threading"
Cohesion: 0.23
Nodes (8): save_settings(), settings(), configured(), digest_loop(), keep_awake_loop(), notify(), send(), uid_or_none()

### Community 80 - "PeakAscii"
Cohesion: 0.40
Nodes (3): PeakAscii(), draw(), loop()

### Community 81 - "AIError"
Cohesion: 0.29
Nodes (3): AIError, list_models(), explained()

## Knowledge Gaps
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `live.py`, `ask_ai`, `os`, `jobs.py`, `render.py`, `build_profile`, `creators.py`, `delete_creator`, `narrate`, `user_dir`, `create_from_link`, `_run_job`, `json`, `ready`, `references.py`, `vision.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `uid()` (e.g. with `Rules worth knowing` and `run()`) actually correct?**
  _`uid()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `live.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12258064516129032 - nodes in this community are weakly interconnected._
- **Why does `_run_job()` connect `_run_job` to `media.py`, `os`, `save`, `jobs.py`, `fetch_model.py`, `creators.py`, `threading`, `admin.py`, `_fetch_piece`, `json`, `status`, `brain.py`, `time`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `main()` (e.g. with `dead()` and `fake_look()`) actually correct?**
  _`main()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `media.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10756302521008404 - nodes in this community are weakly interconnected._
- **Why does `Session` connect `save` to `live.py`, `os`, `_trim_names`, `_fetch_piece`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._