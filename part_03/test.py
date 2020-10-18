from part_03.lexer import *
from part_03.parser import *

code_ = """
        a b  = = "not valid" 3
        """
rule = LexerRules.DEFAULT
res = tokenize(rule, code_)

parser = Parser(res)
res = parser.parse()

print("\n".join(map(repr, res)))
