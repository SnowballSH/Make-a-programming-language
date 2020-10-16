## Part 02

#### First, we will start from a lexer, or lexical analyzer

- Let's create a file called `lexer.py`

Before we get started, let me explain what does a lexer do.

- A lexer breaks a string of code down to pieces of Tokens

For example,
```python
"  \t print  ('Hello, world!'  \t  )  \n\t"
```

This is an extremely unexpected format. 

We got tabs, new lines, and lots of unwanted spaces, so split() method won't work.

However, with a lexer, we can make it into this clean list:
```python
[
Token(
    type: "IDEN", 
    text: "print", 
    value: "print"
),
Token(
    type: "LPAREN", 
    text: "(", 
    value: "("
),
Token(
    type: "STRING", 
    text: "'Hello, world!'",  # Notice text is different than value
    value: "Hello, world!"
)
Token(
    type: "RPAREN", 
    text: ")", 
    value: ")"),
Token(
    type: "EOF", 
    text: "", 
    value: ""
)]
```

If you look carefully, you will find that there is a "EOF" token at the end, every time.

This is because we want to keep track of whether we reached the end of input/file.

Lexer is the easiest part - so let's jump into it.

***

First, let's create a main function called `tokenize`.

```python
# lexer.py
def tokenize(rules: list, code: str):
    # Trim the input first, so it becomes way faster
    code = code.strip()
    return []
```

However, for better practice, we need to have a Token object, so we can track things more easily.

So, to create a basic data class, we use the `dataclasses` module.

```python
# lexer.py

from dataclasses import dataclass

@dataclass()  # decorator - make sure you know how a decorator works
class Token:
    type: str
    text: str
    value: any  # It may be a string or a number
    line: int
    column: int
```

The dataclasses module handles dunder methods, like `__repr__`, `__eq__`, `__init__` for us, 
since we don't really need to add anything on.

We will also be using regular expressions for lexer:
```python
# lexer.py
import re
```

Our rules will be a list of tuple like:
```python
ID = ('ID', r'[A-Za-z_][A-Za-z_0-9]*')
OP = ('OP', r'[*][*]|[+\-*/]')
STRING = ('STRING', r'("(.*?))"|(\'(.*?)\')')
# goes to:
l = [ID, OP, STRING]
```

Let's create groups for the rules:

```python
# lexer.py
def tokenize(rules: list, code: str):
    # Trim the input first, so it becomes way faster
    code = code.strip()
    
    # Get the regex out of a list of rules
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in rules)
    
    return []
```

Now, for the main loop, we'll use `re.finditer` method

You can attempt to do it on your own, but you can also follow the comments

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
            # Float ot integer
            value = float(value) if '.' in value else int(value)
        elif kind == "STRING":
            # Chop of the two quote marks for the value
            # We don't want something like "'Hello, world!'"
            value = value[1:-1]
        elif kind == 'NEWLINE':
            # New line character, change line number
            line_start = mo.end()
            line_num += 1
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

We have successfully defined the main method

Now, we are going to define our rules
(Which is the most fun part xD)

```python
# lexer.py
class LexerRules:
    NUMBER = ('NUMBER', r'\d+(\.\d*)?')
    ID = ('ID', r'[A-Za-z_][A-Za-z_0-9]*')
    OP = ('OP', r'[*][*]|[+\-*/]')
    STRING = ('STRING', r'("(.*?))"|(\'(.*?)\')')

    LPAREN = ('LPAREN', r'\(')
    RPAREN = ('RPAREN', r'\)')
    ASSIGN = ('ASSIGN', r'=')

    NEWLINE = ('NEWLINE', r'[\r\n]+')
    SKIP = ('SKIP', r'[ \t]+')

    OTHER = ('OTHER', r'.')

    DEFAULT = \
        [
            NUMBER,  # Integer or decimal number
            ID,  # Identifiers
            OP,  # Arithmetic operators
            STRING,  # String

            ASSIGN,  # Assignment operator
            LPAREN,
            RPAREN,

            NEWLINE,  # Line endings
            SKIP,  # Skip over spaces and tabs
            OTHER,  # Any other character
        ]
```

You can write any rules yourself, but these are only the basic rules I will be using.

Now test our tokenizer:

```python
if __name__ == '__main__':
    code = """
            print(\t"Hello, world!"  )
            a_09 = 9 + 100
            """
    rule = LexerRules.DEFAULT

    res = tokenize(rule, code)

    print("\n".join(map(repr, res)))
```

Now from the terminal we get:

```python
Token(type='ID', text='print', value='print', line=1, column=0)
Token(type='LPAREN', text='(', value='(', line=1, column=5)
Token(type='STRING', text='Hello, world!', value='"Hello, world!"', line=1, column=7)
Token(type='RPAREN', text=')', value=')', line=1, column=24)
Token(type='NEWLINE', text='\n', value='\n', line=1, column=25)
Token(type='ID', text='a_09', value='a_09', line=2, column=12)
Token(type='ASSIGN', text='=', value='=', line=2, column=17)
Token(type='NUMBER', text=9, value='9', line=2, column=19)
Token(type='OP', text='+', value='+', line=2, column=21)
Token(type='NUMBER', text=100, value='100', line=2, column=23)
Token(type='EOF', text='', value='', line=2, column=23)
```

**NICE!!** We successfully broke the weird input into these tokens.

With some minor changes, here is the final code:

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
            # Float ot integer
            value = float(value) if '.' in value else int(value)
        elif kind == "STRING":
            # Chop of the two quote marks for the value
            # We don't want something like "'Hello, world!'"
            value = value[1:-1]
        elif kind == 'NEWLINE':
            # New line character, change line number
            line_start = mo.end()
            line_num += 1
            yield Token(kind, value, text, line_num - 1, column)
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


class LexerRules:
    NUMBER = ('NUMBER', r'\d+(\.\d*)?')
    ID = ('ID', r'[A-Za-z_][A-Za-z_0-9]*')
    OP = ('OP', r'[*][*]|[+\-*/]')
    STRING = ('STRING', r'("(.*?))"|(\'(.*?)\')')

    LPAREN = ('LPAREN', r'\(')
    RPAREN = ('RPAREN', r'\)')
    ASSIGN = ('ASSIGN', r'=')

    NEWLINE = ('NEWLINE', r'[\r\n]+')
    SKIP = ('SKIP', r'[ \t]+')

    OTHER = ('OTHER', r'.')

    DEFAULT = \
        [
            NUMBER,  # Integer or decimal number
            ID,  # Identifiers
            OP,  # Arithmetic operators
            STRING,  # String

            ASSIGN,  # Assignment operator
            LPAREN,
            RPAREN,

            NEWLINE,  # Line endings
            SKIP,  # Skip over spaces and tabs
            OTHER,  # Any other character
        ]


if __name__ == '__main__':
    code = """
            print(\t"Hello, world!"  )
            a_09 = 9 + 100
            """
    rule = LexerRules.DEFAULT

    res = tokenize(rule, code)

    print("\n".join(map(repr, res)))
```

*** 

#### Now, let's step into part 3: parser!
