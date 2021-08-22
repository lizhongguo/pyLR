from entity.Token import END, Token, VN,VT

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

    def __len__(self):
        if len(self.child) == 1 and self.child[0] == END:
            return 0
        return len(self.child)

    def __hash__(self) -> int:
        return hash(self.parent) ^ hash(self.child)

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        
        if not isinstance(o, SingleRule):
            return False
        
        return self.parent == o.parent and self.child == o.child

    def __str__(self) -> str:
        return '%s : %s' % (str(self.parent), ','.join([str(token) for token in self.child]))
