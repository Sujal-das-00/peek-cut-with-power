# Graph Report - PeakCut  (2026-11-21)

## Corpus Check
- 85 files · ~149,993 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 7, .ttf 3, .example 1)

## Summary
- 1660 nodes · 4495 edges · 94 communities (76 shown, 18 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a5d8b27d`
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
- account.py
- uid
- Request
- post
- db.py
- tts.py
- create_from_link
- profiles.py
- _write
- _run_job
- json
- test_speech.py
- brain.py
- ai.py
- auth.py
- references.py
- time
- vision.py
- ctx.py
- asr
- facecam.py
- main
- roman.py
- ask_ai
- storage.py
- subprocess
- fetch_model.py
- config.py
- re
- numpy
- transcribe.py
- updates.py
- studio/__init__.py
- asr_worker.py
- test_channels.py
- mailer.py
- main
- overview
- user_dir
- .__call__
- _finish
- make
- status
- try_files
- Gaming mode
- test_ai.py
- proxy
- build_profile
- games.py
- _FairQueue
- quality.py
- test_connect.py
- StuckProc
- test_local.py
- send
- transcribe
- missing
- test_retry.py
- test_robustness.py
- test_roman.py
- google_client
- english_captions
- make_lines
- save_app
- LimitReached
- settings
- _h
- _load_sherpa
- PeakAscii
- AIError
- _Quiet
- _Quiet
- _decode_remote
- Compress
- google
- busy_for
- GradientASCII
- _json_schema
- touch

## God Nodes (most connected - your core abstractions)
1. `uid()` - 55 edges
2. `main()` - 52 edges
3. `_run_job()` - 41 edges
4. `save()` - 31 edges
5. `_admin()` - 30 edges
6. `_run_vision_job()` - 29 edges
7. `Session` - 29 edges
8. `get()` - 21 edges
9. `ask_ai()` - 20 edges
10. `start_session()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Rules worth knowing` --references--> `local_user()`  [INFERRED]
  AGENTS.md → studio/auth.py
- `Rules worth knowing` --references--> `_safe()`  [INFERRED]
  AGENTS.md → studio/brain.py
- `Rules worth knowing` --references--> `_text()`  [INFERRED]
  AGENTS.md → studio/brain.py
- `1. It knows which game it is` --references--> `_tidy()`  [INFERRED]
  GAMING.md → studio/brain.py
- `2. The crowd is counted as people` --references--> `judge_signals()`  [INFERRED]
  GAMING.md → studio/brain.py

## Import Cycles
- 2-file cycle: `studio/fetch_model.py -> studio/transcribe.py -> studio/fetch_model.py`
- 2-file cycle: `studio/ai.py -> studio/config.py -> studio/ai.py`

## Communities (94 total, 18 thin omitted)

### Community 0 - "live.py"
Cohesion: 0.07
Nodes (30): configured(), digest_loop(), keep_awake_loop(), notify(), send(), user_ids(), as_user(), uid_or_none() (+22 more)

### Community 1 - "media.py"
Cohesion: 0.08
Nodes (27): _fetch_piece(), resolve(), _biggest(), _caption_words(), check_youtube(), cookie_opts(), download(), download_audio() (+19 more)

### Community 2 - "server.py"
Cohesion: 0.07
Nodes (41): admin_page(), ai_usage(), app_page(), asset(), auth_page(), _back(), brand(), channels() (+33 more)

### Community 3 - "app"
Cohesion: 0.04
Nodes (47): build, cpu_shares, cpus, depends_on, env_file, environment, mem_limit, memswap_limit (+39 more)

### Community 4 - "os"
Cohesion: 0.09
Nodes (3): main(), _session(), session()

### Community 5 - "save"
Cohesion: 0.07
Nodes (9): save(), submit_live(), media_safe(), _plain(), recover(), cleanup(), Session, cleanup() (+1 more)

### Community 6 - "accounts.py"
Cohesion: 0.12
Nodes (32): add_group(), app_keys(), can_connect(), _check(), clip_link(), connect_finish(), connect_url(), _ig_token() (+24 more)

### Community 7 - "jobs.py"
Cohesion: 0.08
Nodes (24): all_jobs(), _caption_words(), clean_hashtags(), _english_part(), enqueue(), _f(), _live_worker(), load_all() (+16 more)

### Community 8 - "PeakCut"
Cohesion: 0.05
Nodes (38): Installing or updating PeakCut for someone, Run and test, Where things are, Working on PeakCut, Channels: connect many, schedule everything in one click, How it fits together, Part 1: register PeakCut with Google (once per PeakCut install), Part 2: connect each channel (+30 more)

### Community 9 - "render.py"
Cohesion: 0.07
Nodes (20): build_ass(), _clean(), _filter(), _Font, geometry(), _groups(), has_audio(), _hook_events() (+12 more)

### Community 10 - "posting.py"
Cohesion: 0.10
Nodes (26): get(), _add(), _after_limit_reset(), cancel(), _caption(), digest_text(), dismiss(), enqueue() (+18 more)

### Community 11 - "creators.py"
Cohesion: 0.12
Nodes (25): all_creators(), _clean(), clean_description(), clean_hook(), create(), _fix(), get(), _mine() (+17 more)

### Community 12 - "account.py"
Cohesion: 0.09
Nodes (18): Busy, _busy(), clip_title_name(), delete_account(), delete_clip(), delete_creator(), delete_many(), zip_clips() (+10 more)

### Community 13 - "uid"
Cohesion: 0.09
Nodes (26): uid(), version(), busy_count(), queue_epoch(), check_now(), run(), mine(), read_all() (+18 more)

### Community 14 - "Request"
Cohesion: 0.12
Nodes (31): _admin(), admin_delete_user(), admin_disable(), admin_feedback(), admin_feedback_status(), admin_overview(), admin_user(), _ai_error() (+23 more)

### Community 15 - "post"
Cohesion: 0.09
Nodes (26): cookie_args(), is_verified(), public(), throttle(), ready(), change_password(), delete_my_account(), forgot_password() (+18 more)

### Community 16 - "db.py"
Cohesion: 0.10
Nodes (14): _cli(), _log(), Refused, set_admin(), set_disabled(), user_detail(), _fast_sqlite(), init() (+6 more)

### Community 17 - "tts.py"
Cohesion: 0.13
Nodes (17): WrongFile, _fetch(), folder(), narrate(), preview(), previews(), _reader(), ready() (+9 more)

### Community 18 - "create_from_link"
Cohesion: 0.12
Nodes (20): job_dir(), public(), create_from_file(), create_from_link(), allowed(), go_live(), _job_slots(), _need_verified() (+12 more)

### Community 19 - "profiles.py"
Cohesion: 0.12
Nodes (17): _clean_name(), fetch(), _fetch(), _get(), live_now(), live_shared(), _meta(), _no_date() (+9 more)

### Community 20 - "_write"
Cohesion: 0.11
Nodes (20): _all(), _channels(), delete_group(), _dir(), get(), groups(), in_group(), list_accounts() (+12 more)

### Community 21 - "_run_job"
Cohesion: 0.11
Nodes (17): log(), bind(), apply(), _covers(), _facecam(), _run_job(), got(), hear() (+9 more)

### Community 22 - "json"
Cohesion: 0.19
Nodes (17): read_clip_link(), _anthropic(), base_url(), call(), _fail(), _from_events(), _gem(), _gemini() (+9 more)

### Community 23 - "test_speech.py"
Cohesion: 0.10
Nodes (7): Answer, archive(), fake_open(), Reply, fake_open(), model_bytes(), Stream

### Community 24 - "brain.py"
Cohesion: 0.20
Nodes (14): fallback_by_loudness(), find_clips(), find_live_clips(), _fmt(), _game_rules(), judge_transcript(), loud_zscore(), _num() (+6 more)

### Community 25 - "ai.py"
Cohesion: 0.15
Nodes (13): current(), _file(), _from_dashboard(), _json_chunks(), label(), list_models(), models(), provider() (+5 more)

### Community 26 - "auth.py"
Cohesion: 0.22
Nodes (15): AuthError, change_password(), _check_password_rules(), _create(), forget(), get_user(), google_finish(), hash_password() (+7 more)

### Community 27 - "references.py"
Cohesion: 0.19
Nodes (14): clean_name(), cover_path(), create(), delete(), _dir(), get(), list_all(), profile() (+6 more)

### Community 28 - "time"
Cohesion: 0.16
Nodes (13): rfc3339(), schedule_for(), _take_state(), now(), channels_overview(), _day(), _live(), _next_slot() (+5 more)

### Community 29 - "vision.py"
Cohesion: 0.15
Nodes (9): estimate(), find_part(), grids(), part_count(), profile_text(), _schema(), snap(), split() (+1 more)

### Community 30 - "ctx.py"
Cohesion: 0.11
Nodes (3): NoUser, set_uid(), wait_for()

### Community 31 - "asr"
Cohesion: 0.11
Nodes (18): build, deploy, environment, ports, restart, volumes, context, dockerfile (+10 more)

### Community 32 - "facecam.py"
Cohesion: 0.20
Nodes (9): _asked(), detect(), _duration(), _frame_jpeg(), _frames(), _full_frame(), _overlap(), _size() (+1 more)

### Community 33 - "main"
Cohesion: 0.15
Nodes (9): check(), _http(), main(), flaky(), stub(), make_silent(), _raises(), streams() (+1 more)

### Community 34 - "roman.py"
Cohesion: 0.17
Nodes (11): _fix_caption_words(), _same_word(), has_hindi(), _korean(), _letters(), needs_roman(), to_roman(), unicodedata_nfc() (+3 more)

### Community 35 - "ask_ai"
Cohesion: 0.18
Nodes (11): Rules worth knowing, clear_problem(), explain(), look(), note_problem(), ask_ai(), ask_vision(), look_for_facecam() (+3 more)

### Community 36 - "storage.py"
Cohesion: 0.21
Nodes (9): cancel_change(), change(), drive_of(), full_message(), info(), pending(), shutil_free(), _size() (+1 more)

### Community 37 - "subprocess"
Cohesion: 0.13
Nodes (6): open_folder(), pick_folder(), make(), cli(), client(), signup()

### Community 38 - "fetch_model.py"
Cohesion: 0.22
Nodes (9): ensure(), _fetch(), folder(), label(), main(), remove(), _save(), _new() (+1 more)

### Community 39 - "config.py"
Cohesion: 0.15
Nodes (6): ai_key(), _keep(), _read_secret(), _secret(), burn(), worker()

### Community 40 - "re"
Cohesion: 0.15
Nodes (5): asked_wait(), events(), make(), shown_together(), talk()

### Community 41 - "numpy"
Cohesion: 0.15
Nodes (5): _local(), _peaks(), _plausible(), _profiles(), all_at_once()

### Community 42 - "transcribe.py"
Cohesion: 0.21
Nodes (7): decode_pieces(), _give_back(), _pool(), _Pool, _recognizer(), _take(), _take_now()

### Community 43 - "updates.py"
Cohesion: 0.17
Nodes (7): check(), current(), latest(), newest(), start(), loop(), _what_changed()

### Community 45 - "asr_worker.py"
Cohesion: 0.17
Nodes (5): decode(), work(), healthz(), main(), pieces()

### Community 46 - "test_channels.py"
Cohesion: 0.18
Nodes (3): fake_get(), R, refs()

### Community 48 - "main"
Cohesion: 0.20
Nodes (8): 1. It knows which game it is, describe(), _first(), post_text(), _tidy(), check(), fails_with(), main()

### Community 49 - "overview"
Cohesion: 0.20
Nodes (9): _day(), overview(), ready(), start(), run(), status(), running_now(), waiting_total() (+1 more)

### Community 50 - "user_dir"
Cohesion: 0.17
Nodes (7): local_user(), photo(), _photo_stamp(), save_photo(), _data_folder(), _move_folder(), user_dir()

### Community 51 - ".__call__"
Cohesion: 0.18
Nodes (6): seen_recently(), _from_here(), Gate, deny(), receive(), _own_address()

### Community 52 - "_finish"
Cohesion: 0.21
Nodes (6): _best(), _corner(), _finish(), _seen(), _snap(), line()

### Community 53 - "make"
Cohesion: 0.24
Nodes (6): channel_tag(), keywords(), make(), add(), numbered(), _tag()

### Community 54 - "status"
Cohesion: 0.22
Nodes (8): site_allowed(), channel_preview(), link_preview(), _lookup(), me(), _me(), _speech_brief(), status()

### Community 55 - "try_files"
Cohesion: 0.24
Nodes (7): _model_files(), _words(), _add_meta(), export(), main(), try_files(), _try_one()

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

### Community 60 - "games.py"
Cohesion: 0.31
Nodes (4): detect(), name_of(), _norm(), tags_of()

### Community 62 - "quality.py"
Cohesion: 0.28
Nodes (3): motion_map(), static_overlap(), static_ranges()

### Community 63 - "test_connect.py"
Cohesion: 0.28
Nodes (3): get(), post(), R

### Community 64 - "StuckProc"
Cohesion: 0.22
Nodes (3): one_shot_popen(), StuckProc, _Out

### Community 65 - "test_local.py"
Cohesion: 0.28
Nodes (3): fake_get(), fake_post(), Reply

### Community 66 - "send"
Cohesion: 0.29
Nodes (6): forgot(), _make_link(), send_verify(), smtp_password(), send(), work()

### Community 67 - "transcribe"
Cohesion: 0.36
Nodes (4): _chunks(), _remote_ok(), transcribe(), decode()

### Community 68 - "missing"
Cohesion: 0.25
Nodes (4): explain(), missing(), _places(), setup()

### Community 69 - "test_retry.py"
Cohesion: 0.32
Nodes (3): daily_then_ok(), failure(), Resp

### Community 72 - "google_client"
Cohesion: 0.33
Nodes (5): google_ready(), google_url(), google_client(), _read_google_client(), google_start()

### Community 73 - "english_captions"
Cohesion: 0.29
Nodes (3): english_captions(), fix_caption_words(), needs_translation()

### Community 74 - "make_lines"
Cohesion: 0.29
Nodes (3): make_lines(), _spread(), translate_caption_words()

### Community 75 - "save_app"
Cohesion: 0.47
Nodes (4): _apps_file(), apps_public(), _apps_saved(), save_app()

### Community 76 - "LimitReached"
Cohesion: 0.33
Nodes (3): LimitReached, _yt_limits(), fake_upload()

### Community 77 - "settings"
Cohesion: 0.40
Nodes (5): parse_times(), public_settings(), save_settings(), settings(), put_settings()

### Community 78 - "_h"
Cohesion: 0.33
Nodes (5): end_session(), _h(), start_session(), user_for(), person()

### Community 79 - "_load_sherpa"
Cohesion: 0.40
Nodes (4): _load_sherpa(), forget(), load_from(), _sherpa()

### Community 80 - "PeakAscii"
Cohesion: 0.40
Nodes (3): PeakAscii(), draw(), loop()

## Knowledge Gaps
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Rules worth knowing` connect `ask_ai` to `PeakCut`, `render.py`, `account.py`, `uid`, `user_dir`, `brain.py`, `build_profile`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `uid()` (e.g. with `Rules worth knowing` and `run()`) actually correct?**
  _`uid()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `live.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06821480406386067 - nodes in this community are weakly interconnected._
- **Why does `Working on PeakCut` connect `PeakCut` to `ask_ai`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `main()` (e.g. with `dead()` and `fake_look()`) actually correct?**
  _`main()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `media.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0792156862745098 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `main` to `live.py`, `media.py`, `ask_ai`, `subprocess`, `jobs.py`, `render.py`, `build_profile`, `creators.py`, `account.py`, `db.py`, `tts.py`, `user_dir`, `create_from_link`, `_run_job`, `ai.py`, `references.py`, `vision.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._