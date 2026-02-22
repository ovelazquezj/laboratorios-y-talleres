T_INT = "int"
T_BOOL = "bool"

class Sym:
    __slots__ = ("name","type","is_array","size","extern_name")
    def __init__(self, name, ty, is_array=False, size=0, extern_name=None):
        self.name = name; self.type = ty; self.is_array = is_array; self.size = size
        self.extern_name = extern_name or f"var_{name}"

class Symbols:
    def __init__(self): self.table = {}
    def declare(self, name, ty, is_array=False, size=0):
        if name in self.table: raise SyntaxError(f"[Semantics] Redeclaración de '{name}'")
        if is_array and size <= 0: raise SyntaxError(f"[Semantics] Tamaño inválido para arreglo '{name}'")
        sym = Sym(name, ty, is_array, size); self.table[name] = sym; return sym
    def get(self, name):
        if name not in self.table: raise SyntaxError(f"[Semantics] Identificador no declarado '{name}'")
        return self.table[name]
