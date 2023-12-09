import discord, os
from discord.embeds import Embed
from discord.ext import commands
from openai import OpenAI

class GPT(commands.Cog):

    MESSAGE_PREFIX = [
                {"role": "system", "content": "You are a helpful assistant on discoard as a bot. Your name is 幕後大總管, aka 大總管"},
                {"role": "system", "content": "You work at a place called KFP, a fried chicken fast food restaurant."},
                {"role": "system", "content": "KFP stands for Kiara Fried Phoenix."},
                {"role": "system", "content": "KFP is own by a Virtual YouTuber named Takanashi Kiara."},
                {"role": "system", "content": "Use Kikkeriki to greet people."},
                {"role": "system", "content": "凡是使用中文的場合 一率使用繁體中文"},
                {"role": "system", "content": "Use display name to address the user when needed."},
                {"role": "system", "content": "If any question regarding to bot or engineering, please refer them to 偷筆姊姊"},
                {"role": "system", "content": "Do not mention user id, talk like a human being and use display name"}]

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(name = 'chat', invoke_without_command=True)
    @commands.cooldown(1, 30, type=commands.BucketType.guild)
    async def chat(self, ctx:commands.Context):
        message = ctx.message.content.replace('!chat ', '')
        message = ctx.message.content.replace('!chat', '')
        if len(message) < 1:
            await ctx.channel.send("請輸入你想要聊的話題")
            return
        async with ctx.typing():
            fullMessages = await self.generateMessageHistory(ctx)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages = self.MESSAGE_PREFIX + [
                    {"role": "system", "content": "This user has discord display name: "+ ctx.author.display_name},
                ] + fullMessages,
                max_tokens=2048,
                temperature=0.5
            )

        await ctx.reply(response.choices[0].message.content)

    @commands.group(name = 'draw', invoke_without_command=True)
    @commands.cooldown(1, 30, type=commands.BucketType.guild)
    async def draw(self, ctx:commands.Context):
        message = ctx.message.content.replace('!draw ', '')
        message = ctx.message.content.replace('!draw', '')
        if len(message) < 1:
            await ctx.channel.send("請輸入你想要繪製的圖片")
            return
        async with ctx.typing():
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=message,
                size="1024x1024",
                quality="standard",
                n=1,
            )

        embedImage = discord.Embed()
        embedImage.set_image(url=response.data[0].url)

        await ctx.reply("好的, 我使用了以下的提示詞: " + response.data[0].revised_prompt, embed=embedImage)

    @chat.error
    async def chat_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply("聊天機制限制30秒一次")
        else:
            raise error
        
    async def generateMessageHistory(self, ctx:commands.Context):
        result = []
        message = ctx.message
        while True:
            result.insert(0, self.getMessageOut(message))
            if message.reference == None:
                break
            else:
                message = await ctx.channel.fetch_message(message.reference.message_id)
                if message == None:
                    break
        return result

    def getMessageOut(self, message: discord.Message):
        role: str
        content = message.content
        if (message.author.bot):
            role = "system"
        else:
            role = "user"
            content = content.replace('!chat ', '')
            content = content.replace('!chat', '')
        return {"role": role, "content": content}
    

async def setup(client):
    await client.add_cog(GPT(client))