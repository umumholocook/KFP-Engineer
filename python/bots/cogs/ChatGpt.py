import openai
from discord.ext import commands
from discord.app_commands import Choice
from discord import app_commands

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def generate_response(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.5,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response.choices[0].text.strip()

    @app_commands.command(name = 'chat', description="咦？")
    @app_commands.describe(type = "話就放這了")
    @commands.cooldown(1, 15, type=commands.BucketType.user)
    async def ask_chatgpt(self, ctx: commands.ApplicationContext, question: str):
        prompt = f"{ctx.author.name}: {question}"
        response = await self.generate_response(prompt)
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))