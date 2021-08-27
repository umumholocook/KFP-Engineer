from contextlib import contextmanager
import functools as fntl
import inspect
import itertools as ittl

'''TransRule.build, DataRule.build

Param:
    self:
    syntaxnode:

Returns:
    elem: 必須有 text: str, tail: str 屬性
          以及 append, extend, __len__,  __index__ 方法
    *factor: 沒有限制，自訂定義，可以在元素建立前後，估計東西

'''

class Builder:
    '''指定 Rules.Rule 轉換'''
    
    def __init__(self, rule, build):
        self.key = rule
        self.build = build

class Builder_Data:
    '''指定 Datatypes.BaseData 轉換'''
    
    def __init__(self, datatype, build):
        self.key = datatype
        self.build = build

class Translator:
    # 結構: 意為 syntaxnode
    # 元素: 意為轉譯後的物件
    
    def __init__(self):
        
        self._trans = self._make_transdict_from_objmembers(Builder)
        self._transd = self._make_transdict_from_objmembers(Builder_Data)
    
    # 用 genarator 是因為如果多個元素沒有父元素的話，只能一一 yield
    def translate(self, syntaxnode, data,  estimation=None):
        # 預先建立好終結符結構的元素，使得同個資料只會建立一個元素
        terminal = {
            d: self._transd[type(d)](d) for d in data if type(d) in self._transd
        }
        
        elemseq = self._dfs_translate(syntaxnode, terminal, estimation)
        yield from elemseq
    
    def _dfs_translate(self, syntaxnode, terminal, estimation):
        rule = syntaxnode['rule']
        elem, *factors = self._trans[rule](syntaxnode)
        
        with self.estimate(estimation, *factors):
            if isinstance(elem, str):
                return (yield elem)
            
            if 'children' in syntaxnode:
                elem_children = (
                    elem_child
                    for child in syntaxnode['children']
                    for elem_child in self._dfs_translate(child, terminal, estimation)
                )
                return (yield from self._elem_extend(elem, elem_children))
                 
            data = syntaxnode['data']
            elem_child, *child_factors = terminal.get(data, (data,))
            with self.estimate(estimation, *child_factors):
                yield from self._elem_extend(elem, ittl.repeat(elem_child, 1))
    
    def _elem_extend(self, elem, elem_children):
        if elem is None:
            # 表示此元素在轉譯後，沒有實際的節點，直接把子元素丟給上層處理
            return (yield from elem_children)
        texts = [elem.text] if elem.text else []
        for e in elem_children:
            if isinstance(e, str):
                texts.append(e)
            elif e is not None:
                self._elem_extend_text(elem, texts)
                elem.append(e)
                texts = [e.tail] if e.tail else []
        self._elem_extend_text(elem, texts)
        yield elem
    
    def _elem_extend_text(self, elem, texts):
        process = iter(self.translate_text(*texts))
        if len(elem):
            elem[-1].tail = next(process)
        else:
            elem.text = next(process)
        elem.extend(process)
        
    @staticmethod
    def translate_text(*texts):
        yield ''.join(texts)
    
    @staticmethod
    @contextmanager
    def estimate(estimation, *factor):
        # 建立元素前
        yield
        # 建立元素後
        
    @classmethod
    def builder(cls, rule):
        return lambda build: Builder(rule, build)
        
    @classmethod
    def builder_data(cls, datatype):
        return lambda build: Builder_Data(datatype, build)
    
    def _build(self, member, syntaxnode):
        result = member.build(self, syntaxnode)
        # 如果 build 回傳的不是 tuple，要包裝成 tuple
        return result if isinstance(result, tuple) else (result,)

    def _make_transdict_from_objmembers(self, membercls):
        members = inspect.getmembers(self, lambda o: isinstance(o, membercls))
        return {m.key: fntl.partial(self._build, m) for _, m in members}

