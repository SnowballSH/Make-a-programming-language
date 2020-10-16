## Part 01

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
```
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


