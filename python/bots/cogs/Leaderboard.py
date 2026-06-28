import discord
from discord import app_commands
from discord.ext import commands

from common.DiscordUtil import DiscordUtil
from common.LeaderboardUtil import LeaderboardUtil


@app_commands.guild_only()
class Leaderboard(commands.GroupCog, group_name="排行榜", group_description="表情符號反應排行榜"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return not interaction.user.bot

    @app_commands.command(name="說明", description="排行榜使用方法")
    @app_commands.checks.cooldown(1, 10.0)
    async def leaderboard_help(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "排行榜使用方法:\n"
            "\t/排行榜 分類列表 顯示目前所有的排行榜名稱\n"
            "\t/排行榜 清空 <排行榜名稱> - 清空排行榜計數 \n"
            "\t/排行榜 清空符號 <排行榜名稱> - 清空排行榜追蹤的符號 \n"
            "\t/排行榜 新增符號 <排行榜名稱> <符號> - 新增追蹤的符號至排行榜裡 \n"
            "\t/排行榜 移除符號 <排行榜名稱> <符號> - 從排行榜移除追蹤的符號 \n"
            "\t/排行榜 符號列表 <排行榜名稱> - 顯示目前排行榜追蹤的符號 \n"
            "\t/排行榜 排名 <排行榜名稱> [上限X] - 顯示前X名排行榜, 預設是10 \n"
            "\t/排行榜 倒數排名 <排行榜名稱> [上限X] - 顯示後X名排行榜, 預設是10 \n"
        )

    @app_commands.command(name="管理說明", description="排行榜管理員使用方法")
    async def show_secret_menu(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "排行榜使用方法:\n"
            "\t/排行榜 新增分類 <排行榜名稱> <符號> - 新增排行榜 並追蹤符號\n"
            "\t/排行榜 移除分類 <排行榜名稱> 移除排行榜 並解除追蹤符號\n"
            "\t/排行榜 分類列表 顯示目前所有的排行榜名稱\n"
            "\t/排行榜 清空 <排行榜名稱> - 清空排行榜計數 \n"
            "\t/排行榜 清空符號 <排行榜名稱> - 清空排行榜計數 \n"
            "\t/排行榜 新增符號 <排行榜名稱> <符號> - 新增追蹤的符號至排行榜裡 \n"
            "\t/排行榜 新增多符號 <排行榜名稱> <符號> ... - 新增追蹤的符號們至排行榜裡 \n"
            "\t/排行榜 移除符號 <排行榜名稱> <符號> - 從排行榜移除追蹤的符號 \n"
            "\t/排行榜 符號列表 <排行榜名稱> - 顯示目前排行榜追蹤的符號 \n"
            "\t/排行榜 排名 <排行榜名稱> [上限X] - 顯示前X名排行榜, 預設是10 \n"
            "\t/排行榜 倒數排名 <排行榜名稱> [上限X] - 顯示後X名排行榜, 預設是10 \n"
        )

    @app_commands.command(name="新增分類", description="新增排行榜並追蹤符號")
    @app_commands.describe(lb_name="排行榜名稱", emoji_str="要追蹤的符號")
    async def add_category(self, interaction: discord.Interaction, lb_name: str, emoji_str: str) -> None:
        if LeaderboardUtil.findLeaderboard(lb_name):
            await interaction.response.send_message(
                f"排行榜'{lb_name}'已經存在了, 你可以使用 新增符號 來修改要追蹤的表符."
            )
            return

        emoji = LeaderboardUtil.findEmoji(emoji_str)
        if not emoji:
            leaderboard = LeaderboardUtil.getOrCreateLeaderboard(lb_name)
            LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
            await interaction.response.send_message(f"新增排行榜'{lb_name}'成功並開始追蹤表符'{emoji_str}'")
        else:
            e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
            await interaction.response.send_message(
                f"符號'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 符號列表 來查看追蹤中的列表."
            )

    @app_commands.command(name="移除分類", description="移除排行榜並解除追蹤符號")
    @app_commands.describe(lb_name="排行榜名稱")
    async def remove_category(self, interaction: discord.Interaction, lb_name: str) -> None:
        if not LeaderboardUtil.findLeaderboard(lb_name):
            await interaction.response.send_message(f"排行榜'{lb_name}'並不存在.")
            return
        LeaderboardUtil.removeCategory(lb_name)
        await interaction.response.send_message(f"排行榜'{lb_name}'已經移除並解除所追蹤的表符.")

    @app_commands.command(name="分類列表", description="顯示目前所有的排行榜名稱")
    async def list_categories(self, interaction: discord.Interaction) -> None:
        leaderboards = LeaderboardUtil.listLeaderboards()
        if not leaderboards:
            await interaction.response.send_message("目前沒有任何排行榜")
            return
        result = "```目前有以下排行榜:\n"
        for i, leaderboard in enumerate(leaderboards):
            result += f"{i + 1}. {leaderboard.name}\n"
        result += "```"
        await interaction.response.send_message(result)

    @app_commands.command(name="清空", description="清空排行榜計數")
    @app_commands.describe(lb_name="排行榜名稱")
    async def clear_records(self, interaction: discord.Interaction, lb_name: str) -> None:
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await interaction.response.send_message(f"排行榜'{lb_name}'不存在, 請輸入正確排行榜名稱")
            return
        LeaderboardUtil.clearRankRecords(leaderboard.name)
        await interaction.response.send_message(f"排行榜'{lb_name}'紀錄清除完畢.")

    @app_commands.command(name="清空符號", description="清空排行榜所有追蹤表符的計數")
    @app_commands.describe(lb_name="排行榜名稱")
    async def clear_emojis(self, interaction: discord.Interaction, lb_name: str) -> None:
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await interaction.response.send_message(f"排行榜'{lb_name}'不存在, 請輸入正確排行榜名稱")
            return
        emojis = LeaderboardUtil.listEmojis(lb_name)
        if not emojis:
            await interaction.response.send_message(f"排行榜'{lb_name}'並沒有追蹤任何表符.")
            return
        for emoji in emojis:
            LeaderboardUtil.setRecord(leaderboard.id, emoji.id, 0)
        await interaction.response.send_message(f"排行榜'{lb_name}'已清理完畢")

    @app_commands.command(name="新增符號", description="新增追蹤的符號至排行榜")
    @app_commands.describe(lb_name="排行榜名稱", emoji_str="符號")
    async def add_emoji(self, interaction: discord.Interaction, lb_name: str, emoji_str: str) -> None:
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await interaction.response.send_message(
                f"排行榜'{lb_name}'並不存在, 請使用 新增分類 建立新排行榜"
            )
            return

        emoji = LeaderboardUtil.findEmoji(emoji_str)
        if not emoji:
            LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
            await interaction.response.send_message(f"增加表符{emoji_str}至排行榜'{lb_name}'成功!")
            return

        e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
        await interaction.response.send_message(
            f"表符'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 符號列表 來查看追蹤中的列表."
        )

    @app_commands.command(name="新增多符號", description="一次新增多個追蹤符號至排行榜")
    @app_commands.describe(
        lb_name="排行榜名稱",
        emoji1="符號（可用空格分隔多個）",
        emoji2="符號",
        emoji3="符號",
    )
    async def add_emojis(
        self,
        interaction: discord.Interaction,
        lb_name: str,
        emoji1: str,
        emoji2: str | None = None,
        emoji3: str | None = None,
    ) -> None:
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await interaction.response.send_message(
                f"排行榜'{lb_name}'並不存在, 請使用 新增分類 建立新排行榜"
            )
            return

        emoji_list: list[str] = []
        for emoji_arg in (emoji1, emoji2, emoji3):
            if emoji_arg:
                emoji_list.extend(emoji_arg.split())

        if not emoji_list:
            await interaction.response.send_message("請至少提供一個符號.")
            return

        responses: list[str] = []
        for emoji_str in emoji_list:
            emoji = LeaderboardUtil.findEmoji(emoji_str)
            if not emoji:
                LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
                responses.append(f"增加表符'{emoji_str}'至排行榜'{lb_name}'成功!")
                continue

            e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
            responses.append(
                f"表符'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 符號列表 來查看追蹤中的列表."
            )

        await interaction.response.send_message("\n".join(responses))

    @app_commands.command(name="移除符號", description="從排行榜移除追蹤的符號")
    @app_commands.describe(lb_name="排行榜名稱", emoji_str="符號")
    async def remove_emoji(self, interaction: discord.Interaction, lb_name: str, emoji_str: str) -> None:
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            await interaction.response.send_message(
                f"排行榜'{lb_name}'並不存在, 請使用 新增分類 建立新排行榜"
            )
            return

        emoji = LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji_str)
        e_lb = LeaderboardUtil.findLeaderboardById(emoji.leaderboard_id)
        if e_lb.id != leaderboard.id:
            await interaction.response.send_message(
                f"表符'{emoji_str}'已經被排行榜'{e_lb.name}'追蹤, 你可以使用 符號列表 來查看追蹤中的列表."
            )
            return

        LeaderboardUtil.removeEmoji(lb_name, emoji_str)
        await interaction.response.send_message(f"移除表符{emoji_str}成功!")

    @app_commands.command(name="符號列表", description="顯示目前排行榜追蹤的符號")
    @app_commands.describe(lb_name="排行榜名稱")
    async def list_emoji(self, interaction: discord.Interaction, lb_name: str) -> None:
        lb = LeaderboardUtil.findLeaderboard(lb_name)
        if not lb:
            await interaction.response.send_message(
                f"排行榜'{lb_name}'並不存在, 請使用 新增分類 建立新排行榜"
            )
            return

        emojis = LeaderboardUtil.listEmojis(lb_name)
        if not emojis:
            await interaction.response.send_message(f"排行榜'{lb_name}'並沒有追蹤任何表符.")
            return

        result = f"'{lb_name}'排行榜正在追蹤以下表符:\n"
        for emoji in emojis:
            result += f"{emoji.emoji}\n"
        await interaction.response.send_message(result)

    @app_commands.command(name="排名", description="顯示前X名排行榜")
    @app_commands.describe(lb_name="排行榜名稱", limit="顯示名次上限")
    async def show_rank(self, interaction: discord.Interaction, lb_name: str, limit: int = 10) -> None:
        ranks = LeaderboardUtil.getRankResult(lb_name)
        if not ranks:
            await interaction.response.send_message(f"'{lb_name}'排行榜沒有資料, 請稍後重試.")
            return

        result = f"```'{lb_name}'排行榜目前順序如下:\n"
        result += await Leaderboard.create_rank_result_string(interaction.guild, ranks, limit, True)
        result += "```"
        await interaction.response.send_message(result)

    @app_commands.command(name="倒數排名", description="顯示後X名排行榜")
    @app_commands.describe(lb_name="排行榜名稱", limit="顯示名次上限")
    async def show_rank_reverse(self, interaction: discord.Interaction, lb_name: str, limit: int = 10) -> None:
        ranks = LeaderboardUtil.getRankResult(lb_name)
        if not ranks:
            await interaction.response.send_message(f"'{lb_name}'排行榜沒有資料, 請稍後重試.")
            return

        result = f"```'{lb_name}'排行榜順序如下:\n"
        result += await Leaderboard.create_rank_result_string(interaction.guild, ranks, limit, False)
        result += "```"
        await interaction.response.send_message(result)

    @staticmethod
    async def create_rank_result_string(
        guild: discord.Guild, ranks: dict, limit: int, reversed: bool
    ) -> str:
        result = ""
        count = 0
        sorted_list = sorted(ranks.items(), key=lambda item: item[1], reverse=reversed)
        for member_id, score in sorted_list:
            if count >= limit:
                break
            member = await DiscordUtil.fetch_guild_member(guild, member_id)
            if member:
                result += f"{member.display_name}: {score}次\n"
                count += 1
        return result

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = "請稍候 {:.1f} 秒後再使用此指令.".format(error.retry_after)
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Leaderboard(client))