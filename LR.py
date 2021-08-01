from collections import defaultdict
from enum import Enum
import re
from typing import ForwardRef, ItemsView, Iterable
import queue

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
        if not isinstance(o, VT):
            return False
        return self.tag == o.tag

    def __hash__(self) -> int:
        return hash(self.tag)

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
        if not isinstance(o, VN):
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

class SingleRule:
    """ 单独拆分出来的一条推导规则
    """    
    def __init__(self, parent:VN, child) -> None:
        self.parent = parent
        self.child:tuple = tuple(child)

    def __hash__(self) -> int:
        return hash(self.parent) ^ hash(self.child)

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        
        if not isinstance(o, SingleRule):
            return False
        
        return self.parent == o.parent and self.child == o.child

    def __str__(self) -> str:
        return '%s : %s' % (str(self.parent), ','.join([token for token in self.child]))

class ProjectItem:
    # 项目, 某个规则的前pos个条件已经满足
    # 每一个项目由项目id, 和项目位置唯一标定
    def __init__(self, rule:SingleRule, pos:int) -> None:
        self.rule = rule
        self.pos = 0

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

class ProjectItemExtends:
    # 项目, 某个规则的前pos个条件已经满足
    # 每一个项目由项目id, 和项目位置, 和展望符唯一标定
    def __init__(self, rule:SingleRule, pos:int, expectedVT:Iterable[VT]) -> None:
        self.projectItem = ProjectItem(rule, pos)

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

class Project:
    # 项目集
    # 数据结构为 {ProjectItem: ExpectedVT}
    # 一经构建，不允许修改
    def __init__(self, items:Iterable[ProjectItemExtends]) -> None:        
        self.items: dict[ProjectItem, frozenset[VT]] = dict()
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
def getFirstOfSeq(First:dict[VN, VT], seq:Iterable):
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
def constructFollowSet(rules:dict[VN,Rule], First:dict[VN, VT], beginning:VN):
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

                #如果b->epsilon, B的Follow集增加Follow(A)
                for i in range(len(child)-1, 0, -1):
                    if isinstance(child[i], VN):
                        if EPSILON in getFirstOfSeq(First,child[i+1:]):
                            updated = True if updateSet(Follow[child[i]], Follow[parentVN], True) else updated


    return Follow

class Action:
    def __init__(self) -> None:
        pass

class LR_FSA:
    def __init__(self) -> None:
        pass

def closure(rules:dict[VN, Rule], First:dict[VN, VT], coreToExpectedVT:dict[ProjectItem, set[VT]]):
    if not coreToExpectedVT:
        return None

    # 计算项目闭包
    updated = True
    while updated:
        updated = False
        for projectItem in coreToExpectedVT:
            if isinstance(projectItem.nextToken(), VN):
                rule = rules[projectItem.nextToken()]
                for child in rule.children:
                    followSet = getFirstOfSeq(First, projectItem.restToken() + tuple(coreToExpectedVT[projectItem]))
                    derivedProjectItem = ProjectItem(SingleRule(rule.parent,child), 0)

                    if derivedProjectItem not in coreToExpectedVT:
                        coreToExpectedVT[derivedProjectItem] = set()
                        updated = True
                    
                    if not followSet.issubset(coreToExpectedVT[derivedProjectItem]):
                        coreToExpectedVT[derivedProjectItem] |= followSet
                        updated = True
    
    return [ProjectItemExtends(projectItem.rule,projectItem.pos, coreToExpectedVT[projectItem]) for projectItem in coreToExpectedVT]


# 计算某一项目的后继派生
def deriveProject(rules:dict[VN, Rule], First:dict[VN, VT], project:Project, tokens:Iterable):
    results = dict()
    for token in tokens:
        coreToExpectedVT:dict[ProjectItem, set[VT]] = dict()
        for curItem in project.items:
            if token is not curItem.nextToken():
                continue

            # 接收nextToken, 状态转移, pos+1, 展望符不变
            newProjectItem = ProjectItem(curItem.rule, curItem.pos+1)
            if newProjectItem not in coreToExpectedVT:
                coreToExpectedVT[newProjectItem] = set()
            coreToExpectedVT[newProjectItem] |= project.items[curItem]

        
        if not coreToExpectedVT:
            results[token] = None
            continue

        results[token] = Project(closure(rules,First,coreToExpectedVT))

    return results

# 构建LR(1)自动机
def constructLR1(rules:dict[VN, Rule], beginning:VN):
    # 自动机定义
    # 动作状态

    # 文法定义
    # 文法token序列
    E, E_, T, T_, F, PLUS, MUL, LB, RB, ID = VN('E'), VN('E_'), VN('T'), VN('T_'), VN('F'), VT('PLUS','+'), VT('MUL','*'), VT('LB','('), VT('RB', ')'), VT('ID', 'id')

    S = VN('S')

    tokens = [S, E, E_, T, T_, F, PLUS, MUL, LB, RB, ID]

    rule_S = Rule(S)
    rule_S.addChild((E,))
    beginning = S

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

    rules = {S:rule_S, E:rule_E, E_:rule_E_, T:rule_T, T_:rule_T_, F:rule_F}

    # 项目集定义
    projectIdx = 0
    projects = dict()

    # 构造First集合
    First = constructFirstSet(rules)

    # 将终结符放入开始文法
    assert len(rules[beginning].children) == 1
    child = list(rules[beginning].children)[0]

    # 计算开始项目集
    headProject = Project(closure(rules, First, {ProjectItem(SingleRule(rules[beginning].parent, child),0):set([END,])}))
    projects[headProject] = projectIdx

    # 计算后继项目集，并不断更新，直到没有新的项目集出现
    projectQueue:queue.Queue[Project] = queue.Queue()
    projectQueue.put(headProject)

    # 记录状态转移表
    # src 与 dst分别为项目集, token为vn或者vt
    # {src: token -> dst}
    transformMap:dict[Project,dict[object,Project]] = dict()

    def printProject(project:Project):
        print('project begin')
        for item in project.items:
            print(str(item.rule), item.pos)
        print('project end\n')

    while not projectQueue.empty():
        project = projectQueue.get()
        token_to_project = deriveProject(rules,First,project,tokens)
        for token in token_to_project:
            print(str(token))
            printProject(token_to_project[token])

        transformMap[project] = {token:token_to_project[token] for token in token_to_project}

    # 打印结果

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
    # printSet(First)

    Follow = constructFollowSet(rules, First, E)

    # printSet(First)
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
    # testConstructFollowSet()
    # E, E_, T, T_, F, PLUS, MUL, LB, RB, ID = VN('E'), VN('E_'), VN('T'), VN('T_'), VN('F'), VT('PLUS','+'), VT('MUL','*'), VT('LB','('), VT('RB', ')'), VT('ID', 'id')

    # rule_A = SingleRule(E, (T, E_))
    # rule_B = SingleRule(E, (T, E_, F))
    # rule_C = SingleRule(E, (T, F, E_))
    # rule_D = SingleRule(E, (T, E_, F))

    # print(hash(rule_A), hash(rule_B), hash(rule_C), hash(rule_D))
    # print(rule_A == rule_B, rule_B == rule_C, rule_B == rule_D)
    constructLR1(None,None)
