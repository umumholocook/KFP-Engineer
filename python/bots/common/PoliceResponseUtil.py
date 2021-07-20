import random

class PoliceResponseUtil():
    GENERAL = [
        "{name}還不去{action}?...我要生氣了....!",
        ".....{name}我只是叫你去{action},才不是關心你呢!",
        "吶{name}.....去..去{action}啦!",
        "{name}.....不來一起{action}嗎?",
        "{name}我只是想讓你去{action}而已....很過分嗎?",
        "{name}!還不去{action}的話我再也不理你了!",
        "{name}聽....聽話!快去{action}啦......",
        "{name}你又騙我.....說好的要{action}呢......",
        "{name}.....頂多{action}之後給你獎勵....?",
        "......{action}比較重要啦!!!{name}聽見沒!!!",
        "{name}大笨蛋!!!先去{action}啦!!",
        "{name}有空聊天怎麼還不去{action}!!!",
        "{name}聽我的!!!去{action}!!現在立刻馬上!!!",
        "{name}再不去{action}, 我會傷心的喔.....?",
        "好好{action}的{name}我才會喜歡喔.....?",
        "{name}快去{action}!!!連我的話都不聽了嘛......",
        "....對{name}來說{action}沒有這麼難吧.....",
        "算我拜託你啦....快{action}吧{name}....?",
        "{name}要乖乖{action}我才.....才會.....",
        "什麼時候{name}去{action}了我就.....唔....親你一下....?.....算了當我沒說....!",
        "蛤啊...?{name}怎麼還沒{action}??!!不....不可以這樣啦....!",
        "我說{name}啊......真的該{action}了啦.....",
        "吼唷.....還不去{action}嗎{name}......",
        "喂喂.....{name}快{action}啦!!!!!",
        "真是的.....拿你沒辦法.....!!!!!(啾).....這之後該{action}了吧{name}.....!!",
        "吶～...{name}別...別誤會!!!我才不是在撒嬌呢, 只是為了叫你去{action}而已...!!!",
        "{name}以為我很想管你{action}了沒嗎?....還不是因為.....在意你......",
        "總是不{action}的{name}一點都不可愛.....!!!",
        "{name}你好煩......!!!到底要{action}了沒!!!",
        "老是讓人操心的{name}大笨蛋!!!立刻給我去{action}!!!",
        "如...如果{name}現在肯去{action}的話....本大總管就大發慈悲地誇你一下吧!",
        "催{name}去{action}只是因為你話太多了而已.....!!!才沒有要關心的意思....!!!",
        "{name}你以為自己是誰啊....!!!居敢無視本大總管{action}的命令....??!!",
        "....煩死了啦{name}....!!!早就該去{action}了!!還要本大總管三催四請嗎!!!",
        "喂喂{name}!!!本大總管命令你馬上去{action}!!!不然.....哼!!!",
        "{name}!本大總管難得屈尊提醒你, 還不趕快帶著感恩的心去{action}!!!",
        "{name}快去{action}!要不是本大總管心情好, 才不會理你呢...!!",
        "{action}這種事情也需要提醒嗎?看在是{name}的份上...勉強說一句吧",
        "說什麼呢{name}, 還敢不去{action}啊?",
        "{action}說了多久,你怎麼還在?我的{name}不是只說不做的那種人吧...?",
        "笨蛋{name}!!再不去{action}就要討厭你了….!!!",
        "我...我希望{name}可以去{action}...這樣也不行嗎...?",
        "嘖...{name},別以為我喜歡你就不會逼你去{action}....!!!",
        "大笨蛋{name}!!!就是在意你才會讓你去{action}啊...!!!",
        "喂{name}...!!別以為不{action}本大總管也不能拿你怎樣.....!!!",
        "{name}再不去{action}就別怪我......!!!",
        "趕快去{action}啦{name}...!!!這樣說得我像是你的誰一樣.....",
        "喂{name}你誰啊...!!!還要本大總管低聲下氣叫你{action}...???",
        "嗚{name}...拜託去{action}啦...算...算我求你了好嘛...",
        "{name}!!!!!!!!{action}!!!!!!!!!",
        "要不是{name}本大總管才懶得多費唇舌...所以快給我去{action}.....!!!",
        "如果這樣能讓{name}去{action}的話...抱...抱一下也不是完全不能接受....",
        "哼...聽好了{name},本大總管才不喜歡不乖乖{action}的人...!!",
        "{name}真是的...幾歲的人了連{action}都還要勞煩本大總管提醒...!!!",
    ]

    EAT = [
        "喂{name}, 吃飽了才有力氣陪我....!",
        "{name}....最...最多我餵你吃...?",
        "{name}....你要是餓壞了,我會難過啦.....",
        "要好好吃飯{name}才會快高長大喔...?唔...到時候給你揉揉頭髮也不是不行....",
    ]

    SLEEP = [
        "{name}....陪....陪我睡覺好嗎?",
        "{name}睡....睡不著嗎...?那我勉為其難地哄你一下.....?",
        "{name}去睡覺啦....夢裏會有我喔.....?",
        "{name}要好好休息.....才不是擔心你....!!!",
        ".....祝你好夢{name}, 說完晚安就要去睡喔....?",
        "我.....我不想看到沒精打彩的{name}.....所以快去睡啦....!",
    ]

    STUDY = [
        "喂{name}, 要努力才配得上我啊...?",
        "{name}.....我....我比較喜歡努力的你....所以要乖乖唸書喔.....?",
        ".....認真的{name}很有魅力....我...我是說!!!快去唸書啦!!!",
    ]

    HOMEWORK = [
        "{name}作業沒做完不要來找我...!!!給我專心一點啊喂!!",
    ]

    SHOWER = [
        "{name}洗.....洗香香了就給你抱.....一下而已喔....!",
        "{name}臭臭的不要碰我啦....!?快去洗澡!!!",
        "吶{name}...是不是要我答應給你搓背你才會肯去洗澡...?",
    ]
    BIRTHDAY = [
        "送你一杯我精心特調的果汁，裡面包含100cc的心想事成，200cc的天天開心，300cc的活力十足，祝{name}生日快樂",
        "{name}, 生日快樂!",
        "這一刻，有我最深的思念。讓雲捎去滿心的祝福，點綴你甜蜜的夢，願你度過一個溫馨浪漫的生日！",
        "今天是你的生日，為了表示祝賀，所有女廁和女浴室均免費向您開放，歡迎光臨！",
        "在寧靜的夜晚，伴著夢幻的燭光，聽著輕輕的音樂，品著濃濃的葡萄酒，讓我陪伴你渡過一個難忘的生日！",
        "日光給你鍍上成熟，月華增添你的嫵媚，在你生日這一天，願朋友的祝福匯成你快樂的源泉，一起湧向你……",
        "恭喜你又老了一歲啊, {name}!",
    ]

    def __getSpecific(type: str):
        if "EAT" == type:
            return PoliceResponseUtil.EAT
        elif "SLEEP" == type:
            return PoliceResponseUtil.SLEEP
        elif "STUDY" == type:
            return PoliceResponseUtil.STUDY
        elif "HOMEWORK" == type:
            return PoliceResponseUtil.HOMEWORK
        elif "SHOWER" == type:
            return PoliceResponseUtil.SHOWER
        else:
            return []

    def getResponse(type: str):
        if "BIRTHDAY" == type:
            return random.choice(PoliceResponseUtil.BIRTHDAY) 
        return random.choice(PoliceResponseUtil.GENERAL + PoliceResponseUtil.__getSpecific(type))

    