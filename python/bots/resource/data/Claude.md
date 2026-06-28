# resource/data/

## Purpose
Python modules containing fortune-telling / divination text data used by the Kuji (抽籤) feature.

## Files
| File | Content |
|------|---------|
| `omikuji.py` | Japanese omikuji fortunes (99 entries) — `OMIKUJI` list |
| `lungshan.py` | Longshan Temple fortunes — `LUNGSHAN` list |
| `yi.py` | I Ching (易經) hexagram data |
| `rick_roll.py` | Rickroll-related text data |

## Usage
Imported by `cogs/Kuji.py` and `cogs/Kuji_slash.py`:
```python
from resource.data.omikuji import OMIKUJI
from resource.data.lungshan import LUNGSHAN
```

## Related
- `common/KujiUtil.py` — draw logic, image compositing, daily-limit tracking
- `ui/Kuji/KujiEmbed.py` — Discord embed formatting

## Note
`python/shiritori/` has duplicate copies of `omikuji.py`, `lungshan.py`, `yi.py` for the separate Shiritori bot.