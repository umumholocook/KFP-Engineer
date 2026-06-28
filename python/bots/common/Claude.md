# common/

## Purpose
Shared business logic, utilities, and database layer used by cogs. Not Discord-facing directly.

## Key Files

| File | Role |
|------|------|
| `KFP_DB.py` | Main DB facade — member XP/coins, guild setup. Initializes Peewee + migrations |
| `database_API.py` | **Legacy** raw SQLite. Only `RoleSelectSpecial` still imports it — migrate away |
| `MemberUtil.py` | Member CRUD, coin/XP operations |
| `ChannelUtil.py` | Channel-type registry (rank-up, RPG, bank, etc.) |
| `RoleUtil.py` | Discord role ↔ DB sync |
| `LeaderboardUtil.py` | Emoji reaction leaderboard tracking |
| `GamblingUtil.py` | Betting pool logic |
| `KujiUtil.py` / `KujiObj.py` | Fortune-draw logic + image generation |
| `ImageUtil.py` | Profile/image helpers (PIL, OpenCV) |
| `NicknameUtil.py` | Display name resolution |
| `BotAvatarUtil.py` | Twitter avatar fetch — **disabled** (API pricing change) |
| `InteractionUtil.py` | Slash command helpers (`require_channel`, `respond`) |
| `ShiritoriStringUtil.py` | Shiritori text normalization + word matching (`zhconv`) |
| `DiscordUtil.py` | Modern Discord API helpers (`fetch_text_channel`, `fetch_guild_member`, `read_avatar_image`, `invite_url`) |
| `TestUtil.py` | Test helpers |

## Subfolders
- `models/` — Peewee ORM table definitions
- `database/` — Schema migrations (`KfpMigrator.py`)
- `RPGUtil/` — RPG game engine (status, items, buffs, revive)
- `customField/` — Peewee custom field types

## Database
- Path: `./common/KFP_bot.db` (SQLite)
- ORM: Peewee with `DatabaseProxy` in `models/BaseModel.py`
- Migrations run on every `KfpDb()` init via `KfpMigrator`

## Conventions
- `*Util.py` = stateless or static helper classes
- Guild-scoped data uses `guild_id` + `channel_id` patterns
- `Util.ChannelType`, `Util.GamblingStatus`, etc. are `IntEnum` — **never reorder or delete members**

## When Editing
- Prefer adding methods to existing `*Util` classes over duplicating in cogs
- New tables: add model in `models/`, register in `KFP_DB.MODULES`, add migration in `KfpMigrator`