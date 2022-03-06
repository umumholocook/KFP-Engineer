from typing import List
from common.Position import Position

# Simple image name and position pair. Each Position 
# Represent each Chinese character's position
class ImageWithTextPosition():
    image_path: str
    charPositions: List[Position]

    def __init__(self, image_path: str, charPositions:List[Position]):
        self.image_path = image_path
        self.charPositions = charPositions