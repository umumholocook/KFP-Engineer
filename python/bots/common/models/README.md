# models

本資料夾存放基於 Peewee 所撰寫的ORM資料庫物件

## 檔案

BaseModel.py
---
Peewee所需要的基本ORM模型, 為了unit test而使用DatabaseProxy()來連接database

Member.py
---
基本Member模型, 由於資料庫table是採用server_{guild_id}的格式, 所以本模型是動態模型
