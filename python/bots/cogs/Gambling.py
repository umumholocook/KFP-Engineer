import asyncio
from common.models.GamblingBet import GamblingBet
from ui.gambling.GamblingEmbed import GamblingEmbed
from common.GamblingUtil import GamblingUtil
from time import time
from common.models.Member import Member
from common.models.Channel import Channel
from common.ChannelUtil import ChannelUtil
from common.models.GamblingGame import GamblingGame
from common.KFP_DB import KfpDb
from common.Util import Util
import json
from discord import Guild, Embed, Message, Role
from discord.ext import commands, tasks

class Gambling(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.bot = client
        self.database = KfpDb()
        self.betting_permissions = self.database.load_permissions(Util.ManagementType.Gambling)

    @commands.Cog.listener('on_message')
    async def profile_on_message(self, message:Message):
        if self.database.is_channel_auto_clear(message.guild.id, message.channel.id) and not message.author.bot:
            await message.delete()
    
    @commands.Cog.listener('on_guild_role_delete')
    async def betting_on_guild_role_delete(self, old_role:Role):
        pass
        # new_role = await old_role.guild.create_role(name= '賭盤權限狗(可以自由編輯這個身分組)')
        # self.database.update_permission_role(old_role.id, new_role.id, old_role.guild.id, Util.ManagementType.Gambling)
    
    @commands.Cog.listener('on_guild_join')
    async def betting_guild_join(self, guild:Guild):
        pass
        # role = await guild.create_role(name= '賭盤權限狗(可以自由編輯這個身分組)')
        # self.database.add_permission_role(guild, role, Util.ManagementType.Gambling)

    @commands.command(name = 'cheat', description= 'argv: <@!member_id> token_numbers\n set tokens number that someone owns, this is cheating!')
    async def betting_cheat_command(self, ctx:commands.Context, *argv):
        if ctx.channel == None or ctx.guild == None:
            await ctx.author.send('權限錯誤: 請在伺服器中做設置')
            return
        if len(argv) < 2 or len(argv[0]) < 3 or not argv[0][3:-1].isdigit() or not argv[1].isdigit():
            await ctx.channel.send('參數錯誤: !cheat @成員 🍗量')
            return
        check_role = True
        for member_role in ctx.author.roles:
            if self.database.has_permission(ctx.guild.id, member_role.id, Util.ManagementType.Gambling):
                check_role = False  
        if check_role:
            await ctx.channel.send('權限錯誤: 你沒有使用這個指令的權限')
            return
        if argv[0].startswith('<@!'):
            target_id = argv[0][3:-1]
        elif argv[0].startswith('<@'):
            target_id = argv[0][2:-1]
        else:
            await ctx.channel.send('參數錯誤: !cheat @成員 🍗量')
            return
        target_member = ctx.guild.get_member(int(target_id))
        if target_member == None:
            await ctx.channel.send('權限錯誤: 無法獲得成員，id: {}'.format(argv[0][3:-1]))
            return
        self.database.add_token(target_member.id, int(argv[1]))
        await ctx.channel.send('將成員: {}的🍗量設置為{}。'.format(target_member.display_name, argv[1]))
        await target_member.send('你的🍗量被{}設置為{}'.format(ctx.author.display_name, argv[1]))

    @commands.group(name = 'keep_clear', invoke_without_command = True)
    async def betting_keep_clear_group(self, ctx:commands.Context, *argv):
        if ctx.channel == None:
            await ctx.author.send("請在頻道中設置這個指令")
            return
        if not self.database.has_channel(ctx.guild.id, ctx.channel.id, Util.ChannelType.AUTO_DELETE):
            result = ChannelUtil.setChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.AUTO_DELETE)
            if result:
                await ctx.channel.send('這個頻道將開始自動刪除接下來的所有成員留言')
                self.database.set_ignore_xp_channel(ctx.guild.id, ctx.channel.id)
            else:
                await ctx.channel.send('這個頻道已經開啟自動刪除')
        else:
            await ctx.channel.send('這個頻道已經開啟自動刪除')

    # 取消自動刪除留言功能
    @betting_keep_clear_group.command(name = 'disable')
    async def keep_clear_disable_command(self, ctx:commands.Context, *argv):
        if ctx.channel == None:
            await ctx.author.send("請在頻道中設置這個指令")
            return
        if ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.AUTO_DELETE):
            ChannelUtil.removeChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.AUTO_DELETE)
            await ctx.channel.send('取消這個頻道自動刪除成員留言功能')
            self.database.remove_ignore_xp_channel(ctx.guild.id, ctx.channel.id)
    
        
    # 顯示所有啟動自動刪除留言功能的頻道        
    @betting_keep_clear_group.command(name = 'list')
    async def keep_clear_list_command(self, ctx:commands.Context, *argv):
        if ctx.guild == None:
            await ctx.author.send("請在伺服器中呼叫這個指令")
            return
        result = ''
        autoDeleteList = ChannelUtil.GetChannelWithGuild(ctx.guild.id, Util.ChannelType.AUTO_DELETE)
        channel: Channel
        for channel in autoDeleteList:
            if ctx.uild.get_channel(channel.channel_id) != None:
                result += '<#{}>'.format(channel.channel_id)
        await ctx.channel.send(result)

    # 啟動下注, 格式為 "!bet 加注數量 下注編號 [賭局ID]"
    @commands.command(name = 'bet')
    async def betting_bte_command(self, ctx:commands.Context, *argv):
        guild = ctx.guild
        channel = ctx.channel
        ## 
        if channel == None:
            await ctx.author.send('請到開啟賭牌的頻道下注!!')
            return
        if guild == None:
            await ctx.author.send('無法處理的伺服器!')
            return
        if not self.database.has_channel(guild.id, channel.id, Util.ChannelType.AUTO_DELETE):
            await ctx.message.delete()
        flag = False
        if len(argv) < 2:
            flag = True
        elif not argv[0].isdigit() or not argv[1].isdigit():
            flag = True
        if flag:
            await ctx.author.send('參數錯誤: `!bet 加注數量 下注編號 [賭局ID]`')
            return
        bet_amount = int(argv[0]) # 加注數量
        choice_id = int(argv[1]) # 下注編號

        _bettings = GamblingUtil.get_active_game_in_channel(guild.id, ctx.channel.id)
        ready_games = []
        game: GamblingGame
        for game in _bettings:
            if game.status == Util.GamblingStatus.ready:
                ready_games.append(game)
        if len(ready_games) == 0:
            await ctx.author.send('參數錯誤: 這個頻道沒有開啟的賭局!')
            return
        if len(ready_games) > 1:
            if len(argv) <= 2:
                tem_betting_list = ''
                for game in ready_games:
                    tem_betting_list += '\n賭局名:{}, id: {}'.format(game.name, game.id)
                await ctx.author.send('這個頻道有複數賭局開啟中\n請指定賭局`!bet 下注數 賭局ID`'+tem_betting_list)
                return
            if not argv[2].isdigit():
                await ctx.author.send('參數錯誤: 賭局ID必須是數字')
            betting_id = int(argv[2])
            flag = True
            for game in ready_games:
                if betting_id == game.id:
                    flag = False
                    break
            if flag:
                ctx.author.send('參數錯誤: 這個<#{}>沒有ID為: {}的賭局'.format(ctx.channel.id, betting_id))
            ready_games = game
        elif len(ready_games) == 1:
            ready_games = ready_games[0]
        else:
            await ctx.channel.send('未預期的錯誤: <@!326752816238428164>快修阿!')
            return
        game: GamblingGame = ready_games
        if game.status != Util.GamblingStatus.ready:
            await ctx.author.send('權限錯誤: 現在的賭局狀態為: {}不能下注'.format(Util.GamblingStatus(game.status).name))
            return
        if bet_amount < 1:
            await ctx.author.send('參數錯誤: 下注🍗不能為此數: {}'.format(bet_amount))
            return
        # 所有可下注選項
        betting_item_list = json.load(game.item_list)
        if not choice_id < len(betting_item_list):
            await ctx.author.send('參數錯誤: 不存在編號: {}'.format(choice_id))
            return
        member = self.database.get_member(ctx.author.id)
        if member == None:
            member = self.database.add_member(ctx.author.id)
        require_amount = bet_amount * game.base
        if member.coin < require_amount:
            await ctx.author.send('道德錯誤: 你的🍗不夠啦! ...剩餘{}，下注{}'.format(member.coin, require_amount))
            return
        self.database.add_coin(member, -1 * require_amount)
        GamblingUtil.add_bet(game=game, user_id=member.member_id, amount=require_amount, item_index=choice_id)

        await ctx.author.send('你成功對{} 下注了{}點🍗。...餘額為: {}。'.format(betting_item_list[choice_id], require_amount, member.coin))
        
    @commands.group(name = 'betting', invoke_without_command = True)
    async def betting_command_group(self, ctx:commands.Context, *attr):
        # TODO print help commands
        pass
    # 顯示所有賭盤列表
    @betting_command_group.command(name= 'list')
    async def betting_list_command(self, ctx:commands.Context, *argv):
        guild = ctx.guild
        game_list = GamblingUtil.get_active_games(guild.id)
        if len(game_list) == 0:
            return
        embed = Embed()
        embed.title = '賭盤列表'
        game: GamblingGame
        for game in game_list:
            channel = ctx.channel
            embed.add_field(name=game.name, value= '每注: {}, 獎金池: {}, 狀態: {}\n頻道: <#{}>, 伺服器:{}'.format(game.base, game.pool, game.status.name, channel.id, guild.name), inline=False)            
        await ctx.channel.send(embed= embed)

    @betting_command_group.command(name= '紅包')
    async def betting_red_command(self, ctx:commands.Context, *argv):
        # 輸入參數檢查開始
        if ctx.channel == None:
            await ctx.author.send('權限錯誤: 請在頻道中使用這個指令!')
            return 
        if len(argv) < 2 or len(argv) > 2:
            await ctx.channel.send('參數錯誤: 請使用`!betitng 紅包 🍗數 紅包量`')
            return
        if not argv[0].isdigit() and not argv[1].isdigit():
            await ctx.channel.send('參數錯誤: 請使用`!betitng 紅包 🍗數 紅包量`')
            return
        
        token_num = int(argv[0])
        beg_num = int(argv[1])

        if token_num < 1:
            await ctx.channel.send('參數錯誤: 🍗數必須大於 0`')
            return
        
        if beg_num < 1:
            await ctx.channel.send('參數錯誤: 紅包量必須大於 0`')
            return
        # 輸入參數檢查結束

        member: Member = self.database.get_member(ctx.author.id)
        if member == None:
            member = self.database.add_member(ctx.author.id)
        
        required_token = token_num * beg_num
        if member.token < required_token:
            await ctx.author.send(f"道德錯誤: 同志別裝大款，你只有{member.token}枚🍗。")
        
        # 移除發紅包人的 🍗
        self.database.add_token(member.id, -1 * required_token)

        main_message = await ctx.channel.send("<@{}> 發紅包拉!!限時1分鐘!!!".format(ctx.author.id))
        await main_message.add_reaction('🤑')
        def reaction_check(reaction, user):
            if reaction.message == main_message and not user.bot:
                return str(reaction.emoji) == '🤑'
            else:
                return False
        temp_list = []
        start_time = time.time()
        while time.time() - start_time < 60 and beg_num > 0:
            try:
                reaction = await self.bot.wait_for('reaction_add', timeout=3, check=reaction_check)
            except asyncio.TimeoutError:
                continue
            else:
                if not reaction[1].id in temp_list:
                    temp_list.append(reaction[1].id)
                    member: Member = self.database.get_member(reaction[1].id)
                    if member == None:
                        member = self.database.add_member(reaction[1].id)
                    self.database.add_token(reaction[1].id, token_num)
                    beg_num -= 1
                    await ctx.channel.send('恭喜{}從{}的紅包獲得{}點🍗!'.format(reaction[1].display_name, ctx.author.display_name, token_num))
        if beg_num < 1:
            await main_message.edit(content='紅包搶光拉!')
        else:
            self.database.add_token(ctx.author.id, token_num * beg_num)
            await main_message.edit(content='時間到!')
            await ctx.channel.send('返還{} 給<@{}>。'.format(token_num * beg_num, ctx.author.id))

    @betting_command_group.command(name= 'info')
    async def betting_info_command(self, ctx:commands.Context, *argv):
        member: Member = self.database.get_member(ctx.author.id)
        if member == None:
            member = self.database.add_member(ctx.author.id)
        if ctx.channel == None:
            await ctx.author.send(f"您目前持有硬幣{member.coin}\n持有🍗{member.token}根")
        else:
            await ctx.channel.send(f"您目前持有硬幣{member.coin}\n持有🍗{member.token}根")

    # 創立賭盤
    @betting_command_group.command(name= 'create')
    async def betting_create_command(self, ctx:commands.Context, *argv):
        
        descript_base = '請<@{}>跟著指示完成創建\n'.format(ctx.author.id)
        embed = Embed()
        embed.title = '創建賭盤: 創建者<@!{}>'.format(ctx.author.id)
        embed.description = descript_base
        embed.add_field(name= '設定賭盤名稱', value='請直接回覆賭局名稱',inline=False)
        embed.add_field(name= '設定賭注單位', value='請先回覆賭局名稱',inline=False)
        main_message = await ctx.channel.send(embed= embed)
        def reaction_check(reaction, user):
            if user == ctx.author and reaction.message == main_message:
                return str(reaction.emoji) == '⭕' or '❌'
            else:
                return False
        betting_count = 0
        bet_item_offset = 2

        if not await GamblingUtil.create_loop(embed, main_message, ctx, type(str()), '賭盤名稱', 0):
            return
        embed.set_field_at(1,name= '設定賭注單位', value='請直接回覆每注單位',inline=False)
        await main_message.edit(embed= embed)
        if not await GamblingUtil.create_loop(embed, main_message, ctx, type(int()), '賭注單位', 1):
            return
        add_flag = True
        while add_flag or betting_count < 2:
            embed.add_field(name= '設定賭注項目-第{}項'.format(betting_count), value= '請先回覆賭注項目-第{}項'.format(betting_count), inline=False)
            await main_message.edit(embed= embed)
            if not await GamblingUtil.create_loop(embed, main_message, ctx, type(str()), '賭品-第{}項'.format(betting_count), betting_count+bet_item_offset):
                return    
            if betting_count > 0:
                embed.add_field(name= '完成設定?', value= '完成設定⭕️繼續設定❌', inline=False)
                await main_message.edit(embed= embed)
                await main_message.add_reaction('⭕')
                await main_message.add_reaction('❌')
                try:
                    get_reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=reaction_check)
                except asyncio.TimeoutError:
                    embed.set_field_at(betting_count+bet_item_offset+1 , name= '完成設定?-等待反應超時', value='error')
                    await main_message.clear_reactions()
                    await main_message.edit(embed= embed)
                    return False
                else:
                    if get_reaction[0].emoji == '⭕':
                        tem_list = []
                        for i in embed.fields[2:-1]:
                            tem_list.append(i.value)
                        game: GamblingGame = GamblingUtil.create_game(ctx.guild.id, embed.fields[0].value, int(embed.fields[1].value), tem_list, ctx.author.id)
                        embed.set_field_at(betting_count+bet_item_offset+1 , name= '完成設定!!!', value='設定完成!!!\n請<@{}> 到想要的頻道輸入\n`!betting start {}`\n開啟賭局!'.format(ctx.author.id, game.id), inline=False)
                        add_flag = False
                    else:
                        embed.remove_field(betting_count+bet_item_offset+1)
                    await main_message.clear_reactions()
                    await main_message.edit(embed= embed)

            betting_count+=1

    # 開放賭盤
    @betting_command_group.command(name= 'start')
    async def betting_start_command(self, ctx:commands.Context, *argv):
        if len(argv) != 1 or not argv[0].isdigit():
            await ctx.channel.send('參數錯誤: 請使用`!betitng start 賭局id`')
            return
        game_id = int(argv[0])
        game: GamblingGame = GamblingUtil.get_game(game_id)
        if game == None:
            await ctx.channel.send('參數錯誤: 無法找到id 為:{} 的賭盤。請使用`!betitng list`查詢。'.format(game_id))
            return
        if game.creater_id != ctx.author.id:
            await ctx.channel.send('權限錯誤: 這個賭盤不是你創建的!')
            return
        if game.guild_id != ctx.guild.id:
            await ctx.channel.send('權限錯誤: 這個賭盤不是在這裡創建的，創建的伺服為: {}'.format(self.bot.get_guild(game.guild_id).name))
            return
        if game.status != Util.GamblingStatus.init:
            await ctx.channel.send('權限錯誤: 這個賭盤的狀態為: {}，無法開始。'.format(Util.GamblingStatus(game.status).name))
            return
        embed = GamblingEmbed.get_betting_embed(game)
        msg = await ctx.channel.send(embed= embed)
        await msg.pin()
        GamblingUtil.update_game_status(game, Util.GamblingStatus.ready, ctx.channel.id, msg.id)
    
    @betting_command_group.command(name= 'lock')
    async def betting_lock_command(self, ctx:commands.Context, *argv):
        send_target = None
        if ctx.channel == None:
            send_target = ctx.author
        else:
            send_target = ctx.channel
        if len(argv) != 1 or not argv[0].isdigit():
            await send_target.send('參數錯誤: `!betting lock 賭盤id`')
            return
        game_id = int(argv[0])
        game: GamblingGame = GamblingUtil.get_game(game_id)
        if game == None:
            await send_target.send('參數錯誤: 沒有ID為{}的賭盤'.format(game_id))
            return
        if game.creater_id != ctx.author.id:
            await send_target.send('權限錯誤: 你不是創建這個賭盤的人')
            return
        if game.status != Util.GamblingStatus.ready:
            await send_target.send('權限錯誤: 這個賭盤的狀態為:{}'.format(game.status.name))
            return
        GamblingUtil.update_game_status(game, Util.GamblingStatus.wait)
        await send_target.send('更新賭盤狀態為: {}'.format(Util.GamblingStatus.wait.name))

    @betting_command_group.command(name= 'end')
    async def betting_end_command(self, ctx:commands.Context, *argv):
        if len(argv) != 2:
            await ctx.channel.send('參數錯誤: `!betting lock 勝利編號 賭盤id`')
            return
        if not argv[1].isdigit() or not argv[0].isdigit():
            await ctx.channel.send('參數錯誤: `!betting lock 勝利編號 賭盤id`')
            return
        game_id = int(argv[1])
        option_index = int(argv[0])
        game: GamblingGame = GamblingUtil.get_game(int(argv[1]))
        if not game:
            await ctx.channel.send('參數錯誤: 找不到id 為{}的賭盤'.format(game_id))
            return
        if game.creater_id != ctx.author.id:
            await ctx.channel.send('權限錯誤: 你不是創建這個賭盤的人')
            return
        if game.status != Util.GamblingStatus.wait:
            await ctx.channel.send('權限錯誤: 這個賭盤的狀態為:{}'.format(game.status.name))
            return
        betting_items = json.loads(game.item_list)
        if option_index < 0 or option_index > len(betting_items):
            await ctx.channel.send(f'參數錯誤: `勝利編號 {option_index} 為無效編號`')
            return

        #[第一項總注，第n項總注...,總項總注]
        member_charge_sum = [0] * len(betting_items)
        member_bet = {}
        winning_item = betting_items[option_index]
        bets = GamblingUtil.get_bets(game)
        bet:GamblingBet
        for bet in bets:
            member_charge_sum[bet.item_index] += bet.charge
            member_bet[bet.member_id] = member_bet.get(bet.member_id, 0) + bet.charge

        for member_id in member_bet:
            member: Member = self.database.get_member(member_id)
            if member == None:
                continue
            token_spent = 0
            if member_bet[member_id].get(winning_item, 0) != 0:
                token_spent = member_bet[member_id][winning_item]
            coin_won = 0
            winning_sum = member_charge_sum[option_index] 
            if winning_sum != 0:
                coin_won = int(token_spent/winning_sum * game.base * game.pool)
            user = await self.bot.fetch_user(member_id)
            if user == None:
                await ctx.channel.send('無法找到該id的用戶: {}，跳過!')
                continue
            self.database.add_token(member_id, coin_won)
            member = self.database.get_member(member_id)
            await user.send('恭喜獲得{}點🍗, ...結餘:{}'.format(coin_won, member.coin))
        
        GamblingUtil.update_game_status(game, Util.GamblingStatus.end, winning_index=option_index)
        
        channel = await self.bot.fetch_channel(game.channel_id)
        if channel != None:
            msg = await channel.fetch_message(game.message_id)
            await msg.edit(embed = GamblingEmbed.get_betting_embed(self.bot, self.database, game))
            if msg.pinned:
                await msg.unpin()
        await ctx.channel.send('結算成功')

    @tasks.loop(seconds=5.0)
    async def refresh_betting_message(self):
        for guild in self.bot.guilds:
            games = GamblingUtil.get_active_games(guild.id)
            game: GamblingGame
            for game in games:
                channel = game.guild_id
                massage = await channel.fetch_message(game.message_id)
                embed = self.get_betting_embed(game)
                await massage.edit(embed= embed)
        
    # 查詢兌換率
    @betting_command_group.command(name= 'rate')
    async def betting_exchange_rate_command(self, ctx:commands.Context, *argv):
        exchange_rate = GamblingUtil.get_token_rate()
        await ctx.channel.send(f"目前🍗兌換率為 {exchange_rate} 硬幣:1隻🍗")

    # 兌換🍗
    @betting_command_group.command(name= 'exchange')
    async def betting_exchange_command(self, ctx:commands.Context, *argv):
        exchange_rate = GamblingUtil.get_token_rate()
        if len(argv) != 1:
            await ctx.channel.send('參數錯誤: 請使用`!betitng exchange 🍗數量`')
            return
        if not argv[0].isdigit():
            await ctx.channel.send('參數錯誤: 🍗數量必須為數字')
            return
        desired_token = int(argv[0])
        if desired_token < 1:
            await ctx.channel.send('參數錯誤: 🍗數量不能低於1')
            return

        member: Member = self.database.get_member(ctx.author.id)
        if member == None:
            member = self.database.add_member(ctx.author.id)

        required_coin = exchange_rate * desired_token
        if member.coin < required_coin:
            await ctx.channel.send(f'參數錯誤: 您目前手持硬幣數量不夠 目前 {exchange_rate}硬幣兌換1🍗\n目前您擁有硬幣{member.coin}, 小於交換所需量 {required_coin}')
            return
        
        self.database.add_coin(member.member_id, -1 * required_coin)
        self.database.add_token(member.member_id, desired_token)
        member: Member = self.database.get_member(ctx.author.id)
        msg = "```兌換完成! 兌換明細如下:\n"
        msg+=f"本次兌換匯率: {exchange_rate}\n"
        msg+=f"本次兌換消耗硬幣: {required_coin}\n"
        msg+=f"本次兌換獲得🍗: {desired_token}根\n"
        msg+=f"目前持有硬幣: {member.coin}\n"
        msg+=f"目前持有🍗: {member.token}根\n"
        msg+= "```"
        await ctx.channel.send(msg)
    
    # 重置所有人
    @betting_command_group.command(name = 'reset_everyone')
    async def reset_everyone_command(self, ctx:commands.Context, *argv):
        self.database.reset_everyone_token()

def setup(client):
    client.add_cog(Gambling(client))