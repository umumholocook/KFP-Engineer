import discord

# import asyncio
from base64 import b64encode
from mimetypes import MimeTypes
from pathlib import PurePath
from typing import Tuple, Union
from urllib.parse import urlparse

import aiohttp
from async_lru import alru_cache

from .SimpleDiscordMarkdown.Datatypes import EmojiData

mimetypes = MimeTypes()
mimetypes.types_map[True]['.webp'] = 'image/webp'

@alru_cache(maxsize=128)
async def read(asset: Union[discord.Asset, Tuple[EmojiData, str]]) -> bytes:
    if isinstance(asset, tuple) and isinstance(asset[0], EmojiData):
        asset = f'https://cdn.discordapp.com/emojis/{asset[0].id}.{asset[1]}'
        async with aiohttp.ClientSession() as session, \
                   session.get(asset) as resp:
            return await resp.read()
    if isinstance(asset, discord.Asset):
        return await asset.read()

@alru_cache(maxsize=128)
async def read_as_dataurl(asset: Union[discord.Asset, Tuple[EmojiData, str]]) -> str:
    if isinstance(asset, tuple) and isinstance(asset[0], EmojiData):
        suffix = f'.{asset[1]}'
    else:
        suffix = PurePath(urlparse(str(asset)).path).suffix
    mediatype = mimetypes.types_map[True][suffix]
    content = await read(asset)
    # loop = asyncio.get_running_loop()
    # content = await loop.run_in_executor(None, b64encode, content)
    content = b64encode(content)
    content = f'data:{mediatype};base64,{content.decode()}'
    return content
