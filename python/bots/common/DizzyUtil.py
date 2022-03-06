import os, random
from typing import List
from common.Position import Position
from common.ImageWithTextPosition import ImageWithTextPosition
from common.ImageUtil import ImageUtil


class DizzyUtil():

    def _getImageLocation(name: str):
        return os.sep.join((os.getcwd(), "resource", "image", "dizzy", name))
    _mizuki_c1 = (252, 173, 183)
    _mizuki_c2 = (226, 199, 97)
    _mizuki_c3 = (232, 68, 86)
    _mizuki_c4 = (109, 228, 235)

    _images = [
        ImageWithTextPosition(
            _getImageLocation("01.jpg"), 
            [Position(10, 10), Position(10, 154), Position(154, 10), Position(154, 154)]),
        ImageWithTextPosition(
            _getImageLocation("02.jpg"), 
            [Position(10, 10), Position(10, 90), Position(70, 140), Position(140, 140)], size = 70),
        ImageWithTextPosition(
            _getImageLocation("03.jpg"), 
            [Position(10, 150), Position(60, 150), Position(110, 150), Position(160, 150)]),
        ImageWithTextPosition(
            _getImageLocation("04.jpg"), 
            [Position(0, 150), Position(50, 150), Position(100, 150), Position(150, 150)],
            colors = [_mizuki_c1, _mizuki_c2, _mizuki_c3, _mizuki_c4],
            angles = [20, -20, 20, -20]),
        ImageWithTextPosition(
            _getImageLocation("05.jpg"), 
            [Position(0, 0), Position(144, 0), Position(0, 144), Position(144, 144)],
            angles = [45, -45, -225, 225]),
        ImageWithTextPosition(
            _getImageLocation("06.jpg"), 
            [Position(10, 170), Position(35, 160), Position(60, 150), Position(75, 135)],
            angles = [20, 5, -10, -30],
            size = 20),
        ]
    
    def drawDizzy(text: str):
        return ImageUtil.renderText(text, random.choice(DizzyUtil()._images))
    
