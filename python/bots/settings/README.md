# Settings

本資料夾放置各種以 Python 內建型別記錄的設定檔

## 設定檔

IMGKitSetting.py
---

1. `CONFIG: dict`

    與 `imgkit.config` 的關鍵字參數一致，參考 [IMGKit#Usage](https://github.com/jarrekk/imgkit#usage)，以下說明與 imgkit 一致

    + `'wkhtmltoimage'`: wkhtmltoimage 的二進制檔案位置，若不指定預設使用 `which (類 UNIX 系統)` 或 `where (Windows)` 作定位
    + `'xvfb'`: xvfb-run 的二進制檔案位置，若不指定預設使用 `which (類 UNIX 系統)` 或 `where (Windows)` 作定位
    + `'meta_tag_prefix'`: 指定 html meta tags 的前綴，預設與 imgkit 一致

2. `CACHE_DIR: str`

   指定 wkhtmltoimage 的快取資料夾位置

SuperChatSetting.py
---
指定 unicode emoji 的字型來源，形式與 CSS `@font-face` 的 src 一致，參考 [MDN CSS @font-face](https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face)

1. `EMOJI_FONT_FACE_SRC: str`

    `'url(網路字型)'`, `'local(本地安裝字型)'`, 或 `'本地字型檔案位置'`

2. `EMOJI_FONT_FACE_FORMAT: str`

    提示字型資源的格式，省略的話為 `''` 空字串，或者 `'format(字型格式)'`

UnicodeEmojiSetting.py
---

1. `ASSETS_DIR: str`

    提供 unicode emoji 的圖檔資源資料夾位置，資料夾中的圖檔名稱必須符合以下的形式，可以參考 [twemoji](https://github.com/twitter/twemoji)  
    `<codepoint>-<codepoint>-...-<codepoint>.png`

