from common.Util import Util
import pytest
from common.models.KujiObj import KujiObj

class TestKuji():
    def setup_method(self):
        self.testKuji = {
            "title":"第一",
            "status":"大吉",
            "poem_line1":"七寶浮圖塔",
            "poem_line1_explain":"就像出現了用美麗寶石做成的佛塔般地，似乎會有非常好的事情。",
            "poem_line2":"高峰頂上安",
            "poem_line2_explain":"因為能改用放眼萬事的立場，可以得到周圍的人們的信賴吧。",
            "poem_line3":"眾人皆仰望",
            "poem_line3_explain":"合乎正道的你的行為，能被很多人的認同及鼓勵。",
            "poem_line4":"莫作等閒看",
            "poem_line4_explain":"不用隨便的態度看事情，用正確的心思會招來更多的好的結果。",
            "type": "omikuji",
            "payload":{
                "願望":"會充分地實現吧。",
                "疾病":"會治癒吧。",
                "盼望的人":"會出現吧。",
                "遺失物":"變得遲遲地才找到吧。",
                "蓋新居、搬家、嫁娶、旅行、交往等":"諸事皆順。"
            }
        }
        pass
    def teardown_method(self):
        pass

    def test_kujiType(self):
        kuji = KujiObj(self.testKuji)
        assert kuji.kujitype == Util.KujiType.OMIKUJI

    def test_getMainText(self):
        kuji = KujiObj(self.testKuji)
        expectedMainText = "{}\n{}\n{}\n{}".format(
            "七寶浮圖塔",
            "高峰頂上安",
            "眾人皆仰望",
            "莫作等閒看"
        )
        assert kuji.getMainText() == expectedMainText