from common.InventoryUtil import InventoryUtil
from discord.ext import commands

class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'shop', invoke_without_command=True)
    async def shop_group(self, ctx:commands.Context, *attr):
        msg = "歡迎來到KFP炸機店小賣部\n"
        msg+= "本小賣部一律使用雞腿來購買商品\n"
        msg+= "```"
        msg+= "!shop buy <商品號碼> 購買指定的商品號碼\n"
        msg+= "!shop menu 展示目前販賣中的商品\n"
        msg+= "!shop exchange <雞腿數量> 兌換雞腿\n"
        msg+= "```"
        await ctx.send(msg)

    @shop_group.command(name = "menu")
    async def show_menu(self, ctx:commands.Command):
        await ctx.send("不好意思, 小賣部正在籌備中...")

    @shop_group.command(name = "buy")
    async def buy_item(self, ctx:commands.Command, item_index:int):
        await ctx.send("不好意思, 小賣部正在籌備中...")

    @shop_group.command(name = "secrete")
    async def list_items(self, ctx:commands.Command):
        msg = "```"
        msg+= "!shop add <商品名稱> <數量> \n"
        msg+= "```"
        await ctx.send(msg)

    @shop_group.command(name = "exchange")
    async def exchange_token(self, ctx:commands.Command):
        await ctx.send("不好意思, 小賣部正在籌備中...")

    @shop_group.command(name = "add")
    async def add_item(self, ctx:commands.Command, item_name:str, item_count:int = 1):
        InventoryUtil.addItemToShop(ctx.guild.id, item_name)

def setup(client):
    client.add_cog(Shop(client))