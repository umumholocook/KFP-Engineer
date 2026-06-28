# common/RPGUtil/

## Purpose
RPG mini-game engine — character lifecycle, combat statuses, items, buffs, and periodic revival.

## Files

| File | Role |
|------|------|
| `RPGCharacterUtil.py` | Create/retire characters, adventure start, combat |
| `StatusUtil.py` | Apply/expired statuses (rest, coma, etc.); `reviveComaStatus()` |
| `StatusUpdate.py` | Discord message sender for status change notifications |
| `StatusType.py` | Status enum (REST, COMA, etc.) |
| `ItemUtil.py` / `ItemType.py` | Item definitions and usage |
| `InventoryUtil.py` | Player inventory (distinct from top-level `common/InventoryUtil.py`) |
| `Buff.py` / `BuffField` (in customField/) | Temporary buff system |
| `ReviveUtil.py` | Coma revival announcements + channel routing |

## Background Tasks (main.py)
- `refreshStatus` (60s) → `StatusUtil.applyExpiredStatus()`
- `reviveComaStatus` (1h) → `StatusUtil.reviveComaStatus(reviveMemberCount=5)`

## Channel Types Used
- `Util.ChannelType.RPG_GUILD` — general RPG commands
- `Util.ChannelType.RPG_BATTLE_GROUND` — attack commands

## Cog Entry Point
`cogs/RPG.py` — uses `@commands.hybrid_group(name='rpg')` (only hybrid group in codebase)

## DB Models
`RPGCharacter`, `RPGStatus`, `Item`, `InventoryRecord` in `common/models/`