from queue import Queue


class DFA:
    """ 确定有限状态自动机, 不允许空边
        输入序列，每读入一个，实现状态转移
    """
    error = -1

    def __init__(self, states: set[int], stateMap: dict[int, dict[str, int]], acceptedState: set[int], beginningState: int) -> None:
        """__init__ 可以看作一个有向图, 点表示状态, 边表示接收某些输入时, 需要转移状态
            初始状态为0
        Args:
            states (list[int]): 状态序列
            stateMap (dict[int, dict[str, int]]): 状态转移表
            acceptedState (set[int]): 接收状态
        """
        self.state = 0 if not beginningState else beginningState
        self.stateMap = stateMap
        if self.state not in self.stateMap:
            raise Exception(
                "beginningState %d must be in stateMap" % self.state)
        self.acceptedState = acceptedState

    def consume(self, c):
        if not c:
            raise Exception("Empty input is not allowed")

        if self.state == DFA.error:
            return

        if c not in self.stateMap[self.state]:
            self.state == DFA.error

        self.state = self.stateMap[self.state][c]

    def accept(self) -> bool:
        return self.state in self.acceptedState


class NFA:
    """非确定有限状态自动机 允许空边的存在
        空串''表示空边
    """

    def __init__(self, states: set[int], stateMap: dict[int, dict[str, int]], acceptedState: set[int], beginningState: int, chars: set[str]) -> None:
        """__init__ 可以看作一个有向图, 点表示状态, 边表示接收某些输入时, 需要转移状态
            初始状态为0
        Args:
            states (list[int]): 状态序列
            stateMap (dict[int, dict[str, int]]): 状态转移表
            acceptedState (set[int]): 接收状态
            chars (set[str]): 符号集
        """
        self.state = 0 if not beginningState else beginningState
        self.stateMap = stateMap
        if self.state not in self.stateMap:
            raise Exception(
                "beginningState %d must be in stateMap" % self.state)
        self.acceptedState = acceptedState
        self.beginningState = beginningState
        self.chars = chars

    def closure(self, originStates: set[int]):
        """closure 计算状态闭包

        Args:
            originStates (set[int]): 当前状态
        """
        updated = True
        tmpSet = set()
        resultSet = set(originStates)

        while updated:
            updated = False
            for state in resultSet:
                if state in self.stateMap and self.stateMap[state].get('', default=-1) >= 0:
                    if self.stateMap[state] not in resultSet:
                        tmpSet.add(self.stateMap[state])
                        updated = True
            resultSet.update(tmpSet)
            tmpSet.clear()
        return frozenset(resultSet)

    def toDFA(self) -> DFA:
        """toDFA 子集法根据NFA构造DFA

        Returns:
            DFA: 确定有限状态自动机
        """

        headStates = self.closure(set((self.beginningState,)))
        q: Queue[frozenset] = Queue
        q.put(headStates)

        stateMap: dict[int, dict[str, int]] = dict()
        statesToIdx: dict[frozenset, int] = dict()
        statesIdx: int = 0

        while not q.empty():
            states = q.get()
            for c in self.chars:
                nextStates = set()
                for s in states:
                    if s in self.stateMap and self.stateMap[s].get(c, default=-1) >= 0:
                        nextStates.add(self.stateMap[s].get(c))
                nextStates = self.closure(nextStates)



class MNFA:
    """ 允许多个目标的NFA
    """

    def __init__(self) -> None:
        pass
