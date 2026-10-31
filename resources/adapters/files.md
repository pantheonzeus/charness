# files — capability contract

## Operations (used today)
| Operation | Used by | Notes |
|---|---|---|
| `search_touched_by(people, since, limit) → [File]` | meeting-prep sync | files participants modified or own, all drives, top 5 per meeting |
| `get(ref) → File` | meeting-prep sync | metadata for calendar attachments |
| `export_text(ref) → str` | meeting-prep sync | native documents to plain text |

Read-only everywhere.

## Normalized shape
`File{id, name, mime, modified, last_modifier, link}` plus exported text, held in meeting-prep's prep cache.

## Implementations
| Adapter | Where | Auth |
|---|---|---|
| `google` | `meeting-prep-loop/scripts/sync.py` (Drive REST files.list/get/export) + `drive_auth.py`; workspace-mcp `drive:readonly docs:readonly` for interactive questions | `~/.config/meeting-prep-loop/drive-token.json` |
| `m365` | **stub — not built.** Notes (unverified): `/me/drive/search`, `/me/insights/shared` / `used`; Office files have no native text export, so `export_text` needs a conversion step. | |
