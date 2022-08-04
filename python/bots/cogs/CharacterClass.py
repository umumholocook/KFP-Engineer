from discord.ext import commands

# 職業
class CharacterClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='job', invoke_without_command=True)
    async def job_group(self, ctx: commands.Context, *attr):
        msg  = "歡迎來到KFP轉職所\n"
        msg += "你可以在轉職所使用以下的功能:\n"
        msg += "```\n"
        msg += "!job list 列出所有職業\n"
        msg += "!job requirement <職業名稱> 查看此職業的需求\n"
        msg += "!job apply <職業名稱> 選擇此職業為自己的職業\n"
        msg += "!job quit <職業名稱> 放棄職業"
        msg += "```\n"
        await ctx.send(msg)

    @job_group.command(name="list")
    async def show_jobs(self, ctx: commands.Command):
        await ctx.send("轉職所準備中...")
    
    @job_group.command(name="requirement")
    async def show_job_requirement(self, ctx: commands.Command):
        await ctx.send("轉職所準備中...")
    
    @job_group.command(name="apply")
    async def apply_job(self, ctx: commands.Command):
        await ctx.send("轉職所準備中...")

    @job_group.command(name="quit")
    async def quit_job(self, ctx: commands.Command):
        await ctx.send("轉職所準備中...")

async def setup(client):
    await client.add_cog(CharacterClass(client))