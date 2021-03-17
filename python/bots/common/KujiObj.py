# Kiji 代表了一個籤
import os
from common.Util import Util
from PIL import Image

class KujiObj():
    def __init__(self, kuji):
        self.kuji = kuji
        if "ls" == kuji["type"]:
            self.kujitype = Util.KujiType.LUNGSHAN
            return
        if "omikuji" == kuji["type"]:
            self.kujitype = Util.KujiType.OMIKUJI
            return
        if "yi" == kuji["type"]:
            self.kujitype = Util.KujiType.YI
            return

    # main text 指籤詩
    def getMainText(self):
        return {
            Util.KujiType.LUNGSHAN: self.__getPoem(),
            Util.KujiType.OMIKUJI: self.__getPoem(),
            Util.KujiType.YI: self.__getPoemFromYi()
        }[self.kujitype]
    
    def getImage(self):
        if Util.KujiType.OMIKUJI == self.kujitype:
            return Image.open(os.sep.join((os.getcwd(), 'resource', 'image', "shiritori", self.__getImageName())))
        return None

    def __getImageName(self):
        if Util.KujiType.OMIKUJI == self.kujitype:
            # get image for OMIKUJI
            return {
                "凶": "bad.jpg",
                "大吉": "big.jpg",
                "半吉": "half.jpg",
                "吉": "normal.jpg",
                "小吉": "small.jpg",
                "末小吉": "tail_small.jpg",
                "末吉": "tail.jpg"
            }[self.kuji["status"]]
        return None # don't support LS nor Yi until NINI gives me images

    def __getPoem(self):
        return "{}\n{}\n{}\n{}".format(
            self.kuji["poem_line1"],
            self.kuji["poem_line2"],
            self.kuji["poem_line3"],
            self.kuji["poem_line4"])
    
    def __getPoemFromYi(self):
        return "" # TODO(umum) WTF?