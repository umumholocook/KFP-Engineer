import re
from zhconv import convert

emoji_pattern = re.compile(
    "["
    u"\U0001F600-\U0001F64F"
    u"\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F6FF"
    u"\U0001F1E0-\U0001F1FF"
    "]+",
    flags=re.UNICODE,
)


class ShiritoriStringUtil:
    @staticmethod
    def remove_emoji(text: str) -> str:
        return emoji_pattern.sub("", text)

    @staticmethod
    def remove_stickers(text: str) -> str:
        return re.sub(r":\w+:", "", text)

    @staticmethod
    def match_the_last_word(history: list[str], word: str) -> bool:
        last_char = convert(history[-1][-1], "zh-hans")
        first_char = convert(word[0], "zh-hans")
        return last_char == first_char

    @staticmethod
    def to_history_string(history: list[str]) -> str:
        if not history:
            return "[]"
        return "".join(f"{word}\n" for word in history)

    @staticmethod
    def split_history_message(message: str) -> list[str]:
        chunk_size = 1800
        return [message[i : i + chunk_size] for i in range(0, len(message), chunk_size)]