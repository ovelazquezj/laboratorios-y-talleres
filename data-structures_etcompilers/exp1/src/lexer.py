# MiniSEC Lexer
KEYWORDS = {
    "int": "INTKW",
    "bool": "BOOLKW",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "print": "PRINT",
    "read": "READ",
    "true": "TRUE",
    "false": "FALSE",
}

SYMBOLS = {
    "{": "LBRACE", "}": "RBRACE", "(": "LPAREN", ")": "RPAREN",
    "[": "LBRACK", "]": "RBRACK", ";": "SEMICOLON", ",": "COMMA",
    "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH", "%": "PERCENT",
    "=": "ASSIGN", "!": "BANG", "<": "LT", ">": "GT",
    "&&": "AND", "||": "OR", "==": "EQ", "!=": "NEQ", "<=": "LE", ">=": "GE",
}

class Token:
    __slots__ = ("kind","lexeme","line","col")
    def __init__(self, kind, lexeme, line, col):
        self.kind = kind; self.lexeme = lexeme; self.line = line; self.col = col
    def __repr__(self): return f"Token({self.kind},{self.lexeme!r},{self.line}:{self.col})"

class Lexer:
    def __init__(self, text):
        self.text = text; self.i = 0; self.line = 1; self.col = 1; self.n = len(text); self.tokens = []
    def peek(self, k=0):
        j = self.i + k
        return '\0' if j >= self.n else self.text[j]
    def advance(self):
        ch = self.peek(); self.i += 1
        if ch == '\n': self.line += 1; self.col = 1
        else: self.col += 1
        return ch
    def add(self, kind, lexeme, line=None, col=None):
        if line is None: line = self.line
        if col is None: col = self.col
        self.tokens.append(Token(kind, lexeme, line, col))
    def lex(self):
        while self.i < self.n:
            ch = self.peek()
            if ch in ' \t\r': self.advance(); continue
            if ch == '\n': self.advance(); continue
            # comments
            if ch == '/':
                if self.peek(1) == '/':
                    while self.peek() not in ('\n','\0'): self.advance()
                    continue
                if self.peek(1) == '*':
                    self.advance(); self.advance()
                    while True:
                        if self.peek() == '\0': self.error("Unterminated block comment")
                        if self.peek() == '*' and self.peek(1) == '/':
                            self.advance(); self.advance(); break
                        self.advance()
                    continue
            # identifiers
            if ch.isalpha() or ch == '_':
                si, sc, sl = self.i, self.col, self.line
                s = []
                while self.peek().isalnum() or self.peek() == '_': s.append(self.advance())
                lexeme = ''.join(s)
                kind = KEYWORDS.get(lexeme, "IDENT")
                self.add(kind, lexeme, sl, sc); continue
            # numbers
            if ch.isdigit():
                si, sc, sl = self.i, self.col, self.line
                s = []
                while self.peek().isdigit(): s.append(self.advance())
                lexeme = ''.join(s)
                self.add("INTLIT", lexeme, sl, sc); continue
            # two-char ops
            two = ch + self.peek(1)
            if two in SYMBOLS:
                line, col = self.line, self.col
                self.advance(); self.advance()
                self.add(SYMBOLS[two], two, line, col); continue
            # single-char
            if ch in SYMBOLS:
                line, col = self.line, self.col
                self.advance(); self.add(SYMBOLS[ch], ch, line, col); continue
            self.error(f"Caracter inesperado: {ch!r}")
        self.add("EOF","", self.line, self.col); return self.tokens
    def error(self, msg): raise SyntaxError(f"[Lexer] {msg} at line {self.line}, col {self.col}")
