# resource/

## Purpose
Static assets bundled with the bot — images, fonts, and fortune-telling datasets.

## Structure
```
resource/
├── image/     → PNG/WebP assets (profile cards, memes, kuji backgrounds, etc.)
├── ttf/       → Fonts (NotoSansMonoCJKtc-Regular.otf for profile cards)
├── data/      → Python modules with fortune text (see resource/data/Claude.md)
└── default_rank_roles.json
```

## Path Convention
Code references assets via `os.path.join(os.getcwd(), 'resource', ...)` — bot must be launched from `bots/` directory.

## Key Assets
- `image/card_base.png` — profile card template (`NewProfile.py`)
- `image/no_futa.webp` — easter-egg response in `main.py`
- Kuji fortune images referenced by `KujiUtil.py`

## Do Not
Commit generated temp images; large binary updates should be intentional.