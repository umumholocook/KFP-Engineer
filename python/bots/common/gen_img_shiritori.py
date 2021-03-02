# This is to generate image with Shiritori result
from common.models.Kuji import Kuji
from PIL import Image

class GenImgShiritori():
    def __init(self, kuji: Kuji):
        self.kuji = kuji
    
    # 步驟
    # 1. load image
    # 2. extract data
    # 3. put text within image
    