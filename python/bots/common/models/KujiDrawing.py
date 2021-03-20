import os
from common.KujiObj import KujiObj
from PIL import Image, ImageDraw, ImageFont

class KujiDrawing:
    __font_size = 60
    def __init__(self, kujiObj: KujiObj):
        self.kuji = kujiObj
        self.fontPath = os.sep.join((os.getcwd(), 'resource', 'ttf', 'A_KsoKaisho.otf'))

    def _prepareCanvas(self):
        self.image = Image.new('RGBA', (960, 540), (0, 0, 0, 0))
        pass

    def _drawBackgroundImage(self):
        self.image.paste(self.kuji.getImage())
        pass

    def _drawPoemText(self):
        draw = ImageDraw.Draw(self.image)
        lines = self.kuji.getPoemLines()
        startPoint = self.kuji.getStartPosition()
        x_offset = 0
        y_offset = 0
        for line in lines:
            self._drawPoemLine(startPoint[0] + x_offset, startPoint[1] + y_offset, line, draw)
            x_offset -= self.__font_size * 1.3
            y_offset += self.__font_size / 3

    
    # draw single poem line
    def _drawPoemLine(self, x:int, y:int, line: str, draw: ImageDraw):
        y_offset = 0
        for character in line:
            self._drawSingleChinese(x, y+y_offset, character, draw)
            y_offset += self.__font_size

    # draw single chinese, return height of the text
    def _drawSingleChinese(self, x:int, y:int, singleCharacter: str, draw: ImageDraw):
        text_size =  self.__font_size
        font = ImageFont.truetype(font = self.fontPath, size=text_size, encoding='utf-8')
        draw.text((x, y), singleCharacter, font=font, fill=(28, 28, 28, 255))
        return text_size

    def generateKujiJpImage(self, path:str):
        self._prepareCanvas()
        self._drawBackgroundImage()
        self._drawPoemText()
        self.image.save(path, format="PNG")
        