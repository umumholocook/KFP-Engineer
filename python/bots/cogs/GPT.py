import discord, openai, os
from discord import app_commands
from discord.ext import commands

class GPT(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        openai.api_key = os.getenv("OPENAI_API_KEY")

    @commands.group(name = 'chat', invoke_without_command=True)
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def chat(self, ctx:commands.Context, *attr):
        message = ctx.message.content.replace('!chat ', '')
        if len(message) < 1:
            await ctx.channel.send("請輸入你想要聊的話題")
            return
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": "You are a helpful assistant on discoard as a bot. Your name is 幕後大總管, aka 大總管"},
                {"role": "system", "content": "You work at a place called KFP, a fried chicken fast food restaurant."},
                {"role": "system", "content": "KFP stands for Kiara Fried Phoenix."},
                {"role": "system", "content": "KFP is own by a Virtual YouTuber named Takanashi Kiara."},
                {"role": "system", "content": "Use Kikkeriki to greet people."},
                {"role": "system", "content": "凡是使用中文的場合 一率使用繁體中文"},
                {"role": "system", "content": "This user has discord display name: "+ ctx.author.display_name},
                {"role": "system", "content": "Use user id for context reference. Use display name to address the user"},
                {"role": "system", "content": "If any question regarding to bot or engineering, please refer them to 姊姊"},
                {"role": "system", "content": "Do not mention user id, talk like a human being and use display name"},
                {"role": "user", "content": message}
            ],
            max_tokens=2048,
            temperature=0.5
        )

        await ctx.reply(response.choices[0].message.content)

    @chat.error
    async def chat_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("聊天機制限制10秒一次")
        else:
            raise error    

async def setup(client):
    await client.add_cog(GPT(client))