import io
import time
import os
from discord.ext import commands
from enum import Enum
from PIL import Image

class AvatarType(Enum):
        ORIGINAL = 1
        CAT_SHARK = 2

class BotAvatarUtil():
    # def getImagePath(type: AvatarType):
    #     return os.sep.join((os.getcwd(), 'resource', 'avatars', {
    #         'ORIGINAL': 'pain_peko.jpg',
    #         'CAT_SHARK': 'cat_shark.jpg'
    #     }[type.name]))

    # def getImageBytes(type: AvatarType):
    #     img_path = BotAvatarUtil.getImagePath(type)
    #     img = Image.open(img_path, mode='r')
    #     img_resize = img.resize((500, 500))
    #     img_byte_arr = io.BytesIO()
    #     img_resize.save(img_byte_arr, format='JPEG')
    #     return img_byte_arr.getvalue()

    # async def sendMessageWithImage(bot: commands.bot, ctx:commands.Context, message: str, avatarType: AvatarType):
    #     await bot.user.edit(avatar=BotAvatarUtil.getImageBytes(avatarType))
    #     await ctx.channel.send(message)
    #     time.sleep(5)
    #     await bot.user.edit(avatar=BotAvatarUtil.getImageBytes(AvatarType.ORIGINAL))
        
