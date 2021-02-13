
class KujiUtil():
    def getImageUrl(status):
        if "大吉" == status:
            return "https://sozai.kingyomon.com/wp-content/uploads/2016/11/daokichi.png"
        if "吉" == status:
            return "https://upload.wikimedia.org/wikipedia/commons/b/b8/%E5%90%89.png"
        return None

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
