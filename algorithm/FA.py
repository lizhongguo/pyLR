from entity.Graph import DirectedGraph, Edge, Node
from entity.FA import DFA
nodeIdx = 0

class Stack(list):
    def __init__(self) -> None:
        super().__init__()

    def tail(self) :
        return self.__getitem__(-1)

def RegExpToDFA(pattern:str)->DFA:
    """RegExpToDFA 正则表达式，先构建NFA，再构造DFA
        支持的正则表达式语法, *:匹配0,1,n次, +:匹配1,n次, ?:匹配0,1次, [a,b]:匹配a或者b, ()分组
        使用栈来处理正则表达式语法
        正则表达式构造NFA:
            1) ab : a前后增加两个状态 0-a->1-epsilon->2-b->3
            2) a[b,c]d : abd构造边, acd构造边
            3) (ab)前后各加两个状态, 转化为a类似的
    """ 
    def addNode():
        global nodeIdx
        node = Node(nodeIdx)
        nodeIdx += 1
        return node

    def addEdge(graph,head,tail,tag=None) -> Edge:
        if head is None:
            head = addNode()
        if tail is None:
            tail = addNode()

        edge = Edge(head,tail, tag)
        if graph:
            graph.addEdge(edge)
        return edge

    graph = DirectedGraph()

    edge = addEdge(graph,None,None,'')    
    edgeStack:Stack[Edge] = Stack([edge])
    nodeStack:Stack[Node] = Stack()

    for c in pattern:
        if c == '(':
            # 保存起始点
            edge = addEdge(graph,None,None,'')
            addEdge(graph,edgeStack.tail().tail,edge.head,'')

            edgeStack.append(edge)
            nodeStack.append(edge.head)


        elif c == ')':
            # 虚边 仅表示head可以到达tail
            edge = Edge(nodeStack.pop(), edgeStack.tail().tail)
            edgeStack.pop()
            edgeStack.append(edge)

        elif c == '[':
            edgeStack.append(c)
            edgeStack.append(addEdge(graph,None,None,''))

        elif c == ']':
            tailEdge = addEdge(graph,None,None,'')
            headEdge = addEdge(graph,None,None,'')
            # 向前寻找prevEdge
            while edgeStack.tail() != '[':
                edge = edgeStack.pop()
                addEdge(graph, headEdge.tail, edge.head, '')
                addEdge(graph, edge.tail, tailEdge.head, '')
            edgeStack.pop()
            prevEdge = edgeStack.pop()
            addEdge(graph, prevEdge.tail, headEdge.head)
            edgeStack.append(tailEdge)
            
        elif c == ',':
            edgeStack.append(addEdge(graph,None,None,''))

        elif c == '?':
            edge = edgeStack.pop()

            edgeStack.append(addEdge(graph, edge.head, edge.tail, ''))

            edgeStack.append(edge)

        elif c == '*':
            edge = edgeStack.pop()
            addEdge(graph, edge.tail, edge.head, '')

            edgeStack.append(addEdge(graph, edge.head, None, ''))

        elif c == '+':
            edge = edgeStack.pop()
            addEdge(graph, edge.tail, edge.head, '')

            edgeStack.append(addEdge(graph, edge.tail, None, ''))

        else:
            # 为c创建首尾状态,然后与旧状态连接
            edge = addEdge(graph,None,None,c)
            prevEdge:Edge = edgeStack.tail()
            addEdge(graph, prevEdge.tail, edge.head, '')

            edgeStack.pop()
            edgeStack.append(edge)


