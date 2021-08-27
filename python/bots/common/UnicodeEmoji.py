import emoji
import re
from pathlib import Path

from settings.UnicodeEmojiSetting import ASSETS_DIR

ASSETS_DIR = Path(ASSETS_DIR).absolute()
PATTERN: re.Pattern

def __getattr__(name):
    if name == 'PATTERN':
        return emoji.get_emoji_regexp()
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

def get_name(utf8str):
    return emoji.UNICODE_EMOJI_ENGLISH[utf8str].strip(':')

class Emoji:
    
    def __init__(self, utf8str):
        self.utf8str = utf8str
    
    def __repr__(self):
        return f'UnicodeEmoji({self.utf8str})'
    
    def __eq__(self, other):
        if type(other) is type(self):
            return self.utf8str == other.utf8str
        return NotImplemented
    
    def __hash__(self):
        return hash(self.utf8str)
    
    @property
    def codepoints(self):
        return tuple(map(ord, self.utf8str))
    
    def path(self, *, format=None):
        stem = '-'.join(f'{c:x}' for c in self.codepoints)
        path = (ASSETS_DIR / stem).with_suffix(f'.{format}' if format else '')
        if not path.exists():
            raise FileNotFoundError(f'No corresponding file: {self!r}')
        return path
    
    def url_as(self, *, format=None):
        return self.path(format=format).as_uri()