# cogs/

## Purpose
One file per feature, each a `discord.ext.commands.Cog`. Loaded automatically by `main.py` (`cogs.<module>`).

## Pattern
```python
class Foo(commands.GroupCog, group_name="功能名", group_description="..."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="子指令", description="...")
    async def subcmd(self, interaction: discord.Interaction): ...

async def setup(bot):
    await bot.add_cog(Foo(bot))
```

Standalone slash commands use `commands.Cog` + `@app_commands.command` (e.g. `/聊天`, `/作弊`, `/下注`).

## Cog Inventory

| File | Slash Group / Command | Notes |
|------|----------------------|-------|
| AutoReact | (listener) | Reacts with `w_wake` emoji on certain phrases |
| Bank | `/銀行` | Coin banking |
| CharacterClass | `/轉職` | RPG job/class (stub) |
| CommandControl | `/指令控制` | Channel-restrict commands via `ChannelUtil` |
| Dizzy | `/阿暈` | Dizzy meme image |
| ForwardRule | `/轉發` | Cross-channel message forwarding |
| Gambling | `/下注`, `/作弊`, `/賭盤`, `/自動清除` | Betting pool system |
| Gemini | `/聊天` | AI chat + image gen. Uses `bot_memory.db` |
| InventoryDisplay | `/背包` | Show RPG inventory |
| Kuji | `/抽籤`, `/清除紀錄` | Fortune drawing |
| Leaderboard | `/排行榜` | Emoji reaction leaderboards |
| NewProfile | `/個人檔案` | XP, levels, profile card (on_message XP listener) |
| Nickname | `/暱稱` | Custom nicknames |
| PoliceControl | `/警察` | Police role tools + on_message listener |
| Rickroll | `/瑞克搖` | Rickroll meme generator |
| RockPaperScissors | `/猜拳` | RPS |
| RoleManager | `/身分組` | Role init (owner only) |
| RoleSelectSpecial | `/特殊身分組` | Random role lottery on messages |
| Roulette | `/轉盤說明`, `/開始轉盤`, `/轉盤下注` | Roulette gambling |
| RPG | `/冒險` | Adventure/combat mini-game |
| Shop | `/商店` | Item shop |
| SuperChat | `/超級留言` | Super Chat simulation |
| SusMeme | `/流放` | Among Us meme voting |
| Shiritori | `/文字接龍` | Chinese word chain game (on_message during active game) |
| Yagoo | `/最佳女孩` | Yagoo greeting image |

## Channel Gating
Many cogs check `ChannelUtil.hasChannel(guild_id, channel_id, Util.ChannelType.*)` before running.

## Adding a New Cog
Create `cogs/MyFeature.py` with `GroupCog` + `setup()` — auto-loaded by `main.py`.
Use `common.InteractionUtil.require_channel()` for channel-gated features.
Use Chinese slash names for user-facing commands.