'''
.g4

符号之间按照空格,\n或者\t 分隔, 纯字母
形如\"a\"为终结符, 形如 abcd 为非终结符, 

格式为 VN : VN | VN | VT;

第一个符号被定义为起始符号, 或者分析入度

手动文法分析

Sentences : Sentence ";" Sentences | Empty ;

Sentence : VN ":" Children ;

Children : Tokens "|" Children | Tokens;

Tokens : Token Space Spaces Tokens;

Spaces : Space Spaces | Empty; 

Token : VN | VT;

VN : Chars;

VT : "\"" Char "\"";

Chars : Char Chars;

Char : "A"..."Z" | "a"..."z";

'''
import string
from entity.Token import *
from entity.Rule import *

# 构建简化的g4文法分析器
# 1. 文法
# Sentences = VN('Sentences')
# Sentence = VN('Sentence')
# VN_ = VN('VN')
# VT_ = VT('VT')
# Children = VN('Children')

# Tokens_ = VN('Tokens')
# Token_ = VN('Token')
# Spaces = VN('Spaces')

# Semicolon = VT('Semicolon', ';')
# Colon = VT('Colon',':')
# VerticalBar = VT('VerticalBar', '|')
# Space = VT('Space', ' ')

# SentencesRule = Rule(Sentences,((Sentence, Semicolon, Sentences),(EPSILON)))
# SentenceRule = Rule(Sentence,((VN_, Colon, Children)))
# ChildrenRule = Rule(Children,((Tokens_, VerticalBar, Children ), (Tokens_)))
# TokensRule = Rule(Tokens_, (Token_, Space, Spaces))

def analyze(inputStr):
    # state  VN : Tokens (| Tokens)* ;
    # state  0  1 2     3            4
    state = 0
    idx = 0

    def splitter(ch):
        return ch == ' ' | ch == '\t' | ch == '\n' | ch == '\r'

    while idx < len(inputStr):
        if splitter(inputStr[idx]):
            idx += 1

        if state == 0:
            if inputStr[idx] in string.ascii_letters:
                #读入VN
                state = 1
                idx += 1

        elif state == 1:
            if inputStr[idx] == ':':
                idx += 1
                state = 2
        
        elif state == 2:
            # 读入Tokens,直到遇到 |
            idx += 1

            if state[idx] == '|':
                state = 2
            elif state[idx] == ';':
                state = 0

    if state != 0:
        raise Exception("解析失败")

    pass