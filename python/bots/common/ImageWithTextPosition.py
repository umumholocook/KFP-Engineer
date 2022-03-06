from typing import List, Tuple
from common.Position import Position

# Simple image name and position pair. Each Position 
# Represent each Chinese character's position
class ImageWithTextPosition():
    _yellow = (252, 241, 79)
    _blue = (80, 139, 254)
    image_path: str
    charPositions: List[Position]
    size: int
    angles: List[int]
    colors: List[Tuple[int, int, int]]

    def __init__(self, image_path: str, charPositions:List[Position], size = 50, angles = [0, 0, 0, 0], colors = [_yellow, _yellow, _blue, _blue]):
        self.image_path = image_path
        self.charPositions = charPositions
        self.size = size
        self.angles = angles
        self.colors = colors