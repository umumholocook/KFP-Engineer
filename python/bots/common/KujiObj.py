# Kiji 代表了一個籤
import os, random
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

    def getStartPosition(self):
        if Util.KujiType.OMIKUJI == self.kujitype:
            # get image for OMIKUJI
            return {
                "凶": (625, 100),
                "大吉": (500, 95),
                "半吉": (515, 90),
                "吉": (515, 90),
                "小吉": (625, 100),
                "末小吉": (640, 100),
                "末吉": (640, 100)
            }[self.kuji["status"]]
        return None # don't support LS nor Yi until NINI gives me images

    def __getImageName(self):
        if Util.KujiType.OMIKUJI == self.kujitype:
            # get image for OMIKUJI
            return {
                "凶": random.choice(["bad_01.jpg", "bad_02.jpg", "bad_03.jpg"]),
                "大吉": "big.jpg",
                "半吉": random.choice("half.jpg", "half_02.jpg"),
                "吉": random.choice("normal.jpg", "normal_02.jpg"),
                "小吉": random.choice("small.jpg", "small_02.jpg"),
                "末小吉": "tail_small.jpg",
                "末吉": "tail.jpg"
            }[self.kuji["status"]]
        return None # don't support LS nor Yi until NINI gives me images

    def getPoemLines(self):
        return [self.kuji["poem_line1"], self.kuji["poem_line2"], self.kuji["poem_line3"], self.kuji["poem_line4"]]

    def __getPoem(self):
        return "{}\n{}\n{}\n{}".format(
            self.kuji["poem_line1"],
            self.kuji["poem_line2"],
            self.kuji["poem_line3"],
            self.kuji["poem_line4"])
    
    def __getPoemFromYi(self):
        return "" # TODO(umum) WTF?