from entity.Graph import IndexedSet
from typing import Iterable
from entity.Token import Token, VN, VT, EPSILON, END
from entity.Rule import Rule, SingleRule
from entity.LR1 import Action, ActionKind,  ItemSet,Item,ItemExtends, LR1_FSA
from algorithm.Common import constructFirstSet, getFirstOfSeq
import queue
import graphviz

def closure(rules:dict[VN, Rule], First:dict[VN, VT], coreToExpectedVT:dict[Item, set[VT]]):
    if not coreToExpectedVT:
        return None

    # 计算项目闭包
    updated = True
    while updated:
        updated = False

        tmpCoreToExpectedVT = dict()

        # dict在运行时不允许修改, 重新设计更新算法
        for item in coreToExpectedVT:
            if isinstance(item.nextToken(), VN):
                rule = rules[item.nextToken()]
                for child in rule.children:

                    # 还是需要改变, 展望符作为follow集后加进去
                    followSet = getFirstOfSeq(First, item.restToken(), coreToExpectedVT[item])
                    derivedItem = Item(SingleRule(rule.parent,child), 0)

                    if derivedItem not in coreToExpectedVT:
                        tmpCoreToExpectedVT[derivedItem] = followSet
                        updated = True
                        continue

                    if not followSet.issubset(coreToExpectedVT[derivedItem]):
                        tmpCoreToExpectedVT[derivedItem] = coreToExpectedVT[derivedItem] | followSet
                        updated = True
        
        for item in tmpCoreToExpectedVT:
            coreToExpectedVT[item] = tmpCoreToExpectedVT[item]
    
    return [ItemExtends(item.rule,item.pos, coreToExpectedVT[item]) for item in coreToExpectedVT]


# 计算某一项目的后继派生
def deriveItemSet(rules:dict[VN, Rule], First:dict[VN, VT], itemSet:ItemSet, tokens:Iterable):
    results = dict()
    for token in tokens:
        coreToExpectedVT:dict[Item, set[VT]] = dict()
        for curItem in itemSet.items:
            if token is not curItem.nextToken():
                continue

            # 接收nextToken, 状态转移, pos+1, 展望符不变
            newItemSet = Item(curItem.rule, curItem.pos+1)
            if newItemSet not in coreToExpectedVT:
                coreToExpectedVT[newItemSet] = set()
            coreToExpectedVT[newItemSet] |= itemSet.items[curItem]

        
        if not coreToExpectedVT:
            results[token] = None
            continue

        results[token] = ItemSet(closure(rules,First,coreToExpectedVT))

    return results

def visLR1(transformMap:dict[ItemSet,dict[object,ItemSet]], itemSetToIdx:IndexedSet):
    e = graphviz.Digraph('ER', filename='er.gv', engine='dot',graph_attr={'size':'100,50'})
    # e.attr(rankdir='LR')
    e.attr('node', shape='box')

    for srcItemSet in transformMap:
        e.node('%d' % itemSetToIdx.getIdx(srcItemSet), label='P%d\n%s' % (itemSetToIdx.getIdx(srcItemSet), str(srcItemSet)), fontsize='6')

    for srcItemSet in transformMap:
        for token in transformMap[srcItemSet]:
            dstItemSet = transformMap[srcItemSet][token]
            if dstItemSet:
                e.edge('%d' % itemSetToIdx.get(srcItemSet),'%d' % itemSetToIdx.getIdx(dstItemSet), token.tag, fontsize='6', arrowsize='1.0')

    e.render(filename='LR1', view=True, format='pdf')

# 构建LR(1)自动机
def constructLR1(rules:dict[VN, Rule], beginning:VN, tokens:Iterable[Token]):
    # 自动机定义
    # 动作状态

    # 项目集定义
    # 构造First集合
    First = constructFirstSet(rules)

    # 将终结符放入开始文法
    assert len(rules[beginning].children) == 1
    child = list(rules[beginning].children)[0]

    #  E_ : E

    def printItemSet(itemSet:ItemSet):
        print('ItemSet begin')
        if itemSet is not None:
            print(str(itemSet))
        print('ItemSet end\n')

    # 计算开始项目集
    headItemSet = ItemSet(closure(rules, First, {Item(SingleRule(rules[beginning].parent, child),0):set([END,])}))
    printItemSet(headItemSet)

    # 计算后继项目集，并不断更新，直到没有新的项目集出现
    indexedSet = IndexedSet()
    itemSetQueue:queue.Queue[ItemSet] = queue.Queue()
    indexedSet.add(headItemSet)

    itemSetQueue.put(headItemSet)
    # 记录状态转移表
    # src 与 dst分别为项目集, token为vn或者vt
    # {src: token -> dst}
    transformMap:dict[ItemSet,dict[object,ItemSet]] = dict()

    while not itemSetQueue.empty():
        itemSet = itemSetQueue.get()
        token_to_itemSet = deriveItemSet(rules,First,itemSet,tokens)
        transformMap[itemSet] = dict()
        for token in token_to_itemSet:
            nextItemSet = token_to_itemSet[token]
            transformMap[itemSet][token] = nextItemSet
            if nextItemSet is not None and nextItemSet not in indexedSet:
                indexedSet.add(nextItemSet)
                itemSetQueue.put(nextItemSet)
                print(str(token))
                printItemSet(nextItemSet)
    # 打印结果
    visLR1(transformMap, indexedSet)

    # 生成自动机
    stateToAction:dict[int, dict[Token, Action]] = dict()
    for itemSet in transformMap:

        # 检查 itemSet中是否存在可规约项目
        # 检查是否存在规约冲突
        stateToAction[indexedSet.getIdx(itemSet)] = dict()
        for item in itemSet.items:
            if not item.nextToken():
                # 增加规约结果
                for token in itemSet.items[item]:
                    if token in stateToAction[indexedSet.getIdx(itemSet)]:
                        raise Exception("文法存在规则冲突")

                    # 接受状态
                    if item == Item(SingleRule(rules[beginning].parent, child),1) and token == END:
                        stateToAction[indexedSet.getIdx(itemSet)][token] = Action(ActionKind.Accept, -1, None) 
                        continue
                       
                    stateToAction[indexedSet.getIdx(itemSet)][token] = Action(ActionKind.Reduce, -1, item.rule)
        
        for token in transformMap[itemSet]:
            if transformMap[itemSet][token] is None:
                continue

            if isinstance(token, VN):
                stateToAction[indexedSet.getIdx(itemSet)][token] = \
                    Action(ActionKind.Goto, indexedSet.getIdx(transformMap[itemSet][token]))
            else:
                stateToAction[indexedSet.getIdx(itemSet)][token] = \
                    Action(ActionKind.Shift, indexedSet.getIdx(transformMap[itemSet][token]))
    
    return LR1_FSA(0, stateToAction)



