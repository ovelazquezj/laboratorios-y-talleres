from src.lexer import Lexer

with open("examples/01_sum.ms") as f:
    text = f.read()

lexer = Lexer(text)
lexer.lex()

for token in lexer.tokens:
    print(token)
