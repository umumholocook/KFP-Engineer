from common.GamblingUtil import GamblingUtil
import json
from common.models.GamblingBet import GamblingBet
from common.KFP_DB import KfpDb
from common.models.GamblingGame import GamblingGame
from common.Util import Util
from discord import Color, Embed, Guild
from discord.ext import commands
from random import randint

class GamblingEmbed():
    def get_betting_embed(bot: commands.Bot, database: KfpDb, game:GamblingGame):
        guild: Guild = bot.get_guild(game.guild_id)
        if guild == None:
            return Embed(title= '錯誤', description= '無法處理的伺服id: {}'.format(game.guild_id))
        embed = Embed()
        embed.colour = Color(randint(0, 0xffffff))
        embed.title = game.name
        _description = ''
        if game.status == Util.GamblingStatus.ready:
            _description += '請各位輸入`/下注` 開始下注!（賭局 ID: {}）。\n'.format(game.id)
        if game.status == Util.GamblingStatus.wait:
            _description += '停止下注!'
        _description += '#目前所有選項的期望賠率都是一樣的，有人有想法可以聯絡<@326752816238428164>\n'
        if game.status == Util.GamblingStatus.ready:
            _description += '<@{}>可以輸入`/賭盤 鎖定`（賭局 ID: {}）來停止下注。'.format(game.creater_id, game.id)
        if game.status == Util.GamblingStatus.wait:
            _description += '<@{}>可以輸入`/賭盤 結束`（賭局 ID: {}）來結算賭盤。'.format(game.creater_id, game.id)
        embed.description = _description
        
        betting_items = json.loads(game.item_list)
        #[第一項總注，第n項總注...,總項總注]
        member_charge_sum = [0] * len(betting_items)
        member_bet = {}
        bets = GamblingUtil.get_bets(game)

        bet : GamblingBet
        for bet in bets:
            member_charge_sum[bet.item_index] += bet.charge
            member_bet[bet.member_id] = member_bet.get(bet.member_id, 0) + bet.charge

        for i, target_name in enumerate(betting_items):
            if member_charge_sum[i] > 0:
                embed.add_field(name= '編號: {} #'.format(i)+target_name, value='賠率: {:.3f}'.format(float((game.pool/member_charge_sum[i]))), inline=False)
            else:
                embed.add_field(name= '編號: {} #'.format(i)+target_name, value='賠率: ?', inline=False)
        embed.add_field(name= '賭局id', value=str(game.id))
        embed.add_field(name= '獎金池', value=str(game.pool*game.base))
        embed.add_field(name= '每注單位', value=str('{}🍗'.format(game.base)))
        embed.add_field(name= '刷新速度', value='5s')
        embed.add_field(name= '狀態', value=Util.GamblingStatus(game.status).name)
        embed.add_field(name= '====我是分隔線====', value='#',inline=False)
        inline_flasg = False
        for member_id in member_bet:
            member = guild.get_member(int(member_id))
            if member == None:
                continue
            value = ''
            for bet_item in member_bet[member_id]:
                if game.status == Util.GamblingStatus.end.value:
                    if bet_item == betting_items[game.winning_index]:
                        value += '{}:得到{}點🍗\n'.format(bet_item, member_bet[member_id][bet_item]/member_charge_sum[game.winning_index]*member_charge_sum[-1]*game.base)
                    else:
                        value += '{}:輸掉{}點🍗拉\n'.format(bet_item, member_bet[member_id][bet_item]*game.base)
                else:
                    value += '{}:{}注\n'.format(bet_item, member_bet[member_id][bet_item])
            embed.add_field(name= member.display_name, value=value[:-1],inline=inline_flasg)
            if not inline_flasg:
                inline_flasg = True
        
        return embed