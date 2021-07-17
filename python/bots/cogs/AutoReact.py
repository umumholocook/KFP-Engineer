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
                    if "w_wake" in emoji.name:
                        await message.add_reaction(emoji)
    
    def shouldReact(self, msg: str):
        if self.hasSubString(msg, "我婆") or self.hasSubString(msg, "我老婆") or self.hasSubString(msg, "我老公"):
            return True 
        return False
    
    def hasSubString(self, msg: str, substring: str):
        if substring in msg and len(msg) > len(substring):
            return True
        return False

def setup(bot):
    bot.add_cog(AutoReact(bot))