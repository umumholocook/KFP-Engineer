from random import randint
from data.yi import YI
class KujiUtil():

    def getImageNameLs(status):
        if "下籤" == status:
            return "low.png"
        if "中籤" == status:
            return "middle.png"
        if "上籤" == status:
            return "up.png"
    
    def getImageUrlLs(status):
        return "./resources/{}".format(KujiUtil.getImageNameLs(status))

    def getColorLs(status):
        if "下籤" == status:
            return 0x5A4A4F
        if "中籤" == status:
            return 0x970A8B
        if "上籤" == status:
            return 0xF10A53
        return
        
    def getImageName(status):
        if "大吉" == status:
            return "big_ji.png"
        if "小吉" == status:
            return "small_ji.png"
        if "吉" == status:
            return "ji.png"
        if "半吉" == status:
            return "half_ji.png"
        if "末吉" == status:
            return "end_ji.png"
        if "末小吉" == status:
            return "small_ji_end.png"
        if "凶" == status:
            return "bad.png"

    def getImageUrl(status):
        return "./resources/{}".format(KujiUtil.getImageName(status))

    def getColor(status):
        if "大吉" == status:
            return 0xFFBC03
        if "小吉" == status:
            return 0xFF5E00
        if "吉" == status:
            return 0xFF1E00
        if "半吉" == status:
            return 0xC21700
        if "末吉" == status:
            return 0x800F00
        if "末小吉" == status:
            return 0x5C0B00
        if "凶" == status:
            return 0x170300
        return

    def getYiColor(yi):
        if yi == "乾卦": 
          return 0xF82551
        if yi == "坤卦": 
          return 0xFF006B
        if yi == "屯卦": 
          return 0xFF009F
        if yi == "蒙卦": 
          return 0xFF00C7
        if yi == "需卦": 
          return 0xBD00FF
        if yi == "訟卦": 
          return 0x7F00FF
        if yi == "師卦": 
          return 0x4F00FF
        if yi == "比卦": 
          return 0x0030FF
        if yi == "小畜卦": 
          return 0x006FFF
        if yi == "履卦": 
          return 0x0099FF
        if yi == "泰卦": 
          return 0x00DDFF
        if yi == "否卦": 
          return 0x00FFDB
        if yi == "同人卦": 
          return 0x00FFB7
        if yi == "大有卦": 
          return 0x00FF72
        if yi == "謙卦": 
          return 0x00FF27
        if yi == "豫卦": 
          return 0x12FF00
        if yi == "隨卦": 
          return 0x95FF00
        if yi == "蠱卦": 
          return 0xD6FF00
        if yi == "臨卦": 
          return 0xFFE000
        if yi == "觀卦": 
          return 0xFFB200
        if yi == "噬嗑卦": 
          return 0xFF8D00
        if yi == "賁卦": 
          return 0xFF5C00
        if yi == "剝卦": 
          return 0xFF4500
        if yi == "復卦": 
          return 0xFA6868
        if yi == "无妄卦": 
          return 0xFA687E
        if yi == "大畜卦": 
          return 0xFA68A3
        if yi == "頤卦": 
          return 0xFA68BA
        if yi == "大過卦": 
          return 0xFA68CA
        if yi == "坎卦": 
          return 0xFA68E3
        if yi == "離卦": 
          return 0xC768FA
        if yi == "咸卦": 
          return 0xA068FA
        if yi == "恒卦": 
          return 0x8968FA
        if yi == "遯卦": 
          return 0x6874FA
        if yi == "大壯卦": 
          return 0x688DFA
        if yi == "晉卦": 
          return 0x68A5FA
        if yi == "明夷卦": 
          return 0x68C3FA
        if yi == "家人卦": 
          return 0x68D5FA
        if yi == "睽卦": 
          return 0x6839FA
        if yi == "蹇卦": 
          return 0x68FAF8
        if yi == "解卦": 
          return 0x68FACE
        if yi == "損卦": 
          return 0x68FAA1
        if yi == "益卦": 
          return 0x79FA68
        if yi == "夬卦": 
          return 0x8EFA68
        if yi == "姤卦": 
          return 0xB0FA68
        if yi == "萃卦": 
          return 0xCFFA68
        if yi == "升卦": 
          return 0xE9FA68
        if yi == "困卦": 
          return 0xFAE968
        if yi == "井卦": 
          return 0xFAC768
        if yi == "革卦": 
          return 0xFAB468
        if yi == "鼎卦": 
          return 0xFA8D68
        if yi == "震卦": 
          return 0xFA7068
        if yi == "艮卦": 
          return 0xB61919
        if yi == "漸卦": 
          return 0xB6193C
        if yi == "歸妹卦": 
          return 0xB61972
        if yi == "豐卦": 
          return 0xB6199E
        if yi == "旅卦": 
          return 0xA719B6
        if yi == "巽卦": 
          return 0x8719B6
        if yi == "兌卦": 
          return 0x6919B6
        if yi == "渙卦": 
          return 0x4119B6
        if yi == "節卦": 
          return 0x192DB6
        if yi == "中孚卦": 
          return 0x196FB6
        if yi == "小過卦": 
          return 0x19ADB6
        if yi == "既濟卦": 
          return 0x19B68A
        if yi == "未濟卦": 
          return 0x19B644

    def __getYao():
        collection = (randint(0, 1),)
        collection = collection + (randint(0, 1),)
        collection = collection + (randint(0, 1),)

        if collection.count(1) == 3:
            # 老陽 變卦 陰爻—-
            return 0
        if collection.count(0) == 2:
            # 少陰 陰爻—-
            return 0
        return 1 # 老陰 變卦 陽爻— 或是 少陽 陽爻—
    
    def getTargetedYi(skyIndex:int, bottomIndex:int):
        return YI[skyIndex][bottomIndex]

    def getYi():
        bottom = (KujiUtil.__getYao(), KujiUtil.__getYao(), KujiUtil.__getYao())
        sky = (KujiUtil.__getYao(), KujiUtil.__getYao(), KujiUtil.__getYao())
        
        bottomIndex = bottom[2]*4 + bottom[1]*2 + bottom[0]
        skyIndex = sky[2]*4 + sky[1]*2 + sky[0]

        return (skyIndex, bottomIndex)
        

    
