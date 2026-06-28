# ui/gambling/

## Purpose
Discord embed formatting for the gambling/betting system.

## Files
- `GamblingEmbed.py` — builds embeds for bet status, results, pool info

## Used By
- `cogs/Gambling.py`
- `common/GamblingUtil.py` (may reference for display)

## Related Logic
- `common/GamblingUtil.py` — bet state machine
- `common/models/GamblingGame.py`, `GamblingBet.py`