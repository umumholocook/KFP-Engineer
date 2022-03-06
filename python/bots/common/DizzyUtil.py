import os, random
from typing import List
from common.Position import Position
from common.ImageWithTextPosition import ImageWithTextPosition
from common.ImageUtil import ImageUtil


class DizzyUtil():

    def _getImageLocation(name: str):
        return os.sep.join((os.getcwd(), "resource", "image", "dizzy", name))

    _images = [ImageWithTextPosition(_getImageLocation("01.jpg"), [Position(10, 10), Position(60, 10), Position(10, 60), Position(60, 60)])]
    
    def drawDizzy(text: str):
        return ImageUtil.renderText(text, random.choice(DizzyUtil()._images))
    
