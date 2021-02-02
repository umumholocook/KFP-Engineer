from common import database_API
import json ,os
from random import randint
import discord
from discord.ext import commands
from discord import Guild, Member, Message, Reaction, Role

'''
店長：復甦（劍）、落燼（盾）、不死鳥羽（耳環）、PAPA的制約（封印）、死神誓約（蝴蝶結頸圈）

死神：魂歌死鐮（武器）、地獄獠牙（披風）、不眠者的榮耀（頭冠）、喚魂笛（生草笛）、不死鳥誓約（頭紗）

AME：真實之眼（放大鏡）、還原時空的懷錶（懷錶）、最強偵探的象徵（獵鹿帽+披肩外套）、（頭飾）、可以聽見心聲的黑科技產品-華生讀心器（聽診器）

INA：原始咒書（魔導書）、古神傳承（頭飾）、被召喚的觸手（觸手）、守護諭（腰間的翅膀）、五法靈結（手臂和大腿的繩結飾品）

鯊鯊：亞特蘭蒂斯王器（三叉戟）、鯊鯊帽（在陸地上買的可愛鯊鯊帽，無特殊能力）、鯊鯊裝（腰間的大嘴似乎可以探測到鮭魚）、BLOOP（鯊鯊的備用糧食）、鯊尾啦！（意圖使他人意識到自己是兇猛鯊魚的尾巴）
掛號內的東西....
在想看看有沒有能夠更簡節一點
不然就乾脆用畫的好了

'''
kiara_weapon_role = {
    'name' : '🗡復甦（劍）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xEE7700),
    'hoist' : False,
    'mentionable' : False
    }
kiara_shild_role = {
    'name' : '🛡落燼（盾）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFF8800),
    'hoist' : False,
    'mentionable' : False
}
kiara_earRing_role = {
    'name' : '🪶不死鳥羽（耳環）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFAA33),
    'hoist' : False,
    'mentionable' : False
}
kiara_scroll_role = {
    'name' : '📜PAPA的制約（封印）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFBB66),
    'hoist' : False,
    'mentionable' : False
}
kiara_ribbon_role = {
    'name' : '🎀死神誓約（蝴蝶結頸圈）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFBB66),
    'hoist' : False,
    'mentionable' : False
}

kiara_part_list = (kiara_weapon_role, kiara_shild_role, kiara_earRing_role, kiara_scroll_role, kiara_ribbon_role)

calli_sickle_role = {
    'name' : '🎶魂歌死鐮（武器）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFDEDE),
    'hoist' : False,
    'mentionable' : False
}

calli_cloak_role = {
    'name' : '❇地獄獠牙（披風）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFABAB ),
    'hoist' : False,
    'mentionable' : False
}

calli_crown_role = {
    'name' : '👑不眠者的榮耀（頭冠）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFF7878),
    'hoist' : False,
    'mentionable' : False
}
calli_flute_role = {
    'name' : '📏喚魂笛（生草笛）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFF4545 ),
    'hoist' : False,
    'mentionable' : False
}

calli_veil_role = {
    'name' : '👰不死鳥誓約（頭紗）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFF1212),
    'hoist' : False,
    'mentionable' : False
}
calli_part_list = (calli_sickle_role, calli_cloak_role, calli_crown_role, calli_flute_role, calli_veil_role)

ame_magnifier_role = {
    'name' : '🔍真實之眼（放大鏡）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xEEEE00),
    'hoist' : False,
    'mentionable' : False
}
ame_watch_role = {
    'name' : '🕰還原時空的懷錶（懷錶）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFFF00),
    'hoist' : False,
    'mentionable' : False
}
ame_syringe_role = {
    'name' : '💉生命維持針（針筒)',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFFF33),
    'hoist' : False,
    'mentionable' : False
}
ame_book_role = {
    'name' : '📒強者之證(兒時回憶錄)',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFFF77),
    'hoist' : False,
    'mentionable' : False
}
ame_stethoscope_role = {
    'name' : '🩺可以聽見心聲的黑科技產品-華生讀心器（聽診器）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0xFFFFBB ),
    'hoist' : False,
    'mentionable' : False
}
ame_part_list = (ame_magnifier_role, ame_watch_role, ame_syringe_role, ame_book_role, ame_stethoscope_role)

ina_AO_role = {
    'name' : '📖原始咒書（魔導書）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x580099),
    'hoist' : False,
    'mentionable' : False
}
ina_toko_role = {
    'name' : '🐙古神傳承（頭飾）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x6400B2),
    'hoist' : False,
    'mentionable' : False
}
ina_tentacle_role = {
    'name' : '👾被召喚的觸手（觸手）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x7600CC),
    'hoist' : False,
    'mentionable' : False
}
ian_winds_role = {
    'name' : 'ଘ( ˊωˋ )ଓ 守護諭（腰間的翅膀）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x8400E6),
    'hoist' : False,
    'mentionable' : False
}
ian_ribbon_role = {
    'name' : '💖🎀五法靈結（手臂和大腿的繩結飾品）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x990DFF),
    'hoist' : False,
    'mentionable' : False
}
ina_part_list = (ina_AO_role, ina_toko_role, ina_tentacle_role, ian_winds_role, ian_ribbon_role)

gura_trident_role = {
    'name' : '🔱亞特蘭蒂斯王器（三叉戟）',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x067EBA),
    'hoist' : False,
    'mentionable' : False
}
gura_hat_role = {
    'name' : '🧢鯊鯊帽',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x067EBA),
    'hoist' : False,
    'mentionable' : False
}
gura_cloth_role = {
    'name' : '👚鯊鯊裝',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x067EBA),
    'hoist' : False,
    'mentionable' : False
}
gura_bloop_role = {
    'name' : '🥫BLOOP',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x067EBA),
    'hoist' : False,
    'mentionable' : False
}
gura_tail_role = {
    'name' : '🦈鯊尾',
    'permissions' : discord.Permissions(permissions=0),
    'colour' : discord.Colour(0x067EBA),
    'hoist' : False,
    'mentionable' : False
}
gura_part_list = (gura_trident_role, gura_hat_role, gura_cloth_role, gura_bloop_role, gura_tail_role)

class Special_role(commands.Cog):
    def __init__(self, client):
        self.bot = client

    def check_complete(self,member:Member):
        #TODO:check is user collect complete
        pass
    
    @commands.Cog.listener('on_role_delete')
    async def special_collect_on_role_delete(self, message:Message):
        #TODO:if special roles being delet, recreate!
        pass

    @commands.Cog.listener('on_message')
    async def special_collect_on_message(self, message:Message):
        #TODO:Calculate is user get role or not
        pass

    @commands.group(name = 'special', invoke_without_command = True)
    async def special_collect_group(self, ctx:commands.Command, *attr):
        #TODO:print special collect eqiment state
        pass
    
    @special_collect_group.command(name = 'init_role')
    async def special_collect_init(self, ctx:commands.Command, *argv):
        #TODO:check role on guild and auto create on guild
        role_list = ctx.guild.roles
        has_role = False
        for g_role in role_list:
            if g_role.name == kiara_weapon_role['name']:
                has_role=True
                break
        if not has_role:
            await ctx.guild.create_role(**kiara_weapon_role)

    #TODO: design something special that shown user they got the special roles
    #Note: for inas roles, can upload some voice cut for user
        


def setup(client):
    client.add_cog(Special_role(client))