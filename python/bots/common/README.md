# Common

本資料夾放置各種cog常用功能

## 檔案與資料夾

models
---

基於 Peewee 所寫的 ORM(Object-relational mapping) 資料庫模型

SimpleDiscordMarkdown
---
簡易地將 discord markdown 解析成樹狀結構的 `dict`  
並有個類別，可以繼承並定義規則，將樹狀結構轉譯成可指定的資料結構

AssetCache.py
---
快取 discord asset 的 bytes 或 data url

DatetimeUtil.py
---
將 unix timestamp 格式化成可讀的中文日期  
格式化的風格依照 discord 所顯示

HTMLPainter.py
---
基於 [IMGKit](https://github.com/jarrekk/imgkit)，使用 [wkhtmltoimage](https://wkhtmltopdf.org/) 來將 HTML+CSS 渲染成圖檔  
使用前請安裝 wkhtmltoimage，參考 `settings/` 資料夾內的說明  
使用 `async with` 語法，在退出時將臨時的圖檔刪除

KFP_DB.py
---
基於Peewee 所寫的 database 介面

KFP_DB_test.py
---
KFP_DB.py 的 unit tests

UnicodeEmoji.py
---
提供 unicode emoji 的 regex pattern  
取得指定的 unicode emoji 名稱  
取得指定的 unicode emoji 的圖檔資源路徑  
圖檔資源自行選擇並下載，並在 `settings/` 資料夾裡設定路徑  
圖檔名稱必須符合以下的形式，可以參考 [twemoji](https://github.com/twitter/twemoji)  
`<codepoint>-<codepoint>-...-<codepoint>.png`

database_API.py
---
舊版本 database 介面, 使用純SQL

gen_img_shiritori.py
---
用來產生抽籤結果的畫面, 輸入抽籤結果. 根據結果產生相對應的圖片.
