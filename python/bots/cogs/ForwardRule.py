import io, aiohttp, asyncio
from common.ForwardUtil import ForwardUtil
from common.models.Forward import Forward
from discord import Message, Guild, File
from discord.ext import commands

class ForwardRule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def forward_rule_on_message(self, message:Message):
        if message.author.bot:
            return # 無視機器人的消息 
        forward_rules = ForwardUtil.get_forward(message.guild.id, message.channel.id)
        if len(forward_rules) > 0:
            forward: Forward
            should_delete = False
            for forward in forward_rules:
                guild: Guild = self.bot.get_guild(forward.receive_guild_id)
                if guild:
                    channel = guild.get_channel(forward.receive_channel_id)
                    if channel:
                        files = await self.getFiles(message)
                        await channel.send(content=message.content, files=files)
                        should_delete |= forward.delete_original
            if should_delete:
                await message.delete()
                thanks_msg = await message.channel.send("非常感謝你的投訴, 我們會即刻處理")
                await asyncio.sleep(3)
                await thanks_msg.delete()
    
    async def getFiles(self, message:Message):
        result = []
        for attachment in message.attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        continue
                    data = io.BytesIO(await resp.read())
                    result.append(File(data, attachment.filename))
        return result
    
    @commands.group(name = 'forward', invoke_without_command=True)
    async def forward(self, ctx:commands.Context, *attr):
        msg = "如何使用消息復誦:"
        msg+= "\n"
        msg+= "`!forward list` 顯示目前已有的復誦\n"
        msg+= "`!forward delete <復誦id>` 刪除指定的復誦設定\n"
        msg+= "`!forward send` 設置要監聽的頻道, 後面加 False 表示要保留原始消息\n"
        msg+= "`!forward receive <群組id+頻道id>` 設置接收的頻道\n"
        # msg+= "`!forward setbroadcast` 設置此頻道可以收發其他群的相同類型頻道"
        await ctx.send(msg)

    @forward.command(name = "send")
    async def set_send(self, ctx:commands.Context, delete_original:bool = True):
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        msg = "請在接收的頻道裡輸入下面的指令:\n"
        msg+= f"`!forward receive {guild_id} {channel_id} {delete_original}`"
        await ctx.send(msg)
    
    @forward.command(name = "receive")
    async def set_receive(self, ctx:commands.Context, send_guild_id: int, send_channel_id: int, delete_original: bool):
        if send_guild_id != ctx.guild.id:
            await ctx.send("目前不支持跨服務器復誦")
            return
        sendChannel = self.bot.get_channel(send_channel_id)
        if ForwardUtil.create_forward(send_guild_id, send_channel_id, ctx.guild.id, ctx.channel.id, delete_original):
            await ctx.send(f"從{sendChannel.name}轉至{ctx.channel.name}的復誦建立完成")
        else:
            await ctx.send(f"復誦建立失敗")

    @forward.command(name = "list")
    async def list_forwards(self, ctx:commands.Context):
        forward_list = ForwardUtil.get_all_forward()
        forward: Forward
        msg = "```"
        if len(forward_list) > 0:
            for forward in forward_list:
                guild = self.bot.get_guild(forward.send_guild_id)
                send_channel = self.bot.get_channel(forward.send_channel_id)
                receive_channel = self.bot.get_channel(forward.receive_channel_id)
                msg += f"復誦規則:\n" 
                msg += f"{forward.id}, 從{guild.name}群 {send_channel.name}頻道 復誦到{receive_channel.name}, 刪除原留言: {forward.delete_original}\n"
        else:
            msg += "目前沒有任何復誦規則, 請使用`!forward` 查詢設置方法"
        msg+= "```"
        await ctx.send(msg)

    @forward.command(name = "delete")
    async def delete_forward(self, ctx:commands.Context, forward_id):
        ForwardUtil.delete(forward_id)
        await ctx.channel.send(f"成功移除復誦規則`{forward_id}`")
    
async def setup(bot):
    await bot.add_cog(ForwardRule(bot))