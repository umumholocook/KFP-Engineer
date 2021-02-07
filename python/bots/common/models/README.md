# models

本資料夾存放基於 Peewee 所撰寫的ORM資料庫物件

## 檔案

BaseModel.py
---
Peewee所需要的基本ORM模型, 為了unit test而使用DatabaseProxy()來連接database

Member.py
---
基本Member模型

Channel.py
---
用來記錄Channel以及其discord channel id的模型
