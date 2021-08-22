import graphviz

class Node:
    def __init__(self, nodeId:int) -> None:
        self.nodeId:int = nodeId

    def __hash__(self) -> int:
        return hash(self.nodeId)       

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        if isinstance(o, self.__class__):
            return o.nodeId == self.nodeId
        return False 

class Edge:
    def __init__(self, head:Node, tail:Node, tag = None) -> None:
        self.head = head
        self.tail = tail
        self.tag = tag

    def __hash__(self) -> int:
        return (hash(self.head)>>1) ^ hash(self.tail) ^ hash(self.tag)

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        if isinstance(o, self.__class__):
            return o.head == self.head and o.tail == self.tail and o.tag == self.tag 
        return False 

class DirectedGraph:
    """ 有向图, 允许成对节点间出现多条边
    """    
    def __init__(self) -> None:
        self.cnt = 0
        self.nodes:set[Node] = set()
        self.edges:set[Edge] = set()
        self.graph:dict[Node, dict[Node, set[Edge]]] = dict()

    def addNode(self, node:Node):
        assert node is not None
        self.nodes.add(node)

    def addEdge(self, edge:Edge):
        assert edge is not None

        self.addNode(edge.head)
        self.addNode(edge.tail)

        self.edges.add(edge)

        if edge.head not in self.graph:
            self.graph[edge.head] = dict()

        if edge.tail not in self.graph[edge.head]:
            self.graph[edge.head][edge.tail] = set()

        self.graph[edge.head][edge.tail].add(edge)

    def visualize(self):
        e = graphviz.Digraph('ER', filename='er.gv', engine='dot',graph_attr={'size':'100,50'})
        # e.attr(rankdir='LR')
        e.attr('node', shape='box')

        nodesToIdx = dict()
        idx = 0
        for node in self.nodes:
            nodesToIdx[node] = idx
            e.node('%d' % idx, '%d' % idx)            
            idx += 1

        for head in self.graph:
            for tail in self.graph[head]:
                for edge in self.graph[head][tail]:
                    label = edge.tag if edge.tag else 'ε'
                    e.edge('%d' % nodesToIdx[head], '%d' % nodesToIdx[tail], label)

        e.render(filename='Graph', view=True, format='pdf')
        