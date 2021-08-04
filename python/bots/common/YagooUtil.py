import os, tempfile
from PIL import Image, ImageDraw, ImageFont

class YagooUtil():
    def getTempFileName():
        return "yagoo.jpg"

    def _getStoragePath():
        return os.sep.join((tempfile.gettempdir(), YagooUtil.getTempFileName()))

    def _getMemePath():
        return os.sep.join((os.getcwd(), "resource", "image", "yagoo_hello.jpg"))

    def renderText(text: str):
        offset = 10
        yellow = (252, 241, 79)
        blue = (80, 139, 254)
        image = Image.open(YagooUtil._getMemePath())
        draw = ImageDraw.Draw(image)

        _, text_h = YagooUtil._renderSubText((offset, offset), yellow, text[:2], draw)
        YagooUtil._renderSubText((offset, offset + text_h), blue, text[2:4], draw)
        
        image.save(YagooUtil._getStoragePath())

        return YagooUtil._getStoragePath()

    def _renderSubText(offset, text_color, subText: str, draw: ImageDraw):
        stroke_color = (0, 0, 0)
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=50, encoding='utf-8')
        draw.text(offset, subText, fill=text_color, font=font, stroke_width=2, stroke_fill=stroke_color)
        return draw.textsize(subText, font)