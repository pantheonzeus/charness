#!/usr/bin/env bash
# Jarvis console control: status | stop | start | restart.
# The console (webapp/server.py) runs under launchd as com.cbrain.webapp with KeepAlive, so killing its process
# only makes launchd start it again. stop unloads the job (it stays off until `start` or the next login);
# start loads it; restart kicks it. A copy started by hand (`uv run webapp/server.py`) is stopped too.
# Skill: resources/skills/workflow-ops/jarvis-control/SKILL.md
set -uo pipefail
LABEL=com.cbrain.webapp
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"
PORT="${CBRAIN_WEB_PORT:-8765}"

loaded() { launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; }
listener() { lsof -nP -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null | head -1; }
wait_port() {   # $1 up|down, waits up to 10 s
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if [ "$1" = up ] && [ -n "$(listener)" ]; then return 0; fi
    if [ "$1" = down ] && [ -z "$(listener)" ]; then return 0; fi
    sleep 1
  done
  return 1
}
status() {
  local pid; pid="$(listener)"
  echo "launchd $LABEL: $(loaded && echo loaded || echo 'not loaded')"
  if [ -n "$pid" ]; then echo "listening on http://127.0.0.1:$PORT (pid $pid)"; else echo "nothing listening on port $PORT"; fi
}

case "${1:-status}" in
  status) status ;;
  stop)
    loaded && launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null
    pkill -f "webapp/server.py" 2>/dev/null
    wait_port down || echo "port $PORT still in use by pid $(listener): not a Jarvis process this script owns, left alone"
    status ;;
  start)
    if ! loaded; then
      [ -f "$PLIST" ] || { echo "not installed: cp webapp/com.cbrain.webapp.plist ~/Library/LaunchAgents/ (replace /Users/YOU), then rerun"; exit 1; }
      launchctl bootstrap "$DOMAIN" "$PLIST"
    fi
    wait_port up || echo "started, but nothing listens on $PORT yet: see output/webapp.log"
    status ;;
  restart)
    if loaded; then launchctl kickstart -k "$DOMAIN/$LABEL"; else "$0" start >/dev/null; fi
    sleep 2; wait_port up || echo "restarted, but nothing listens on $PORT yet: see output/webapp.log"
    status ;;
  *) echo "usage: scripts/jarvis.sh status|stop|start|restart"; exit 64 ;;
esac
