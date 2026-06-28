# common/models/

## Purpose
Peewee ORM models for the SQLite database. All inherit from `BaseModel.py` (uses `DatabaseProxy` for testability).

## Models

| Model | Table Purpose |
|-------|---------------|
| `Member` | User XP, coins, tokens, rank |
| `Channel` | Channel ID ↔ feature type mapping (rank-up, RPG, etc.) |
| `KfpRole` | Discord role metadata |
| `PermissionRole` | Permission role assignments |
| `NicknameModel` | Custom nicknames |
| `Leaderboard` / `EmojiTracker` | Reaction leaderboard data |
| `GamblingGame` / `GamblingBet` | Betting pools |
| `KujiRecord` | Fortune-draw history |
| `InventoryRecord` / `Item` / `ShopItem` | RPG items & shop |
| `RPGCharacter` / `RPGStatus` | RPG adventure state |
| `Forward` | Message forwarding rules |
| `Police` | Police/moderation records |
| `Emotion` | Emotion tracking |
| `ProfileObject` | Profile display data (not a DB table — display DTO) |
| `ReactionRole` | Reaction-role mappings |
| `RouletteGame` / `RouletteGameBet` | Roulette (partially used) |

## Registration
Models listed in `KFP_DB.MODULES` are auto-created on bot startup.

## Schema Changes
Do **not** just edit field definitions — add a migration step in `common/database/KfpMigrator.py` for existing deployments.

## Testing
Tests use in-memory or temp DB via `DatabaseProxy.initialize()` — see `tests/Database/`.