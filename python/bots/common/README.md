# Common

本資料夾放置各種cog常用功能

## 檔案與資料夾

models
---

基於 Peewee 所寫的 ORM(Object-relational mapping) 資料庫模型

KFP_DB.py
---
基於Peewee 所寫的 database 介面

KFP_DB_test.py
---
KFP_DB.py 的 unit tests

database_API.py
---
舊版本 database 介面, 使用純SQL

gen_img_shiritori.py
---
用來產生抽籤結果的畫面, 輸入抽籤結果. 根據結果產生相對應的圖片.
