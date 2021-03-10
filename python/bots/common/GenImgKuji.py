# This is to generate image with Shiritori result
import io
from common.models.KujiObj import KujiObj
from PIL import Image


class GenImgShiritori():
    def __init(self, kuji: KujiObj):
        self.kuji = kuji
    
    # 步驟
    # 1. load image
    # 2. extract data
    # 3. put text within image
    
    def generateKujiImage(self, kuji: KujiObj) -> bytes:
        imgByteArr = io.BytesIO()
        return imgByteArr.getvalue()