# ui/

## Purpose
Discord UI presentation layer — embed builders separated from cog business logic.

## Structure
```
ui/
├── gambling/GamblingEmbed.py  → Betting pool embeds
└── Kuji/KujiEmbed.py          → Fortune-draw result embeds
```

## Pattern
Static factory methods returning `discord.Embed`:
```python
KujiEmbed.createEmbededJp(kuji, datetime, footer_text)
GamblingEmbed.create(...)
```

## Used By
- `cogs/Kuji.py`, `cogs/Kuji_slash.py` → `KujiEmbed`
- `cogs/Gambling.py` → `GamblingEmbed`

## When Adding
New visual-heavy features should put embed construction here, not inline in cogs.