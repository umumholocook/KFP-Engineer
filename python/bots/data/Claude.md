# data/

## Purpose
Static seed data for Discord role initialization — Hololive-themed role sets.

## Files
| File | Content |
|------|---------|
| `DefaultRoleData.py` | Default KFP rank roles (egg → phoenix progression) |
| `SpecialRoleData.py` | Hololive EN member-themed collectible roles |
| `LEWDRoleData.py` | LEWD category roles |
| `UtilRoleData.py` | Utility roles |

## Usage
- `cogs/RoleSelectSpecial.py` — random special role lottery from `SpecialRoleData.EN_MEMBERS`
- `cogs/NewProfile.py` / `cogs/RoleManager.py` — role initialization and rank-up
- `resource/default_rank_roles.json` — JSON mirror of default rank role config

## Notes
Role names and colors must match actual Discord server roles. `get(guild.roles, name=...)` is used to find roles by exact name.