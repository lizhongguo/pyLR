from entity.Graph import DirectedGraph, Edge, Node
from entity.FA import DFA
nodeIdx = 0

class Stack(list):
    def __init__(self, e=None) -> None:
        if not e:
            super().__init__()
        else:
            super().__init__(e)

    def tail(self) :
        return self.__getitem__(-1)

def RegExpToDFA(pattern:str)->DFA:
    """RegExpToDFA 正则表达式，先构建NFA，再构造DFA
        支持的正则表达式语法, *:匹配0,1,n次, +:匹配1,n次, ?:匹配0,1次, [a,b]:匹配a或者b, ()分组
        后续需要添加对转义字符的支持
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
    edgeStack = Stack([(edge.head, edge)])
    nodeStack:Stack[Node] = Stack()

    for c in pattern:
        if c == '(':
            # 保存起始点
            edge = addEdge(graph,None,None,'')

            head, prevEdge = edgeStack.pop()
            addEdge(graph,prevEdge.tail,edge.head,'')

            edgeStack.append((head,edge))
            nodeStack.append(edge.head)

        elif c == ')':
            # 虚边 仅表示head可以到达tail
            head, prevEdge = edgeStack.pop()
            edge = Edge(nodeStack.pop(), prevEdge.tail)
            edgeStack.append((head,edge))

        elif c == '[':
            edgeStack.append(c)
            edge = addEdge(graph,None,None,'')
            edgeStack.append((edge.head, edge))

        elif c == ']':
            tailEdge = addEdge(graph,None,None,'')
            headEdge = addEdge(graph,None,None,'')
            # 向前寻找prevEdge
            while edgeStack.tail() != '[':
                head, edge = edgeStack.pop()
                addEdge(graph, headEdge.tail, head, '')
                addEdge(graph, edge.tail, tailEdge.head, '')
            edgeStack.pop()
            head, prevEdge = edgeStack.pop()
            addEdge(graph, prevEdge.tail, headEdge.head, '')
            edgeStack.append((head, tailEdge))
            
        elif c == ',':
            edge = addEdge(graph,None,None,'')
            edgeStack.append((edge.head, edge))

        elif c == '?':
            head, edge = edgeStack.pop()
            edgeStack.append((head, addEdge(graph, edge.head, edge.tail, '')))

        elif c == '*':
            head, edge = edgeStack.pop()
            addEdge(graph, edge.tail, edge.head, '')
            edgeStack.append((head,addEdge(graph, edge.head, None, '')))

        elif c == '+':
            head, edge = edgeStack.pop()
            addEdge(graph, edge.tail, edge.head, '')
            edgeStack.append((head, addEdge(graph, edge.tail, None, '')))

        else:
            # 为c创建首尾状态,然后与旧状态连接
            edge = addEdge(graph,None,None,c)
            head, prevEdge =  edgeStack.pop()
            addEdge(graph, prevEdge.tail, edge.head, '')

            edgeStack.append((head,edge))

    graph.visualize()
    assert len(nodeStack) == 0
    assert len(edgeStack) == 1
    _, edge = edgeStack.pop()

    acceptedState = edge.tail

