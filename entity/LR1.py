from typing import Iterable
from entity.Token import Token,VN,VT, EPSILON, END
from entity.Rule import SingleRule,Rule

class Item:
    # 项目, 某个规则的前pos个条件已经满足
    # 每一个项目由项目id, 和项目位置唯一标定
    def __init__(self, rule:SingleRule, pos:int) -> None:
        self.rule = rule
        self.pos = pos

        # 空推导式直接进入规约状态
        if self.pos<len(self.rule.child) and self.rule.child[self.pos] == EPSILON:
            self.pos = 1

    def nextToken(self):
        if self.pos >= len(self.rule.child):
            return None
        return self.rule.child[self.pos]

    def restToken(self):
        return self.rule.child[self.pos+1:]

    def __hash__(self) -> int:
        return hash(self.rule) ^ hash(self.pos)

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        if isinstance(o, self.__class__):
            return self.rule == o.rule and self.pos == o.pos
        return False


class ItemExtends:
    # 项目, 某个规则的前pos个条件已经满足
    # 每一个项目由项目id, 和项目位置, 和展望符唯一标定
    def __init__(self, rule:SingleRule, pos:int, expectedVT:Iterable[VT]) -> None:
        self.projectItem = Item(rule, pos)

        # 展望符
        self.expectedVT = frozenset( vt for vt in expectedVT)

    def nextToken(self):
        return self.projectItem.nextToken()

    def __hash__(self) -> int:
        return hash(self.projectItem) ^ hash(self.expectedVT)

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        if isinstance(o, self.__class__):
            return self.projectItem == o.projectItem and self.expectedVT == o.expectedVT
        return False


class ItemSet:
    # 项目集
    # 数据结构为 {ProjectItem: ExpectedVT}
    # 一经构建，不允许修改
    def __init__(self, items:Iterable[ItemExtends]) -> None:        
        self.items: dict[Item, frozenset[VT]] = dict()
        for item in items:
            if item.projectItem not in self.items:
                self.items[item.projectItem] = frozenset(item.expectedVT)
            else:
                self.items[item.projectItem] = frozenset( item.expectedVT | self.items[item.projectItem])


    def __hash__(self) -> int:
        v = 0
        for item in self.items:
            v ^= (hash(item) ^ hash(self.items[item])) 
        return v

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        if isinstance(o, self.__class__):
            return self.items == o.items
        return False

    def __str__(self) -> str:
        itemStr = []
        for item in self.items:
            childStr = list(c.tag for c in item.rule.child)
            childStr.insert(item.pos, '~')
            itemStr.append('%s -> %s, (%s)' % (item.rule.parent.tag, ' '.join(childStr), ','.join(token.tag for token in self.items[item]))) 
        return '\n'.join(itemStr)
