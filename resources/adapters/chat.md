# chat — capability contract

## Operations (used today)
| Operation | Used by | Notes |
|---|---|---|
| `list_posts(channel_id, oldest, limit) → [Post]` | slack-intel fetch | top-level posts since the high-water mark |
| `user_profile(id)` | slack-intel fetch | author name |
| `resolve_channel(name) → id` | slack-intel setup | |
| `read_thread(channel, id)` | (planned) | |

Never: send, draft, schedule, react, canvas. The chat adapter is read-only by contract.

## Normalized shape — `output/slack-intel/posts/<id>.json`
`id, channel, channel_id, ts, posted, user, text, reply_count, files, links, permalink`

## Implementations
| Adapter | Where | Auth |
|---|---|---|
| `slack` | `slack-intel/scripts/slack_intel.py` (`READ_TOOLS`: `mcp__claude_ai_Slack__slack_read_channel`, `…slack_read_user_profile`; `NO_TOOLS` denies every write tool) | the claude.ai Slack connector, connected to the employer's workspace |
| `teams` | **stub — not built.** Notes (unverified): `GET /teams/{id}/channels/{id}/messages` usually needs tenant-admin consent (`ChannelMessage.Read.All`), the likeliest blocker at an M365 employer. | |
| `none` | no chat loop: `com.cbrain.slack-intel` is not in the pack's `loops`, and slack-intel refuses to run | |
