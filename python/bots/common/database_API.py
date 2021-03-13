import sqlite3 
from enum import IntEnum, Enum

Data_base = r"./common/KFP_bot.db"

class StrEnum(str, Enum):
    pass

class member_index(IntEnum):
    member_id = 0
    xp = 1
    rank = 2
    item_id_list = 3
    normal_coin = 4
    special_item_id_list = 5
    extra_avator_image = 6
    pure = 7

class channel_index(StrEnum):
    rank_up = 'rank_up_channel_id'

def sort_rank_num(guild_id:int, target_xp:int):
    col = get_members_col(guild_id, 'xp')
    rank = 1
    for c in col:
        if c[0] > target_xp:
            rank+=1
    return rank

def calcuelate_xp(next_rank:int):
    return 5 / 6 * next_rank * (2 * next_rank * next_rank + 27 * next_rank + 91)

def get_table_list():
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('select name from sqlite_master where type = \'table\';')
    result = cu.fetchall()
    sq.close()
    return result

def get_member_row(guild_id:int , member_id:int):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('SELECT * FROM server_{} WHERE member_id=(?);'.format(guild_id),(member_id,))
    member_row = cu.fetchone()
    sq.close()
    return member_row

def get_members_col(guild_id:int, col_name:str):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('SELECT {} FROM server_{};'.format(col_name, guild_id))
    member_row = cu.fetchall()
    sq.close()
    return member_row

def get_members_table(guild_id:int):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()

    cu.execute('SELECT * FROM server_{};'.format( guild_id))
    member_row = cu.fetchall()
    sq.close()
    return member_row

def _check_rank_and_update(guild_id:int, member_id:int, cu:sqlite3.Cursor):
    cu.execute('SELECT xp, rank FROM server_{} WHERE member_id=(?);'.format(guild_id),(member_id,))
    fetch_ = cu.fetchone()
    if fetch_ != None:
        xp, rank = fetch_
    else:
        return False
    if xp >= int(calcuelate_xp(rank+1)):
        cu.execute('UPDATE server_{} SET rank={} WHERE member_id=(?)'.format(guild_id, rank+1), (member_id,))
        cu.execute('SELECT rank FROM server_{} WHERE member_id=(?);'.format(guild_id), (member_id,))
        return cu.fetchone()
    return False

def increase_xp(guild_id:int, member_id:int, increase_num:int):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('UPDATE server_{} SET xp = xp + {} WHERE member_id = (?)'.format(guild_id, increase_num), (member_id,))
    sq.commit()
    is_rankup = _check_rank_and_update(guild_id, member_id, cu)
    if is_rankup:
        sq.commit()
    sq.close()
    return is_rankup
    
def get_message_channel_id(guild_id:int, index:str):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('SELECT {} FROM message_chennel WHERE guild=(?);'.format(index), (guild_id,))
    channel_id = cu.fetchone()
    sq.close()
    return channel_id[0]

def increase_normal_coin(guild_id:int, member_id:int, increase_num:int):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('UPDATE server_{} SET normal_coin = normal_coin + {} WHERE member_id = (?)'.format(guild_id, increase_num), (member_id,))
    sq.commit()
    sq.close()

def add_members(guild_id:int, members_set:set):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    for member_ in members_set:
        cu.execute(
'''INSERT INTO server_{} 
(member_id, xp, rank, item_id_list, normal_coin, special_item_id_list, extra_avator_image, pure)
VALUES ((?), (?), (?), (?), (?), (?), (?), (?));
'''.format(guild_id), member_)
    sq.commit()
    sq.close()

def add_member(guild_id:int, member_id:int):
    if get_member_row(guild_id, member_id) != None:
        return
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute(
'''INSERT INTO server_{} 
(member_id, xp, rank, item_id_list, normal_coin, special_item_id_list, extra_avator_image, pure)
VALUES ((?), (?), (?), (?), (?), (?), (?), (?));
'''.format(guild_id), (member_id, 0, 0,'[]', 0, '[]', None, None))
    sq.commit()
    sq.close()

def set_rankup_channel (guild_id:int, channel_id:int):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('select * FROM message_chennel where guild=(?)',(guild_id,))
    ch_tem = cu.fetchone()
    if ch_tem == None:
        cu.execute('INSERT INTO message_chennel (guild, rank_up_channel_id) VALUES ((?), (?));',(guild_id, channel_id))
    else:
        cu.execute('UPDATE message_chennel SET rank_up_channel_id=(?) WHERE guild=(?);',(channel_id,guild_id))
    sq.commit()
    sq.close()

def creat_server_member_table(guild_id:int):
    sq = sqlite3.connect(Data_base)
    cu = sq.cursor()
    cu.execute('select name from sqlite_master where type = \'table\';')
    table_list = cu.fetchall()
    if not ('server_{}'.format(guild_id),) in table_list:
        cu.execute('''
CREATE TABLE server_{} (
member_id INT PRIMARY KEY NOT NULL,
xp INT NOT NULL,
rank BIGINT,
item_id_list INT NOT NULL,
normal_coin BIGINT,
special_item_id_list BIGINT NOT NULL,
extra_avator_image BLOB,
pure INT 
);
'''.format(guild_id))
    sq.close()
