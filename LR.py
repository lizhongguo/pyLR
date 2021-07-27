from enum import Enum
import re
from typing import ForwardRef, Iterable

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
    def __init__(self, tag, value) -> None:
        self.tag = tag
        self.value = value
    
    def __eq__(self, o: object) -> bool:
        if not o:
            return False
        if not isinstance(o, self.__class__):
            return False
        return self.tag == o.tag

    def __hash__(self) -> int:
        return hash(self.tag) ^ hash(self.value)

    def __str__(self) -> str:
        return 'VT(tag: %s, value: %s)' % (self.tag, str(self.value)) 

class VN:
    """ 非终结符
    """    
    def __init__(self, tag) -> None:
        self.tag = tag

    def __eq__(self, o: object) -> bool:
        if not o:
            return False
        if not isinstance(o, self.__class__):
            return False
        return self.tag == o.tag

    def __hash__(self) -> int:
        return hash(self.tag)

    def __str__(self) -> str:
        return 'VN(tag: %s)' % (self.tag, ) 

# 特殊终结符，表示空值
EPSILON = VT('EPSILON','')
END = VT('END', '$')

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

def printSet(First):
    for vn in First:
        print('VN %s' % str(vn))
        for vt in First[vn]:
            print('VT %s' % str(vt))
        print('VN %s end' % str(vn))

def updateSet(dst:set, src, epsilonNotAllowed=False):
    updated = False
    if isinstance(src, set):
        if epsilonNotAllowed and EPSILON in src:
            src.remove(EPSILON)

        if not src.issubset(dst):
            updated = True
        dst.update(src)
    else:
        if epsilonNotAllowed and src == EPSILON:
            return updated

        updated = src not in dst
        dst.add(src)
    return updated

# 构造First集
def constructFirstSet(rules:dict[VN,Rule]):
    updated = True
    First = {vn:set() for vn in rules}

    while updated:
        updated = False
        for parentVN in rules:
            rule = rules[parentVN]
            assert parentVN == rule.parent

            for child in rule.children:
                for token in child:
                    # 终结符
                    if isinstance(token, VT):
                        # 终结符
                        if token not in First[rule.parent]:
                            updated = True

                        First[rule.parent].add(token)

                        break

                    elif isinstance(token, VN):
                        if not First[token].issubset(First[rule.parent]):
                            updated=True

                        First[rule.parent] |= First[token]

                        # 可推出空匹配，将下一个token的First集合加入parentVN
                        if (EPSILON,) not in rules[token].children:
                            break

    return First

# 将更新过程视为有向图,节点为非终结符,边为更新过程,可以拓扑排序优化构造过程
# 环中的节点可以缩为一点,其First集合必定相同
def testConstructFirstSet():
    E, E_, T, T_, F, PLUS, MUL, LB, RB, ID = VN('E'), VN('E_'), VN('T'), VN('T_'), VN('F'), VT('PLUS','+'), VT('MUL','*'), VT('LB','('), VT('RB', ')'), VT('ID', 'id')


    rule_E = Rule(E)
    rule_E.addChild((T, E_))

    rule_E_ = Rule(E_)
    rule_E_.addChild((PLUS, T, E_))
    rule_E_.addChild((EPSILON,))

    rule_T = Rule(T)
    rule_T.addChild((F,T_))

    rule_T_ = Rule(T_)
    rule_T_.addChild((MUL,F,T_))
    rule_T_.addChild((EPSILON,))

    rule_F = Rule(F)
    rule_F.addChild((LB, E, RB))
    rule_F.addChild((ID,))

    rules = {E:rule_E, E_:rule_E_, T:rule_T, T_:rule_T_, F:rule_F}
    
    First = constructFirstSet(rules)

    printSet(First)

# 获取某个序列的First集合
def getFirstOfSeq(First:dict[VN, Rule], seq:Iterable):
    results = set()

    if len(seq) == 0:
        results.add(EPSILON)
        return results
    
    for token in seq:
        if isinstance(token, VT):
            results.add(token)
            if token is not EPSILON:
                if EPSILON in results:
                    results.remove(EPSILON)
                return results

        elif isinstance(token, VN):
            results.update(First[token])
            if EPSILON not in First[token]:
                if EPSILON in results:
                    results.remove(EPSILON)
                return results

    return results

# 构造Follow集
def constructFollowSet(rules:dict[VN,Rule], First:dict[VN, Rule], beginning:VN):
    # 首先在开始规则的Follow集放入 $
    # 遍历所有规则, 更新Follow集合,直到Follow集合不再更新
    updated = True
    Follow:dict[VN,set] = dict()
    # 在开始文法中加入$，表示结束
    for vn in rules:
        Follow[vn] = set()

    Follow[beginning].add(END)

    while updated:
        updated = False
        # printFirst(Follow)
        for parentVN in rules:
            rule = rules[parentVN]

            # 所有规则中
            for child in rule.children:

                if child[0] == EPSILON:
                    continue

                # A->aBb a的Follow集合增加First(Bb)
                for i in range(len(child)-1):
                    if isinstance(child[i], VN):
                        updated = True if updateSet(Follow[child[i]], getFirstOfSeq(First, child[i+1:]), True) else updated

                #如果b->epsilon, A与B的Follow集相同
                for i in range(len(child)-1, 0, -1):
                    if isinstance(child[i], VN):
                        if EPSILON in getFirstOfSeq(First,child[i+1:]):
                            us = Follow[parentVN] | Follow[child[i]]
                            updated = True if updateSet(Follow[parentVN], us, True) else updated
                            updated = True if updateSet(Follow[child[i]], us, True) else updated


    return Follow

def testConstructFollowSet():
    E, E_, T, T_, F, PLUS, MUL, LB, RB, ID = VN('E'), VN('E_'), VN('T'), VN('T_'), VN('F'), VT('PLUS','+'), VT('MUL','*'), VT('LB','('), VT('RB', ')'), VT('ID', 'id')


    rule_E = Rule(E)
    rule_E.addChild((T, E_))

    rule_E_ = Rule(E_)
    rule_E_.addChild((PLUS, T, E_))
    rule_E_.addChild((EPSILON,))

    rule_T = Rule(T)
    rule_T.addChild((F,T_))

    rule_T_ = Rule(T_)
    rule_T_.addChild((MUL,F,T_))
    rule_T_.addChild((EPSILON,))

    rule_F = Rule(F)
    rule_F.addChild((LB, E, RB))
    rule_F.addChild((ID,))

    rules = {E:rule_E, E_:rule_E_, T:rule_T, T_:rule_T_, F:rule_F}
    
    First = constructFirstSet(rules)
    printSet(First)

    Follow = constructFollowSet(rules, First, E)

    # printFirst(First)
    printSet(Follow)

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
    testConstructFollowSet()