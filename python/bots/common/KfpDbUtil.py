import sqlite3
from common.models.Member import Member

# 導入舊資料庫至新資料庫
class KfpDbUtil():
    def importFromOldDatabase(guild_id: int, db_name: str):
        table_name = "server_{}".format(guild_id)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM {};".format(table_name))
        rows = cursor.fetchall()
        count = 0
        for row in rows:
            member_id = row[0]
            exp = row[1]
            rank = row[2]
            coin = row[4]
            pure = row[7]
            member = Member.create(member_id= member_id, exp= exp, rank= rank, coin= coin, pure= pure)
            member.save()
            count += 1
        conn.close()
        return count

    def getCount(guild_id: int, db_name: str):
        table_name = "server_{}".format(guild_id)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM {};".format(table_name))
        count = cursor.fetchone()
        cursor.close()
        return count[0]