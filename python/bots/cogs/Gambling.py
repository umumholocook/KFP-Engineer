from common.models.GamblingGame import GamblingGame
from common.KFP_DB import KfpDb
from common.Util import Util
import json
from discord import Message, Embed
from discord.ext import commands, tasks

keep_clear_list = None
class Gambling(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.bot = client
        self.database = KfpDb()

    @commands.Cog.listener('on_message')
    async def profile_on_message(self, message:Message):
        if message.channel.id in keep_clear_list and not message.author.bot:
            await message.delete()
    
    @commands.group(name = 'keep_clear', invoke_without_command = True)
    async def betting_keep_clear_group(self, ctx:commands.Context, *argv):
        if ctx.channel == None:
            await ctx.author.send("請在頻道中設置這個指令")
            return
        if not ctx.channel.id in keep_clear_list:
            keep_clear_list.append(ctx.channel.id)
            with open('./clear_channel_list.json', mode='w', encoding='utf-8') as fp:
                json.dump(keep_clear_list, fp)
                fp.close()
            await ctx.channel.send('這個頻道將開始自動刪除接下來的所有成員留言')
            self.database.set_ignore_xp_channel(ctx.guild.id, ctx.channel.id)

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
            if member_role.id in betting_permissions:
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

    @commands.group(name = 'betting', invoke_without_command = True)
    async def betting_command_group(self, ctx:commands.Context, *attr):
        pass

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