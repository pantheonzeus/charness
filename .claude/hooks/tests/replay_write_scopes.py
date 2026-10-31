#!/usr/bin/env python3
"""Replay every historical Write/Edit of each headless job (ledger session → transcript, subagents
included) through .claude/hooks/write-boundary.sh with that job's CBRAIN_JOB, against a mirror repo so
no deny is logged for real. Prints writes and denials per job. Re-run after editing any
`write_scopes:`; every denial listed must be explainable as a write the job should not make.
Run: python3 .claude/hooks/tests/replay_write_scopes.py [--since 2026-10-23]
"""
import json, subprocess, sys, tempfile, os, collections
from pathlib import Path
repo = Path(__file__).resolve().parents[3]; proj = Path.home() / '.claude/projects' / str(repo).replace('/', '-')
since = sys.argv[sys.argv.index('--since') + 1] if '--since' in sys.argv else ''
fake = Path(tempfile.mkdtemp()).resolve(); (fake / '.claude').mkdir()
os.symlink(repo / '.claude/agents', fake / '.claude/agents')
hook = repo / '.claude/hooks/write-boundary.sh'
stats = collections.defaultdict(lambda: [0, 0, 0]); denied = collections.defaultdict(collections.Counter)
for led in sorted((repo / 'output/.runs/_ledger').glob('*.jsonl')):
    job = led.stem
    if not (repo / '.claude/agents' / f'{job}.md').exists(): continue
    for line in led.read_text().splitlines():
        run = json.loads(line) or {}
        sid = run.get('session_id')
        if not sid or (run.get('ts') or '') < since: continue
        files = [proj / f'{sid}.jsonl'] + list((proj / sid).glob('subagents/*.jsonl'))
        files = [f for f in files if f.exists()]
        if not files: continue
        stats[job][0] += 1
        for f in files:
            for raw in f.read_text().splitlines():
                try: ev = json.loads(raw)
                except Exception: continue
                if ev.get('type') != 'assistant': continue
                for c in (ev.get('message') or {}).get('content') or []:
                    if not isinstance(c, dict) or c.get('type') != 'tool_use': continue
                    if c.get('name') not in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'): continue
                    inp = c.get('input') or {}
                    p = inp.get('file_path') or inp.get('notebook_path') or ''
                    if not p: continue
                    p = p.replace(str(repo), str(fake), 1)
                    payload = json.dumps({'tool_name': c['name'], 'cwd': str(fake), 'tool_input': {'file_path': p}})
                    out = subprocess.run(['bash', str(hook)], input=payload, capture_output=True, text=True,
                                         env={**os.environ, 'CLAUDE_PROJECT_DIR': str(fake), 'CBRAIN_JOB': job}).stdout
                    stats[job][1] += 1
                    if '"deny"' in out:
                        stats[job][2] += 1
                        rel = p.replace(str(fake) + '/', '')
                        denied[job][rel] += 1
for job, (runs, writes, den) in sorted(stats.items()):
    print(f'{job:18} runs={runs:3} writes={writes:4} denied={den}')
for job, c in sorted(denied.items()):
    print(f'\n== {job} denied paths:')
    for p, n in c.most_common(25): print(f'  {n:3}x {p}')
