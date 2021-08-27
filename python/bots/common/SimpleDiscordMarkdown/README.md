# SimpleDiscordMarkdown

Module SimpleDiscordMarkdown 的 package

## 檔案

Dataclasses.py
---

Discord markdown 的資料類別，分離於文本  
有 CodeData, EmojiData, MentionData, TimestampData

Parser.py
---
負責解析 discord markdown 成樹狀結構的 `dict`  
並將本質相同的資料精簡，使之只存在一個

Rules.py
---
定義 discord markdown 的 regex 規則，以及如何轉換成樹狀結構的 `dict`

Translator.py
--- 
定義如何將樹狀結構的 `dict` 轉譯成可指定的資料結構  
可以透過繼承來建立自訂轉譯規則的類別  
獨立於上面三個 package，但依賴樹狀結構的 `dict` 是否符合定義

## 樹狀結構的 `dict`

為以下形式

```py
Node ::= {
    'rule': Hashable,
    ExactOne[
        'children': List[Node],
        'data': Union[str, Hashable],
    ],
}
```