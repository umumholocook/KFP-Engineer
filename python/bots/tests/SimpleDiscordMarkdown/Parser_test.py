import pytest

from common.SimpleDiscordMarkdown import Parser, Rules
from common.SimpleDiscordMarkdown.Datatypes import (
    EmojiData,
    MentionData, MentionType,
    TimestampData, TimestampStyle,
    CodeData,
)

    
@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('*a* **b** _c_ __d__ ~~e~~ ||f|| `g` ``h`` ```j```',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a'}]},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'b'}]},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'c'}]},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'd'}]},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.strikethrough,
                        'children': [{'rule': Rules.text, 'data': 'e'}]},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.spoiler,
                        'children': [{'rule': Rules.text, 'data': 'f'}]},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.code_inline, 'data': 'g'},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.code_inline, 'data': 'h'},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.code_block,
                        'data': CodeData(text='j', lang=None)}]},
         {0: 'a', 1: ' ', 2: 'b', 3: ' ', 4: 'c', 5: ' ', 6: 'd', 7: ' ',
          8: 'e', 9: ' ', 10: 'f', 11: ' ', 'g': 'g', 12: ' ', 'h': 'h', 13: ' ',
          CodeData(text='j', lang=None): CodeData(text='j', lang=None)}),
    ],
)
def test_bracket(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_

    
@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('  \n \n   \n\n',
         {'rule': Rules.root,
          'children': [{'rule': Rules.linebreak, 'data': None},
                       {'rule': Rules.text, 'data': ' '},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.linebreak, 'data': None},
                       {'rule': Rules.newline, 'data': '\n'}]},
         {None: None, 0: ' ', '\n': '\n'}),
    ],
)
def test_line(source, syntaxnode, data):
    source = '  \n \n   \n\n'
    syntaxnode = {'rule': Rules.root,
                  'children': [{'rule': Rules.linebreak, 'data': None},
                               {'rule': Rules.text, 'data': ' '},
                               {'rule': Rules.newline, 'data': '\n'},
                               {'rule': Rules.linebreak, 'data': None},
                               {'rule': Rules.newline, 'data': '\n'}]}
    data = {None: None, 0: ' ', '\n': '\n'}
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_

@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('<@1234><@!2341><#3412><@&4123>',
         {'rule': Rules.root,
          'children': [{'rule': Rules.mention,
                        'data': MentionData(id=1234, type=MentionType.USER)},
                       {'rule': Rules.mention,
                        'data': MentionData(id=2341, type=MentionType.USER)},
                       {'rule': Rules.mention,
                        'data': MentionData(id=3412, type=MentionType.CHANNEL)},
                       {'rule': Rules.mention,
                        'data': MentionData(id=4123, type=MentionType.ROLE)}]},
         {MentionData(id=1234, type=MentionType.USER): MentionData(id=1234, type=MentionType.USER),
          MentionData(id=2341, type=MentionType.USER): MentionData(id=2341, type=MentionType.USER),
          MentionData(id=3412, type=MentionType.CHANNEL): MentionData(id=3412, type=MentionType.CHANNEL),
          MentionData(id=4123, type=MentionType.ROLE): MentionData(id=4123, type=MentionType.ROLE)}),
    ],
)
def test_mention(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_

@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
       ('<t:1234><t:2341:d><t:3412:D><t:4123:A>',
        {'rule': Rules.root,
         'children': [{'rule': Rules.timestamp,
                       'data': TimestampData(timestamp=1234)},
                      {'rule': Rules.timestamp,
                       'data': TimestampData(timestamp=2341, style=TimestampStyle.SHORT_DATE)},
                      {'rule': Rules.timestamp,
                       'data': TimestampData(timestamp=3412, style=TimestampStyle.LONG_DATE)},
                      {'rule': Rules.text, 'data': '<t:4123:A>'}]},
        {TimestampData(timestamp=1234): TimestampData(timestamp=1234),
         TimestampData(timestamp=2341, style=TimestampStyle.SHORT_DATE): TimestampData(timestamp=2341, style=TimestampStyle.SHORT_DATE),
         TimestampData(timestamp=3412, style=TimestampStyle.LONG_DATE): TimestampData(timestamp=3412, style=TimestampStyle.LONG_DATE),
         0: '<t:4123:A>'}),
    ],
)
def test_timestamp(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_
    
@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('🐙🔱🔎🐔💀<:wah:520><a:tako:584578>',
         {'rule': Rules.root,
          'children': [{'rule': Rules.unicode_emoji,
                        'data': EmojiData(id='🐙', name='octopus')},
                       {'rule': Rules.unicode_emoji,
                        'data': EmojiData(id='🔱', name='trident_emblem')},
                       {'rule': Rules.unicode_emoji,
                        'data': EmojiData(id='🔎', name='magnifying_glass_tilted_right')},
                       {'rule': Rules.unicode_emoji,
                        'data': EmojiData(id='🐔', name='chicken')},
                       {'rule': Rules.unicode_emoji,
                        'data': EmojiData(id='💀', name='skull')},
                       {'rule': Rules.custom_emoji,
                        'data': EmojiData(id=520, name='wah')},
                       {'rule': Rules.custom_emoji,
                        'data': EmojiData(id=584578, name='tako', animated=True)}]},
         {EmojiData(id='🐙', name='octopus'): EmojiData(id='🐙', name='octopus'),
          EmojiData(id='🔱', name='trident_emblem'): EmojiData(id='🔱', name='trident_emblem'),
          EmojiData(id='🔎', name='magnifying_glass_tilted_right'): EmojiData(id='🔎', name='magnifying_glass_tilted_right'),
          EmojiData(id='🐔', name='chicken'): EmojiData(id='🐔', name='chicken'),
          EmojiData(id='💀', name='skull'): EmojiData(id='💀', name='skull'),
          EmojiData(id=520, name='wah'): EmojiData(id=520, name='wah'),
          EmojiData(id=584578, name='tako', animated=True): EmojiData(id=584578, name='tako', animated=True)}),
    ],
) 
def test_emoji(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_
  
@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('''https://youtu.be/072tU1tamd0
https://youtu.be/072tU1tamd0?t=2
https://youtu.be/
https://youtu.be/>.''',
         {'rule': Rules.root,
          'children': [{'rule': Rules.url, 'data': 'https://youtu.be/072tU1tamd0'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.url, 'data': 'https://youtu.be/072tU1tamd0?t=2'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.url, 'data': 'https://youtu.be/'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.url, 'data': 'https://youtu.be/>'},
                       {'rule': Rules.text, 'data': '.'}]},
         {'https://youtu.be/072tU1tamd0': 'https://youtu.be/072tU1tamd0',
          '\n': '\n',
          'https://youtu.be/072tU1tamd0?t=2': 'https://youtu.be/072tU1tamd0?t=2',
          'https://youtu.be/': 'https://youtu.be/',
          'https://youtu.be/>': 'https://youtu.be/>',
          0: '.'}),
    ],
)
def test_url(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_
    
@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('''> > > 1
2
>>> > 3
>>> 4
> 5''',
         {'rule': Rules.root,
          'children': [{'rule': Rules.quote,
                        'children': [{'rule': Rules.text, 'data': '> > 1'},
                                     {'rule': Rules.newline, 'data': '\n'}]},
                       {'rule': Rules.text, 'data': '2'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.quote,
                        'children': [{'rule': Rules.text, 'data': '> 3'},
                                     {'rule': Rules.newline, 'data': '\n'},
                                     {'rule': Rules.text, 'data': '>>> 4'},
                                     {'rule': Rules.newline, 'data': '\n'},
                                     {'rule': Rules.text, 'data': '> 5'}]}]},
         {0: '> > 1', '\n': '\n', 1: '2', 2: '> 3', 3: '>>> 4', 4: '> 5'}),
    ],
)
def test_quote(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_
    
@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('''🪶`🪶`
``🪶``
```python
||:
```
```oh
```''',
         {'rule': Rules.root,
          'children': [{'rule': Rules.unicode_emoji,
                        'data': EmojiData(id='\U0001fab6', name='feather')},
                       {'rule': Rules.code_inline, 'data': '\U0001fab6'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.code_inline, 'data': '\U0001fab6'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.code_block,
                        'data': CodeData(text='||:', lang='python')},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.code_block,
                        'data': CodeData(text='oh', lang=None)}]},
         {EmojiData(id='\U0001fab6', name='feather'): EmojiData(id='\U0001fab6', name='feather'),
          '\U0001fab6': '\U0001fab6','\n': '\n',
          CodeData(text='||:', lang='python'): CodeData(text='||:', lang='python'),
          CodeData(text='oh', lang=None): CodeData(text='oh', lang=None)}),
        ('''```python
||:
``````oh
```''',
         {'rule': Rules.root,
          'children': [{'rule': Rules.code_block,
                        'data': CodeData(text='||:', lang='python')},
                       {'rule': Rules.code_block,
                        'data': CodeData(text='oh', lang=None)}]},
         None),
        ('''```oh
```
```python
||:
```''',
         {'rule': Rules.root,
          'children': [{'rule': Rules.code_block,
                        'data': CodeData(text='```', lang='oh')},
                       {'rule': Rules.text, 'data': 'python'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.text, 'data': '||:'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.text, 'data': '```'}]},
         None),
        ('''```oh
``````python
||:
```''',
         {'rule': Rules.root,
          'children': [{'rule': Rules.code_block,
                        'data': CodeData(text='`', lang='oh')},
                       {'rule': Rules.text, 'data': '``python'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.text, 'data': '||:'},
                       {'rule': Rules.newline, 'data': '\n'},
                       {'rule': Rules.text, 'data': '```'}]},
         None),
    ],
)
def test_code(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert not data or data == data_

@pytest.mark.parametrize(
    ('source', 'syntaxnode', 'data'),
    [
        ('',
         {'rule': Rules.root,
          'children': [{'rule': Rules.empyt,
                        'data': None}]},
         {None: None}),
        #######################################################################
        (r'\💎',
         {'rule': Rules.root,
          'children': [{'rule': Rules.escape,
                        'data': '💎'}]},
         {'💎': '💎'}),
        #######################################################################
        ('''*First Line*
🤔, __<:xyz:1234>__, ||Emoji||''',
        {'rule': Rules.root,
         'children': [{'rule': Rules.italics,
                       'children': [{'rule': Rules.text, 'data': 'First Line'}]},
                      {'rule': Rules.newline, 'data': '\n'},
                      {'rule': Rules.unicode_emoji,
                       'data': EmojiData(id='🤔', name='thinking_face')},
                      {'rule': Rules.text, 'data': ', '},
                      {'rule': Rules.underline,
                       'children': [{'rule': Rules.custom_emoji,
                                     'data': EmojiData(id=1234, name='xyz')}]},
                      {'rule': Rules.text, 'data': ', '},
                      {'rule': Rules.spoiler,
                       'children': [{'rule': Rules.text, 'data': 'Emoji'}]}]},
        {0: 'First Line',
        '\n': '\n',
         EmojiData(id='🤔', name='thinking_face'): EmojiData(id='🤔', name='thinking_face'),
         1: ', ',
         EmojiData(id=1234, name='xyz'): EmojiData(id=1234, name='xyz'),
         2: ', ',
         3: 'Emoji'}),
        #######################################################################
        ('''> First Line > :
||Emoji|| 🤾‍♀️ __<a:xyz:1234>__
**Mention*** _<@123>_ ~~<#456>~~ *<@&789>*
* escape \<:xyz:1234>
>>> https://youtu.be/dQw4w9WgXcQ<> `code`''',
        {'rule': Rules.root,
         'children': [{'rule': Rules.quote,
                       'children': [{'rule': Rules.text, 'data': 'First Line > :'},
                                    {'rule': Rules.newline, 'data': '\n'}]},
                      {'rule': Rules.spoiler,
                       'children': [{'rule': Rules.text, 'data': 'Emoji'}]},
                      {'rule': Rules.text, 'data': ' '},
                      {'rule': Rules.unicode_emoji,
                       'data': EmojiData(id='🤾\u200d♀️', name='woman_playing_handball')},
                      {'rule': Rules.text, 'data': ' '},
                      {'rule': Rules.underline,
                       'children': [{'rule': Rules.custom_emoji,
                                     'data': EmojiData(id=1234, name='xyz', animated=True)}]},
                      {'rule': Rules.newline, 'data': '\n'},
                      {'rule': Rules.bold,
                       'children': [{'rule': Rules.text, 'data': 'Mention*'}]},
                      {'rule': Rules.text, 'data': ' '},
                      {'rule': Rules.italics,
                       'children': [{'rule': Rules.mention,
                                     'data': MentionData(id=123, type=MentionType.USER)}]},
                      {'rule': Rules.text, 'data': ' '},
                      {'rule': Rules.strikethrough,
                       'children': [{'rule': Rules.mention,
                                     'data': MentionData(id=456, type=MentionType.CHANNEL)}]},
                      {'rule': Rules.text, 'data': ' '},
                      {'rule': Rules.italics,
                       'children': [{'rule': Rules.mention,
                                     'data': MentionData(id=789, type=MentionType.ROLE)}]},
                      {'rule': Rules.newline, 'data': '\n'},
                      {'rule': Rules.text, 'data': '* escape '},
                      {'rule': Rules.escape, 'data': '<'},
                      {'rule': Rules.text, 'data': ':xyz:1234>'},
                      {'rule': Rules.newline, 'data': '\n'},
                      {'rule': Rules.quote,
                       'children': [{'rule': Rules.url,
                                     'data': 'https://youtu.be/dQw4w9WgXcQ'},
                                    {'rule': Rules.text, 'data': '<> '},
                                    {'rule': Rules.code_inline, 'data': 'code'}]}]},
        {0: 'First Line > :', '\n': '\n', 1: 'Emoji', 2: ' ',
         EmojiData(id='🤾‍♀️', name='woman_playing_handball'): EmojiData(id='🤾‍♀️', name='woman_playing_handball'),
         3: ' ',
         EmojiData(id=1234, name='xyz', animated=True): EmojiData(id=1234, name='xyz', animated=True),
         4: 'Mention*', 5: ' ',
         MentionData(id=123, type=MentionType.USER): MentionData(id=123, type=MentionType.USER),
         6: ' ',
         MentionData(id=456, type=MentionType.CHANNEL): MentionData(id=456, type=MentionType.CHANNEL),
         7: ' ',
         MentionData(id=789, type=MentionType.ROLE): MentionData(id=789, type=MentionType.ROLE),
         8: '* escape ', '<': '<', 9: ':xyz:1234>',
         'https://youtu.be/dQw4w9WgXcQ': 'https://youtu.be/dQw4w9WgXcQ',
         10: '<> ', 'code': 'code'}),
    ],
)
def test_general(source, syntaxnode, data):
    syntaxnode_, data_ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
    assert data == data_

@pytest.mark.parametrize(
    ('source', 'syntaxnode'),
    [
        ('**a**',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'a'}]}]}),
        #######################################################################
        ('***a***',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.bold,
                                      'children': [{'rule': Rules.text,
                                                    'data': 'a'}]}]}]}),
        #######################################################################
        ('*a*a*',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a'}]},
                       {'rule': Rules.text, 'data': 'a*'}]}),
        #######################################################################
        ('*a**a*',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a**a'}]}]}),
        #######################################################################
        ('*a***a*',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a**'}]},
                       {'rule': Rules.text, 'data': 'a*'}]}),
        #######################################################################
        ('**a*a**',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'a*a'}]}]}),
        #######################################################################
        ('**a**a**',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'a'}]},
                       {'rule': Rules.text, 'data': 'a**'}]}),
        #######################################################################
        ('**a***a**',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'a*'}]},
                       {'rule': Rules.text, 'data': 'a**'}]}),
        #######################################################################
        ('**a**a**a**',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'a'}]},
                       {'rule': Rules.text, 'data': 'a'},
                       {'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': 'a'}]}]}),
        # 2 ###################################################################
        ('**',
         {'rule': Rules.root, 'children': [{'rule': Rules.text, 'data': '**'}]}),
        # 3 ####################################################################
        ('***',
         {'rule': Rules.root, 'children': [{'rule': Rules.text, 'data': '***'}]}),
        # 4 ###################################################################
        ('****',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': '**'}]}]}),
        # 5 ###################################################################
        ('*****',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': '*'}]}]}),
        # 6 ###################################################################
        ('******',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.text,
                                                    'data': '**'}]}]}]}),
        # 7 ###################################################################
        ('*******',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.text, 'data': '***'}]}]}),
        # 8 ###################################################################
        ('********',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.italics,
                                                    'children': [{'rule': Rules.text,
                                                                  'data': '**'}]}]}]}]}),
        # 9 ###################################################################
        ('*********',
         {'rule': Rules.root,
          'children': [{'rule': Rules.bold,
                        'children': [{'rule': Rules.bold,
                                      'children': [{'rule': Rules.text,
                                                    'data': '*'}]}]}]}),
        # 10 ##################################################################
        ('**********',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.italics,
                                                    'children': [{'rule': Rules.italics,
                                                              'children': [{'rule': Rules.text,
                                                                            'data': '**'}]}]}]}]}]}),
    ],
)
def test_asterisk(source, syntaxnode):
    syntaxnode_, _ = Parser.parse(source)
    assert syntaxnode == syntaxnode_

@pytest.mark.parametrize(
    ('source', 'syntaxnode'),
    [
        ('__a__',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'a'}]}]}),
        #######################################################################
        ('___a___',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.underline,
                                      'children': [{'rule': Rules.text,
                                                    'data': 'a'}]}]}]}),
        #######################################################################
        ('a_a_',
         {'rule': Rules.root,
          'children': [{'rule': Rules.text, 'data': 'a'},
                       {'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a'}]}]}),
        #######################################################################
        ('_a_a',
         {'rule': Rules.root, 'children': [{'rule': Rules.text, 'data': '_a_a'}]}),
        #######################################################################
        ('_a_a_',
         {'rule': Rules.root,
          'children': [{'rule': Rules.text, 'data': '_a'},
                       {'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a'}]}]}),
        #######################################################################
        ('_a__a_',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': 'a__a'}]}]}),
        #######################################################################
        ('_a___a_',
         {'rule': Rules.root,
          'children': [{'rule': Rules.text, 'data': '_a'},
                       {'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': '__a'}]}]}),
        #######################################################################
        ('__a_a__',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'a_a'}]}]}),
        #######################################################################
        ('__a__a__',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'a'}]},
                       {'rule': Rules.text, 'data': 'a__'}]}),
        #######################################################################
        ('__a___a__',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'a_'}]},
                       {'rule': Rules.text, 'data': 'a__'}]}),
        #######################################################################
        ('__a__a__a__',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'a'}]},
                       {'rule': Rules.text, 'data': 'a'},
                       {'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': 'a'}]}]}),
        # 2 ###################################################################
        ('__',
         {'rule': Rules.root, 'children': [{'rule': Rules.text, 'data': '__'}]}),
        # 3 ####################################################################
        ('___',
         {'rule': Rules.root, 'children': [{'rule': Rules.text, 'data': '___'}]}),
        # 4 ###################################################################
        ('____',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.text, 'data': '__'}]}]}),
        # 5 ###################################################################
        ('_____',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': '_'}]}]}),
        # 6 ###################################################################
        ('______',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.text,
                                                    'data': '__'}]}]}]}),
        # 7 ###################################################################
        ('_______',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.text, 'data': '___'}]}]}),
        # 8 ###################################################################
        ('________',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.italics,
                                                    'children': [{'rule': Rules.text,
                                                              'data': '__'}]}]}]}]}),
        # 9 ###################################################################
        ('_________',
         {'rule': Rules.root,
          'children': [{'rule': Rules.underline,
                        'children': [{'rule': Rules.underline,
                                      'children': [{'rule': Rules.text,
                                                    'data': '_'}]}]}]}),
        # 10 ##################################################################
        ('__________',
        {'rule': Rules.root,
         'children': [{'rule': Rules.italics,
                       'children': [{'rule': Rules.italics,
                                     'children': [{'rule': Rules.italics,
                                                'children': [{'rule': Rules.italics,
                                                              'children': [{'rule': Rules.text,
                                                                            'data': '__'}]}]}]}]}]}),
    ],
)    
def test_underline(source, syntaxnode):
    syntaxnode_, _ = Parser.parse(source)
    assert syntaxnode == syntaxnode_

@pytest.mark.parametrize(
    ('source', 'syntaxnode'),
    [
        ('*_a_*',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.text,
                                                    'data': 'a'}]}]}]}),
        #######################################################################
        ('_*a*_',
         {'rule': Rules.root,
          'children': [{'rule': Rules.italics,
                        'children': [{'rule': Rules.italics,
                                      'children': [{'rule': Rules.text,
                                                    'data': 'a'}]}]}]}),
    ],
)
def nest_test(source, syntaxnode):
    syntaxnode_, _ = Parser.parse(source)
    assert syntaxnode == syntaxnode_
