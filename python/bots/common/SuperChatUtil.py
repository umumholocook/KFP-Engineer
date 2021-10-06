import asyncio
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import pprint
from typing import List, Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from jinja2 import Template

from . import (
    HTMLPainter,
    SimpleDiscordMarkdown as sdcmd,
    UnicodeEmoji as uemoji
)
from .SimpleDiscordMarkdown import Rules
from .SimpleDiscordMarkdown.Datatypes import (
    MentionData, MentionType, TimestampData, EmojiData, CodeData,
)
from data.MaterialColor import COLORS
from settings.SuperChatSetting import EMOJI_FONT_FACE_SRC, EMOJI_FONT_FACE_FORMAT

_RESOURCE_PATHS = [uemoji.ASSETS_DIR]
if (path := Path(EMOJI_FONT_FACE_SRC)).exists():
    _RESOURCE_PATHS.append(path.absolute())
    EMOJI_FONT_FACE_SRC = f'url("{path.as_uri()}")'

_CURRENCY_DISPLAY_NAME = 'Coin.'
_TEMPLATE: Template
_TEMPLATEFILE = Path('resource/templates/superchat.html').absolute()
with _TEMPLATEFILE.open('r', encoding='u8') as f:
    _TEMPLATE = Template(f.read())

# %% 定義資料
class Currency(Enum):
    TWD = auto()

SUPERCHAT_STEP = {
    Currency.TWD: [15, 30, 75, 150, 300, 750, 1500, 3000, 4500, 6000, 7500],
}

@dataclass(frozen=True)
class Style:
    # 預設紅色
    color: str = '#fff'
    name_color: str = 'rgba(255, 255, 255, .7)'
    header_bgcolor: str = COLORS['red']['800']
    content_bgcolor: str = COLORS['red']['600']
    quote_sidebar_color: str = COLORS['red']['200']
    
class ColorRank(Enum):
    # name = lengthlimit
    ZERO = 0
    BLUE = 0
    CYAN = 50
    TEAL = 150
    AMBER = 200
    ORANGE = 225
    PINK = 250
    RED = 270
    RED1 = 290
    RED2 = 310
    RED3 = 330
    RED4 = 350
    
    def __new__(cls, lengthlimit):
        obj = object.__new__(cls)
        obj._value_ = len(cls)
        obj.lengthlimit = lengthlimit
        obj.style = Style()
        return obj
    
    def __bool__(self):
        return bool(self.value)
    
    @classmethod
    def judge(cls, money, currency=Currency.TWD):
        step = SUPERCHAT_STEP[currency]
        l, r = 0, len(step)
        while l < r:
            m = l+r >> 1
            if money > step[m]-1:
                l = m + 1
            elif money < step[m]-1:
                r = m
            else:
                break
        return ColorRank(min(len(cls)-1, l+r >> 1))
    
    def lowerbound(self, currency=Currency.TWD):
        if self == type(self)(0):
            return
        step = SUPERCHAT_STEP[currency]
        return step[self.value-1]
    
    def upperbound(self, currency=Currency.TWD):
        if self == type(self)(len(type(self))-1):
            return
        step = SUPERCHAT_STEP[currency]
        return step[self.value]

for rank, style in {
    ColorRank.BLUE: Style(
        '#fff', 'rgba(255, 255, 255, .7)',
        COLORS['blue']['800'], COLORS['blue']['600'], COLORS['blue']['200'],
    ),
    ColorRank.CYAN: Style(
        '#000', 'rgba(0, 0, 0, .5)',
        COLORS['cyan']['a700'], COLORS['cyan']['a400'], COLORS['cyan']['200'],
    ),
    ColorRank.TEAL: Style(
        '#000', 'rgba(0, 0, 0, .5)',
        COLORS['teal']['a700'], COLORS['teal']['a400'], COLORS['teal']['200'],
    ),
    ColorRank.AMBER: Style(
        '#000', 'rgba(0, 0, 0, .5)',
        COLORS['amber']['600'], COLORS['amber']['400'], COLORS['amber']['100'],
    ),
    ColorRank.ORANGE: Style(
        '#fff', 'rgba(255, 255, 255, .7)',
        COLORS['orange']['900'], COLORS['orange']['700'], COLORS['orange']['200'],
    ),
    ColorRank.PINK: Style(
        '#fff', 'rgba(255, 255, 255, .7)',
        COLORS['pink']['700'], COLORS['pink']['500'], COLORS['pink']['200'],
    ),
}.items():
    rank.style = style

# %% 定義轉譯規則

@dataclass
class WidthFactor:
    enter: int = 0
    exit: int = 0
    append_estimation_enter: Optional[int] = None
    append_estimation_exit: Optional[int] = None

class SCTranslator(sdcmd.Translator):
    
    @staticmethod
    def str_width_estimate(source):
        return 8 * len(source.encode())
    
    # 這是因為 wkhtmltoimage，css font unicode-range 無法作用而所做的因應
    # 將 emoji-char 變成 span 元素，<span class="emoji-char">emoji-char</span>
    # 就可以另外設定字型
    # p.s. 如果情形在複雜點，應該可以為此建立指定的 Rule Object，獨立解析、轉譯
    #      另外使用 rules, parser, sdcmd.Translator 這些 package
    #      或者直接添加當前的 rules，就不用額外 translate_text
    @staticmethod
    def translate_text(*texts):
        '''
        
        第一步，yield text
        第二步與後續，yield elem
        
        '''
        texts = ''.join(texts)
        rangeseq = SCTranslator._find_nonemojistr_range(texts)
        start, stop = next(rangeseq)
        yield texts[start:stop]
        emojistr_start = stop
        for start, stop in rangeseq:
            emojistr_stop = start
            elem = Element('span')
            elem.set('class', 'emoji-char')
            elem.text = texts[emojistr_start:emojistr_stop]
            elem.tail = texts[start:stop]
            yield elem
            emojistr_start = stop
                
    @staticmethod
    def _find_nonemojistr_range(source):
        # 非 emoji 的 start
        start = -len(source)
        for match in uemoji.PATTERN.finditer(source):
            if start != match.start():
                yield start, match.start()
            start = match.end()
        yield start, len(source)
    
    @staticmethod
    @contextmanager
    def estimate(widths_each_line_estimation: List[int], widthfactor=WidthFactor()):
        
        widths_each_line_estimation[-1] += widthfactor.enter
        if (n := widthfactor.append_estimation_enter) is not None:
            if widths_each_line_estimation[-1]:
                widths_each_line_estimation.append(n)
            else:
                widths_each_line_estimation[-1] += n
        # 建立元素前，進入點
        yield
        # 建立元素後，退出點
        widths_each_line_estimation[-1] += widthfactor.exit
        if (n := widthfactor.append_estimation_exit) is not None:
            if widths_each_line_estimation[-1]:
                widths_each_line_estimation.append(n)
            else:
                widths_each_line_estimation[-1] += n
    
    # builder
    
    @sdcmd.Translator.builder(Rules.root)
    def root(self, syntaxnode):
        elem = Element('div')
        elem.set('id', 'message')
        return elem
    
    @sdcmd.Translator.builder(Rules.escape)
    def escape(self, syntaxnode):
        text = syntaxnode['data']
        width = self.str_width_estimate(text)
        return text, WidthFactor(width),
    
    @sdcmd.Translator.builder(Rules.newline)
    def newline(self, syntaxnode):
        return ' ', WidthFactor(self.str_width_estimate(' '))
    
    @sdcmd.Translator.builder(Rules.linebreak)
    def linebreak(self, syntaxnode):
        # 注意這個寬度因子
        return Element('br'), WidthFactor(append_estimation_enter=1),
    
    @sdcmd.Translator.builder(Rules.italics)
    def italics(self, syntaxnode):
        return Element('em'),
    
    @sdcmd.Translator.builder(Rules.bold)
    def bold(self, syntaxnode):
        return Element('strong'),
    
    @sdcmd.Translator.builder(Rules.underline)
    def underline(self, syntaxnode):
        return Element('u'),
    
    @sdcmd.Translator.builder(Rules.strikethrough)
    def strikethrough(self, syntaxnode):
        return Element('s'),
    
    @sdcmd.Translator.builder(Rules.spoiler)
    def spoiler(self, syntaxnode):
        elem = Element('span')
        elem.set('class', 'spoiler')
        return elem
    
    @sdcmd.Translator.builder(Rules.mention)
    def mention(self, syntaxnode):
        return None
    
    @sdcmd.Translator.builder(Rules.timestamp)
    def timestamp(self, syntaxnode):
        return None
    
    @sdcmd.Translator.builder(Rules.custom_emoji)
    def custom_emoji(self, syntaxnode):
        return None
    
    @sdcmd.Translator.builder(Rules.unicode_emoji)
    def unicode_emoji(self, syntaxnode):
        return None
    
    @sdcmd.Translator.builder(Rules.url)
    def url(self, syntaxnode):
        href = syntaxnode['data']
        elem = Element('a')
        elem.set('href', href)
        width = self.str_width_estimate(href)
        return elem, WidthFactor(width),
    
    @sdcmd.Translator.builder(Rules.quote)
    def quote(self, syntaxnode):
        return (Element('blockquote'),
                WidthFactor(append_estimation_enter=0, append_estimation_exit=0))
    
    @sdcmd.Translator.builder(Rules.code_block)
    def code_block(self, syntaxnode):
        elem = Element('code')
        elem.set('class', 'block')
        return elem, WidthFactor(append_estimation_enter=0, append_estimation_exit=0),
    
    @sdcmd.Translator.builder(Rules.code_inline)
    def code_inline(self, syntaxnode):
        return Element('code')
    
    @sdcmd.Translator.builder(Rules.text)
    def text(self, syntaxnode):
        text = syntaxnode['data']
        width = self.str_width_estimate(text)
        return text, WidthFactor(width)
    
    @sdcmd.Translator.builder(Rules.empyt)
    def empyt(self, syntaxnode):
        return ''
    
    # builder_data
    
    @sdcmd.Translator.builder_data(MentionData)
    def mentiondata(self, data):
        prefix = '#' if data.type == MentionType.CHANNEL else '@'
        elem = Element('span')
        elem.set('class', 'mention')
        elem.text = prefix + data.display_name
        width = self.str_width_estimate(elem.text)
        return elem, WidthFactor(width)
    
    @sdcmd.Translator.builder_data(TimestampData)
    def timestampdata(self, data):
        elem = Element('span')
        elem.set('class', 'timestamp')
        elem.text = data.str
        width = self.str_width_estimate(elem.text)
        return elem, WidthFactor(width)
    
    @sdcmd.Translator.builder_data(EmojiData)
    def emojidata(self, data):
        if not hasattr(data, 'src'):
            return f':{data.name}:'
        elem = Element('img')
        elem.set('class', 'emoji')
        elem.set('src', data.src)
        return elem, WidthFactor(28)
                                            
    @sdcmd.Translator.builder_data(CodeData)
    def codedata(self, data):
        width = self.str_width_estimate(data.text)
        return data.text, WidthFactor(width)
    
_sctranslator = SCTranslator()

# %% 定義渲染

_WIDTH_BASIS = 360
_MESSAGE_MAX_HIGHT = 100
_MESSAGE_LINE_CLAMP = 3

def _render(name, avatar, money, rank, message, syntaxnode, data, file=None):
    if message:
        widths_each_line_estimation = [0]
        elemseq = _sctranslator.translate(syntaxnode, data, widths_each_line_estimation)
        elem = next(elemseq)
        message = ElementTree.tostring(elem, method='html').decode()

    html = _TEMPLATE.render(
        style=rank.style,
        emoji_font_face_src=EMOJI_FONT_FACE_SRC,
        emoji_font_face_format=EMOJI_FONT_FACE_FORMAT,
        name=name,
        avatar=avatar,
        currency=_CURRENCY_DISPLAY_NAME,
        money=money,
        message=message,
        message_max_hight=_MESSAGE_MAX_HIGHT,
        message_line_clamp=_MESSAGE_LINE_CLAMP,
    )
    if file:
        with open(file, 'w', encoding='u8') as f:
            pprint.pprint(syntaxnode, f)
            f.write(html)
    return html

@asynccontextmanager
async def render(name, avatar, money, rank, message, syntaxnode, data, *, zoom=1):
    # zoom 設太大的話，wkhtmltoimage 會有些東西渲染得太細，e.g. 下劃線、刪除線
    # 猜測是因為這些東西並不會隨著縮放而跟著變大
    # 但是 wkhtmltoimage 沒有 dpi 可以設，只能用 zoom 參數妥協 
    loop = asyncio.get_running_loop()
    html = await loop.run_in_executor(None, _render,
                                      name, avatar, money, rank,
                                      message, syntaxnode, data)
    async with HTMLPainter.paint(
        html, allowpaths=_RESOURCE_PATHS, quality=20, width=zoom*_WIDTH_BASIS, zoom=zoom,
    ) as imgfp:
        yield imgfp


