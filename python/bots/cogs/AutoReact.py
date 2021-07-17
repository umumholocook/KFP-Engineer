from discord.utils import get
from discord.ext import commands
from discord import Message

class AutoReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener('on_message')
    async def auto_react(self, message:Message):
        if message.author.bot:
            return # 無視機器人的消息
        if self.shouldReact(message.content):
            theGuild = await self.bot.fetch_guild(message.guild.id)
            if theGuild.emojis:
                for emoji in theGuild.emojis:
                    if "name" in emoji.name:
                        await message.add_reactions(emoji)
    
    def shouldReact(self, msg: str):
        if "我婆" in msg or "我老婆" in msg or "我老公" in msg:
            return True 
        return False
def setup(bot):
    bot.add_cog(AutoReact(bot))