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
def constructFirstSet(rules:dict[VN,Rule]):
    updated = True
    First = dict()
    while updated:
        for parentVN in rules:
            rule = rules[parentVN]
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

                        break

                    elif isinstance(token, VN):
                        if token not in First:
                            First[token] = set()
                            continue

                        # 空集是任何集合的子集                        
                        if First[token].issubset(First[rule.parent]):
                            continue

                        First[rule.parent] |= First[token]
                        updated=True

                        # 可推出sigma空集，继续
                        if set() not in rules[token]:
                            break

END = VT('$')

# 构造Follow集
def constructFollowSet(rules:dict[VN,Rule], beginning:VN):
    # 首先在开始规则的Follow集放入 $
    # 遍历所有规则, 更新Follow集合,直到Follow集合不再更新
    updated = True
    Follow = dict()
    # 加入$，表示结束
    Follow[beginning] = END

    while updated:
        for parentVN in rules:
            rule = rules[parentVN]
            for child in rule.children:
                # 从后往前遍历规则，更新Follow集合
                first = set()
                followToken = None
                tailIsEmpty = True

                for token in reversed(child):
                    if followToken:
                        if isinstance(token, VN):
                            Follow[token] |= first - EPSILON
                    
                    # 终结符的First集合是它本身
                    if (EPSILON,) in rules[token].children:
                        first |= First[token] - EPSILON
                    else:
                        fisrt = First[token]
                        tailIsEmpty = False

                    if tailIsEmpty:
                        Follow[parentVN] |= first - EPSILON
                        Follow[token] |= Follow[parentVN]

                    followToken = token



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