#!/usr/bin/env bash
# PreToolUse send gate: approval + outbound scan before any MCP send tool. Logic and rules: send_gate.py.
exec /usr/bin/python3 "$(dirname "${BASH_SOURCE[0]}")/send_gate.py"
