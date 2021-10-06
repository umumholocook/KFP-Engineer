from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from typing import Union

class TokenState(Flag):
    INQUOTE = auto()

@dataclass
class BaseData:
    pass

@dataclass(unsafe_hash=True)
class CodeData(BaseData):
    text: str
    lang: str = None

@dataclass(unsafe_hash=True)
class EmojiData(BaseData):
    id: Union[int, str]
    name: str = field(compare=False)
    animated: bool = False
    src: str = field(repr=False, init=False, compare=False)
    alt: str = field(repr=False, init=False, compare=False)
    @property
    def is_unicode_emoji(self):
        return isinstance(self.id, str)
    
class MentionType(Enum):
    USER = auto()
    CHANNEL = auto()
    ROLE = auto()
    EVERYONE = auto()
    HERE = auto()
    
@dataclass(unsafe_hash=True)
class MentionData(BaseData):
    id: int
    type: MentionType
    display_name: str = field(repr=False, init=False, compare=False)

class TimestampStyle(Enum):
    SHORT_TIME = 't'
    LONG_TIME = 'T'
    SHORT_DATE = 'd'
    LONG_DATE = 'D'
    SHORT_DATETIME ='f'
    LONG_DATETIME = 'F'
    RELATIVE_TIME = 'R'
    
    @classmethod
    @property
    def validchars(cls):
        return ''.join(ts.value for ts in TimestampStyle)

@dataclass(unsafe_hash=True)
class TimestampData(BaseData):
    timestamp: int
    style: TimestampStyle = TimestampStyle.SHORT_DATETIME
    str: str = field(repr=False, init=False, compare=False)
