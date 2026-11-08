---
id: jarvis-control
aliases: [jarvis-control, stop-jarvis]
name: "Jarvis Control — Stop, Start, Restart, Status of the Console"
category: workflow-ops
description: Stop, start, restart or check the Jarvis console (webapp/server.py) with one script call, `scripts/jarvis.sh`. The console runs under launchd with KeepAlive, so killing its process only brings it back; the script unloads and loads the job instead, and also stops a copy started by hand.
triggers: [stop jarvis, stop the jarvis app, close jarvis, close the jarvis app, start jarvis, restart jarvis, is jarvis running, jarvis status, stop the app, stop the web app, stop the server, stop the console, restart the console]
tags: [console, ops, launchd]
related: ["[[run-forensics]]"]
status: active
version: 1
created: 2026-11-08
updated: 2026-11-08
---

# Jarvis Control — Stop, Start, Restart, Status of the Console

*The first skill made from session lessons (run-forensics §E, lesson L1): between 2026-10-12 and 2026-11-02, 15 of the principal's sessions asked to stop the app, and each improvised its own `ps`/`kill`/`lsof`, about 43 shell calls in all, against a launchd job that restarted what they killed.*

**Contract**
- **Input:** a request to stop, start, restart or check the console.
- **Output:** one call to `scripts/jarvis.sh <status|stop|start|restart>` and its two status lines, reported back as they are.
- **Allowed tools/artifacts:** `scripts/jarvis.sh` only. No `ps`/`kill`/`lsof` of your own.
- **Done when:** the script's status line shows the requested state (stopped: nothing listening on 8765, job not loaded; started: listening).

**Triggers/Context**
- "stop jarvis", "stop the app", "close the jarvis app", "restart jarvis", "is jarvis running".
- "The app" in this repo means the Jarvis console unless the session started another server (e.g. `demos/frameshift/server.py`); then ask which one.

**Core Blueprint**
1. Map the ask to one verb: stop · start · restart · status.
2. Run `scripts/jarvis.sh <verb>` once.
3. Report the status line. If it says a port is still in use by a process the script doesn't own, say which pid and leave it alone.

**Optimizations/Gotchas**
- **Stop lasts until start or the next login.** The installed plist has `RunAtLoad`, so a login loads it again. That is intended: stopping is for now, not forever. To turn it off for good, remove `~/Library/LaunchAgents/com.cbrain.webapp.plist` (the principal's call).
- **Restart after a code change** is `scripts/jarvis.sh restart` (it runs `launchctl kickstart -k` when the job is loaded).
- **Port:** `CBRAIN_WEB_PORT`, default 8765, as in `webapp/README.md`.
