
class KujiUtil():
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

    
