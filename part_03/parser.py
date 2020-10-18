# parser.py

from dataclasses import dataclass


class Parser:
    def __init__(self, tokens: any) -> None:
        self.tokens = iter(tokens)
        self.current: any = None
        self.next()

    def next(self) -> None:
        try:
            self.current = next(self.tokens)
        except StopIteration:
            # End of File
            raise EOFError("Unexpected End of File")

    def parse(self):
        while self.current.type != "EOF":
            res = self.expr()
            yield res

    def expr(self):
        # kind = self.current.type
        return self.factor()

    def factor(self):
        kind = self.current.type
        if kind == "NUMBER":
            res = self.current.value
            self.next()
            return NumberNode(res)

        if kind == "STRING":
            res = self.current.value
            self.next()
            return StringNode(res)

        if kind == "ID":
            name = self.current
            self.next()
            if self.current.type == "EQ":
                self.next()
                value = self.factor()
                return VarAssignNode(name, value)

            else:
                return VarAccessNode(name)

        raise SyntaxError(f"Invalid Syntax\nUnexpected {self.current.type}")


@dataclass()
class NumberNode:
    value: int or float
    kind = "Number"


@dataclass()
class StringNode:
    value: str
    kind = "String"


@dataclass()
class VarAccessNode:
    name: any
    kind = "VarAccess"


@dataclass()
class VarAssignNode:
    name: any
    value: any
    kind = "VarAssign"
