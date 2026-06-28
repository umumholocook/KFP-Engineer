import discord
from io import BytesIO
from PIL import Image


class DiscordUtil:
    @staticmethod
    async def fetch_text_channel(
        bot: discord.Client, channel_id: int
    ) -> discord.TextChannel | discord.Thread | None:
        if not channel_id:
            return None
        channel = bot.get_channel(channel_id)
        if channel is not None:
            return channel
        try:
            fetched = await bot.fetch_channel(channel_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None
        if isinstance(fetched, (discord.TextChannel, discord.Thread)):
            return fetched
        return None

    @staticmethod
    async def fetch_guild_member(
        guild: discord.Guild, user_id: int
    ) -> discord.Member | None:
        member = guild.get_member(user_id)
        if member is not None:
            return member
        try:
            return await guild.fetch_member(user_id)
        except (discord.NotFound, discord.HTTPException):
            return None

    @staticmethod
    async def read_avatar_bytes(user: discord.User | discord.Member) -> bytes:
        return await user.display_avatar.read()

    @staticmethod
    async def read_avatar_image(user: discord.User | discord.Member) -> Image.Image:
        data = await DiscordUtil.read_avatar_bytes(user)
        return Image.open(BytesIO(data))

    @staticmethod
    async def send_user_dm(user: discord.User | discord.Member, content: str) -> bool:
        try:
            await user.send(content)
            return True
        except discord.Forbidden:
            return False
        except discord.HTTPException:
            return False

    @staticmethod
    def invite_url(client_id: int, permissions: int = 1543892049) -> str:
        return (
            "https://discord.com/oauth2/authorize"
            f"?client_id={client_id}"
            f"&permissions={permissions}"
            "&scope=bot%20applications.commands"
        )