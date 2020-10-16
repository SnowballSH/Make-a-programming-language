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
