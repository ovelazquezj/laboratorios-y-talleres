# EXPERIMENTO 0 – LÉXICO Y TU PRIMER COMPILADOR

Clase: Estructura de Datos y Compiladores
Semana: 1
Modalidad: Aprender haciendo
Proyecto: Compilador MiniGUs
Herramientas: Python, NASM, Make, Docker


## OBJETIVO DEL EXPERIMENTO

Construir, ejecutar y comprender un analizador léxico (*lexer*) que lea código fuente MiniGUs y lo transforme en una secuencia de tokens. Este es el primer componente real de tu compilador.


## INTRODUCCIÓN: ¿QUÉ ES UN LEXER?

Un lexer es el componente que lee texto plano y lo traduce a unidades léxicas significativas llamadas tokens.
Actúa como un portero en la entrada de una fiesta: solo deja pasar a quienes reconoce (palabras clave, identificadores, símbolos, etc.) y bloquea lo que no entiende (errores léxicos).

### Analogía: El Lexer como lector de etiquetas

Imagina que estás en un supermercado leyendo productos:

* “Pan Bimbo” → ID
* “\$25.00” → INTLIT
* “2x1” → símbolo/comando → MULTIPLY\_OFFER

El lexer hace eso: lee y clasifica.


## GLOSARIO BÁSICO

| Término       | Definición                                              |
| ------------- | ------------------------------------------------------- |
| Token         | Unidad reconocida del código (ej: `int`, `;`, `42`)     |
| Lexema        | Fragmento exacto del texto que forma un token           |
| Lexer         | Programa que separa y clasifica los tokens              |
| Símbolo       | Caracteres individuales como `+`, `=`, `{`, etc.        |
| Palabra clave | Palabras reservadas del lenguaje (`int`, `if`, `while`) |
| Identificador | Nombres definidos por el usuario (`x`, `contador`)      |
| Literal       | Valores constantes (`42`, `true`, `false`)              |


## FUNCIONES CLAVE EN EL LEXER: `peek()` Y `advance()`

### ¿Qué es `peek()`?

`peek()` permite mirar el carácter actual (o siguiente) **sin avanzar** en el texto. Es útil para tomar decisiones antes de consumir un carácter.

```python
def peek(self, k=0):
    j = self.i + k
    return '\0' if j >= self.n else self.text[j]
```

### ¿Qué es `advance()`?

`advance()` **consume el carácter actual** y mueve el cursor hacia adelante. También actualiza la línea y columna si encuentra un salto de línea.

```python
def advance(self):
    ch = self.peek()
    self.i += 1
    if ch == '\n':
        self.line += 1
        self.col = 1
    else:
        self.col += 1
    return ch
```

### ¿Cómo se usan juntos?

Ejemplo para reconocer una palabra:

```python
if ch.isalpha():
    start = self.i
    while self.peek().isalnum():
        self.advance()
    lexeme = self.text[start:self.i]
```

Esto agrupa caracteres mientras sean letras o dígitos, y luego crea el token.


## CÓDIGO COMPLETO DEL LEXER (EXPLICALO)

A continuación, presentamos el lexer base del compilador MiniGUs, explica lo que entiendes que hace ¿que clases la conforman? ¿que hace cada clase?.

```python
KEYWORDS = {
    "int": "INTKW", "bool": "BOOLKW", "if": "IF",
    "else": "ELSE", "while": "WHILE", "print": "PRINT",
    "read": "READ", "true": "TRUE", "false": "FALSE",
}

SYMBOLS = {
    "{": "LBRACE", "}": "RBRACE", "(": "LPAREN", ")": "RPAREN",
    "[": "LBRACK", "]": "RBRACK", ";": "SEMICOLON", ",": "COMMA",
    "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH", "%": "PERCENT",
    "=": "ASSIGN", "!": "BANG", "<": "LT", ">": "GT",
    "&&": "AND", "||": "OR", "==": "EQ", "!=": "NEQ", "<=": "LE", ">=": "GE",
}

class Token:
    def __init__(self, kind, lexeme, line, col):
        self.kind = kind
        self.lexeme = lexeme
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.kind}, {self.lexeme!r}, {self.line}:{self.col})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.i = 0
        self.line = 1
        self.col = 1
        self.n = len(text)
        self.tokens = []

    def peek(self, k=0):
        j = self.i + k
        return '\0' if j >= self.n else self.text[j]

    def advance(self):
        ch = self.peek()
        self.i += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def add(self, kind, lexeme, line=None, col=None):
        if line is None: line = self.line
        if col is None: col = self.col
        self.tokens.append(Token(kind, lexeme, line, col))

    def lex(self):
        while self.i < self.n:
            ch = self.peek()

            if ch.isspace():
                self.advance()
                continue

            if ch.isalpha():
                start = self.i
                while self.peek().isalnum() or self.peek() == '_':
                    self.advance()
                lexeme = self.text[start:self.i]
                kind = KEYWORDS.get(lexeme, "ID")
                self.add(kind, lexeme)
                continue

            if ch.isdigit():
                start = self.i
                while self.peek().isdigit():
                    self.advance()
                lexeme = self.text[start:self.i]
                self.add("INTLIT", lexeme)
                continue

            two = self.text[self.i:self.i+2]
            if two in SYMBOLS:
                self.add(SYMBOLS[two], two)
                self.advance(); self.advance()
                continue

            if ch in SYMBOLS:
                self.add(SYMBOLS[ch], ch)
                self.advance()
                continue

            self.add("INVALID", ch)
            self.advance()
```


## ACTIVIDADES GUIADAS

### Actividad 1 – Ejecutar el lexer base

Ejecuta el comando `make run` este te mostrara lo que hace el compilador completo (lexer + parser + generador de ensamblador + ejecución del binario). 

Para este primer experimento queremos enfocarnos **solo en el lexer**. Crea un archivo nuevo llamado `test_lexer.py` con el siguiente contenido:

```python
from src.lexer import Lexer

with open("examples/01_sum.ms") as f:
    text = f.read()

lexer = Lexer(text)
lexer.lex()

for token in lexer.tokens:
    print(token)
```

Ejecuta:

```bash
python3 test_lexer.py
```

Esto imprimirá los tokens detectados directamente, por ejemplo:

```
Token(INTKW, 'int', 1:1)
Token(ID, 'x', 1:5)
Token(SEMICOLON, ';', 1:6)
Token(ID, 'x', 2:1)
Token(ASSIGN, '=', 2:3)
Token(INTLIT, '42', 2:5)
Token(SEMICOLON, ';', 2:7)
.
.
.
Token(INTKW, 'int', 1:1)
Token(ID, 'x', 1:5)
Token(SEMICOLON, ';', 1:6)
Token(ID, 'x', 2:1)
Token(ASSIGN, '=', 2:3)
Token(INTLIT, '42', 2:5)
Token(SEMICOLON, ';', 2:7)

```


Agrega la instruccion lexer a tu Makefile para automatizar su ejecución

### Actividad 2 – Construye tu propio lexer desde cero

En esta actividad vas a crear tu propio lexer paso a paso, implementando el algoritmo básico de análisis léxico. Crea un archivo nuevo llamado `lexer_mi_version.py` y sigue este proceso:

#### Algoritmo del lexer básico

1. **Leer el archivo fuente completo**
```python
   with open("examples/01_sum.ms") as f:
       text = f.read()
```

2. **Inicializar variables de control**

   * Índice `i` = 0
   * Línea `line` = 1
   * Columna `col` = 1
   * Lista `tokens = []`

3. **Mientras no llegues al final del texto:**

   * Mira el carácter actual con `peek()`
   * Si es espacio → avanzar y continuar
   * Si es letra → acumular hasta que no haya más letras o dígitos → crear token (palabra clave o identificador)
   * Si es dígito → acumular hasta que no haya más dígitos → crear token (literal entero)
   * Si es símbolo conocido (`+`, `;`, `==`, etc.) → crear token de símbolo
   * En otro caso → crear token INVALID

4. **Guardar cada token** con: tipo, lexema, línea y columna.

5. **Imprimir los tokens al final**.

Ejemplo de prueba inicial:

Archivo de entrada:

```c
bool b;
b = true;
```

Ejecución:

```bash
python3 lexer_mi_version.py
```

Salida esperada:

```
Token(BOOLKW, 'bool', 1:1)
Token(ID, 'b', 1:6)
Token(SEMICOLON, ';', 1:7)
Token(ID, 'b', 2:1)
Token(ASSIGN, '=', 2:3)
Token(TRUE, 'true', 2:5)
Token(SEMICOLON, ';', 2:9)
```


### Actividad 3 – Agrega detección de palabra clave nueva

Ahora que ya tienes un lexer funcionando, vas a extenderlo agregando una palabra clave nueva al lenguaje.

#### Algoritmo de extensión

1. **Abrir tu diccionario KEYWORDS** y añadir:

   ```python
   "const": "CONST",
   ```

2. **Ejecutar una prueba con el siguiente archivo fuente:**

   ```c
   const int a;
   a = 10;
   ```

3. **Ejecutar tu lexer**:

   ```bash
   python3 lexer_mi_version.py
   ```

4. **Salida esperada:**

   ```
   Token(CONST, 'const', 1:1)
   Token(INTKW, 'int', 1:7)
   Token(ID, 'a', 1:11)
   Token(SEMICOLON, ';', 1:12)
   Token(ID, 'a', 2:1)
   Token(ASSIGN, '=', 2:3)
   Token(INTLIT, '10', 2:5)
   Token(SEMICOLON, ';', 2:7)
   ```

Con esto aprendes cómo el lexer se puede extender de forma incremental siguiendo el mismo patrón del algoritmo.


## EVALUACIÓN ESPERADA

| Criterio                                | Puntaje |
| --------------------------------------- | ------- |
| Lexer imprime tokens correctamente      | 40%     |
| Incluye mínimo 2 tipos de tokens nuevos | 20%     |
| Uso correcto del Makefile               | 20%     |
| Estilo de código claro y comentado      | 10%     |
| Bitácora de errores detectados          | 10%     |


## REFLEXIÓN FINAL

Este laboratorio te dio las herramientas para construir el primer paso de un compilador.
Aprendiste cómo leer código, identificar patrones y traducir texto a estructuras comprensibles.
Has enseñado al compilador a leer.


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)