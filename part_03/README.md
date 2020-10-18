## Part 03

#### In this part, we are going to create a parser.

But what is a parser?

A parser generates the Tokens into an AST, or Abstract Syntax Tree.

For example,

```python
Token(type='ID', text='print', value='print', line=1, column=0)
Token(type='LPAREN', text='(', value='(', line=1, column=5)
Token(type='STRING', text='Hello, world!', value='"Hello, world!"', line=1, column=7)
Token(type='RPAREN', text=')', value=')', line=1, column=24)
```

Would become an AST of:

```
( <Main> of
    child: 
    ( <Function Call> of
        name: ( <Identifier> of 
                value: "print" )
        args: ( <Arg List> of
                value: [ ( <String> of
                     value: "Hello, world!" ), ] )
    )
)
```

This is for the computer to understand it better.

First, let's create a simple parser class.

```python
# parser.py

class Parser:
    def __init__(self, tokens: any) -> None:
        self.tokens = iter(tokens)
        self.current: any = None

    def next(self) -> None:
        self.current = next(self.tokens)
        if self.current.type == "EOF":
            # End of File
            raise EOFError("Unexpected End of File")

    def parse(self):
        return
```

So, let's define some simple rules.

```python
    def parse(self):
        while self.current.type != "EOF":
            self.next()
            yield self.expr()

    def expr(self):
        kind = self.current.type

        return self.factor()

    def factor(self):
        kind = self.current.type
        if kind == "NUMBER":
            return  # NumberNode

        if kind == "STRING":
            return  # StringNode

        if kind == "ID":
            name = self.current
            self.next()
            if self.current.type == "EQ":
                self.next()
                value = self.factor()
                return  # VarAssignNode

            else:
                return  # VarAccessNode
```

This code seems a bit long, but let's break it up:

1. `parse()` look for `expr()` of 0 and more
2. `expr()` look for `factor`
3. 
- If String:
    - return StringNode
- If Number:
    - return NumberNode
- If Identifier:
    - If next token is "=":
        - look for factor
        - return VarAssignNode
    - If not,
        - return VarAccessNode
- Else
    - Raise SyntaxError, terminate
    
Let's create these Nodes.

Each Node represents an element in the AST

```python
from dataclasses import dataclass

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
```

Now insert the nodes into the comments:

```python
# parser.py

from dataclasses import dataclass


class Parser:
    def __init__(self, tokens: any) -> None:
        self.tokens = iter(tokens)
        self.current: any = None

    def next(self) -> None:
        self.current = next(self.tokens)
        if self.current.type == "EOF":
            # End of File
            raise EOFError("Unexpected End of File")

    def parse(self):
        while self.current.type != "EOF":
            self.next()
            yield self.expr()

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

...  # Nodes
```

If you try it now, you may encounter some bugs. Let's fix them:

```python
# parser.py

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

        raise SyntaxError(f"{self.current.type}")
```

Also some changes in lexer.py:

```python
# lexer.py

from dataclasses import dataclass
import re


@dataclass()  # decorator - make sure you know how a decorator works
class Token:
    type: str
    text: str
    value: any  # It may be a string or a number
    line: int
    column: int


def tokenize(rules: list, code: str) -> list:
    # Trim the input first, so it becomes way faster
    code = code.strip()

    # Get the regex out of a list of rules
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in rules)

    line_num = 1
    line_start = 0
    column = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        text = value
        if kind == 'NUMBER':
            # Float or integer
            value = float(value) if '.' in value else int(value)
        elif kind == "STRING":
            # Chop of the two quote marks for the value
            # We don't want something like "'Hello, world!'"
            value = value[1:-1]
        elif kind == 'NEWLINE':
            # New line character, change line number
            line_start = mo.end()
            line_num += 1
            # yield Token(kind, value, text, line_num - 1, column)
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'OTHER':
            # Let's just make it Symbol now
            kind = "SYMBOL"

        # Yield that token
        yield Token(kind, value, text, line_num, column)

    # At the end, yield EOF
    yield Token("EOF", "", "", line_num, column)
```

Now, in `test.py`, run

```python
from part_03.lexer import *
from part_03.parser import *

code_ = """
        a = 34
        b = "str"
        c = a
        """
rule = LexerRules.DEFAULT
res = tokenize(rule, code_)

parser = Parser(res)
res = parser.parse()

print("\n".join(map(repr, res)))
```

We get:

```python
VarAssignNode(name=Token(type='ID', text='a', value='a', line=1, column=0), value=NumberNode(value='34'))
VarAssignNode(name=Token(type='ID', text='b', value='b', line=2, column=8), value=StringNode(value='"str"'))
VarAssignNode(name=Token(type='ID', text='c', value='c', line=3, column=8), value=VarAccessNode(name=Token(type='ID', text='a', value='a', line=3, column=12)))
```

Great! Now the code is turned into these Nodes...

If we run something invalid, like

```
a b  = = "not valid" 3
```

We will get error of

```python
SyntaxError: Invalid Syntax
Unexpected EQ
```

Full code:

```python
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
```

Nice! Let's move on to the next part.
