import os
from discord import File

from common.ChannelUtil import ChannelUtil
from common.Util import Util
from common.models.RPGStatus import RPGStatus
import random


class ReviveUtil():

    def getKiraraImagePath(number: int):
        return os.sep.join((os.getcwd(), "resource", "image", "revive", str(number) + ".JPG"))

    def getReviveMsgChannel(status: RPGStatus):
        result = []
        for status in status:
            channel = ChannelUtil.GetChannelWithGuild(status.guild_id, Util.ChannelType.RPG_BATTLE_GROUND)
            for ch in channel:
                # if is not test channel
                if not ChannelUtil.hasChannel(status.guild_id, ch, Util.ChannelType.BANK):
                    if not (ch.channel_id in result):
                        result.append(ch.channel_id)
        return result

    def getPic():
        number = random.randint(1, 10)
        return File(ReviveUtil.getKiraraImagePath(number), filename=str(number) + ".JPG")
    