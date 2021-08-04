import os, tempfile, unicodedata
from PIL import Image, ImageDraw, ImageFont

class YagooUtil():
    def getTempFileName():
        return "yagoo.jpg"

    def _getStoragePath():
        return os.sep.join((tempfile.gettempdir(), YagooUtil.getTempFileName()))

    def _getMemePath():
        return os.sep.join((os.getcwd(), "resource", "image", "yagoo_hello.jpg"))

    def _getSubText(text: str, offset: int):
        subText = ""
        length = 0
        for i in range(offset, min(offset + 4, len(text))):
            status = unicodedata.east_asian_width(text[i])
            if status == 'W':
                length += 2    
            else:
                length += 1
            if length > 4:
                break
            subText += text[i] 
        return subText

    def renderText(text: str):
        offset = 10
        yellow = (252, 241, 79)
        blue = (80, 139, 254)
        image = Image.open(YagooUtil._getMemePath())
        draw = ImageDraw.Draw(image)

        subText_1 = YagooUtil._getSubText(text, 0)
        _, text_h = YagooUtil._renderSubText((offset, offset), yellow, subText_1, draw)

        subText_2 = YagooUtil._getSubText(text, len(subText_1))
        YagooUtil._renderSubText((offset, offset + text_h), blue, subText_2, draw)
        
        image.save(YagooUtil._getStoragePath())

        return YagooUtil._getStoragePath()

    def _renderSubText(offset, text_color, subText: str, draw: ImageDraw):
        stroke_color = (0, 0, 0)
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=50, encoding='utf-8')
        draw.text(offset, subText, fill=text_color, font=font, stroke_width=2, stroke_fill=stroke_color)
        return draw.textsize(subText, font)