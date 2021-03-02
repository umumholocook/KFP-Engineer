# This is to generate image with Shiritori result
from common.models.Kiji import Kuji

class GenImgShiritori():
    def __init(self, kuji: Kuji):
        self.kuji = kuji
    
    # 步驟
    # 1. load image
    # 2. extract data
    # 3. put text within image
    