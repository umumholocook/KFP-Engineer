import re
from typing import Optional

from .Datatypes import (
    TokenState as State,
    MentionData, MentionType,
    TimestampData, TimestampStyle,
    EmojiData,
    CodeData,
)
from .. import UnicodeEmoji as uemoji

class Token:
    '''表示語法結構
    
    Args:
        data: 當語法結構為終結符時所負載的資料
        start: 未被解析內部結構的起點
        stop: 未被解析內部結構的終點
    
    Attributes:
        dict: 留下 Token 必要資訊，將語法樹的結構以 dict 儲存
        rule: 語法結構匹配的規則
        state: 語法結構此時的狀態，表示語法結構在特定結構中
        captured: 語法結構所捕獲的字串
        data: 當語法結構為終結符時所承載的資料
        start: 未被解析內部結構的起點
        stop: 未被解析內部結構的終點
        remaining: 剩餘未被解析內部結構的字串
        isterminal: 是否為終結符，若是則有 data 屬性，反之有 start, stop 屬性
    
    '''
    
    def __init__(self, *args, **kwargs):
        self.dict = {'rule': ...}
        self.state: State
        self.captured: str
        self.start: Optional[int]
        self.stop: Optional[int]
        if kwargs:
            self.dict.update(kwargs)
        else:
            self.start, self.stop = args
            self.dict['children'] = []
    
    def __repr__(self):
        if self.isterminal:
            param = f'data={self.data!r})'
        else:
            param = f'remaining=({self.start}, {self.stop})'
        return f'Token<{self.rule!r}>({self.captured!r}, {param})'
    
    @property
    def isterminal(self):
        return 'data' in self.dict
    
    @property
    def remaining(self) -> str:
        return self.captured[self.start:self.stop]
    
    @property
    def rule(self):
        return self.dict['rule']
        
    @rule.setter
    def rule(self, value):
        self.dict['rule'] = value
    
    @property
    def data(self):
        return self.dict['data']
    
    @data.setter
    def data(self, value):
        self.dict['data'] = value
    
    def append_or_update(self, child) -> Optional[str]:
        '''新增或更新子結構，並且將 self.start 移到新的位置
        
        通常新增子結構，但連續子結構的 rule 為 text，會更新成一個子結構

        Returns:
            舊的 data，如果子結構被整合了

        '''
        self.start += len(child.captured)
        children = self.dict['children']
        if child.rule == text and len(children) and children[-1]['rule'] == text:
            # 此處不直接對字串做加法串接
            # 因此從 captured 做 slice，參照出子結構所整合的字串
            old = children[-1]['data']
            cat = child.data
            new = self.captured[self.start-len(old)-len(cat):self.start]
            children[-1]['data'] = child.data = new
            return old
        children.append(child.dict)

class RootToken(Token):
    
    def __init__(self, source):
        super().__init__(0, len(source))
        self.rule = root
        self.state = State(0)
        self.captured = source
        # self.dict['source'] = source

class _Rule():
    
    def __init__(self, pattern, flag, state, isblock, tokenize):
        # 為了預設 flag 為 re.A 所做的因應
        if flag is None:
            flag = re.RegexFlag(0)
        elif not flag & re.U:
            flag |= re.A
        self.pattern = re.compile(pattern, flag)
        self.state = state
        self.isblock = isblock
        self.tokenize = tokenize
    
    def __repr__(self):
        return f'Rule({self.tokenize.__name__})'
    
    def parse(self, source, state, last_captured):
        '''
        
        第一步，yield 是否匹配
        第二步，yield 解析完的結果
        
        '''
        # 已在該 state 中，規則不適用
        if state & self.state:
            return (yield False)
        # block 應獨立成行
        if self.isblock and last_captured and not last_captured.endswith('\n'):
            return (yield False)
        yield (match := self.pattern.match(source))
        
        token = self.tokenize(match)
        token.rule = self
        token.state = state | self.state
        token.captured = match.group()
        yield token
    
def _rule(pattern, flag=re.RegexFlag(0), state=State(0), *, isblock=False):
    return lambda tokenize: _Rule(pattern, flag, state, isblock, tokenize)

# 注意到，規則即使匹配成功
# 仍然可能在 discord 顯示失敗或渲染失敗
# 因為其負載的資料是錯誤的
# 但是其語法結構在 discord 是一致的

@_rule(r'.*')
def root(match):
    pass

@_rule(r'\\([^0-9A-Za-z\s])')
def escape(match):
    return Token(data=match.group(1))

@_rule(r'(\n ?)*\n')
def newline(match):
    return Token(data=match.group())

@_rule(r' {2,}\n')
def linebreak(match):
    return Token(data=None)

@_rule(r'\b_((?:__|\\.|[^\\_])+?)_\b'
       r'|'
       r'\*(?=\S)((?:\*\*|\s+(?:[^*\s]|\*\*)|[^\s*])+?)\*(?!\*)', re.S)
def italics(match):
    group = 1 if match.group(1) else 2
    return Token(match.start(group), match.end(group))

@_rule(r'\*\*(.+?)\*\*(?!\*)', re.S)
def bold(match):
    return Token(match.start(1), match.end(1))

@_rule(r'__(.+?)__(?!_)', re.S)
def underline(match):
    return Token(match.start(1), match.end(1))

@_rule(r'~~(.+?)~~(?!~)', re.S)
def strikethrough(match):
    return Token(match.start(1), match.end(1))
    
@_rule(r'\|\|(.+?)\|\|', re.S)
def spoiler(match):
    return Token(match.start(1), match.end(1))

@_rule(r'<(@!?|#|@&)(\d+)>|@(here)|@(everyone)')
def mention(match):
    if id := match.group(4):
        type = MentionType.EVERYONE
    elif id := match.group(3):
        type = MentionType.HERE
    else:
        id = int(match.group(2))
        type = match.group(1)
        type = (MentionType.USER if type == '@' or type == '@!' else
                MentionType.CHANNEL if type == '#' else
                MentionType.ROLE if type == '@&' else
                None)
    return Token(data=MentionData(id, type))

@_rule(fr'<t\:(\d+)(?:\:([{TimestampStyle.validchars}]))?>')
def timestamp(match):
    timestamp = int(match.group(1))
    if style := match.group(2):
        return Token(data=TimestampData(timestamp, TimestampStyle(style)))
    else:
        return Token(data=TimestampData(timestamp))

@_rule(r'<(a?)\:(\w+)\:(\d+)>')
def custom_emoji(match):
    id = int(match.group(3))
    name = match.group(2)
    animated = bool(match.group(1))
    return Token(data=EmojiData(id, name, animated))

@_rule(uemoji.PATTERN, None)
def unicode_emoji(match):
    id = match.group()
    name = uemoji.get_name(match.group())
    return Token(data=EmojiData(id, name))

@_rule(r'(https?://[^\s<]+[^<.,:;"\')\]\s])')
def url(match):
    return Token(data=match.group())

@_rule(r' *>>> ?(.+)| *> ([^\n]*\n?)', re.S, State.INQUOTE, isblock=True)
def quote(match):
    group = 1 if match.group(1) else 2
    return Token(match.start(group), match.end(group))

@_rule(r'```(?:([+\-.\w]+?)?\s*\n)?(.+?)\n*```', re.S)
def code_block(match):
    text = match.group(2)
    lang = match.group(1)
    return Token(data=CodeData(text, lang))

@_rule(r'`(.*[^`])`(?!`)|``(.*[^`])``(?!`)', re.S)
def code_inline(match):
    return Token(data=match.group(1) or match.group(2))

# 參考來源中的 regex [^0-9A-Za-z\s\u00c0-\uffff]，相當令人困惑
# 在 JS 中，string 是以 UTF-16BE 編碼
# 並且 regex 的行為是以 2 byte 作為 width，匹配 UTF-16BE 編碼的 bytes
# 意即，[^\u00c0-\uffff] 只會匹配 Unicode \u0000-\u00df 的 Codepoint
# 然而，Unicode \u0000-\u00df 的 codepoint 仍有英文以外其他語言一般的字母
# 無法滿足此規則的目的
# 但若考慮 UTF-8
# 0xc0-0xff 正好是 Unicode 0x007f 以上的 Codepoint，UTF-8 才會使用到編碼
# 以外的編碼，UTF-8 只對應到 ASCII 的字元
# 無法確定參考來源究竟想排除那些字元
# 假設這 pattern 是為了排除帶有語義的符號，以此寫出 Python 的 pattern
# 注意到，Python 的 string 是以 UTF-8 編碼
# 不過 regex 的行為是以 codepoint 作為 width，匹配 codepoint 序列
# p.s. \u????，在 JS 代表 UTF-16 的編碼；在 Python 代表 codepoint
@_rule(r'.+?(?=(\W|_)|\n| {2,}\n|https?://|$)', re.U|re.S)
def text(match):
    return Token(data=match.group())

@_rule(r'$')
def empyt(match):
    return Token(data=None)
