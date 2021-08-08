from typing import Iterable
from entity.Token import Token, VN, VT, EPSILON, END
from entity.Rule import Rule

def updateSet(dst: set, src, epsilonNotAllowed=False):
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
# 所有终结符的First集为本身
def constructFirstSet(rules: dict[VN, Rule]):
    updated = True
    First = {vn: set() for vn in rules}

    while updated:
        updated = False
        for parentVN in rules:
            rule = rules[parentVN]
            assert parentVN == rule.parent

            for child in rule.children:
                for token in child:

                    if isinstance(token, VT):
                        # E : a B c, 如果a为终结符, 将a加入First(E)中，结束该规则的处理
                        if token not in First[rule.parent]:
                            updated = True

                        # 如果为 E : Epsilon, 将Epsilon加入First(E)中
                        First[rule.parent].add(token)

                        break

                    elif isinstance(token, VN):

                        # E: a B c, 如果a为非终结符, 将First(a)加入First(E)中
                        if not First[token].issubset(First[rule.parent]):
                            updated = True

                        First[rule.parent] |= First[token]

                        # 如果a不能推出空推导，不再向下继续
                        # 否则可推出空匹配，将下一个token的First集合加入parentVN

                        if EPSILON not in First[token]:
                            break


                        # if (EPSILON,) not in rules[token].children:
                            # break

    return First


# 获取某个序列的First集合
def getFirstOfSeq(First: dict[VN, VT], seq: Iterable[Token], followSet: set[VT] = None):
    results = set()

    if len(seq) == 0:
        results.add(EPSILON)
        if EPSILON in results and followSet is not None:
            results.remove(EPSILON)
            return results | followSet
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

    if EPSILON in results and followSet is not None and followSet:
        results.remove(EPSILON)
        return results | followSet

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

                # 空产生式不处理
                if child[0] == EPSILON:
                    continue

                # A ： a B b , a的Follow集合增加First(Bb)
                for i in range(len(child)-1):
                    if isinstance(child[i], VN):
                        updated = True if updateSet(Follow[child[i]], getFirstOfSeq(First, child[i+1:]), True) else updated

                #如果b ： Epsilon, B的Follow集增加Follow(A)
                for i in range(len(child)-1, 0, -1):
                    if isinstance(child[i], VN):
                        if EPSILON in getFirstOfSeq(First,child[i+1:]):
                            updated = True if updateSet(Follow[child[i]], Follow[parentVN], True) else updated


    return Follow

