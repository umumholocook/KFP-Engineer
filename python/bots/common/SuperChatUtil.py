import os
import tempfile
import unicodedata
from PIL import Image, ImageDraw, ImageFont


class SuperChatUtil():

    _avatar_size = 165

    _picList = [
        "BLUE.png",
        "CYAN.png",
        "LIGHTBLUE.png",
        "MAGENTA.png",
        "ORANGE.png",
        "RED.png",
        "YELLOW.png"
    ]

    _word_color = {
        "BLUE_name": [185, 209, 236],
        "BLUE_word": [255, 255, 255],
        "CYAN_name": [0, 88, 76],
        "CYAN_word": [0, 0, 0],
        "LIGHTBLUE_name": [0, 55, 63],
        "LIGHTBLUE_word": [0, 0, 0],
        "MAGENTA_name": [237, 186, 206],
        "MAGENTA_word": [255, 255, 255],
        "ORANGE_name": [248, 203, 179],
        "ORANGE_word": [252, 233, 233],
        "RED_name": [241, 179, 179],
        "RED_word": [255, 255, 255],
        "YELLOW_name": [117, 82, 0],
        "YELLOW_word": [32, 25, 5],
    }

    _allOffSet = {
        "avatar": [140, 110],
        "name": [350, 112],
        "money": [350, 192],
        "text": [140, 350],
    }

    def getSuperChatPath():
        return os.sep.join((tempfile.gettempdir(), "result.png"))

    def createSC(user_name:str , avatar: Image, sc_money: int, sc_msg: str, sc_color: str):
        if os.path.exists(SuperChatUtil.getSuperChatPath()):
            os.remove(SuperChatUtil.getSuperChatPath())

        # background
        background_path = os.sep.join((os.getcwd(), "resource", "image", "superchatMeme", f"{sc_color}.png"))
        background = Image.open(background_path)

        # avatar
        mask = Image.open(SuperChatUtil._getMaskImagePath()).resize((SuperChatUtil._avatar_size, SuperChatUtil._avatar_size))
        img = avatar.resize((SuperChatUtil._avatar_size, SuperChatUtil._avatar_size))
        background.paste(img, tuple(SuperChatUtil._allOffSet["avatar"]), mask)

        # see need to add text image or not
        if sc_color != "BLUE":
            addPage, newMsg = SuperChatUtil._resizeMsg(offset=1625, msg=sc_msg, img=background)
            if addPage != 0:
                text_path = os.sep.join(
                    (os.getcwd(), "resource", "image", "superchatMeme", f"{sc_color}_text.png"))
                textground = Image.open(text_path)
                if addPage == 1:
                    background.paste(textground, (0, 390))
                elif addPage == 2:
                    background.paste(textground, (0, 390))
                    background.paste(textground, (0, 460))
        draw = ImageDraw.Draw(background)

        # name
        key = sc_color + "_name"
        nameColor = SuperChatUtil._word_color[key]
        SuperChatUtil._pasteName(SuperChatUtil._allOffSet["name"], user_name, nameColor, draw)

        # money
        key = sc_color + "_word"
        nameColor = SuperChatUtil._word_color[key]
        SuperChatUtil._pasteMoney(SuperChatUtil._allOffSet["money"], str(sc_money), nameColor, draw)

        # msg
        if sc_color != "BLUE":
            SuperChatUtil._pasteText(SuperChatUtil._allOffSet["text"], newMsg, nameColor, draw)

        background.save(os.sep.join((tempfile.gettempdir(), "result.png")))
        return SuperChatUtil.getSuperChatPath()

    def _pasteName(offset, username: str, color: list, draw: ImageDraw):
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "msjh.ttc")), size=60,
                                  encoding='utf-8')
        draw.text(offset, username, fill=tuple(color), font=font, stroke_width=1)

    def _pasteMoney(offset, money: str, color: list, draw: ImageDraw):
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "msjh.ttc")), size=60,
                                  encoding='utf-8')
        money = money[::-1]
        result = ','.join([money[i:i+3] for i in range(0, len(money), 3)])
        result = "Coin. " + result[::-1] + ".00"
        draw.text(offset, result, fill=tuple(color), font=font, stroke_width=1)

    def _getFont():
        font: ImageFont = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "SourceHanSans-VF.ttf.ttc")), size=80,encoding='utf-8')
        # SourceHanSans has the following styles:
        # [b'ExtraLight', b'Light', b'Normal', b'Regular', b'Medium', b'Bold', b'Heavy']
        font.set_variation_by_name('Medium')
        return font

    def _pasteText(offset, msg: str, color: list, draw: ImageDraw):
        font = SuperChatUtil._getFont()
        for c in msg:
            print(f"{c} has {unicodedata.east_asian_width(c)}")
        draw.text(offset, msg, fill=tuple(color), font=font)

    def _resizeMsg(offset: int, msg: str, img: Image):
        font = SuperChatUtil._getFont()
        addPage = 0
        newMsg = ""
        for i in range(len(msg)):
            newMsg += msg[i]
            if ImageDraw.Draw(img).textsize(newMsg, font)[0] > offset:
                newMsg = newMsg[:-1] + "\n" + newMsg[-1]
                addPage += 1
                if addPage == 3:
                    newMsg = newMsg[:-3] + "..."
                    addPage -= 1
                    return addPage, newMsg
        return addPage, newMsg

    def _getMaskImagePath():
        return os.sep.join((os.getcwd(), "resource", "image", "superchatMeme", "mask.png"))
