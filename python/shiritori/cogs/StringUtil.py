import re

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

class StringUtil():
    def removeEmoji(input:str):
        return emoji_pattern.sub(r'', input)
    
    def removeStickers(input:str):
        return re.sub(r':\w+:', '', input)

    def matchTheLastWord(history, input):
        return history[-1].endswith(input[0])

    def toHistoryString(history):
        if len(history) < 1:
            return '[]'
        result = '['
        for i in range(len(history)):
            word = history[i]
            if i == len(history) -1:
                result += '{}'.format(word)
            else:
                result += '{}, '.format(word)
        return result + ']'
