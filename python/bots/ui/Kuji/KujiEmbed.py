import pytz
from common.KujiUtil import KujiUtil
from discord import Embed

class KujiEmbed():
    __timeZone = "Asia/Taipei"
    # __timeZone = "America/Los_Angeles"
    # KujiDb(timeZone = self.timeZone)

    def getTitle(timestamp):
        timezone = pytz.timezone(KujiEmbed.__timeZone)
        d_aware = timestamp.astimezone(timezone)
        return d_aware.strftime("%Y年%m月%d日")

    def createEmbededCn(yi, timestamp, author:str):
        title = KujiEmbed.getTitle(timestamp)
        title+= "\n易經 · {} · {} {}".format(yi["name"], yi["shape"], yi["symbol"])
        embedMsg = Embed(title=title, description=yi["description"], color=KujiUtil.getYiColor(yi["name"]))
        embedMsg.set_author(name=author)
        payload = yi["payload"]
        for key in payload:
            embedMsg.add_field(name=key, value=payload[key], inline=True)
        return embedMsg

    def createEmbededLs(ls, timestamp, author:str):
        status = ls["status"]
        title = KujiEmbed.getTitle(timestamp)
        imageUri = 'attachment://{}'.format(KujiUtil.getImageNameLs(status))
        title+= "\n台北龍山寺觀音籤· {}\n".format(status)
        if len(ls["image"]) > 0:
            title+= "{} · {}".format(ls["title"], ls["image"])
        else:
            title+= "{}".format(ls["title"])
        payload = ls["payload"]
        description = "**{}**\n".format(ls["poem_line1"])
        description+= "**{}**\n".format(ls["poem_line2"])
        description+= "**{}**\n".format(ls["poem_line3"])
        description+= "**{}**\n".format(ls["poem_line4"])
        description+= "\n詩意:\n{}\n".format(ls["meaning"])
        description+= "\n解曰:\n{}\n".format(ls["explain"])
        if len(payload) > 0:
            description+= "\n聖意:\n"

        embedMsg = Embed(title=title, description=description, color=KujiUtil.getColorLs(status))
        embedMsg.set_author(name=author)
        embedMsg.set_thumbnail(url=imageUri)
        embedMsg.set_image(url=ls["url"])
        for key in payload:
            embedMsg.add_field(name=key, value=payload[key], inline=True)
        return embedMsg

    def createEmbededJp(kuji, timestamp, author:str):
        status = kuji["status"]
        title = KujiEmbed.getTitle(timestamp)
        imageUri = 'attachment://{}'.format(KujiUtil.getImageName(status))
        title+= "\n東京淺草觀音寺御神籤· {}籤 · {}".format(kuji["title"], status)
        description = "{}\n".format(kuji["poem_line1"])
        description+= "`{}`\n".format(kuji["poem_line1_explain"])
        description+= "{}\n".format(kuji["poem_line2"])
        description+= "`{}`\n".format(kuji["poem_line2_explain"])
        description+= "{}\n".format(kuji["poem_line3"])
        description+= "`{}`\n".format(kuji["poem_line3_explain"])
        description+= "{}\n".format(kuji["poem_line4"])
        description+= "`{}`\n".format(kuji["poem_line4_explain"])
        embedMsg = Embed(title=title, description=description, color=KujiUtil.getColor(status))
        embedMsg.set_author(name=author)
        embedMsg.set_thumbnail(url=imageUri)
        payload = kuji["payload"]
        for key in payload:
            embedMsg.add_field(name=key, value=payload[key], inline=True)
        return embedMsg
