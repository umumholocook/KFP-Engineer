# lib/

## Purpose
Small, mostly pure-Python helper libraries with no Discord or DB dependencies.

## Files
| File | Role |
|------|------|
| `Dice.py` | Dice rolling + CoC (Call of Cthulhu) skill check logic |
| `Clear.py` | Message clearing utilities |
| `ImageTransformer.py` | Image manipulation helpers (used by `common/Util.py`) |

## Usage
Imported by `common/` and occasionally cogs. Keep functions stateless.

## Note
`Dice.py` has a `__main__` self-test block — not part of the bot runtime.