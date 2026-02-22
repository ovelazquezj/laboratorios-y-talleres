# src/parser.py
from .lexer import Lexer
from .symbols import Symbols, T_INT, T_BOOL
from .emitter import Emitter

class Parser:
    def __init__(self, tokens):
        self.toks = tokens; self.i = 0
        self.syms = Symbols(); self.em = Emitter()

    def cur(self): return self.toks[self.i]
    def at(self, kind): return self.cur().kind == kind
    def eat(self, kind):
        if not self.at(kind):
            t = self.cur()
            self.error(f"Se esperaba {kind}, se encontró {t.kind} ('{t.lexeme}') en {t.line}:{t.col}")
        t = self.cur(); self.i += 1; return t
    def match(self, kind):
        if self.at(kind): t = self.cur(); self.i += 1; return t
        return None
    def error(self, msg): raise SyntaxError(f"[Parser] {msg}")

    # program := { decl | stmt } EOF
    def parse_program(self):
        while not self.at("EOF"):
            if self.at("INTKW") or self.at("BOOLKW"): self.parse_decl()
            else: self.parse_stmt()

    def parse_decl(self):
        ty = self.parse_type()
        name = self.eat("IDENT").lexeme
        if self.match("LBRACK"):
            size_tok = self.eat("INTLIT"); size = int(size_tok.lexeme)
            self.eat("RBRACK"); self.eat("SEMICOLON")
            sym = self.syms.declare(name, ty, True, size)
            if ty == T_INT: self.em.emit_bss(f"{sym.extern_name}: resq {size}")
            else: self.em.emit_bss(f"{sym.extern_name}: resb {size}")
        else:
            self.eat("SEMICOLON")
            sym = self.syms.declare(name, ty, False, 0)
            if ty == T_INT: self.em.emit_bss(f"{sym.extern_name}: resq 1")
            else: self.em.emit_bss(f"{sym.extern_name}: resb 1")

    def parse_type(self):
        if self.match("INTKW"): return T_INT
        if self.match("BOOLKW"): return T_BOOL
        self.error("Tipo esperado (int|bool)")

    def parse_stmt(self):
        if self.at("LBRACE"): self.parse_block(); return
        if self.at("IF"): self.parse_if(); return
        if self.at("WHILE"): self.parse_while(); return
        if self.at("PRINT"):
            self.i += 1; self.eat("LPAREN"); ty = self.parse_expr(); self.eat("RPAREN"); self.eat("SEMICOLON")
            if ty == T_INT: self.em.emit("    call print_int")
            elif ty == T_BOOL: self.em.emit("    call print_bool")
            else: self.error("print() soporta solo int/bool"); return
            return
        self.parse_assign(); self.eat("SEMICOLON")

    def parse_block(self):
        self.eat("LBRACE")
        while not self.at("RBRACE"):
            if self.at("INTKW") or self.at("BOOLKW"): self.parse_decl()
            else: self.parse_stmt()
        self.eat("RBRACE")

    def parse_assign(self):
        loc, lty = self.parse_lvalue_address()
        self.eat("ASSIGN")
        rty = self.parse_expr()
        if lty != rty: self.error(f"Asignación incompatible: {lty} = {rty}")
        if lty == T_INT: self.em.emit("    mov [rdi], rax")
        else: self.em.emit("    mov byte [rdi], al")

    def parse_lvalue_address(self):
        ident = self.eat("IDENT").lexeme
        sym = self.syms.get(ident)
        if self.match("LBRACK"):
            if not sym.is_array: self.error(f"Indexación no válida, '{ident}' no es arreglo")
            ty_index = self.parse_expr()
            if ty_index != T_INT: self.error("El índice de un arreglo debe ser int")
            self.eat("RBRACK")
            if sym.type == T_INT:
                self.em.emit(f"    lea rdi, [{sym.extern_name}]")
                self.em.emit("    mov rbx, rax"); self.em.emit("    imul rbx, 8"); self.em.emit("    add rdi, rbx")
                return ("array-int", T_INT)
            else:
                self.em.emit(f"    lea rdi, [{sym.extern_name}]"); self.em.emit("    add rdi, rax"); return ("array-bool", T_BOOL)
        else:
            self.em.emit(f"    lea rdi, [{sym.extern_name}]"); return ("var", sym.type)

    def parse_if(self):
        self.eat("IF"); self.eat("LPAREN")
        ty = self.parse_expr()
        if ty != T_BOOL: self.error("La condición de if debe ser bool")
        self.eat("RPAREN")
        l_else = self.em.fresh("Lelse"); l_end = self.em.fresh("Lendif")
        self.em.emit("    cmp rax, 0"); self.em.emit(f"    je {l_else}")
        self.parse_block(); self.em.emit(f"    jmp {l_end}")
        self.em.emit(f"{l_else}:")
        if self.match("ELSE"): self.parse_block()
        self.em.emit(f"{l_end}:")

    def parse_while(self):
        self.eat("WHILE"); self.eat("LPAREN")
        l_top = self.em.fresh("Lwhile"); l_end = self.em.fresh("Lendw")
        self.em.emit(f"{l_top}:")
        ty = self.parse_expr()
        if ty != T_BOOL: self.error("La condición de while debe ser bool")
        self.eat("RPAREN")
        self.em.emit("    cmp rax, 0"); self.em.emit(f"    je {l_end}")
        self.parse_block(); self.em.emit(f"    jmp {l_top}"); self.em.emit(f"{l_end}:")

    def parse_expr(self): return self.parse_logic_or()

    def parse_logic_or(self):
        ty = self.parse_logic_and()
        while self.match("OR"):
            l_true = self.em.fresh("Lor_true"); l_end = self.em.fresh("Lor_end")
            if ty != T_BOOL: self.error("Operador || requiere bool")
            self.em.emit("    cmp rax, 0"); self.em.emit(f"    jne {l_true}")
            ty_r = self.parse_logic_and()
            if ty_r != T_BOOL: self.error("Operador || requiere bool")
            self.em.emit(f"    jmp {l_end}"); self.em.emit(f"{l_true}:"); self.em.emit("    mov rax, 1"); self.em.emit(f"{l_end}:")
            ty = T_BOOL
        return ty

    def parse_logic_and(self):
        ty = self.parse_equality()
        while self.match("AND"):
            l_false = self.em.fresh("land_false"); l_end = self.em.fresh("land_end")
            if ty != T_BOOL: self.error("Operador && requiere bool")
            self.em.emit("    cmp rax, 0"); self.em.emit(f"    je {l_false}")
            ty_r = self.parse_equality()
            if ty_r != T_BOOL: self.error("Operador && requiere bool")
            self.em.emit(f"    jmp {l_end}"); self.em.emit(f"{l_false}:"); self.em.emit("    xor rax, rax"); self.em.emit(f"{l_end}:")
            ty = T_BOOL
        return ty

    def parse_equality(self):
        ty = self.parse_relational()
        while True:
            if self.match("EQ"):
                self.em.emit("    push rax")
                ty_r = self.parse_relational()
                if ty != ty_r: self.error("Comparación == entre tipos distintos")
                self.emit_cmp_set("sete"); ty = T_BOOL
            elif self.match("NEQ"):
                self.em.emit("    push rax")
                ty_r = self.parse_relational()
                if ty != ty_r: self.error("Comparación != entre tipos distintos")
                self.emit_cmp_set("setne"); ty = T_BOOL
            else: break
        return ty

    def emit_cmp_set(self, setcc):
        self.em.emit("    mov rbx, rax"); self.em.emit("    pop rax")
        self.em.emit("    cmp rax, rbx"); self.em.emit(f"    {setcc} al"); self.em.emit("    movzx rax, al")

    def parse_relational(self):
        ty = self.parse_additive()
        while True:
            if self.at("LT") or self.at("LE") or self.at("GT") or self.at("GE"):
                op = self.cur().kind; self.i += 1
                if ty != T_INT: self.error("Relacionales requieren int")
                self.em.emit("    push rax")
                ty_r = self.parse_additive()
                if ty_r != T_INT: self.error("Relacionales requieren int")
                self.em.emit("    mov rbx, rax"); self.em.emit("    pop rax")
                self.em.emit("    cmp rax, rbx")
                if op == "LT": self.em.emit("    setl  al")
                elif op == "LE": self.em.emit("    setle al")
                elif op == "GT": self.em.emit("    setg  al")
                else: self.em.emit("    setge al")
                self.em.emit("    movzx rax, al"); ty = T_BOOL
            else: break
        return ty

    def parse_additive(self):
        ty = self.parse_multiplicative()
        while self.at("PLUS") or self.at("MINUS"):
            op = self.cur().kind; self.i += 1
            if ty != T_INT: self.error("Aditivos requieren int")
            self.em.emit("    push rax")
            ty_r = self.parse_multiplicative()
            if ty_r != T_INT: self.error("Aditivos requieren int")
            self.em.emit("    mov rbx, rax"); self.em.emit("    pop rax")
            if op == "PLUS": self.em.emit("    add rax, rbx")
            else: self.em.emit("    sub rax, rbx")
            ty = T_INT
        return ty

    def parse_multiplicative(self):
        ty = self.parse_unary()
        while self.at("STAR") or self.at("SLASH") or self.at("PERCENT"):
            op = self.cur().kind; self.i += 1
            if ty != T_INT: self.error("Multiplicativos requieren int")
            self.em.emit("    push rax")
            ty_r = self.parse_unary()
            if ty_r != T_INT: self.error("Multiplicativos requieren int")
            self.em.emit("    mov rbx, rax"); self.em.emit("    pop rax")
            if op == "STAR": self.em.emit("    imul rax, rbx")
            elif op == "SLASH":
                self.em.emit("    cqo"); self.em.emit("    idiv rbx")
            else:
                self.em.emit("    cqo"); self.em.emit("    idiv rbx"); self.em.emit("    mov rax, rdx")
            ty = T_INT
        return ty

    def parse_unary(self):
        if self.match("BANG"):
            ty = self.parse_unary()
            if ty != T_BOOL: self.error("! requiere bool")
            self.em.emit("    cmp rax, 0"); self.em.emit("    sete al"); self.em.emit("    movzx rax, al")
            return T_BOOL
        if self.match("MINUS"):
            ty = self.parse_unary()
            if ty != T_INT: self.error("Negación unaria requiere int")
            self.em.emit("    neg rax"); return T_INT
        return self.parse_primary()

    def parse_primary(self):
        t = self.cur()
        if self.match("INTLIT"):
            self.em.emit(f"    mov rax, {int(t.lexeme)}"); return T_INT
        if self.match("TRUE"): self.em.emit("    mov rax, 1"); return T_BOOL
        if self.match("FALSE"): self.em.emit("    xor rax, rax"); return T_BOOL
        if self.match("LPAREN"):
            ty = self.parse_expr(); self.eat("RPAREN"); return ty
        if self.at("IDENT"):
            ident = self.eat("IDENT").lexeme; sym = self.syms.get(ident)
            if self.match("LBRACK"):
                if not sym.is_array: self.error(f"Indexación no válida, '{ident}' no es arreglo")
                ty_idx = self.parse_expr()
                if ty_idx != T_INT: self.error("Índice debe ser int")
                self.eat("RBRACK")
                if sym.type == T_INT:
                    self.em.emit(f"    lea rbx, [{sym.extern_name}]")
                    self.em.emit("    imul rax, 8"); self.em.emit("    add rbx, rax")
                    self.em.emit("    mov rax, [rbx]"); return T_INT
                else:
                    self.em.emit(f"    lea rbx, [{sym.extern_name}]")
                    self.em.emit("    add rbx, rax"); self.em.emit("    movzx rax, byte [rbx]"); return T_BOOL
            else:
                if sym.type == T_INT: self.em.emit(f"    mov rax, [{sym.extern_name}]")
                else: self.em.emit(f"    movzx rax, byte [{sym.extern_name}]")
                return sym.type
        self.error(f"Expresión primaria inesperada en {t.line}:{t.col} ({t.kind})")

def compile_source(source_code: str) -> str:
    lx = Lexer(source_code); toks = lx.lex()
    p = Parser(toks); p.parse_program()
    return p.em.finalize()
