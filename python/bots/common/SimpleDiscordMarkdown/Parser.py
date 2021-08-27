'''將 Discord 的訊息內容解析成簡單的語法樹

Discord 所客製化的 Markdown 沒有現成套件可以使用
因為 Markdown 原始支援更多語法，現成套件會解析出多餘的結構
並且 Discord 另外有自定義的語法，i.e. Mention, Emoji...
實作 LL 似乎不容易，因為 Markdown 的語法有些寬容、歧義與互斥嵌套組合
連 Discord 在網頁版與手機版，所解析語法的結果也不一致
此模組以盡量貼近 Discord 所呈現的 Markdown
除了不解析 Code 區塊的文本，其餘以接近 Discord 的方法解析 
參考了 SimpleAST 為主及 simple-markdown 的語法規則
然而 Discord 並沒有公開所有規則
並且 Discord Github 上的規則似乎與實際上的呈現仍略有差異
為了彌補與比較，另外參考第三方所寫語法規則

Example:
    >>> form common.simple_discord_markdown import parser
    >>> print(parser.parse('*First Line*\n🤔, __<:xyz:1234>__, ||Emoji||'))
    ({'rule': Rule(root),
      'children': [{'rule': Rule(italics),
                    'children': [{'rule': Rule(text), 'data': 'First Line'}]},
                   {'rule': Rule(newline), 'data': None},
                   {'data': EmojiData(id='🤔', name='thinking_face', animated=False),
                    'rule': Rule(unicode_emoji)},
                   {'data': ', ', 'rule': Rule(text)},
                   {'rule': Rule(underline),
                    'children': [{'data': EmojiData(id=1234, name='xyz', animated=False),
                                  'rule': Rule(custom_emoji)}]},
                   {'data': ', ', 'rule': Rule(text)},
                   {'rule': Rule(spoiler),
                    'children': [{'rule': Rule(text), 'data': 'Emoji'}]}]},
     {0: 'First Line',
      None: None,
      EmojiData(id='🤔', name='thinking_face', animated=False): EmojiData(id='🤔', name='thinking_face', animated=False),
      1: ', ',
      EmojiData(id=1234, name='xyz', animated=False): EmojiData(id=1234, name='xyz', animated=False),
      2: ', ',
      3: 'Emoji'})
    
Reference:
    https://github.com/discord/SimpleAST
    https://github.com/discord/simple-markdown
    https://github.com/brussell98/discord-markdown
    https://blog.discord.com/how-discord-renders-rich-messages-on-the-android-app-67b0e5d56fbe

'''
from typing import Tuple

from . import Rules

_rules = [
    Rules.escape,
    Rules.newline,
    Rules.linebreak,
    Rules.italics,
    Rules.bold,
    Rules.underline,
    Rules.strikethrough,
    Rules.spoiler,
    Rules.mention,
    Rules.timestamp,
    Rules.custom_emoji,
    Rules.unicode_emoji,
    Rules.url,
    Rules.quote,
    Rules.code_block,
    Rules.code_inline,
    Rules.text,
    Rules.empyt,
]

class ParseError(Exception):
    pass

def parse(source) -> Tuple[dict, dict]:
    '''
    
    Returns:
        syntaxnode: 語法結構
            SyntaxNode ::= {
                'rule': Rule,
                ExactOne[
                    'data': Union[str, BaseData]
                    'children': List[SyntaxNode],
                ],
            }
        data: 蒐集 syntaxnode 裡所參照的資料
            Dict[
                Union[Tuple[int, str], BaseData]:
                Union[Tuple[int, str], BaseData],
            ]
    
    '''
    stack = []
    data = {}
    root = Rules.RootToken(source)
    stack.append(root)
    last_captured = ''
    # 讓不同位置的子字串可以分別
    text_count = 0
    while stack:
        token = stack.pop()
        for rule in _rules:
            process = rule.parse(token.remaining, token.state, last_captured)
            process = iter(process)
            if match := next(process):
                break
        else:
            raise ParseError(f'Failed to find rule into token: {token!r}')
        child_token = next(process)
        old = token.append_or_update(child_token)
        last_captured = child_token.captured
        if token.remaining:
            stack.append(token)
        if child_token.isterminal:
            if old:
                text_count -= 1
            if child_token.rule == Rules.text:
                data[text_count] = child_token.data
                text_count += 1
            else:
                # 如果該資料已出現過，替換掉
                child_token.data = data.setdefault(child_token.data, child_token.data)
        else:
            stack.append(child_token)
    return root.dict, data
