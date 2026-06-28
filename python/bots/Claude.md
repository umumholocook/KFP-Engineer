# KFP Discord Bot (bots/)

## Purpose
Main Discord bot for the KFP (Kiara Fried Phoenix) community server. Nicknamed **幕後大總管** (Grand Steward). Built on **discord.py 2.7.1**, Python **3.12.7**.

## Entry Point
- `main.py` — `Steward` bot class, cog auto-loader, background tasks, global slash commands (`/invite_link`, `/update`, `/version`)
- `start_kfp.sh` — launcher (`--check`, `--foreground`, `--background`); requires `KFP_TOKEN`
- `update_and_restart.sh` — git pull + `start_kfp.sh --background` (triggered by `/更新`)
- Env var: `KFP_TOKEN` (required)

## Architecture
```
main.py
  ├── cogs/          → feature modules (commands.Cog)
  ├── common/        → shared logic, DB, models
  ├── ui/            → Discord embed builders
  ├── lib/           → small pure helpers
  ├── data/          → static role seed data
  └── resource/      → images, fonts, fortune-telling data
```

## Key Runtime Behavior
- **Commands**: slash only (`commands.GroupCog` + `@app_commands.command`, Chinese names)
- **Prefix**: disabled (`command_prefix=commands.when_mentioned` — only responds if @mentioned)
- **DB**: SQLite at `common/KFP_bot.db` via Peewee ORM
- **Background tasks**: RPG status expiry (60s), coma revive (1h)
- **Cog loading**: auto-loads all `cogs/*.py` except `__init__`
- **AI**: `Gemini.py` — `/聊天` (OpenAI `GPT.py` removed)

## Known Issues / Tech Debt
- Twitter avatar sync disabled (`BotAvatarUtil.py`)
- Shiritori game merged as `cogs/Shiritori.py` (`/文字接龍`); standalone `python/shiritori/` deprecated
- README still references removed `discord_bot_2_0.py`

## Tests
Run from `bots/`: `./test_kfp.sh` (pytest)

## Do Not
- Change `Util.ChannelType` enum ordering (DB migration depends on IntEnum values)
- Delete existing enum members in `Util` classes (comments warn against this)