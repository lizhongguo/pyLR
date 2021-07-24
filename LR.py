from enum import Enum
import re

class Tag:
    # 非终结符
    Shift = 1
    # 规约动作
    Reduce = 2
    # 转移动作
    Godo = 3

class VT:
    """ 终结符
    """    
    def __init__(self) -> None:
        self.tag = None
        self.value = None
    
    def __eq__(self, o: object) -> bool:
        if not o:
            return False
        if not isinstance(o, self.__class__):
            return False
        return self.tag == o.tag

    def __hash__(self) -> int:
        return hash(self.tag) ^ hash(self.value)

class VN:
    """ 非终结符
    """    
    def __init__(self) -> None:
        self.tag = None

    def __eq__(self, o: object) -> bool:
        if not o:
            return False
        if not isinstance(o, self.__class__):
            return False
        return self.tag == o.tag

    def __hash__(self) -> int:
        return hash(self.tag)

class Rule:
    # 推导规则
    def __init__(self, parent:VN) -> None:
        self.parent = parent
        self.children = set()

    def addChild(self, child):
        if child is None:
            return

        self.children.add(tuple(child))

class Item:
    # 项目, 某个规则的前pos个条件已经满足
    def __init__(self) -> None:
        self.rule = None
        self.pos = 0

        # 展望符
        self.expectedVT = None

class ItemsSet:
    # 项目集
    def __init__(self) -> None:        
        pass
 
class NFA:
    def __init__(self) -> None:
        pass

class DFA:
    def __init__(self) -> None:
        pass

class LRDFA:
    # LR有限状态自动机
    def __init__(self) -> None:
        # Action表
        # Goto表
        pass

# 构造First集
def constructFirstSet(rules:list[Rule]):
    updated = True
    First = dict()
    while updated:
        for rule in rules:
            for child in rule.children:
                for token in child:
                    # 终结符
                    if isinstance(token, VT):
                        if rule.parent not in First:
                            First[rule.parent] = set()

                        # 终结符
                        if token in First[rule.parent]:
                            continue

                        First[rule.parent].add(token)
                        updated = True

                    elif isinstance(token, VN):
                        if token not in First:
                            First[token] = set()
                        
                        if First[token].issubset(First[rule.parent]):
                            continue

                        updated=True

# 构造Follow集
def constructFollowSet():
    pass

# LR(1)
# 构建LR-有限状态自动机, 输入为文法规则, 文法规则 : VN -> VN VT混合序列;
def constructFA(rules:list[Rule], codes:list[VN,VT]):
    pass

# 自动机 状态, 输入 -> 状态 
# 输入结束后确认最终状态

# 使用正则表达式，或者手动构建自动机提取token, 输入为字符串
# 确定有限状态自动机，转非确定有限状态自动机
def extractToken():
    pass

# LR自动机构建AST, 输入为 VT VN序列
def parseExpression():
    pass

if __name__ == '__main__':
    pass