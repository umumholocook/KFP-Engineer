import os
from common.ImageUtil import ImageUtil
from common.Position import Position
from common.ImageWithTextPosition import ImageWithTextPosition
from common.ImageUtil import ImageUtil

class YagooUtil():

    def _getMemePath():
        return os.sep.join((os.getcwd(), "resource", "image", "yagoo_hello.jpg"))

    _image = ImageWithTextPosition(_getMemePath(), [Position(10, 10), Position(60, 10), Position(10, 60), Position(60, 60)])
    
    def drawYagoo(text: str):
        return ImageUtil.renderText(text, YagooUtil._image)
