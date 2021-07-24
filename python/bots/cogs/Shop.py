from common.InventoryUtil import InventoryUtil
from discord.ext import commands


class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='shop', invoke_without_command=True)
    async def shop_group(self, ctx: commands.Context, *attr):
        msg = "歡迎來到KFP炸機店小賣部\n"
        msg += "本小賣部一律使用雞腿來購買商品\n"
        msg += "```"
        msg += "!shop buy <商品號碼> 購買指定的商品號碼\n"
        msg += "!shop menu 展示目前販賣中的商品\n"
        msg += "!shop exchange <雞腿數量> 兌換雞腿\n"
        msg += "```"
        await ctx.send(msg)

    # list 上架的商品
    @shop_group.command(name="menu")
    async def show_menu(self, ctx: commands.Command):
        result = InventoryUtil.ShopMenu(ctx.guild.id)
        if len(result) < 1:
            await ctx.send('目前商品都被買光了!')
        else:
            msg = "==================商品價目表==================\n"
            for products in result:
                msg += "\tIndex: " + str(products.item.id)
                msg += "\tName: " + products.item.name
                msg += "\tLevel required: " + str(products.item.level_required)
                msg += "\tPrice: " + str(products.item.token_required) + "\n"
            await ctx.send(msg)

    @shop_group.command(name="buy")
    async def buy_item(self, ctx: commands.Command, item_index: int, count: int):
        result = InventoryUtil.buyItem(ctx.guild_id, ctx.author.id, item_index, count)
        if result == 1:
            await ctx.send("購買成功!")
        elif result == 0:
            await ctx.send("購買失敗!請確認")

    # 管理員用
    @shop_group.command(name="secrete")
    async def list_items(self, ctx: commands.Command):
        msg = "```"
        msg += "如何新增?\n"
        msg += "先create再把item add上架販售\n"
        msg += "!shop create <商品名稱> <等級限制> <價錢>\n"
        msg += "!shop add <商品名稱> <數量> \n"
        msg += "```"
        await ctx.send(msg)

    @shop_group.command(name="exchange")
    async def exchange_token(self, ctx: commands.Command):
        await ctx.send("不好意思, 小賣部正在籌備中...")

    @shop_group.command(name="add")
    async def add_item(self, ctx: commands.Command, item_name: str, item_count: int = 1):
        result = InventoryUtil.addItemToShop(ctx.guild.id, item_name)
        if result != -1:
            await ctx.send(item_name + " 上架成功!")
        else:
            await ctx.send(item_name + " 上架失敗!請確認名字是否正確!")

    @shop_group.command(name="create")
    async def create_item(self, ctx: commands.Command, item_name: str, level_required: int, price: int):
        result = InventoryUtil.createItem(ctx.guild.id, item_name, level_required, price)
        if result == -1:
            await ctx.send(item_name + ' 已經存在!')
        elif result == -2:
            await ctx.send(item_name + ' 新增失敗!請確認指令是否輸入錯誤!')
        else:
            await ctx.send(item_name + ' 新增成功!')



    @shop_group.command(name="listItem")
    async def list_item(self, ctx: commands.Command):
        result = InventoryUtil.ListAllItem(ctx.guild.id)
        if len(result) < 1:
            await ctx.send('目前沒有商品')
        else:
            msg = "```"
            for products in result:
                msg += "\tIndex: " + str(products.id)
                msg += "\tName: " + products.name
                msg += "\tLevel required: " + str(products.level_required)
                msg += "\tPrice: " + str(products.token_required) + "\n"
            msg += "```"
            await ctx.send(msg)


def setup(client):
    client.add_cog(Shop(client))
