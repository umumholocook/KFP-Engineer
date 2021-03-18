# 一些輔助性質的功能
import asyncio
from common.MemberUtil import MemberUtil
from common.models.GamblingBet import GamblingBet
from common.Util import Util
from datetime import datetime
from common.models.GamblingGame import GamblingGame

class GamblingUtil():

    DEFAULT_RATE = 5

    async def create_loop(bot, embed, main_message, ctx, value_type, main_name, embed_index):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        def reaction_check(reaction, user):
            if user == ctx.author and reaction.message == main_message:
                return str(reaction.emoji) == '⭕' or '❌'
            else:
                return False
        flag = True
        while flag:
            wait_msg = await bot.wait_for('message', check=check)
            if value_type == type(int()) and not wait_msg.content.isdigit():
                embed.set_field_at(embed_index,name= '設定{}-輸入的不是數字重新輸入'.format(main_name), value='請直接回覆{}'.format(main_name),inline=False)
                await wait_msg.delete()
                await main_message.edit(embed= embed)
                continue
            elif value_type != type(int()):
                pass
            embed.set_field_at(embed_index, name= '設定{}-確認⭕️取消❌'.format(main_name), value=wait_msg.content, inline=False)
            await wait_msg.delete()
            await main_message.edit(embed= embed)
            await main_message.add_reaction('⭕')
            await main_message.add_reaction('❌')
            try:
                get_reaction = await bot.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            except asyncio.TimeoutError:
                embed.set_field_at(embed_index , name= '設定{}-等待反應超時'.format(main_name), value='error')
                await main_message.clear_reactions()
                await main_message.edit(embed= embed)
                return False
            else:
                if get_reaction[0].emoji == '⭕':
                    embed.set_field_at(embed_index , name= '設定{}-完成'.format(main_name), value=wait_msg.content)
                    flag = False
                elif get_reaction[0].emoji == '❌':
                    embed.set_field_at(embed_index ,name= '設定{}-重新輸入'.format(main_name), value='請直接回覆{}'.format(main_name),inline=False)
                await main_message.clear_reactions()
                await main_message.edit(embed= embed)
        return True

    # 建立新的賭盤
    def create_game(guild_id:int, game_name: str, base: int, options:list, creater_id):
        game = GamblingGame.create(
            name=game_name, 
            guild_id=guild_id, 
            base=base, 
            start=datetime.now(),
            status=Util.GamblingStatus.init,
            pool=0,
            creater_id=creater_id,
            item_list=options)
        game.save()
        return game

    # 取得現在這個群所有的賭盤
    def get_active_games(guild_id:int):
        result = []
        query = GamblingGame.select().where(GamblingGame.guild_id == guild_id, (GamblingGame.status == Util.GamblingStatus.ready) | (GamblingGame.status == Util.GamblingStatus.wait))
        if query.exists():
            game: GamblingGame
            for game in query.iterator():
                result.append(game)
        return result
    
    # 取得現在這個頻道所有的賭盤
    def get_active_game_in_channel(guild_id: int, channel_id: int):
        result = []
        query = GamblingGame.select().where(GamblingGame.guild_id == guild_id, GamblingGame.channel_id == channel_id)
        if query.exists():
            game: GamblingGame
            for game in query.iterator():
                result.append(game)
        return result
    
    # 新增賭注
    def add_bet(game: GamblingGame, user_id: int, amount: int, item_index: int, timestamp=datetime.now()):
        if game.status != Util.GamblingStatus.ready:
            return False
        # 檢查有沒有現存的賭注
        query = GamblingBet.select().where(GamblingBet.member_id == user_id, GamblingBet.game_id == game.id, GamblingBet.item_index == item_index)
        bet: GamblingBet
        if query.exists():
            # 找到現存的賭注　更新此賭注
            bet = query.get()
            bet.charge += amount
        else:
            # 沒有找到賭注的紀錄　新建一個新的
            bet = GamblingBet(member_id = user_id, game_id = game.id, item_index = item_index, charge = amount, create = timestamp)
        bet.save()
        GamblingUtil.add_game_pool_amount(game, amount)
        return True

    # 取得賭盤所有的賭注
    def get_bets(game: GamblingGame):
        result = []
        query = GamblingBet.select().where(GamblingBet.game_id == game.id)
        if query.exists():
            bet: GamblingBet
            for bet in query.iterator():
                result.append(bet)
        return result
    
    # 增加賭池
    def add_game_pool_amount(game:GamblingGame, amount: int):
        game.pool += amount
        game.save()
    
    # 透過賭盤id 獲取賭盤
    def get_game(gambling_id: int):
        query = GamblingGame.select().where(GamblingGame.id == gambling_id)
        if query.exists():
            return query.get()
        return None

    # 更新賭盤狀態
    def update_game_status(game: GamblingGame, status: Util.GamblingStatus, channel_id:int, message_id: int, winning_index = None):
        game.status = status
        game.channel_id = channel_id
        game.message_id = message_id
        if status == Util.GamblingStatus.end:
            game.end = datetime.now()
        if not winning_index:
            game.winning_index = winning_index
        game.save()

    # 目前雞腿匯率
    def get_token_rate():
        current_token = MemberUtil.get_total_token()
        current_coins = MemberUtil.get_total_coin()
        if current_token == 0 or current_coins == 0:
            return GamblingUtil.DEFAULT_RATE
        return max(current_coins // current_token, GamblingUtil.DEFAULT_RATE)
    
    