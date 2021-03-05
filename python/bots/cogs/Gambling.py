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
        self.betting_permissions = self.database.load_permissions()

    @commands.Cog.listener('on_message')
    async def profile_on_message(self, message:Message):
        if message.channel.id in keep_clear_list and not message.author.bot:
            await message.delete()
    
    @commands.Cog.listener('on_guild_role_delete')
    async def betting_on_guild_role_delete(self, old_role:Role):
        new_role = await old_role.guild.create_role(name= '賭盤權限狗(可以自由編輯這個身分組)')
        self.database.update_permission_role(old_role.id, new_role.id, old_role.guild.id, Util.RoleType.Gambling)
    
    @commands.Cog.listener('on_guild_join')
    async def betting_guild_join(self, guild:Guild):
        role = await guild.create_role(name= '賭盤權限狗(可以自由編輯這個身分組)')
        self.database.add_permission_role(guild, role, Util.RoleType.Gambling)

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
            if self.database.has_permission(ctx.guild.id, member_role.id, Util.RoleType.Gambling):
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
        
        if not self.database.has_member(target_member.id):
            self.database.add_member(target_member.id)
        self.database.get_member(target_member.id)
        self.database.update_token(target_member.id, int(argv[1]))

        await ctx.channel.send('將成員: {}的🍗量設置為{}。'.format(target_member.display_name, argv[1]))
        await target_member.send('你的🍗量被{}設置為{}'.format(ctx.author.display_name, argv[1]))

    @commands.group(name = 'keep_clear', invoke_without_command = True)
    async def betting_keep_clear_group(self, ctx:commands.Context, *argv):
        if ctx.channel == None:
            await ctx.author.send("請在頻道中設置這個指令")
            return
        if not self.database.has_channel(ctx.guild.id, ctx.channel.id, Util.ChannelType.AUTO_DELETE):
            result = self.database.add_channel(ctx.guild.id, ctx.channel.id, Util.ChannelType.AUTO_DELETE)
            if result:
                await ctx.channel.send('這個頻道將開始自動刪除接下來的所有成員留言')
                self.database.set_ignore_xp_channel(ctx.guild.id, ctx.channel.id)
            else:
                await ctx.channel.send('這個頻道已經開啟自動刪除')

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

        _bettings = self.database.get_active_betting_list_in_channel(guild.id, ctx.channel.id)
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
        self.database.update_coin(member, -1 * require_amount)
        self.database.add_bet(game=game, user_id=member.member_id, amount=require_amount, item_index=choice_id)
        self.database.add_game_pool_amount(game, bet_amount)

        await ctx.author.send('你成功對{} 下注了{}點🍗。...餘額為: {}。'.format(betting_item_list[choice_id], require_amount, member.coin))
        
    @commands.group(name = 'betting', invoke_without_command = True)
    async def betting_command_group(self, ctx:commands.Context, *attr):
        pass
    
    # 取消自動刪除留言功能
    @betting_keep_clear_group.command(name = 'disable')
    async def keep_clear_disable_command(self, ctx:commands.Context, *argv):
        if ctx.channel == None:
            await ctx.author.send("請在頻道中設置這個指令")
            return
        if ctx.channel.id in keep_clear_list:
            keep_clear_list.pop(keep_clear_list.index(ctx.channel.id))
            with open('./clear_channel_list.json', mode='w', encoding='utf-8') as fp:
                json.dump(keep_clear_list, fp)
                fp.close()
            await ctx.channel.send('取消這個頻道自動刪除成員留言功能')
            self.database.remove_ignore_xp_channel(ctx.guild.id, ctx.channel.id)
    
    # 顯示所有啟動自動刪除留言功能的頻道
    @betting_keep_clear_group.command(name = 'list')
    async def keep_clear_list_command(self, ctx:commands.Context, *argv):
        if ctx.guild == None:
            await ctx.author.send("請在伺服器中呼叫這個指令")
            return
        result = ''
        for channel_id in keep_clear_list:
            if ctx.guild.get_channel(channel_id) != None:
                result += '<#{}>'.format(channel_id)
        await ctx.channel.send(result)

    # 顯示所有賭盤列表
    @betting_command_group.command(name= 'list')
    async def betting_list_command(self, ctx, *argv):
        guild = ctx.guild
        betting_list = self.database.get_active_betting_list(guild.id)
        if len(betting_list) == 0:
            return
        embed = Embed()
        embed.title = '賭盤列表'
        game: GamblingGame
        for game in betting_list:
            guild = self.bot.get_guild(game.guild_id)
            embed.add_field(name= game.name, 
            value= '每注: {}, 獎金池: {}, 狀態: {}\n頻道: <#{}>, 伺服器:{}'.format(game.base, game.pool, game.status, game.channel_id, guild.name), inline=False)
        await ctx.channel.send(embed= embed)

    # 開放賭盤
    @betting_command_group.command(name= 'start')
    async def betting_start_command(self, ctx:commands.Context, *argv):
        if len(argv) != 1 or not argv[0].isdigit():
            await ctx.channel.send('參數錯誤: 請使用`!betitng start 賭局id`')
            return
        game_id = int(argv[0])
        game: GamblingGame = self.database.get_gambling_game(game_id)
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
        embed = self.get_betting_embed(game)
        msg = await ctx.channel.send(embed= embed)
        await msg.pin()
        self.database.update_gambling_game(game, Util.GamblingStatus.ready, ctx.channel.id, msg.id)
    
    @tasks.loop(seconds=5.0)
    async def refresh_betting_message(self):
        for guild in self.bot.guilds:
            games = self.database.get_active_betting_list(guild.id)
            game: GamblingGame
            for game in games:
                channel = game.guild_id
                massage = await channel.fetch_message(game.message_id)
                embed = self.get_betting_embed(game)
                await massage.edit(embed= embed)
        
def setup(client):
    client.add_cog(Gambling(client))