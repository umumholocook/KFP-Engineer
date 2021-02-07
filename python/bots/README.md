# BOTS 檔案夾

這裡放置的都是基於 discord.py 所編寫的 Discord 專用 bot

## 如何使用

0. 安裝所需的library

```
pip install -r requirements.txt
```

NOTE: 如果要更新 requirements.txt, 可以跑下面的指令

```
pip freeze > requirements.txt
```

1. 機器人需要開啟下面兩個權限

```
PRESENCE INTENT
SERVER MEMBERS INTENT
```

並且要有Manage Roles Permission

2. 修改discord_bot_2_0.py裡面的token

3. 使用 start_kfp.sh

4. 邀請bot到聊天室


## 如何增加新功能？

在 cogs/ 檔案夾底下添加新的功能即可

## 如何跑unit tests?

本項目使用了pytest作為unit test framework, 請使用以下命令執行

```
test_kfp.sh
```

TODO: 導出測試覆蓋率


## 常見問題

### 找不到table?

把bot啟動起來 然後踢出聊天室 再重新加回來

