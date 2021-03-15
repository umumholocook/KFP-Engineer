from common.ForwardUtil import ForwardUtil
from discord import Guild
from discord.ext import commands

class Forward(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'forward', invoke_without_command=True)
    async def forward(self, ctx:commands.Context, *attr):
        msg = "如何使用消息復誦:"
        msg+= "`!forward list` 顯示目前已有的復誦"
        msg+= "`!forward delete <復誦id>` 刪除指定的復誦設定"
        msg+= "`!forward send` 設置要監聽的頻道, 後面加 true 表示要刪除原始消息"
        msg+= "`!forward receive <群組id+頻道id>` 設置接收的頻道"
        # msg+= "`!forward setbroadcast` 設置此頻道可以收發其他群的相同類型頻道"
        ctx.send(msg)

    @forward.command(name = "send")
    async def set_send(self, ctx:commands.Context):
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        msg = "請在接收的頻道裡輸入下面的指令:"
        msg = f"`!forward receive {guild_id} {channel_id}`"
    
    @forward.command(name = "receive")
    async def set_receive(self, ctx:commands.Context, send_guild_id: int, send_channel_id: int):
        if send_guild_id != ctx.guild.id:
            await ctx.send("目前不支持跨服務器復誦")
            return
        sendChannel = self.bot.get_channel(send_channel_id)
        if ForwardUtil.create_forward(send_guild_id, send_channel_id, ctx.guild.id, ctx.channel.id):
            await ctx.send(f"從{sendChannel.name}轉至{ctx.channel.name}的復誦建立完成")
        else:
            await ctx.send(f"復誦建立失敗")

    @forward.command(name = "list")
    async def list_forwards(self, ctx:commands.Context):
        

    @forward.command(name = "delete")
    async def delete_forward(self, ctx:commands.Context, forward_id):
        ForwardUtil.delete(forward_id)
    
def setup(bot):
    bot.add_cog(Forward(bot))