import discord
from discord import Embed, app_commands
from discord.ext import commands

from common.RPGUtil.InventoryUtil import InventoryUtil


@app_commands.guild_only()
class InventoryDisplay(commands.GroupCog, group_name="背包", group_description="查看與管理物品清單"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return not interaction.user.bot

    @app_commands.command(name="說明", description="物品清單指令說明")
    async def inventory_help(self, interaction: discord.Interaction) -> None:
        msg = "物品清單指令\n"
        msg += "```"
        msg += "/背包 列表 列出玩家(你)的物品清單\n"
        msg += "/背包 物品 <物品名稱> 列出玩家(你)的物品清單中特定物品詳細資料\n"
        msg += "```"
        msg += "\n:warning:\n"
        msg += "```"
        msg += "/背包 清空 清空使用者物品清單"
        msg += "```"
        await interaction.response.send_message(msg)

    @app_commands.command(name="列表", description="列出你的物品清單")
    async def show_inventory(self, interaction: discord.Interaction) -> None:
        result = InventoryUtil.getAllItemsBelongToUser(interaction.guild.id, interaction.user.id)
        result_count = len(result)
        if result_count < 1:
            await interaction.response.send_message("`你尚未擁有任何物品!`")
            return

        embed_inventory = Embed(
            title=f"{interaction.user.name}的物品清單",
            description="清單每頁20筆資料",
            color=0xff8000,
        )

        for item_index, item_display in enumerate(result[:], start=1):
            embed_inventory.add_field(
                name=None,
                value=f"{item_index}. {item_display.item.name} x {item_display.amount}",
                inline=False,
            )

        embed_inventory.set_thumbnail(url="https://s1.zerochan.net/Takanashi.Kiara.600.3145979.jpg")
        embed_inventory.set_footer(text=f"一共{result_count}種物品")
        await interaction.response.send_message(embed=embed_inventory)

    @app_commands.command(name="物品", description="查看特定物品的詳細資料")
    @app_commands.describe(item_name="物品名稱")
    async def show_item(self, interaction: discord.Interaction, item_name: str) -> None:
        result = InventoryUtil.getAllItemsBelongToUser(interaction.guild.id, interaction.user.id)
        if len(result) < 1:
            await interaction.response.send_message("`你尚未擁有任何物品!`")
            return

        for result_item in result:
            if result_item.item.name == item_name:
                embed_specific_item = Embed(
                    title=f"物品名稱: {result_item.item.name}",
                    description=f"描述: {result_item.item.description}",
                    color=0xff8000,
                )
                embed_specific_item.add_field(
                    name="ID:",
                    value="{}".format(str(result_item.item.id).ljust(3, " ")),
                    inline=True,
                )
                embed_specific_item.add_field(
                    name="持有數量:",
                    value="{}".format(str(result_item.amount).ljust(3, " ")),
                    inline=True,
                )
                embed_specific_item.add_field(
                    name="等級限制:",
                    value="{}".format(str(result_item.item.level_required).ljust(3, " ")),
                    inline=True,
                )
                embed_specific_item.add_field(
                    name="價格:",
                    value="{}".format(str(result_item.item.token_required).ljust(3, " ")),
                    inline=True,
                )
                embed_specific_item.add_field(
                    name="物品類型:",
                    value="{}".format(str(result_item.item.type).ljust(3, " ")),
                    inline=True,
                )
                embed_specific_item.add_field(
                    name="增幅類型:",
                    value="{}".format(str(result_item.item.buff.buff_type).ljust(3, " ")),
                    inline=True,
                )
                embed_specific_item.set_thumbnail(url="https://images.heb.com/is/image/HEBGrocery/001584756")
                await interaction.response.send_message(embed=embed_specific_item)
                return

        await interaction.response.send_message("`你的物品清單裡沒有此物品!`")

    @app_commands.command(name="清空", description="[開發人員專用] 清空使用者物品清單")
    async def clear_inventory(self, interaction: discord.Interaction) -> None:
        InventoryUtil.removeUserItems_TEST(interaction.guild.id, interaction.user.id)
        await interaction.response.send_message("`物品清單已清空.`", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InventoryDisplay(bot))