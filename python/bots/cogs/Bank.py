from discord.ext import commands


# 金融系統, 以大總管為主體的操作
class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='bank', invoke_without_command=True)
    async def bank_group(self, ctx: commands.Context):
        pass
    

def setup(client):
    client.add_cog(Bank(client))