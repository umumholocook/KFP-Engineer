import pytest

import inspect
from xml.etree import ElementTree

from common.SuperChatUtil import _sctranslator
from common.SimpleDiscordMarkdown import Parser, Rules, Datatypes

@pytest.mark.parametrize(
    ('texts', 'translateds'),
    [
        (['🙂'], ['', '<span class="emoji-char">🙂</span>']),
        (['🙂', '🙂'], ['', '<span class="emoji-char">🙂🙂</span>']),
        (['a', 'a'], ['aa']),
        (['a🙂', 'a🙂'], ['a', '<span class="emoji-char">🙂</span>a', '<span class="emoji-char">🙂</span>']),
        (['a🙂', '🙂a'], ['a', '<span class="emoji-char">🙂🙂</span>a']),
        (['🙂a', 'a🙂'], ['', '<span class="emoji-char">🙂</span>aa', '<span class="emoji-char">🙂</span>']),
        (['🙂a', '🙂a'], ['', '<span class="emoji-char">🙂</span>a', '<span class="emoji-char">🙂</span>a']),
    ],
)
def test_sctranslator_translate_text(texts, translateds):
    process = _sctranslator.translate_text(*texts)
    translateds_ = [
        next(process),
        *(ElementTree.tostring(e, 'u8', 'html').decode() for e in process)
    ]
    assert translateds == translateds_
    

def test_sctranslator_own_rules():
    rules_ = set(_sctranslator._trans.keys())
    
    assert rules_ >= {Rules.root, *Parser._rules}
    
    datatype_ = set(_sctranslator._transd.keys())
    
    datatype = {d for _, d
                in inspect.getmembers(
                    Rules,
                    lambda o: inspect.isclass(o) and issubclass(o, Datatypes.BaseData)
                )}
    
    assert datatype_ >= set(datatype)








