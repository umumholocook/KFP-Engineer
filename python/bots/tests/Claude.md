# tests/

## Purpose
pytest unit tests for `common/` utilities and some cog logic. Run via `./test_kfp.sh` from `bots/`.

## Structure
One subfolder per feature area, mirroring `common/`:
```
tests/
├── Channel/       → ChannelUtil
├── Database/      → KfpDb, KfpMigrator
├── ForwardRule/   → ForwardUtil
├── Gambling/      → GamblingUtil
├── Inventory/     → InventoryUtil
├── Item/          → ItemUtil
├── Leaderboard/   → LeaderboardUtil
├── Level/         → LevelUtil
├── Member/        → MemberUtil
├── NewProfile/    → Profile cog logic
├── Nickname/      → NicknameUtil
├── Police/        → PoliceUtil
├── Role/          → RoleUtil, RoleSelectSpecial
├── RPG/           → Buff, RPGCharacterUtil, StatusUtil
├── RPS/           → RockPaperScissors
├── Shiritori/     → KujiObj, KujiUtil
└── Util/          → Util
```

## Conventions
- Tests use `TestUtil` helpers and temp/in-memory DB
- `KfpDb.teardown()` drops tables — test-only
- File naming: `*_test.py`

## Coverage Gaps
Most cogs (Gambling, Shop, Gemini, etc.) have no direct cog tests. Tests focus on `common/` layer.

## Adding Tests
Place in matching subfolder; use pytest fixtures pattern from existing tests in same area.