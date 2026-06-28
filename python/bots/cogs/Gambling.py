import asyncio

import discord
from discord.channel import DMChannel
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
from discord import Guild, Embed, Message, Role, app_commands
from discord.ext import commands, tasks


class Gambling(commands.Cog):
    keep_clear_group = app_commands.Group(name="自動清除", description="自動清除頻道留言設定")
    betting_group = app_commands.Group(name="賭盤", description="賭盤管理")

    def __init__(self, client: commands.Bot):
        self.bot = client
        self.database = KfpDb()
        self.betting_permissions = self.database.load_permissions(Util.ManagementType.Gambling)

    def _has_gambling_permission(self, interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        member = interaction.user
        if not isinstance(member, discord.Member):
            return False
        for member_role in member.roles:
            if self.database.has_permission(
                interaction.guild.id, member_role.id, Util.ManagementType.Gambling
            ):
                return True
        return False

    @commands.Cog.listener("on_message")
    async def profile_on_message(self, message: Message):
        if isinstance(message.channel, DMChannel):
            return
        if self.database.is_channel_auto_clear(message.guild.id, message.channel.id) and not message.author.bot:
            await message.delete()

    @commands.Cog.listener("on_guild_role_delete")
    async def betting_on_guild_role_delete(self, old_role: Role):
        pass

    @commands.Cog.listener("on_guild_join")
    async def betting_guild_join(self, guild: Guild):
        pass

    @app_commands.command(name="作弊", description="設置成員的雞腿數量（賭盤權限專用）")
    @app_commands.describe(member="目標成員", token_amount="雞腿數量")
    @app_commands.guild_only()
    async def betting_cheat_command(
        self, interaction: discord.Interaction, member: discord.Member, token_amount: int
    ):
        if not self._has_gambling_permission(interaction):
            await interaction.response.send_message("權限錯誤: 你沒有使用這個指令的權限")
            return
        self.database.add_token(member.id, token_amount)
        await interaction.response.send_message(
            f"將成員: {member.display_name}的🍗量設置為{token_amount}。"
        )
        try:
            await member.send(f"你的🍗量被{interaction.user.display_name}設置為{token_amount}")
        except discord.HTTPException:
            pass

    @keep_clear_group.command(name="啟用", description="啟用此頻道自動刪除成員留言")
    @app_commands.guild_only()
    async def keep_clear_enable_command(self, interaction: discord.Interaction):
        if not self.database.has_channel(
            interaction.guild.id, interaction.channel.id, Util.ChannelType.AUTO_DELETE
        ):
            result = ChannelUtil.setChannel(
                interaction.guild.id, interaction.channel.id, Util.ChannelType.AUTO_DELETE
            )
            if result:
                await interaction.response.send_message("這個頻道將開始自動刪除接下來的所有成員留言")
                self.database.set_ignore_xp_channel(interaction.guild.id, interaction.channel.id)
            else:
                await interaction.response.send_message("這個頻道已經開啟自動刪除")
        else:
            await interaction.response.send_message("這個頻道已經開啟自動刪除")

    @keep_clear_group.command(name="停用", description="停用此頻道自動刪除成員留言")
    @app_commands.guild_only()
    async def keep_clear_disable_command(self, interaction: discord.Interaction):
        if ChannelUtil.hasChannel(
            interaction.guild.id, interaction.channel.id, Util.ChannelType.AUTO_DELETE
        ):
            ChannelUtil.removeChannel(
                interaction.guild.id, interaction.channel.id, Util.ChannelType.AUTO_DELETE
            )
            await interaction.response.send_message("取消這個頻道自動刪除成員留言功能")
            self.database.remove_ignore_xp_channel(interaction.guild.id, interaction.channel.id)
        else:
            await interaction.response.send_message("這個頻道尚未啟用自動刪除")

    @keep_clear_group.command(name="列表", description="顯示所有啟用自動刪除的頻道")
    @app_commands.guild_only()
    async def keep_clear_list_command(self, interaction: discord.Interaction):
        result = ""
        auto_delete_list = ChannelUtil.GetChannelWithGuild(
            interaction.guild.id, Util.ChannelType.AUTO_DELETE
        )
        channel: Channel
        for channel in auto_delete_list:
            if interaction.guild.get_channel(channel.channel_id) is not None:
                result += "<#{}>".format(channel.channel_id)
        await interaction.response.send_message(result or "目前沒有啟用自動刪除的頻道")

    @app_commands.command(name="下注", description="對開啟中的賭局下注")
    @app_commands.describe(amount="加注數量", choice_id="下注編號", game_id="賭局 ID（多個賭局時必填）")
    @app_commands.guild_only()
    async def betting_bet_command(
        self,
        interaction: discord.Interaction,
        amount: int,
        choice_id: int,
        game_id: int = None,
    ):
        guild = interaction.guild
        channel = interaction.channel

        _bettings = GamblingUtil.get_active_game_in_channel(guild.id, channel.id)
        ready_games = []
        game: GamblingGame
        for game in _bettings:
            if game.status == Util.GamblingStatus.ready:
                ready_games.append(game)
        if len(ready_games) == 0:
            await interaction.response.send_message(
                "參數錯誤: 這個頻道沒有開啟的賭局!", ephemeral=True
            )
            return
        if len(ready_games) > 1:
            if game_id is None:
                tem_betting_list = ""
                for ready_game in ready_games:
                    tem_betting_list += "\n賭局名:{}, id: {}".format(ready_game.name, ready_game.id)
                await interaction.response.send_message(
                    "這個頻道有複數賭局開啟中\n請指定賭局`/下注 下注數 下注編號 賭局ID`" + tem_betting_list,
                    ephemeral=True,
                )
                return
            selected_game = None
            for ready_game in ready_games:
                if game_id == ready_game.id:
                    selected_game = ready_game
                    break
            if selected_game is None:
                await interaction.response.send_message(
                    "參數錯誤: 這個<#{}>沒有ID為: {}的賭局".format(channel.id, game_id),
                    ephemeral=True,
                )
                return
            ready_games = selected_game
        elif len(ready_games) == 1:
            ready_games = ready_games[0]
        else:
            await interaction.response.send_message(
                "未預期的錯誤: <@!326752816238428164>快修阿!", ephemeral=True
            )
            return

        game: GamblingGame = ready_games
        if game.status != Util.GamblingStatus.ready:
            await interaction.response.send_message(
                "權限錯誤: 現在的賭局狀態為: {}不能下注".format(
                    Util.GamblingStatus(game.status).name
                ),
                ephemeral=True,
            )
            return
        if amount < 1:
            await interaction.response.send_message(
                "參數錯誤: 下注🍗不能為此數: {}".format(amount), ephemeral=True
            )
            return

        betting_item_list = json.loads(game.item_list)
        if choice_id >= len(betting_item_list):
            await interaction.response.send_message(
                "參數錯誤: 不存在編號: {}".format(choice_id), ephemeral=True
            )
            return

        member = self.database.get_member(interaction.user.id)
        if member is None:
            member = self.database.add_member(interaction.user.id)
        require_amount = amount * game.base
        if member.coin < require_amount:
            await interaction.response.send_message(
                "道德錯誤: 你的🍗不夠啦! ...剩餘{}，下注{}".format(member.coin, require_amount),
                ephemeral=True,
            )
            return

        self.database.add_coin(member, -1 * require_amount)
        GamblingUtil.add_bet(
            game=game, user_id=member.member_id, amount=require_amount, item_index=choice_id
        )

        await interaction.response.send_message(
            "你成功對{} 下注了{}點🍗。...餘額為: {}。".format(
                betting_item_list[choice_id], require_amount, member.coin
            ),
            ephemeral=True,
        )

    @betting_group.command(name="列表", description="顯示所有賭盤列表")
    @app_commands.guild_only()
    async def betting_list_command(self, interaction: discord.Interaction):
        guild = interaction.guild
        game_list = GamblingUtil.get_active_games(guild.id)
        if len(game_list) == 0:
            await interaction.response.send_message("目前沒有進行中的賭盤")
            return
        embed = Embed()
        embed.title = "賭盤列表"
        game: GamblingGame
        for game in game_list:
            channel = interaction.channel
            embed.add_field(
                name=game.name,
                value="每注: {}, 獎金池: {}, 狀態: {}\n頻道: <#{}>, 伺服器:{}".format(
                    game.base, game.pool, game.status.name, channel.id, guild.name
                ),
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @betting_group.command(name="紅包", description="發送限時紅包")
    @app_commands.describe(token_num="每個紅包的雞腿數", beg_num="紅包數量")
    @app_commands.guild_only()
    async def betting_red_command(
        self, interaction: discord.Interaction, token_num: int, beg_num: int
    ):
        if token_num < 1:
            await interaction.response.send_message("參數錯誤: 🍗數必須大於 0")
            return

        if beg_num < 1:
            await interaction.response.send_message("參數錯誤: 紅包量必須大於 0")
            return

        member: Member = self.database.get_member(interaction.user.id)
        if member is None:
            member = self.database.add_member(interaction.user.id)

        required_token = token_num * beg_num
        if member.token < required_token:
            await interaction.response.send_message(
                f"道德錯誤: 同志別裝大款，你只有{member.token}枚🍗。", ephemeral=True
            )
            return

        self.database.add_token(member.id, -1 * required_token)

        await interaction.response.defer()
        main_message = await interaction.followup.send(
            "<@{}> 發紅包拉!!限時1分鐘!!!".format(interaction.user.id), wait=True
        )
        await main_message.add_reaction("🤑")

        def reaction_check(reaction, user):
            if reaction.message == main_message and not user.bot:
                return str(reaction.emoji) == "🤑"
            else:
                return False

        temp_list = []
        start_time = time.time()
        while time.time() - start_time < 60 and beg_num > 0:
            try:
                reaction = await self.bot.wait_for("reaction_add", timeout=3, check=reaction_check)
            except asyncio.TimeoutError:
                continue
            else:
                if reaction[1].id not in temp_list:
                    temp_list.append(reaction[1].id)
                    red_member: Member = self.database.get_member(reaction[1].id)
                    if red_member is None:
                        red_member = self.database.add_member(reaction[1].id)
                    self.database.add_token(reaction[1].id, token_num)
                    beg_num -= 1
                    await interaction.followup.send(
                        "恭喜{}從{}的紅包獲得{}點🍗!".format(
                            reaction[1].display_name, interaction.user.display_name, token_num
                        )
                    )
        if beg_num < 1:
            await main_message.edit(content="紅包搶光拉!")
        else:
            self.database.add_token(interaction.user.id, token_num * beg_num)
            await main_message.edit(content="時間到!")
            await interaction.followup.send(
                "返還{} 給<@{}>。".format(token_num * beg_num, interaction.user.id)
            )

    @betting_group.command(name="資訊", description="查詢目前持有的硬幣與雞腿")
    async def betting_info_command(self, interaction: discord.Interaction):
        member: Member = self.database.get_member(interaction.user.id)
        if member is None:
            member = self.database.add_member(interaction.user.id)
        await interaction.response.send_message(
            f"您目前持有硬幣{member.coin}\n持有🍗{member.token}根", ephemeral=True
        )

    @betting_group.command(name="建立", description="建立新賭盤")
    @app_commands.guild_only()
    async def betting_create_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        descript_base = "請<@{}>跟著指示完成創建\n".format(interaction.user.id)
        embed = Embed()
        embed.title = "創建賭盤: 創建者<@!{}>".format(interaction.user.id)
        embed.description = descript_base
        embed.add_field(name="設定賭盤名稱", value="請直接回覆賭局名稱", inline=False)
        embed.add_field(name="設定賭注單位", value="請先回覆賭局名稱", inline=False)
        main_message = await interaction.followup.send(embed=embed, wait=True)

        def reaction_check(reaction, user):
            if user == interaction.user and reaction.message == main_message:
                return str(reaction.emoji) == "⭕" or str(reaction.emoji) == "❌"
            else:
                return False

        betting_count = 0
        bet_item_offset = 2

        if not await GamblingUtil.create_loop(
            self.bot,
            embed,
            main_message,
            interaction.user,
            interaction.channel,
            type(str()),
            "賭盤名稱",
            0,
        ):
            return
        embed.set_field_at(1, name="設定賭注單位", value="請直接回覆每注單位", inline=False)
        await main_message.edit(embed=embed)
        if not await GamblingUtil.create_loop(
            self.bot,
            embed,
            main_message,
            interaction.user,
            interaction.channel,
            type(int()),
            "賭注單位",
            1,
        ):
            return
        add_flag = True
        while add_flag or betting_count < 2:
            embed.add_field(
                name="設定賭注項目-第{}項".format(betting_count),
                value="請先回覆賭注項目-第{}項".format(betting_count),
                inline=False,
            )
            await main_message.edit(embed=embed)
            if not await GamblingUtil.create_loop(
                self.bot,
                embed,
                main_message,
                interaction.user,
                interaction.channel,
                type(str()),
                "賭品-第{}項".format(betting_count),
                betting_count + bet_item_offset,
            ):
                return
            if betting_count > 0:
                embed.add_field(name="完成設定?", value="完成設定⭕️繼續設定❌", inline=False)
                await main_message.edit(embed=embed)
                await main_message.add_reaction("⭕")
                await main_message.add_reaction("❌")
                try:
                    get_reaction = await self.bot.wait_for(
                        "reaction_add", timeout=30.0, check=reaction_check
                    )
                except asyncio.TimeoutError:
                    embed.set_field_at(
                        betting_count + bet_item_offset + 1,
                        name="完成設定?-等待反應超時",
                        value="error",
                    )
                    await main_message.clear_reactions()
                    await main_message.edit(embed=embed)
                    return
                else:
                    if get_reaction[0].emoji == "⭕":
                        tem_list = []
                        for i in embed.fields[2:-1]:
                            tem_list.append(i.value)
                        game: GamblingGame = GamblingUtil.create_game(
                            interaction.guild.id,
                            embed.fields[0].value,
                            int(embed.fields[1].value),
                            tem_list,
                            interaction.user.id,
                        )
                        embed.set_field_at(
                            betting_count + bet_item_offset + 1,
                            name="完成設定!!!",
                            value="設定完成!!!\n請<@{}> 到想要的頻道輸入\n`/賭盤 開始 {}`\n開啟賭局!".format(
                                interaction.user.id, game.id
                            ),
                            inline=False,
                        )
                        add_flag = False
                    else:
                        embed.remove_field(betting_count + bet_item_offset + 1)
                    await main_message.clear_reactions()
                    await main_message.edit(embed=embed)

            betting_count += 1

    @betting_group.command(name="開始", description="開放賭盤")
    @app_commands.describe(game_id="賭局 ID")
    @app_commands.guild_only()
    async def betting_start_command(self, interaction: discord.Interaction, game_id: int):
        game: GamblingGame = GamblingUtil.get_game(game_id)
        if game is None:
            await interaction.response.send_message(
                "參數錯誤: 無法找到id 為:{} 的賭盤。請使用`/賭盤 列表`查詢。".format(game_id)
            )
            return
        if game.creater_id != interaction.user.id:
            await interaction.response.send_message("權限錯誤: 這個賭盤不是你創建的!")
            return
        if game.guild_id != interaction.guild.id:
            guild = self.bot.get_guild(game.guild_id)
            guild_name = guild.name if guild else str(game.guild_id)
            await interaction.response.send_message(
                "權限錯誤: 這個賭盤不是在這裡創建的，創建的伺服為: {}".format(guild_name)
            )
            return
        if game.status != Util.GamblingStatus.init:
            await interaction.response.send_message(
                "權限錯誤: 這個賭盤的狀態為: {}，無法開始。".format(
                    Util.GamblingStatus(game.status).name
                )
            )
            return
        embed = GamblingEmbed.get_betting_embed(game)
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.pin()
        GamblingUtil.update_game_status(
            game, Util.GamblingStatus.ready, interaction.channel.id, msg.id
        )

    @betting_group.command(name="鎖定", description="鎖定賭盤停止下注")
    @app_commands.describe(game_id="賭局 ID")
    async def betting_lock_command(self, interaction: discord.Interaction, game_id: int):
        game: GamblingGame = GamblingUtil.get_game(game_id)
        if game is None:
            await interaction.response.send_message("參數錯誤: 沒有ID為{}的賭盤".format(game_id))
            return
        if game.creater_id != interaction.user.id:
            await interaction.response.send_message("權限錯誤: 你不是創建這個賭盤的人")
            return
        if game.status != Util.GamblingStatus.ready:
            await interaction.response.send_message(
                "權限錯誤: 這個賭盤的狀態為:{}".format(game.status.name)
            )
            return
        GamblingUtil.update_game_status(
            game, Util.GamblingStatus.wait, game.channel_id, game.message_id
        )
        await interaction.response.send_message(
            "更新賭盤狀態為: {}".format(Util.GamblingStatus.wait.name)
        )

    @betting_group.command(name="結束", description="結束賭盤並結算")
    @app_commands.describe(option_index="勝利編號", game_id="賭局 ID")
    @app_commands.guild_only()
    async def betting_end_command(
        self, interaction: discord.Interaction, option_index: int, game_id: int
    ):
        await interaction.response.defer()
        game: GamblingGame = GamblingUtil.get_game(game_id)
        if not game:
            await interaction.followup.send("參數錯誤: 找不到id 為{}的賭盤".format(game_id))
            return
        if game.creater_id != interaction.user.id:
            await interaction.followup.send("權限錯誤: 你不是創建這個賭盤的人")
            return
        if game.status != Util.GamblingStatus.wait:
            await interaction.followup.send(
                "權限錯誤: 這個賭盤的狀態為:{}".format(game.status.name)
            )
            return
        betting_items = json.loads(game.item_list)
        if option_index < 0 or option_index >= len(betting_items):
            await interaction.followup.send(
                f"參數錯誤: `勝利編號 {option_index} 為無效編號`"
            )
            return

        member_charge_sum = [0] * len(betting_items)
        member_bet = {}
        winning_item = betting_items[option_index]
        bets = GamblingUtil.get_bets(game)
        bet: GamblingBet
        for bet in bets:
            member_charge_sum[bet.item_index] += bet.charge
            member_bet[bet.member_id] = member_bet.get(bet.member_id, 0) + bet.charge

        for member_id in member_bet:
            member: Member = self.database.get_member(member_id)
            if member is None:
                continue
            token_spent = 0
            if member_bet[member_id].get(winning_item, 0) != 0:
                token_spent = member_bet[member_id][winning_item]
            coin_won = 0
            winning_sum = member_charge_sum[option_index]
            if winning_sum != 0:
                coin_won = int(token_spent / winning_sum * game.base * game.pool)
            user = await self.bot.fetch_user(member_id)
            if user is None:
                await interaction.followup.send("無法找到該id的用戶: {}，跳過!")
                continue
            self.database.add_token(member_id, coin_won)
            member = self.database.get_member(member_id)
            try:
                await user.send("恭喜獲得{}點🍗, ...結餘:{}".format(coin_won, member.coin))
            except discord.HTTPException:
                pass

        GamblingUtil.update_game_status(
            game,
            Util.GamblingStatus.end,
            game.channel_id,
            game.message_id,
            winning_index=option_index,
        )

        channel = await self.bot.fetch_channel(game.channel_id)
        if channel is not None:
            msg = await channel.fetch_message(game.message_id)
            await msg.edit(embed=GamblingEmbed.get_betting_embed(self.bot, self.database, game))
            if msg.pinned:
                await msg.unpin()
        await interaction.followup.send("結算成功")

    @tasks.loop(seconds=5.0)
    async def refresh_betting_message(self):
        for guild in self.bot.guilds:
            games = GamblingUtil.get_active_games(guild.id)
            for game in games:
                if not game.channel_id or not game.message_id:
                    continue
                channel = await self.bot.fetch_channel(game.channel_id)
                if channel is None:
                    continue
                try:
                    message = await channel.fetch_message(game.message_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    continue
                embed = GamblingEmbed.get_betting_embed(self.bot, self.database, game)
                await message.edit(embed=embed)

    @betting_group.command(name="匯率", description="查詢雞腿兌換率")
    async def betting_exchange_rate_command(self, interaction: discord.Interaction):
        exchange_rate = GamblingUtil.get_token_rate()
        await interaction.response.send_message(f"目前🍗兌換率為 {exchange_rate} 硬幣:1隻🍗")

    @betting_group.command(name="兌換", description="用硬幣兌換雞腿")
    @app_commands.describe(desired_token="欲兌換的雞腿數量")
    async def betting_exchange_command(
        self, interaction: discord.Interaction, desired_token: int
    ):
        exchange_rate = GamblingUtil.get_token_rate()
        if desired_token < 1:
            await interaction.response.send_message("參數錯誤: 🍗數量不能低於1")
            return

        member: Member = self.database.get_member(interaction.user.id)
        if member is None:
            member = self.database.add_member(interaction.user.id)

        required_coin = exchange_rate * desired_token
        if member.coin < required_coin:
            await interaction.response.send_message(
                f"參數錯誤: 您目前手持硬幣數量不夠 目前 {exchange_rate}硬幣兌換1🍗\n"
                f"目前您擁有硬幣{member.coin}, 小於交換所需量 {required_coin}"
            )
            return

        self.database.add_coin(member.member_id, -1 * required_coin)
        self.database.add_token(member.member_id, desired_token)
        member = self.database.get_member(interaction.user.id)
        msg = "```兌換完成! 兌換明細如下:\n"
        msg += f"本次兌換匯率: {exchange_rate}\n"
        msg += f"本次兌換消耗硬幣: {required_coin}\n"
        msg += f"本次兌換獲得🍗: {desired_token}根\n"
        msg += f"目前持有硬幣: {member.coin}\n"
        msg += f"目前持有🍗: {member.token}根\n"
        msg += "```"
        await interaction.response.send_message(msg)

    @betting_group.command(name="重置全員", description="重置所有人的雞腿")
    async def reset_everyone_command(self, interaction: discord.Interaction):
        self.database.reset_everyone_token()
        await interaction.response.send_message("已重置全員雞腿")


async def setup(client):
    await client.add_cog(Gambling(client))