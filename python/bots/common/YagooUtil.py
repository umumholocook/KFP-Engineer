import os, tempfile, unicodedata, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class YagooUtil():
    def getTempFileName():
        return "yagoo.jpg"

    def _getStoragePath():
        return os.sep.join((tempfile.gettempdir(), YagooUtil.getTempFileName()))

    def _getMemePath():
        return os.sep.join((os.getcwd(), "resource", "image", "yagoo_hello.jpg"))
    
    def _getDizzyPath():
        return os.sep.join((os.getcwd(), "resource", "image", "dizzy", random.choice(["01.jpg", "02.jpg", "03.jpg", "04.jpg"])))

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
    
    def renderDizzyText(text: str):
        return YagooUtil._renderText(text, YagooUtil._getDizzyPath())
    
    def renderYagooText(text: str):
        return YagooUtil._renderText(text, YagooUtil._getMemePath())

    def _renderText(text: str, imagePath: str):
        offset = 10
        yellow = (252, 241, 79)
        blue = (80, 139, 254)
        image = Image.open(imagePath)
        draw = ImageDraw.Draw(image)

        subText_1 = YagooUtil._getSubText(text, 0)
        YagooUtil._renderSubTextShadow((offset, offset), subText_1, image)
        _, text_h = YagooUtil._renderSubText((offset, offset), yellow, subText_1, draw)

        subText_2 = YagooUtil._getSubText(text, len(subText_1))
        YagooUtil._renderSubTextShadow((offset, offset + text_h), subText_2, image)
        YagooUtil._renderSubText((offset, offset + text_h), blue, subText_2, draw)
        
        image.save(YagooUtil._getStoragePath())

        return YagooUtil._getStoragePath()

    def _renderSubTextShadow(offset, subText: str, image: Image):
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=50, encoding='utf-8')
        textSize = ImageDraw.Draw(image).textsize(subText, font)

        blurred = Image.new('RGBA', textSize)
        draw = ImageDraw.Draw(blurred)
        size = 1.2
        draw.text((textSize[0] / 2, textSize[1] / 2), subText, fill=(255, 255, 255), font=font, anchor='mm')
        blurred = blurred.resize((int(blurred.size[0] * size), int(blurred.size[1] * size)))
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=2))
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=2))
        white = Image.new('RGBA', blurred.size, (255, 255, 255))
        
        # Paste soft text onto background
        image.paste(white, (offset[0] * -1 , offset[1] - 4), blurred)


    def _renderSubText(offset, text_color, subText: str, draw: ImageDraw):
        stroke_color = (0, 0, 0)
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=50, encoding='utf-8')
        draw.text(offset, subText, fill=text_color, font=font, stroke_width=2, stroke_fill=stroke_color)
        return draw.textsize(subText, font)