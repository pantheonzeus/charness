---
id: recall
aliases: [recall]
name: "Recall — Load Context from Vault Memory"
category: workflow-ops
description: Load context from vault/session memory — temporal recall (yesterday/last week from native JSONL), topic recall (QMD BM25 search), and an interactive session-file graph, ending every recall with the "One Thing" highest-leverage next action.
triggers: [recall, what did we work on, load context about, remember when we, prime context, yesterday, what was I doing, last week, session history, recall graph, session graph]
tags: [workflow-ops, recall, memory, context, claude-code, sessions, observability]
related: ["[[sync-claude-sessions]]", "[[person-dossier]]"]
requires:
  tools: [bash, python]
  cli: [qmd]
environment: "Terminal / Claude Code slash-command (/recall). Temporal recall needs no setup (reads native Claude Code JSONL). Topic recall needs the `qmd` CLI; optional session auto-indexing via a session-end hook."
scripts: [scripts/extract-sessions.py, scripts/recall-day.py, scripts/session-graph.py]
workflows: [workflows/recall.md]
status: active
version: 1
created: 2026-07-05
updated: 2026-07-05
# Claude Code slash-command fields preserved below; original upstream frontmatter was {name, description, argument-hint, allowed-tools}.
argument-hint: [yesterday|today|last week|this week|TOPIC|graph DATE_EXPR]
allowed-tools: Bash(qmd:*), Bash(python3:*)
---

# Recall Skill

Three modes: temporal (date-based session timeline), topic (BM25 search across QMD collections), and graph (interactive visualization of session-file relationships). Every recall ends with the **One Thing** - a concrete, highest-leverage next action synthesized from the results.

## What It Does

- **Temporal queries** ("yesterday", "last week", "what was I doing"): Scans native Claude Code JSONL files by date. Shows a table of sessions with time, message count, and first message. Expand any session for conversation details.
- **Topic queries** ("QMD video", "authentication"): BM25 search across sessions, notes, and daily logs in QMD collections.
- **Graph queries** ("graph yesterday", "graph last week"): Generates an interactive HTML graph showing sessions as nodes connected to files they touched. Sessions colored by day, files colored by folder. Clusters reveal related work streams, shared files show cross-session dependencies.
- **One Thing synthesis**: After presenting results, synthesizes the single most impactful next action based on what has momentum, what's blocked, and what's closest to done. Not generic - specific and actionable.

No custom setup needed for temporal recall - every Claude Code user has JSONL files.

## Auto-Indexing (Optional)

You can auto-index sessions into QMD on every session end via a Claude Code hook. See AGENTS.md for setup instructions.

## Usage

```
/recall yesterday
/recall last week
/recall 2026-02-25
/recall QMD video
/recall authentication work
```

**Graph mode** - visualize session relationships over time:
```
/recall graph yesterday        # what you touched today
/recall graph last week        # week overview - find clusters
/recall graph this week        # current week so far
/recall graph last 3 days      # recent activity window
```

Graph options: `--min-files 5` for cleaner graphs (only sessions touching 5+ files), `--all-projects` to scan beyond current vault.

## Workflow

See `workflows/recall.md` for routing logic and step-by-step process.
