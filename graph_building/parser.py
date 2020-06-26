from lark import Lark
from lark import Transformer, Visitor
from lark.lexer import Token
from lark import Tree
import sys

GILBRETH_PARSER = Lark("""
expr : assign
    | io
    | for_loop
    | while_loop
    | bool                      -> bool
    | cond
    | "START"                   -> start
    | "STOP"                    -> stop
    | "start"                   -> start
    | "stop"                    -> stop
    | "Start"                   -> start
    | "Stop"                    -> stop
    | expr "."
    | [ expr ("," expr)+ ]

for_loop : "for" assign ";" cmp ";" assign | "FOR" assign ";" cmp ";" assign

while_loop : "while" cmp | "WHILE" cmp

cond: "if" cmp | "IF" cmp

bool: "TRUE"                    -> true
    | "true"                    -> true
    | "True"                    -> true
    | "FALSE"                   -> false
    | "false"                   -> false
    | "False"                   -> false

cmp : arith cmpop arith | bool

assign : var assignop arith
    | var shortassignop arith
    | var incr_op

?arith : arith binop arith
    | "(" arith ")"
    | SIGNED_NUMBER             -> num
    | var                       

io : iofunc ":" [ io_comp ("," io_comp)* ]

?io_comp : ESCAPED_STRING       -> str
    | var
    | SIGNED_NUMBER             -> num

cmpop : "<"                     -> lt
    | ">"                       -> gt
    | "=="                      -> eq
    | ">="                      -> ge
    | "<="                      -> le

assignop : "="

shortassignop : binop"="

binop : "+"                     -> add
    | "-"                       -> min
    | "*"                       -> mul
    | "/"                       -> div
    | "%"                       -> mod

incr_op : "++"                  -> add_incr
    | "--"                      -> min_incr

var : CNAME

iofunc : "in"                   -> in
    | "IN"                      -> in
    | "OUT"                     -> out
    | "out"                     -> out

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.CNAME
%import common.WS
%ignore WS
""", start="expr")

class ASTNode:
    def __init__(self):
        self.elem = None
        self.children = []

    def __repr__(self):
        return str(self.elem) + ": " + str(self.children) if len(self.children) > 0 else str(self.elem)

    def __str__(self):
        return self.__repr__()

class Tree2AST:
    def __init__(self, tree: Tree):
        self.tree = tree
    
    def gen_AST(self):
        n = self._gen_AST(self.tree)
        return n

    def _gen_AST(self, tree):
        n = ASTNode()
        n.elem = tree.data
        
        for child in tree.children:
            if type(child) == Tree:
                childnode = self._gen_AST(child)
            else:
                assert type(child) == Token
                childnode = ASTNode()
                childnode.elem = child.value
            n.children.append(childnode)
        return n