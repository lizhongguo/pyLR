class Token:
    def __init__(self, tag) -> None:
        self.tag = tag

    def __eq__(self, o: object) -> bool:
        if not o:
            return False
        if not isinstance(o, VT):
            return False
        return self.tag == o.tag

    def __hash__(self) -> int:
        return hash(self.tag)

    def __str__(self) -> str:
        return 'Token(tag: %s)' % self.tag
     

class VT(Token):
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

class VN(Token):
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
