import random

class PoliceResponseUtil():
    GENERAL = [
        "還不快去{action}!!",
        "{name}你怎麼還在, 不是要去{action}嗎?",
        "{name}剛剛不是說要{action}, 怎麼還在?",
        "你再不去{action}我就不理你了, 哼",
        "你快去{action}啦... 我會等你... >////<",
        "{name}很閒喔... 剛剛不是說要{action}?"
        "{name}快去{action}!!"
    ]

    def getResponse():
        return random.choice(PoliceResponseUtil.GENERAL)

    