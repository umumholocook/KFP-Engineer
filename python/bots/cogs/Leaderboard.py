from discord.ext import commands
from common.LeaderboardUtil import LeaderboardUtil
from common.NicknameUtil import NicknameUtil

class Leaderboard(commands.Cog):
    
    @commands.group(name = 'lb', invoke_without_command=True)
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def leaderboard_group(self, ctx:commands.Context):
        if ctx.author.bot:
            return
        await ctx.send(
            "排行榜使用方法:\n" +
            "\t!lb list_category 顯示目前所有的排行榜名稱\n" +
            "\t!lb clear <排行榜名稱> - 清空排行榜計數 \n" +
            "\t!lb clear_emojis <排行榜名稱> - 清空排行榜追蹤的符號 \n" +
            "\t!lb add_emoji <排行榜名稱> <符號> - 新增追蹤的符號至排行榜裡 \n" +
            "\t!lb remove_emoji <排行榜名稱> <符號> - 從排行榜移除追蹤的符號 \n" +
            "\t!lb list_emoji <排行榜名稱> - 顯示目前排行榜追蹤的符號 \n" +
            "\t!lb rank <排行榜名稱> [上限X] - 顯示前X名排行榜, 預設是10 \n" +
            "\t!lb rank_r <排行榜名稱> [上限X] - 顯示後X名排行榜, 預設是10 \n"
            )
    
    @leaderboard_group.command(name = 'secret')
    async def show_secret_menu(self, ctx: commands.Context):
        if ctx.author.bot:
            return
        await ctx.send(
            "排行榜使用方法:\n" +
            "\t!lb add_category <排行榜名稱> <符號> - 新增排行榜 並追蹤符號\n" +
            "\t!lb remove_category <排行榜名稱> 移除排行榜 並解除追蹤符號\n" +
            "\t!lb list_category 顯示目前所有的排行榜名稱\n" +
            "\t!lb clear <排行榜名稱> - 清空排行榜計數 \n" +
            "\t!lb clear_emojis <排行榜名稱> - 清空排行榜計數 \n" +
            "\t!lb add_emoji <排行榜名稱> <符號> - 新增追蹤的符號至排行榜裡 \n" +
            "\t!lb add_emojis <排行榜名稱> <符號> <符號> ... - 新增追蹤的符號們至排行榜裡 \n" +
            "\t!lb remove_emoji <排行榜名稱> <符號> - 從排行榜移除追蹤的符號 \n" +
            "\t!lb list_emoji <排行榜名稱> - 顯示目前排行榜追蹤的符號 \n" +
            "\t!lb rank <排行榜名稱> [上限X] - 顯示前X名排行榜, 預設是10 \n" +
            "\t!lb rank_r <排行榜名稱> [上限X] - 顯示後X名排行榜, 預設是10 \n"
            )

    # 新增排行榜 並追蹤符號
    @leaderboard_group.command(name = 'add_category')
    async def add_category(self, ctx: commands.Context, lb_name: str, emoji_str:str):
        if ctx.author.bot:
            return
        if LeaderboardUtil.findLeaderboard(lb_name):
            await ctx.send(f"排行榜'{lb_name}'已經存在了, 你可以使用 add_emoji 來修改要追蹤的表符.")
            return
        emoji = LeaderboardUtil.findEmoji(emoji_str)

        if not emoji:
            leaderboard = LeaderboardUtil.getOrCreateLeaderboard(lb_name)
            LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
            await ctx.send(f"新增排行榜'{lb_name}'成功並開始追蹤表符'{emoji_str}'")
        else:
            e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
            await ctx.send(f"符號'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 list_emoji 來查看追蹤中的列表.")
    
    # 移除排行榜 並解除追蹤符號
    @leaderboard_group.command(name = 'remove_category')
    async def remove_category(self, ctx: commands.Context, lb_name: str):
        if ctx.author.bot:
            return
        if not LeaderboardUtil.findLeaderboard(lb_name):
            await ctx.send(f"排行榜'{lb_name}'並不存在.")
            return
        LeaderboardUtil.removeCategory(lb_name)
        await ctx.send(f"排行榜'{lb_name}'已經移除並解除所追蹤的表符.")
    
    # 顯示目前所有的排行榜名稱
    @leaderboard_group.command(name = 'list_category')
    async def list_categories(self, ctx: commands.Context):
        if ctx.author.bot:
            return
        leaderboards = LeaderboardUtil.listLeaderboards()
        if not leaderboards:
            await ctx.send("目前沒有任何排行榜")
            return
        result = "```目前有以下排行榜:\n"
        for i, leaderboard in enumerate(leaderboards):
            result += f"{i+1}. {leaderboard.name}\n"
        result += "```"
        await ctx.send(result)

    # 清空排行榜計數
    @leaderboard_group.command(name = 'clear')
    async def clear_records(self, ctx: commands.Context, lb_name: str):
        if ctx.author.bot:
            return
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard :
            await ctx.send(f"排行榜'{lb_name}'不存在, 請輸入正確排行榜名稱")
            return
        LeaderboardUtil.clearRankRecords(leaderboard.name)
        await ctx.send(f"排行榜'{lb_name}'紀錄清除完畢.")
        
    # 移除排行榜所有追蹤表符
    @leaderboard_group.command(name = 'clear_emojis')
    async def clear_emojis(self, ctx: commands.Context, lb_name: str):
        if ctx.author.bot:
            return
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard :
            await ctx.send(f"排行榜'{lb_name}'不存在, 請輸入正確排行榜名稱")
            return
        emojis = LeaderboardUtil.listEmojis(lb_name)
        if not emojis:
            await ctx.send(f"排行榜'{lb_name}'並沒有追蹤任何表符.")
            return
        for emoji in emojis:
            LeaderboardUtil.setRecord(leaderboard.id, emoji.id, 0)
        await ctx.send(f"排行榜'{lb_name}'已清理完畢")
    
    @leaderboard_group.command(name = 'add_emoji')
    async def add_emoji(self, ctx: commands.Context, lb_name: str, emoji_str: str):
        if ctx.author.bot:
            return
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await ctx.send(f"排行榜'{lb_name}'並不存在, 請使用 add_category 建立新排行榜")
            return
        emoji = LeaderboardUtil.findEmoji(emoji_str)

        if not emoji:
            LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
            await ctx.send(f"增加表符{emoji_str}至排行榜'{lb_name}'成功!")
            return

        e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
        await ctx.send(f"表符'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 list_emoji 來查看追蹤中的列表.")
    
    @leaderboard_group.command(name = 'add_emojis')
    async def add_emojis(self, ctx: commands.Context, lb_name: str, *emojis):
        if ctx.author.bot:
            return
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await ctx.send(f"排行榜'{lb_name}'並不存在, 請使用 add_category 建立新排行榜")
            return
        for emoji_str in emojis:
            emoji = LeaderboardUtil.findEmoji(emoji_str)

            if not emoji:
                LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
                await ctx.send(f"增加表符'{emoji_str}'至排行榜'{lb_name}'成功!")
                continue
            
            e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
            await ctx.send(f"表符'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 list_emoji 來查看追蹤中的列表.")
    
    @leaderboard_group.command(name = 'remove_emoji')
    async def remove_emoji(self, ctx: commands.Context, lb_name: str, emoji_str: str):
        if ctx.author.bot:
            return
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await ctx.send(f"排行榜'{lb_name}'並不存在, 請使用 add_category 建立新排行榜")
            return
        emoji = LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
        e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)

        if e_lb.id != leaderboard.id:
            await ctx.send(f"表符'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 list_emoji 來查看追蹤中的列表.")
            return
        
        LeaderboardUtil.removeEmoji(lb_name, emoji_str)
        await ctx.send(f"移除表符{emoji_str}成功!")
    
    # 顯示目前排行榜追蹤的符號
    @leaderboard_group.command(name = 'list_emoji')
    async def list_emoji(self, ctx: commands.Context, lb_name: str):
        if ctx.author.bot:
            return
        lb = LeaderboardUtil.findLeaderboard(lb_name)
        if not lb:
            await ctx.send(f"排行榜'{lb_name}'並不存在, 請使用 add_category 建立新排行榜")
            return
        
        emojis = LeaderboardUtil.listEmojis(lb_name)
        if not emojis:
            await ctx.send(f"排行榜'{lb_name}'並沒有追蹤任何表符.")
            return
        result = f"'{lb_name}'排行榜正在追蹤以下表符:\n"
        for emoji in emojis:
            result += f"{emoji.emoji}\n"
            print(emoji.emoji)
        await ctx.send(result)
    
    @leaderboard_group.command(name = 'rank')
    async def show_rank(self, ctx: commands.Context, lb_name: str, limit: int = 10):
        if ctx.author.bot:
            return
        ranks = LeaderboardUtil.getRankResult(lb_name)
        if not ranks:
            await ctx.send(f"'{lb_name}'排行榜沒有資料, 請稍後重試.")
            return
        
        result = f"```'{lb_name}'排行榜目前順序如下:\n"
        result += Leaderboard.createRankResultString(ctx, ranks, limit, True)
        result += "```"

        await ctx.send(result)
    
    @leaderboard_group.command(name = 'rank_r')
    async def show_rank_reverse(self, ctx: commands.Context, lb_name: str, limit: int = 10):
        if ctx.author.bot:
            return
        ranks = LeaderboardUtil.getRankResult(lb_name)
        if not ranks:
            await ctx.send(f"'{lb_name}'排行榜沒有資料, 請稍後重試.")
            return
        
        result = f"```'{lb_name}'排行榜順序如下:\n"
        result += Leaderboard.createRankResultString(ctx, ranks, limit, False)
        result += "```"

        await ctx.send(result)
        
    def createRankResultString(ctx: commands.Context, ranks: dict, limit: int, reversed: bool):
        result = ""
        count = 0
        sortedList = sorted(ranks.items(), key=lambda item: item[1], reverse=reversed) 
        for k, v in sortedList:
            if count >= limit: break
            member = ctx.guild.get_member(k)
            if member:
                result += f"{member.display_name}: {v}次\n"
                count += 1
        return result


async def setup(client):
    await client.add_cog(Leaderboard(client))