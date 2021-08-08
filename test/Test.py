from typing import Iterable
from entity.Token import Token, VN, VT, EPSILON, END
from entity.Rule import Rule
from utils.formatedPrint import printSet
from algorithm.Common import constructFirstSet,constructFollowSet
from algorithm.LR1 import constructLR1

# 将更新过程视为有向图,节点
# 为非终结符,边为更新过程,可以拓扑排序优化构造过程
# 环中的节点可以缩为一点,其First集合必定相同
def testConstructFirstSet():
    E, E_, T, T_, F, PLUS, MUL, LB, RB, ID = VN('E'), VN('E_'), VN('T'), VN('T_'), VN('F'), VT('PLUS', '+'), VT('MUL','*'), VT('LB','('), VT('RB', ')'), VT('ID', 'id')


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



# 构建LR(1)自动机
def testConstructLR1():
    # 文法定义
    # 文法token序列
    rules:dict[VN, Rule]
    beginning:VN

    E, E_, T, T_, F, PLUS, MUL, LB, RB, ID = VN('E'), VN('E_'), VN('T'), VN('T_'), VN('F'), VT('Plus','+'), VT('Mul','*'), VT('Lb','('), VT('Rb', ')'), VT('Id', 'id')

    S = VN('S')

    tokens = [E, E_, T, T_, F, PLUS, MUL, LB, RB, ID]

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

    # constructLR1(rules, beginning, tokens)

    S_,S,L,R = VN('S_'), VN('S'), VN('L'), VN('R')
    Eq, Pt, Id = VT('Eq','='), VT('Pt', '*'), VT('Id', 'id')

    rule_S_ = Rule(S_)
    rule_S_.addChild((S,))

    rule_S = Rule(S)
    rule_S.addChild((L,Eq,R))
    rule_S.addChild((R,))

    rule_L = Rule(L)
    rule_L.addChild((Pt,R))
    rule_L.addChild((Id,))

    rule_R = Rule(R)
    rule_R.addChild((L,))

    rules = {S_:rule_S_, S:rule_S,L:rule_L,R:rule_R}
    tokens = [S,L,R,Eq,Pt,Id]

    constructLR1(rules,S_,tokens)

