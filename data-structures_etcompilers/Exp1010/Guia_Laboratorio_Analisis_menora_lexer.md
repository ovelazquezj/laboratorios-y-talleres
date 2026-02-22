# Compilador didáctico MiniGUs
## LABORATORIO: DESCUBRE LO QUE TU LEXER REALMENTE HACE

**Curso:** Estructuras de Datos y Compiladores  
**Sesión:** 23  
**Duración:** 2 horas  
**Modalidad:** Investigación guiada + Descubrimiento  

---

## PARTE 1: Análisis Crítico - ¿Qué Hace Tu Lexer? (40 minutos)

Abre el lab de la primer semana en búsqueda de lo que hiciste:
- `src/lexer.py` (código que escribieron hace semanas)
- `examples/01_sum.ms` (programa de prueba)

### Paso 1.1: Ejecuta Tu Lexer (5 min)
NOTA: Busca la guía del Exp0 para mayores detalles y ejecuta test_kexer.py

Verás tokens fluyendo. **Pausa un momento.**

Pregunta: ¿De dónde vinieron esos tokens?
```
Respuesta en 1 línea:
_______________________________________________________________________
```

### Paso 1.2: Lee el Código - Cazando Patrones (15 min)

Abre `src/lexer.py`. Lee **sin copiar, solo entender**.

**Pregunta 1: ¿Qué son KEYWORDS y SYMBOLS?**

Mira estas líneas:
```python
KEYWORDS = {
    "int": "INTKW",
    "bool": "BOOLKW",
    "if": "IF",
    ...
}

SYMBOLS = {
    "{": "LBRACE",
    "}": "RBRACE",
    ...
}
```

**¿Qué estructura de datos son?**

☐ Arreglos  
☐ Diccionarios  
☐ Listas enlazadas  
☐ Pilas  

**¿Por qué crees que el programador eligió esa estructura?**

Pista: ¿Cuánto tarda buscar "int" en un diccionario? ¿Y en un arreglo?
```
Tu respuesta:
_______________________________________________________________________
```

---

**Pregunta 2: ¿Qué es `self.tokens`?**

Mira:
```python
self.tokens = []
...
self.add(kind, lexeme, line, col)
```

¿Qué estructura es `self.tokens`?

☐ Diccionario  
☐ Lista  
☐ Pila  
☐ Cola  

**¿Por qué el orden importa?**
```
Tu respuesta:
_______________________________________________________________________
```

---

**Pregunta 3: ¿Cómo el lexer "sabe" qué hacer?**

Mira la función `lex()`. Señala dónde el código DECIDE:
```python
def lex(self):
    while self.i < self.n:
        ch = self.peek()
        
        if ch.isspace():
            self.advance()
            continue
        
        # ← AQUÍ EMPIEZA LO INTERESANTE
        if ch.isalpha():
            # ... acumula letras y dígitos
            kind = KEYWORDS.get(lexeme, "IDENT")
            self.add(kind, lexeme)
            continue
        
        if ch.isdigit():
            # ... acumula dígitos
            self.add("INTLIT", lexeme)
            continue
        
        # ... más condiciones
```

**¿En qué se basa la decisión de qué camino tomar?**

☐ En línea y columna  
☐ En el token anterior  
☐ En qué carácter ve ahora (ch)  
☐ En toda la entrada  
```
Tu respuesta y justificación:
_______________________________________________________________________
```

---

**Pregunta 4: Traza Manual (dibuja lo que pasa)**

Tomemos esta entrada pequeña:
```
int x;
```

Mientras el lexer procesa, **dibuja qué estado tiene en cada paso:**

| Paso | Carácter (ch) | ¿Qué hace? | Token creado |
|------|---------------|-----------|--------------|
| 1 | 'i' | Entra en IF isalpha() | (nada aún) |
| 2 | 'n' | ¿? | ¿? |
| 3 | 't' | ¿? | ¿? |
| 4 | ' ' | ¿? | ¿? |
| 5 | 'x' | ¿? | ¿? |
| 6 | ';' | ¿? | ¿? |

Completa la tabla (pista: mira el código).

---

### Paso 1.3: ¿En Qué "Modo" Está Tu Lexer? (15 min)


Mientras lee "int x;", el lexer está haciendo diferente según dónde esté:

- Mientras lee 'i', 'n', 't': está **acumulando letras** (es como un "modo IDENTIFIER")
- Cuando ve el espacio: **cambia de modo** (crea el token, vuelve a START)
- Cuando ve 'x': entra en **modo IDENTIFIER de nuevo**
- Cuando ve ';': **cambia de modo** a SYMBOL

**Pregunta: ¿Cuáles son todos los "modos" en los que puede estar tu lexer?**

Mira el código y lista:
```
Modo 1: _____________ (cuando lee letras)
Modo 2: _____________ (cuando lee dígitos)
Modo 3: _____________ (cuando busca símbolos)
Modo 4: _____________ (esperando siguiente token)
```

**¿Qué hace cambiar de modo?**
```
Tu respuesta:
_______________________________________________________________________
```

---

## PARTE 2: Extensión - Elige Tu Camino (60 minutos)

Ahora que entiendes cómo funciona, **elegirás mejorar el lexer en UNA dirección**.

Tienes 4 opciones. **Lee las 4, elige 1.**

---

### 🔧 OPCIÓN A: Robustez - Comentarios

**Desafío:** Haz que el lexer ignore comentarios de línea (`//`) y bloque (`/* */`)

**¿Por qué?** Programas reales necesitan comentarios.

#### Paso A.1: Entiende el Problema

Prueba esto en tu lexer actual:
```bash
# Crea archivo test_comments.ms:
cat > test_comments.ms << 'EOF'
// esto es comentario
int x;  /* bloque */
EOF

python3 test_lexer.py  # ¿Qué pasó?
```

**¿Qué error apareció?**
```
Respuesta:
_______________________________________________________________________
```

Ahí está el problema. Tu lexer no sabe qué hacer con `/`.

#### Paso A.2: Diseña la Solución

**Pregunta:** Si ves una `/`, ¿cómo sabes si es comentario o división?

Pista: mira lo siguiente (`peek(1)`)
```python
if ch == '/' and self.peek(1) == '/':
    # Es comentario de línea
    ...
elif ch == '/' and self.peek(1) == '*':
    # Es comentario de bloque
    ...
else:
    # Es el símbolo de división
    ...
```

**¿Ves? Otra decisión basada en qué ves ahora.**

#### Paso A.3: Implementa

Abre `src/lexer.py`. En la función `lex()`, **antes de procesar otros tokens**, agrega:
```python
def lex(self):
    while self.i < self.n:
        ch = self.peek()
        
        # Espacios en blanco
        if ch.isspace():
            self.advance()
            continue
        
        # ← AGREGA AQUÍ, ANTES DE TODO
        # Comentario de línea
        if ch == '/' and self.peek(1) == '/':
            while self.peek() not in ('\n', '\0'):
                self.advance()
            continue
        
        # Comentario de bloque
        if ch == '/' and self.peek(1) == '*':
            self.advance()  # Consume /
            self.advance()  # Consume *
            while True:
                if self.peek() == '\0':
                    raise SyntaxError("Comentario no cerrado")
                if self.peek() == '*' and self.peek(1) == '/':
                    self.advance()  # Consume *
                    self.advance()  # Consume /
                    break
                self.advance()
            continue
        
        # ... resto del código
```

#### Paso A.4: Prueba
```bash
python3 test_lexer.py
```

¿Desaparecieron los comentarios? ¿Los tokens son correctos?
```
Prueba exitosa: ☐ Sí  ☐ No
```

#### Paso A.5: Reflexiona

**Pregunta:** ¿Cuántos "modos" nuevos agregaste?

Pista: modo "DENTRO DE COMENTARIO DE LÍNEA" y "DENTRO DE COMENTARIO DE BLOQUE"
```
Respuesta:
_______________________________________________________________________
```

---

### 🔧 OPCIÓN B: Manejo de Errores - Mensajes Claros

**Desafío:** Cuando el lexer encuentra un carácter que no entiende, 
que dé un error **útil** en lugar de genérico.

**¿Por qué?** Buenos mensajes de error ayudan a debuggear.

#### Paso B.1: Provoca el Error
```bash
# Crea archivo con carácter inválido:
cat > test_error.ms << 'EOF'
int x @ 5;
EOF

python3 test_lexer.py
```

**¿Qué error aparece?**
```
Respuesta:
_______________________________________________________________________
```

Es genérico, ¿no? Solo dice "carácter inesperado: '@'".

#### Paso B.2: Mejora el Mensaje

En `src/lexer.py`, agrega método que sugiera qué pasó:
```python
def analyze_invalid_char(self, char):
    """Sugiere qué salió mal"""
    suggestions = {
        '@': "¿Quisiste usar un operador? Intenta: + - * / ==",
        '#': "¿Comentario? Usa // para comentarios",
        '\\': "Escape no soportado",
        '$': "Variables sin $, solo nombre",
    }
    
    if char in suggestions:
        return suggestions[char]
    return f"Carácter '{char}' no permitido en MiniGUs"
```

Y al final de `lex()`, reemplaza el manejo de error:
```python
# En lugar de:
self.error(f"Carácter inesperado: {ch!r}")

# Haz:
suggestion = self.analyze_invalid_char(ch)
self.error(suggestion)
```

#### Paso B.3: Prueba
```bash
python3 test_lexer.py  # test_error.ms
```

**¿El mensaje es mejor?**
```
Respuesta:
_______________________________________________________________________
```

#### Paso B.4: Agrega Más Casos

Diseña **3 caracteres inválidos diferentes** y sus mensajes:
```python
# En analyze_invalid_char, agrega:
'?': "...",
...
```

#### Paso B.5: Reflexión

**Pregunta:** ¿Cómo este cambio afecta los "modos" del lexer?

Pista: ¿agregaste nuevos modos o solo mejoraste mensajes?
```
Respuesta:
_______________________________________________________________________
```

---

### 🔧 OPCIÓN C: Extensión - Strings y Floats

**Desafío:** Haz que MiniGUs soporte:
- Strings (cadenas): `"hola mundo"`
- Floats (decimales): `3.14`

**¿Por qué?** Lenguajes reales tienen tipos complejos.

#### Paso C.1: Entiende el Problema

Prueba esto:
```bash
cat > test_types.ms << 'EOF'
string msg = "hola";
float pi = 3.14;
EOF

python3 test_lexer.py  # ¿Funciona?
```

**¿Qué pasó?**
```
Respuesta:
_______________________________________________________________________
```

#### Paso C.2: Diseña para Strings

**Pregunta:** ¿Cómo reconoces un string?

Empieza con `"` y termina con `"`.

¿Eso es un nuevo "modo" del lexer?
```
Respuesta: Sí / No, porque...
_______________________________________________________________________
```

#### Paso C.3: Implementa Strings

En `lex()`, después de las palabras clave, agrega:
```python
# Strings
if ch == '"':
    line, col = self.line, self.col
    self.advance()  # Consume "
    s = []
    while self.peek() != '"':
        if self.peek() == '\0':
            raise SyntaxError(f"String no cerrado en {line}:{col}")
        s.append(self.advance())
    self.advance()  # Consume comilla final
    lexeme = ''.join(s)
    self.add("STRINGLIT", lexeme, line, col)
    continue
```

#### Paso C.4: Diseña para Floats

**Pregunta:** Un número como `3.14` tiene:
- Parte entera: `3`
- Punto: `.`
- Parte decimal: `14`

¿Cómo distingues `3.14` de dos tokens `3` y `.` y `14`?

Pista: cuando terminas de leer `3`, miras si sigue `.` con dígitos.
```
Tu estrategia:
_______________________________________________________________________
```

#### Paso C.5: Implementa Floats

Modifica donde procesas números:
```python
if ch.isdigit():
    si, sc, sl = self.i, self.col, self.line
    s = []
    while self.peek().isdigit():
        s.append(self.advance())
    
    # Mira si hay punto seguido de dígito
    if self.peek() == '.' and self.peek(1).isdigit():
        s.append(self.advance())  # Consume punto
        while self.peek().isdigit():
            s.append(self.advance())
        lexeme = ''.join(s)
        self.add("FLOATLIT", lexeme, sl, sc)
    else:
        lexeme = ''.join(s)
        self.add("INTLIT", lexeme, sl, sc)
    continue
```

#### Paso C.6: Prueba
```bash
python3 test_lexer.py  # test_types.ms
```

**¿Aparecen STRINGLIT y FLOATLIT?**
```
Respuesta: Sí / No
```

#### Paso C.7: Reflexión

**Pregunta:** ¿Cuántos modos nuevos agregaste?

Dibuja los modos:
```
START
  ├─ [letra] → IDENTIFIER_MODE
  ├─ [dígito] → NUMBER_MODE
  │    └─ [.dígito] → ¿? (FLOAT_MODE? o mismo?)
  ├─ ["] → ¿? (STRING_MODE?)
  └─ [símbolo] → SYMBOL_MODE

¿Cuáles son los modos nuevos?
_______________________________________________________________________
```

---

### 🔧 OPCIÓN D: Rendimiento - Hash Explícito

**Desafío:** Implementar tabla hash manual en lugar de diccionario.

**¿Por qué?** Entender cómo funciona hashing bajo la superficie.

#### Paso D.1: Entiende el Problema

Python usa diccionarios (ya son hash tables). Pero, **¿qué pasa si implementas una tu versión?**

Idea: en lugar de:
```python
kind = KEYWORDS.get(lexeme, "IDENT")
```

Hacer:
```python
kind = my_hash_table.get(lexeme, "IDENT")
```

#### Paso D.2: Diseña tu Hash Table
```python
class MyHashTable:
    def __init__(self, size=16):
        self.table = [None] * size
        self.size = size
    
    def hash(self, key):
        # Función hash simple
        h = 0
        for c in key:
            h = (h + ord(c)) % self.size
        return h
    
    def put(self, key, value):
        idx = self.hash(key)
        self.table[idx] = (key, value)
    
    def get(self, key, default=None):
        idx = self.hash(key)
        if self.table[idx]:
            return self.table[idx][1]
        return default
```

#### Paso D.3: Integra en Lexer

Reemplaza:
```python
KEYWORDS = {
    "int": "INTKW",
    ...
}
```

Con:
```python
keywords_hash = MyHashTable()
keywords_hash.put("int", "INTKW")
keywords_hash.put("bool", "BOOLKW")
...
```

Y en `lex()`:
```python
# Antes:
kind = KEYWORDS.get(lexeme, "IDENT")

# Ahora:
kind = keywords_hash.get(lexeme, "IDENT")
```

#### Paso D.4: Prueba
```bash
time python3 test_lexer.py  # Mide tiempo
```

#### Paso D.5: Compara

¿Es más rápido tu hash o el diccionario de Python?

**Prueba con archivo grande:**
```bash
python3 -c "print('int ' * 10000)" > big.ms
time python3 test_lexer.py big.ms
```
```
Resultado:
_______________________________________________________________________
```

#### Paso D.6: Reflexión

**Pregunta:** ¿Cambió algo en cómo el lexer "decide"?

Pista: El mecanismo de búsqueda cambió, pero ¿los modos?
```
Respuesta: Sí / No, porque...
_______________________________________________________________________
```

---

## PARTE 3: Documentación - Mapea Tu Descubrimiento (30 minutos)

### Paso 3.1: Escribe Tu Diagrama de Flujo (15 min)

Dibuja **cómo funciona tu lexer modificado**.

Usa este formato (ASCII art está bien):
```
          Input (carácter)
                ↓
    ┌─────────────────────────┐
    │  START (esperando)      │
    └─────────────────────────┘
           ↓    ↓    ↓    ↓
        [a-z] [0-9] ["] [+...]
           │     │    │    │
           ↓     ↓    ↓    ↓
      [ID]   [NUM] [STR] [SYM]
           │     │    │    │
           └─────┴────┴────┘
               ↓
        Crea Token → OUTPUT
```

Dibuja el tuyo (incluye tu mejora):
```
[Tu diagrama aquí]
```

---

### Paso 3.2: Escribe Tu Reporte (15 min)

Responde estas preguntas:

**1. ¿Qué mejora agregaste y por qué?**
```
Respuesta:
_______________________________________________________________________
_______________________________________________________________________
```

**2. ¿Qué "modos" nuevos tiene tu lexer comparado con el original?**
```
Respuesta:
_______________________________________________________________________
_______________________________________________________________________
```

**3. ¿Qué estructuras de datos usaste? ¿Por qué cada una?**
```
Respuesta:
_______________________________________________________________________
_______________________________________________________________________
```

**4. Escribe 2 casos de prueba:**

**Caso que funciona:**
```
Entrada:
[código MiniGUs aquí]

Token esperado:
[lista de tokens]

Token obtenido:
[qué imprimió tu lexer]

¿Correcto? Sí / No
```

**Caso límite (edge case):**
```
Entrada:
[código que prueba el límite]

¿Qué pasa?
[descripción]

¿Esperado? Sí / No
```

---

## PARTE 4: Reflexión Final - Tu Momento EUREKA (20 minutos)

### Paso 4.1: Responde Sin Ver Atrás (10 min)

**Pregunta 1:** Mira tu diagrama de flujo. Describe lo que ves:
```
¿Qué observas en tu diagrama?
_______________________________________________________________________
_______________________________________________________________________
```

**Pregunta 2:** ¿Tu lexer está en un "estado" mientras procesa?

☐ Sí, estados como: START, IN_IDENTIFIER, IN_NUMBER, etc.  
☐ No, solo procesa  

Explica:
```
_______________________________________________________________________
```

**Pregunta 3:** ¿Qué hace cambiar de estado?
```
_______________________________________________________________________
```

**Pregunta 4:** Cuando cambias de estado, ¿qué entrada causa el cambio?
```
_______________________________________________________________________
```

---

### Paso 4.2: Compara con las Diapositivas (10 min)

Ahora abre nuevamente las diapositivas del docente (Parte 0).

**Mira el diagrama que te mostraron al inicio.**

**Pregunta:** ¿Se parece a tu diagrama?
```
Respuesta:
_______________________________________________________________________
```

**Pregunta:** ¿Recuerdas la definición de autómata que viste?

"Un autómata es una máquina que:
- Existe en un ESTADO en cada momento
- Lee una ENTRADA
- Toma una DECISIÓN (transición)
- Cambia a un nuevo ESTADO"

**¿Tu lexer hace eso?**
```
Sí / No

¿Por qué?
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________
```

---

### Paso 4.3: Tu Pregunta Inicial (5 min)

Vuelve al Paso 0.1. Escribiste una pregunta al ver las diapositivas.

Esa pregunta era:
```
_______________________________________________________________________
```

**Ahora, ¿cuál es la respuesta?**
```
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________
```

---

##  CONCLUSIÓN: Tú Descubriste

**Lo que implementaste hace semanas (el lexer)  
es la implementación práctica de lo que estudiaste hoy (autómata).**

Específicamente, tu lexer es un **DFA (Deterministic Finite Automaton)**:

- **D**eterminístico: Una entrada → Una decisión (if/elif/else)
- **Finite**: Número finito de estados (START, ID, NUM, etc.)
- **Automaton**: Máquina que cambia de estado automáticamente

Tu mejora agregó **nuevas transiciones y estados** al autómata.

---

##  ENTREGABLE

Copia todo esto en un documento y entrega:

1. **Respuestas a Parte 1** (Análisis)
2. **Código modificado** (Parte 2 - tu mejora)
3. **Diagrama de flujo** (Parte 3)
4. **Reporte** (Parte 3)
5. **Reflexión** (Parte 4)

**Nombre del archivo:** `mi_lexer_eureka_[TU_NOMBRE].pdf`
Subelo a tu drive en la semana correspondiente
---


Felicidades. Acabas de descubrir que fuiste arquitecto de un autómata 
sin saberlo. Eso es compiladores.

# Anexo
## Tipos de Autómatas

#### 1. DFA (Deterministic Finite Automaton)
```
Característica: Una entrada → Una salida posible (determinístico)
Ejemplo: Lexer, validador de email
Poder: Reconoce lenguajes REGULARES
```

#### 2. NFA (Non-Deterministic Finite Automaton)
```
Característica: Una entrada → Múltiples salidas posibles
Ejemplo: Buscar patrón en texto (regex)
Poder: Igual poder que DFA, pero más expresivo
```

#### 3. PDA (Pushdown Automaton)
```
Característica: + PILA (memoria)
Ejemplo: Parser, validador de paréntesis anidados
Poder: Reconoce lenguajes LIBRES DE CONTEXTO (más potentes)
```

### Tabla Comparativa:

| Tipo | Memoria | Uso | Ejemplo |
|------|---------|-----|---------|
| DFA | Ninguna (solo estado) | Lexer | Reconocer `int`, `42`, `+` |
| NFA | Ninguna | Regex | Buscar `hola\*` |
| PDA | Pila | Parser | Validar `{...}` anidados |




---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)