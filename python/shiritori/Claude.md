# shiritori/ (deprecated standalone bot)

## Status
**Merged into main KFP bot** as `bots/cogs/Shiritori.py` (`/文字接龍`).
Do not run `Shiritori.py` separately unless maintaining legacy deployment.

## What was here
| File | Purpose |
|------|---------|
| `Shiritori.py` | Standalone bot entry (prefix `!`, separate `KFP_SHIRITORI_TOKEN`) |
| `cogs/Game.py` | Word chain game logic — **ported to main bot** |
| `cogs/Kuji.py` | Fortune draw — **replaced by main bot `/抽籤`** |
| `cogs/StringUtil.py` | Text normalization — **ported to `bots/common/ShiritoriStringUtil.py`** |
| `database/` | Separate SQLite for kuji records (not used by main bot) |
| `data/` | Duplicate omikuji/lungshan/yi data |

## Main bot equivalent
```
/文字接龍 開始 [字數上限]
/文字接龍 停止
/文字接龍 紀錄
/文字接龍 顯示設定
/文字接龍 設定字數
/文字接龍 設定等待
```
Game play happens via normal chat messages while a round is active.