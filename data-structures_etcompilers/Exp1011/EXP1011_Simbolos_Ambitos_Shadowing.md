# Laboratorio: Tabla de Símbolos, Ámbitos Anidados y Shadowing en MiniGUS

**Curso:** Estructuras de Datos y Compiladores  
**Semana:** 11 
**Proyecto:** Compilador MiniGUS  

---

## Objetivos del Laboratorio

Al completar este laboratorio, serás capaz de:

1. **Entender el modelo de tabla de símbolos plana actual** en `symbols.py` y reconocer sus limitaciones para manejar ámbitos anidados.

2. **Analizar cómo el parser** (`parser.py`) interactúa con la tabla de símbolos al declarar y usar identificadores, y por qué actualmente no maneja bloques anidados con ámbitos locales.

3. **Diseñar e implementar una pila de scopes** que reemplace el modelo plano, permitiendo que la tabla de símbolos maneje ámbitos jerárquicos y bloques anidados.

4. **Integrar el nuevo modelo de scopes** con el parser, modificando `parse_block()` para que llame a `enter_scope()` y `leave_scope()` en los momentos correctos.

5. **Experimentar con fenómenos de shadowing** (cuando un identificador local oculta a uno externo del mismo nombre) mediante programas de prueba ejecutados con el compilador.

6. **Reflexionar sobre cómo las limitaciones de ámbitos** impactan en compiladores reales y cómo la estructura jerárquica resuelve problemas de resolución de nombres.

---

## Contexto y Recordatorio

En el laboratorio de la primera semana (EXP0 – Léxico), trabajaste con el analizador léxico (*lexer*) de MiniGUS. Aprendiste cómo la entrada de texto sin estructura se transforma en una secuencia de tokens, y comprendiste que el lexer implementa conceptos de máquinas de estados (DFA).

Ahora nos enfocamos en la **siguiente etapa del compilador**: el análisis semántico a través de la **tabla de símbolos**. 

El lexer nos dio tokens; ahora necesitamos entender qué representan esos identificadores:
- ¿Qué tipo tienen? (`int` o `bool`)
- ¿Dónde se declararon?
- ¿En qué ámbito son válidos?
- ¿Qué pasa cuando el mismo nombre aparece en ámbitos diferentes?

Esto es precisamente lo que **gestiona la tabla de símbolos**. En compiladores reales, es una "base de datos interna" que mapea nombres a información semántica completa, permitiendo detectar errores y generar código correcto.

---

## Cómo Ejecutar el Compilador

### Ejecución Local

El compilador MiniGUS incluye un `Makefile` que automatiza la compilación y ejecución. Sigue estos pasos:

#### 1. Ejecutar el compilador completo (lexer + parser + generación de código)

```bash
make run
```

Este comando compila un programa MiniGUS por defecto y lo ejecuta. Es útil para ver el flujo completo del compilador.

#### 2. Ejecutar un archivo específico de prueba

Si deseas compilar y ejecutar un archivo `.ms` específico, puedes modificar el Makefile o usar directamente Python:

```bash
python3 main.py examples/01_sum.ms
```

Esto ejecutará el compilador sobre `01_sum.ms` e imprimirá:
- Tokens generados (si hay verbose/debug activo)
- Errores semánticos o sintácticos (si existen)
- Resultado de la ejecución del código compilado

#### 3. Ejecutar solo el parser con un archivo de prueba

Para este laboratorio, a menudo querrás probar solo el parser y la tabla de símbolos sin generar código:

```bash
python3 -c "
from src.lexer import Lexer
from src.parser import Parser

with open('examples/01_sum.ms') as f:
    source = f.read()

lexer = Lexer(source)
tokens = lexer.lex()
parser = Parser(tokens)
try:
    parser.parse_program()
    print('✓ Parse completado exitosamente')
except Exception as e:
    print(f'✗ Error: {e}')
"
```

**Nota:** Los comandos anteriores son los mismos que se usaron en EXP0. Adapta las rutas según tu estructura de proyecto.

#### 4. Crear un script de prueba local

Para pruebas repetidas, es recomendable crear un archivo `test_symbols.py` en la raíz del proyecto:

```python
#!/usr/bin/env python3
import sys
from src.lexer import Lexer
from src.parser import Parser

def test_file(filename):
    """Prueba un archivo .ms y reporta errores semánticos."""
    try:
        with open(filename) as f:
            source = f.read()
        lexer = Lexer(source)
        tokens = lexer.lex()
        parser = Parser(tokens)
        parser.parse_program()
        print(f"✓ {filename}: Análisis completado")
        return True
    except SyntaxError as e:
        print(f"✗ {filename}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_file(sys.argv[1])
    else:
        # Prueba todos los ejemplos
        for example in ["examples/01_sum.ms", "examples/02_mod.ms"]:
            test_file(example)
```

Luego ejecuta:

```bash
python3 test_symbols.py examples/01_sum.ms
```

---

## Sección A: Análisis del Estado Actual de la Tabla de Símbolos

### ¿Qué es un símbolo en MiniGUS?

Un **símbolo** es una representación interna de un identificador declarado en el programa. En MiniGUS, cada símbolo almacena:

- **`name`**: el identificador textual (ej: `x`, `suma`, `flag`)
- **`type`**: el tipo del símbolo (`T_INT` o `T_BOOL`)
- **`is_array`**: si es un arreglo o variable escalar
- **`size`**: tamaño del arreglo (si aplica)
- **`extern_name`**: nombre externo usado en el código generado (ej: `var_x`, `var_suma`)

### Modelo Actual: La Tabla Plana

Actualmente, `symbols.py` implementa una tabla de símbolos **plana** (diccionario simple):

```python
class Symbols:
    def __init__(self):
        self.table = {}  # Diccionario simple: { "x": Sym(...), "y": Sym(...) }

    def declare(self, name, ty, is_array=False, size=0):
        if name in self.table:
            raise SyntaxError(f"Redeclaración de '{name}'")
        sym = Sym(name, ty, is_array, size)
        self.table[name] = sym
        return sym

    def get(self, name):
        if name not in self.table:
            raise SyntaxError(f"Identificador no declarado '{name}'")
        return self.table[name]
```

**Características:**
- Todos los símbolos se almacenan en un único diccionario.
- No hay diferenciación entre ámbito global y local.
- Una redeclaración en cualquier parte del programa causa error.
- La búsqueda siempre ocurre en la misma tabla.

### Limitaciones del Modelo Plano

Este modelo funciona para programas simples, pero tiene limitaciones críticas:

1. **Sin ámbitos anidados:** No es posible que una variable local en un bloque `{...}` tenga el mismo nombre que una variable global. Ejemplo:

   ```c
   int x;        // x global
   x = 5;
   if (true) {
     int x;      // ¿Nuevo x local? No, actualmente ERROR: redeclaración
     x = 10;
   }
   ```

2. **Sin visibilidad local:** Todas las variables son "globales". No hay concepto de que un símbolo declarado dentro de un bloque deje de existir al salir del bloque.

3. **Resolución de nombres uniforme:** Cuando usas un identificador, solo se busca en la tabla global. No hay forma de "resolver hacia afuera" desde un ámbito local hasta encontrar un símbolo en un ámbito más externo.

4. **Imposible implementar shadowing intencional:** En muchos lenguajes, el shadowing es válido y útil. Aquí no es posible.

### Preguntas Guiadas (Responder en tu reporte)

1. ¿Cuáles son los campos de la clase `Sym`? ¿Qué información representa cada uno?

2. Mira el archivo `symbols.py`. ¿Cómo se almacenan los símbolos? ¿Es un diccionario, una lista, un árbol?

3. ¿Qué sucede hoy si declaras una variable `int x;` dos veces en el mismo programa?

4. ¿Hay alguna verificación de ámbito local vs global en el método `declare()`? ¿Por qué?

5. ¿Cómo se vería el diccionario `self.table` después de procesar las primeras 2 líneas del archivo `01_sum.ms`?

---

## Sección B: Conexión con el Parser

### Dónde se Usa la Tabla de Símbolos

En `parser.py`, la tabla de símbolos se crea una sola vez:

```python
class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0
        self.syms = Symbols()  # ← Una única instancia global
        self.em = Emitter()
```

Luego se usa en varios puntos:

#### 1. **Declaración de símbolos** (`parse_decl()`)

Cuando el parser ve `int x;` o `bool flag;`, llama a:

```python
sym = self.syms.declare(name, ty, is_array, size)
```

Esto agrega el símbolo a la tabla.

#### 2. **Uso de identificadores** (`parse_primary()`, `parse_lvalue_address()`)

Cuando el parser ve un identificador usado en una expresión o asignación:

```python
sym = self.syms.get(ident)  # Busca el símbolo
```

Si el símbolo no existe, lanza error semántico.

### Análisis de `parse_block()`

Actualmente, `parse_block()` reconoce bloques `{...}` pero NO maneja ámbitos:

```python
def parse_block(self):
    self.eat("LBRACE")
    while not self.at("RBRACE"):
        if self.at("INTKW") or self.at("BOOLKW"):
            self.parse_decl()  # Declara aquí
        else:
            self.parse_stmt()
    self.eat("RBRACE")
```

**Observación:** No hay `enter_scope()` ni `leave_scope()`. Todas las declaraciones van a la misma tabla global.

### Preguntas Guiadas (Responder en tu reporte)

1. ¿Cuántas instancias de `Symbols` existen durante la ejecución del compilador? ¿Una, varias, o depende del programa?

2. Busca en `parser.py` todos los lugares donde se llama a `self.syms.declare()`. ¿En qué métodos ocurre?

3. Busca todos los lugares donde se llama a `self.syms.get()`. ¿Qué diferencia hay entre un `declare()` y un `get()`?

4. En `parse_block()`, ¿hay alguna llamada a funciones que no ves en el código actual? (Pista: funciones que deberían existir pero no existen todavía.)

5. Traza la ejecución de `01_sum.ms` a través del parser. ¿Qué orden de declaraciones ocurre?

---

## Sección C: Diseño e Implementación de la Pila de Scopes

### Visión de la Nueva Tabla de Símbolos

En lugar de:

```python
self.table = {}  # Un diccionario plano
```

Queremos:

```python
self.scopes = [{}]  # Una lista de diccionarios (pila de scopes)
```

**Idea central:** Cada bloque anidado tiene su propio diccionario. Al entrar en un bloque, empilamos un nuevo diccionario. Al salir, desempilamos.

### Ejemplo de Ejecución

Considera este pseudocódigo:

```
INICIO: scopes = [{}]  (scope global vacío)

int x;
  → scopes = [{ "x": Sym(int) }]

if (...) {
  ENTER_SCOPE
    → scopes = [{ "x": Sym(int) }, {}]  (nuevo scope vacío)

  int x;  (declarar x en el scope local)
    → scopes = [{ "x": Sym(int) }, { "x": Sym(int) }]

  x = 10;  (usar x, busca "afuera hacia adentro")
    → Encuentra el "x" del scope local (el más profundo)

  int y;
    → scopes = [{ "x": Sym(int) }, { "x": Sym(int), "y": Sym(int) }]

}
  LEAVE_SCOPE
    → scopes = [{ "x": Sym(int) }]  (scope local desaparece)

x = 20;  (ahora se refiere al x global)
```

### Métodos a Implementar/Modificar

Necesitarás implementar o modificar los siguientes métodos en la clase `Symbols`:

#### 1. `__init__`
Inicializa la pila con un scope global vacío.

#### 2. `enter_scope()`
Empila un nuevo diccionario vacío. Las nuevas declaraciones irán aquí.

#### 3. `leave_scope()`
Desempila el scope actual. Las declaraciones de ese scope desaparecen del alcance.

#### 4. `declare(name, ty, is_array=False, size=0)`
**Modificar:** Declara el símbolo **solo en el scope actual** (el tope de la pila).
- Si el símbolo ya existe **en el scope actual**, lanza error (redeclaración en el mismo scope).
- Si existe en un scope más externo, es válido (esto es shadowing).
- Almacena el símbolo en `self.scopes[-1][name]`.

#### 5. `get(name)`
**Modificar:** Busca el símbolo **desde el scope actual hacia afuera** (búsqueda hacia el scope global).
- Itera `self.scopes` desde el final hacia el inicio.
- Retorna el primer símbolo que encuentra con ese nombre.
- Si no encuentra en ningún scope, lanza error.

### Pseudocódigo de Implementación

No te damos el código exacto porque es tu laboratorio. Aquí están los pasos:

**Para `enter_scope()`:**
```
Agregar un nuevo diccionario vacío al final de self.scopes
```

**Para `leave_scope()`:**
```
Si quedan scopes después del global, remover el último
(Nunca remover el scope global, que siempre debe estar)
```

**Para `declare()`:**
```
scope_actual = self.scopes[-1]  (el último, el más profundo)
Si name está en scope_actual:
    Lanzar error (redeclaración en el mismo scope)
Crear Sym(...)
Guardar en scope_actual[name]
Retornar Sym
```

**Para `get()`:**
```
Para i desde len(self.scopes) - 1 hasta 0 (hacia atrás):
    Si name está en self.scopes[i]:
        Retornar self.scopes[i][name]
Lanzar error (identificador no declarado)
```

### Restricciones de Implementación

1. **No cambies la clase `Sym`.** Esa clase está bien como está.

2. **Preserva la interfaz pública.** Los métodos `declare()` y `get()` deben tener la misma firma (parámetros) que ahora. El parser no debe cambiar la forma de llamarlos.

3. **El scope global siempre debe estar.** Nunca desapilues el primer diccionario (índice 0).

4. **Nombres externos únicos.** El campo `extern_name` debe seguir siendo único para evitar conflictos en la generación de código. Una estrategia simple: usa `f"var_{name}_{depth}"` donde `depth` es la profundidad del scope, o usa un contador incremental.

---

## Sección D: Integración con el Parser

### Modificación de `parse_block()`

Actualmente:

```python
def parse_block(self):
    self.eat("LBRACE")
    while not self.at("RBRACE"):
        if self.at("INTKW") or self.at("BOOLKW"):
            self.parse_decl()
        else:
            self.parse_stmt()
    self.eat("RBRACE")
```

**Debes modificarlo para:**

```python
def parse_block(self):
    self.eat("LBRACE")
    self.syms.enter_scope()  # ← NUEVO: Entrar en nuevo scope
    
    while not self.at("RBRACE"):
        if self.at("INTKW") or self.at("BOOLKW"):
            self.parse_decl()
        else:
            self.parse_stmt()
    
    self.syms.leave_scope()  # ← NUEVO: Salir del scope
    self.eat("RBRACE")
```

**Explicación:**
- Al entrar en `{`, empilamos un nuevo scope.
- Todas las declaraciones dentro del bloque van a este nuevo scope.
- Al salir de `}`, desempilamos el scope. Las variables locales desaparecen del alcance.

### ¿Dónde más cambiar?

El método `parse_program()` también debería comenzar en un scope (el global). Actualiza su inicio si es necesario:

```python
def parse_program(self):
    # Asegúrate de que ya haya un scope global
    # La inicialización en __init__ debe hacerlo
    while not self.at("EOF"):
        if self.at("INTKW") or self.at("BOOLKW"):
            self.parse_decl()
        else:
            self.parse_stmt()
```

---

## Sección E: Pruebas de Shadowing

### ¿Qué es el Shadowing?

**Shadowing** (o "ocultamiento") ocurre cuando un identificador declarado en un ámbito interno tiene el mismo nombre que uno en un ámbito externo. El identificador interno "oculta" al externo dentro de ese bloque.

**Ejemplo:**

```c
int x;
x = 5;
if (true) {
  int x;        // Nuevo x local (shadows al global)
  x = 10;       // Asigna al x local, no al global
  print(x);     // Imprime 10
}
print(x);       // Imprime 5 (el x global aún tiene su valor)
```

### Programas de Prueba Propuestos

Crea estos archivos en la carpeta `examples/` y úsalos para probar tu implementación:

#### Prueba 1: Shadowing Simple

**Archivo:** `examples/shadow_simple.ms`

```c
int x;
x = 100;
if (true) {
  int x;
  x = 50;
}
print(x);
```

**Comportamiento esperado:**
- El `x` global recibe 100.
- El `x` local en el bloque recibe 50 (no afecta al global).
- Al imprimir, debe mostrar 100 (el valor del global).

#### Prueba 2: Múltiples Niveles de Anidamiento

**Archivo:** `examples/shadow_nested.ms`

```c
int x;
x = 1;
if (true) {
  int x;
  x = 2;
  if (true) {
    int x;
    x = 3;
    print(x);  // Debe imprimir 3
  }
  print(x);    // Debe imprimir 2
}
print(x);      // Debe imprimir 1
```

**Comportamiento esperado:**
- Tres niveles de x: global = 1, nivel 1 = 2, nivel 2 = 3.
- En el nivel más profundo, se imprime 3.
- Al retroceder, se imprime 2.
- En el global, se imprime 1.

#### Prueba 3: Shadowless References

**Archivo:** `examples/no_shadow.ms`

```c
int x;
int y;
x = 10;
y = 20;
if (true) {
  int z;
  z = x + y;  // x e y vienen del scope global
  print(z);   // Debe imprimir 30
}
```

**Comportamiento esperado:**
- `x` e `y` no están redeclarados en el bloque local.
- Dentro del bloque, se buscan hacia afuera y se encuentran en el global.
- La suma se calcula correctamente.

#### Prueba 4: Error de Redeclaración en el Mismo Scope

**Archivo:** `examples/error_redecl.ms`

```c
int x;
if (true) {
  int x;
  int x;  // ERROR: Redeclaración en el mismo scope
}
```

**Comportamiento esperado:**
- El compilador debe lanzar un error semántico.
- El mensaje debe indicar que `x` ya fue declarado en este scope.

### Cómo Ejecutar las Pruebas

```bash
# Prueba 1
python3 main.py examples/shadow_simple.ms

# Prueba 2
python3 main.py examples/shadow_nested.ms

# Prueba 3
python3 main.py examples/no_shadow.ms

# Prueba 4 (debe fallar con error)
python3 main.py examples/error_redecl.ms
```

Si configuraste el script `test_symbols.py` del laboratorio anterior, puedes usarlo:

```bash
python3 test_symbols.py examples/shadow_simple.ms
```

---

## Sección F: Actividad de Experimentación

### Diseña Tus Propios Casos de Prueba

Crea al menos **2–3 archivos `.ms` adicionales** que exploren situaciones donde el shadowing sea relevante:

#### Caso A: Shadowing Útil

Diseña un programa donde el shadowing sea intencional y beneficioso. Por ejemplo:
- Una variable contadora global y contadores locales en diferentes bloques.
- Nombres que se reutilizan de forma inteligible en distintos contextos.

**Archivo sugerido:** `examples/shadow_useful.ms`

#### Caso B: Shadowing Confuso

Diseña un programa donde el shadowing cause confusión o potencial bug:
- Muchos niveles de anidamiento.
- Múltiples variables con el mismo nombre que fácilmente pueden confundir.
- Referencia a la variable equivocada debido a la profundidad del scope.

**Archivo sugerido:** `examples/shadow_confusing.ms`

#### Caso C: Combinación de Bloques

Diseña un programa que use `if`, `while`, y bloques anidados para explorar cómo los scopes interactúan:
- Declaraciones dentro de `while`.
- Declaraciones dentro de `if` anidado dentro de `while`.
- Variables locales en cada nivel.

**Archivo sugerido:** `examples/shadow_complex.ms`

### Instrucciones para la Experimentación

1. **Predice el comportamiento:** Antes de ejecutar cada programa, escribe qué esperas que suceda. Sé específico sobre qué valor tendrá cada variable en cada punto.

2. **Ejecuta el compilador:** Usa `python3 main.py ejemplos/...` para cada caso.

3. **Compara con predicciones:** ¿Coincidió el resultado? Si no, ¿por qué?

4. **Documenta hallazgos:** En tu reporte, incluye los casos de prueba, predicciones y resultados reales. Explica cualquier discrepancia.

---

## Sección G: Depuración y Diagnóstico

### Cómo Verificar tu Implementación

Para verificar que tu nueva tabla de símbolos está funcionando correctamente, añade capacidad de depuración. Puedes modificar temporalmente `parse_program()` o crear un método auxiliar:

```python
def print_scopes(self):
    """Método auxiliar para depuración: imprime el estado actual de scopes."""
    for i, scope in enumerate(self.scopes):
        print(f"Scope {i}:")
        for name, sym in scope.items():
            print(f"  {name}: type={sym.type}, extern_name={sym.extern_name}")
```

Llama a este método en puntos estratégicos del parser para ver cómo cambia la pila de scopes:

```python
def parse_block(self):
    self.eat("LBRACE")
    self.syms.enter_scope()
    print(f"DEBUG: Entrando en scope. Pila tiene {len(self.syms.scopes)} niveles.")
    
    while not self.at("RBRACE"):
        if self.at("INTKW") or self.at("BOOLKW"):
            self.parse_decl()
        else:
            self.parse_stmt()
    
    self.syms.leave_scope()
    print(f"DEBUG: Saliendo de scope. Pila tiene {len(self.syms.scopes)} niveles.")
    self.eat("RBRACE")
```

Luego ejecuta un ejemplo pequeño:

```bash
python3 main.py examples/shadow_simple.ms
```

Deberías ver líneas como:

```
DEBUG: Entrando en scope. Pila tiene 2 niveles.
DEBUG: Saliendo de scope. Pila tiene 1 nivel.
```

---

## Sección H: Rúbrica de Evaluación y Conclusión

Este laboratorio se evalúa en **125 puntos** según los siguientes criterios:

---

### Criterio 1: Implementación de Métodos de Scope (25 puntos)

**¿Qué se evalúa?** Que implementaste correctamente `enter_scope()` y `leave_scope()`.

**Indicadores de éxito:**

- **Completo (25 pts):** 
  - `enter_scope()` agrega un diccionario vacío a la pila
  - `leave_scope()` desempila correctamente
  - Nunca se desempila el scope global (siempre queda al menos uno)
  - Se comprueba y testea con al menos 2 ejemplos

- **Parcial (15-20 pts):**
  - Los métodos existen pero tienen pequeños bugs
  - Ocasionalmente desempilan el scope global (pero funcionan en casos simples)
  - Se prueban con un ejemplo

- **Insuficiente (0-10 pts):**
  - Los métodos no funcionan correctamente
  - Se desempila el scope global causando errores
  - No se prueban

**Cómo verificar tu trabajo:**
```python
# Después de implementar, ejecuta:
syms = Symbols()
print(len(syms.scopes))  # Debe imprimir 1 (scope global)
syms.enter_scope()
print(len(syms.scopes))  # Debe imprimir 2
syms.leave_scope()
print(len(syms.scopes))  # Debe imprimir 1 (volvió al global)
```

---

### Criterio 2: Modificación de `declare()` (25 puntos)

**¿Qué se evalúa?** Que `declare()` ahora respeta los scopes locales y permite shadowing.

**Indicadores de éxito:**

- **Completo (25 pts):**
  - `declare()` verifica redeclaración **solo en el scope actual**
  - Permite declarar el mismo nombre en scopes diferentes (shadowing)
  - Genera `extern_name` único por profundidad del scope
  - Se prueba con ejemplos shadow_simple.ms y shadow_nested.ms

- **Parcial (15-20 pts):**
  - `declare()` verifica redeclaración pero con pequeños bugs
  - Permite shadowing pero los `extern_name` pueden tener colisiones
  - Se prueba con un ejemplo

- **Insuficiente (0-10 pts):**
  - `declare()` sigue siendo global (no respeta scopes)
  - No permite shadowing o genera errores incorrectos
  - No se prueba

**Cómo verificar tu trabajo:**
```python
# Debe funcionar sin errores:
syms = Symbols()
x1 = syms.declare("x", T_INT)  # Scope 0
print(x1.extern_name)  # Debe ser diferente de x2

syms.enter_scope()
x2 = syms.declare("x", T_INT)  # Scope 1 (shadowing)
print(x2.extern_name)  # Diferente a x1

# Pero esto debe lanzar error:
try:
    syms.declare("x", T_INT)  # Segunda declaración en scope 1
except SyntaxError:
    print("✓ Redeclaración detectada correctamente")
```

---

### Criterio 3: Modificación de `get()` (25 puntos)

**¿Qué se evalúa?** Que `get()` busca desde el scope actual hacia afuera (hacia el global).

**Indicadores de éxito:**

- **Completo (25 pts):**
  - `get()` busca desde el scope más profundo hacia el global
  - Retorna el símbolo del scope más profundo que lo contiene
  - Lanza error si no encuentra en ningún scope
  - Se prueba con ejemplos no_shadow.ms y shadow_nested.ms

- **Parcial (15-20 pts):**
  - `get()` busca pero con pequeños bugs en la dirección
  - Encuentra símbolos pero ocasionalmente retorna el incorrecto
  - Se prueba con un ejemplo

- **Insuficiente (0-10 pts):**
  - `get()` solo busca en el scope actual
  - No resuelve símbolos de scopes externos
  - No se prueba

**Cómo verificar tu trabajo:**
```python
# Debe encontrar en scope externo:
syms = Symbols()
x_global = syms.declare("x", T_INT)  # Scope 0

syms.enter_scope()  # Scope 1
x_found = syms.get("x")  # Busca en scope 1, luego 0
assert x_found.extern_name == x_global.extern_name
print("✓ Búsqueda hacia afuera funciona")

# Pero debe encontrar el local si existe:
syms.declare("x", T_INT)  # Redeclaración en scope 1 (shadowing)
x_found = syms.get("x")  # Busca en scope 1 primero
assert x_found.extern_name != x_global.extern_name
print("✓ Shadowing funciona")
```

---

### Criterio 4: Integración con Parser (15 puntos)

**¿Qué se evalúa?** Que modificaste `parse_block()` correctamente para manejar scopes.

**Indicadores de éxito:**

- **Completo (15 pts):**
  - `parse_block()` llama a `enter_scope()` inmediatamente después de `eat("LBRACE")`
  - `parse_block()` llama a `leave_scope()` inmediatamente antes de `eat("RBRACE")`
  - No hay otras modificaciones en el parser
  - El compilador ejecuta sin errores en ejemplos prueba

- **Parcial (10 pts):**
  - `enter_scope()` o `leave_scope()` están en posición incorrecta
  - El compilador funciona parcialmente
  - Hay cambios innecesarios en otros métodos

- **Insuficiente (0-5 pts):**
  - Las llamadas no están presentes
  - El compilador falla al procesar bloques anidados

**Cómo verificar tu trabajo:**
```bash
# Ejecuta ejemplos con bloques anidados:
python3 main.py examples/shadow_simple.ms
python3 main.py examples/shadow_nested.ms
# Ambos deben ejecutarse sin errores semánticos
```

---

### Criterio 5: Pruebas y Ejecución (20 puntos)

**¿Qué se evalúa?** Que probaste tu implementación con los ejemplos propuestos.

**Indicadores de éxito:**

- **Completo (20 pts):**
  - Ejecutaste al menos 4 de los 8 ejemplos (shadow_simple.ms, shadow_nested.ms, no_shadow.ms, error_redecl.ms)
  - Documentaste la salida esperada vs salida real
  - Todos los ejemplos funcionan correctamente
  - Comparaste predicciones vs resultados reales

- **Parcial (12-18 pts):**
  - Ejecutaste 2-3 ejemplos
  - Documentaste parcialmente los resultados
  - Algunos ejemplos fallan pero explicaste por qué

- **Insuficiente (0-10 pts):**
  - Ejecutaste 0-1 ejemplo o no documentaste
  - No hay comparación de predicciones vs resultados

**Cómo documentar:**

En tu reporte incluye una tabla como esta para cada ejemplo:

```
Ejemplo: shadow_simple.ms
─────────────────────────────────────────────
Predicción:   El programa imprimirá 100
Salida Real:  100
¿Coincidió?:  SÍ ✓

Explicación: El x global recibe 100. Aunque hay un x local 
dentro del if con valor 50, al salir del bloque, ese x desaparece 
del alcance. Por eso se imprime el x global (100).
```

---

### Criterio 6: Experimentación Propia (20 puntos)

**¿Qué se evalúa?** Que diseñaste 2-3 ejemplos propios de shadowing/scopes.

**Indicadores de éxito:**

- **Completo (20 pts):**
  - Creaste 3 ejemplos propios (archivos .ms) con nombres descriptivos
  - Cada ejemplo explora un aspecto diferente (útil, confuso, complejo)
  - Ejecutaste y documentaste el comportamiento
  - Incluiste predicción y resultado real
  - Reflexionaste sobre lo que aprendiste con cada ejemplo

- **Parcial (12-18 pts):**
  - Creaste 2 ejemplos propios
  - Documentación parcial
  - Algunos fallan pero explicaste por qué

- **Insuficiente (0-10 pts):**
  - Creaste 0-1 ejemplo
  - Sin documentación o sin ejecución

**Qué incluir en cada ejemplo:**
```markdown
## Ejemplo Propio 1: [Nombre descriptivo]

**Objetivo:** [Qué aspecto de scopes/shadowing exploras]

**Código:**
[Tu código .ms]

**Predicción:** [Qué esperas que ocurra]

**Resultado Real:** [Qué pasó al ejecutar]

**Análisis:** [Por qué ocurrió, qué aprendiste]
```

---

### Criterio 7: Reflexión Crítica (15 puntos)

**¿Qué se evalúa?** Que reflexionaste profundamente sobre lo aprendido.

**Preguntas que debes responder (elige 3 de 5):**

1. ¿Cómo la pila de scopes resuelve el problema de visibilidad de nombres que tenía el modelo plano?
2. ¿Por qué es importante que la búsqueda de nombres sea "hacia afuera" en lugar de "solo en el scope actual"?
3. ¿Cuándo es útil permitir shadowing en un lenguaje? ¿Cuándo es fuente de confusión?
4. Ahora que implementaste scopes, ¿qué otros problemas semánticos podrías detectar? (Ejemplos: variables no inicializadas, argumentos de función, acceso a miembros de clases)
5. ¿Cómo cambiaría tu implementación si MiniGUS tuviera funciones, donde cada función introduce su propio scope?

**Indicadores de éxito:**

- **Completo (15 pts):**
  - Respondiste 3 preguntas con profundidad (mínimo 5 líneas cada una)
  - Conectaste conceptos del laboratorio
  - Demostraste entender cómo los scopes impactan en compiladores reales

- **Parcial (10-12 pts):**
  - Respondiste 3 preguntas pero parcialmente
  - Respuestas superficiales pero demuestran comprensión

- **Insuficiente (0-8 pts):**
  - Respondiste menos de 3 preguntas o muy brevemente
  - No hay conexión con conceptos más amplios

---

## Matriz de Evaluación Resumen

| Criterio | Puntaje Máx | Tu Puntaje |
|----------|-------------|-----------|
| 1. Métodos de Scope (enter/leave) | 25 | ___ |
| 2. Modificación declare() | 25 | ___ |
| 3. Modificación get() | 25 | ___ |
| 4. Integración con Parser | 15 | ___ |
| 5. Pruebas y Documentación | 20 | ___ |
| 6. Experimentación Propia | 20 | ___ |
| 7. Reflexión Crítica | 15 | ___ |
| **TOTAL** | **145** | **___** |

---

## Escalas de Evaluación

**Puntaje de Aprobación:** 82/145 puntos (56%) = Mínimo aceptable

**Puntaje Bueno:** 110/145 puntos (76%) = Demuestra dominio de conceptos

**Puntaje Excelente:** 130+/145 puntos (90%+) = Dominio completo + experimentación avanzada

---

## Conclusión Exitosa del Laboratorio

Tu laboratorio se considera **EXITOSO** cuando demuestras:

✓ **Funcionamiento técnico correcto:**
  - El compilador procesa correctamente programas con bloques anidados
  - Implementaste enter_scope/leave_scope que funcionan
  - declare() permite shadowing y detecta redeclaraciones en el mismo scope
  - get() resuelve nombres desde el scope actual hacia el global

✓ **Pruebas rigurosas documentadas:**
  - Ejecutaste al menos 4 ejemplos propuestos
  - Documentaste predicción vs resultado real de cada uno
  - Explicaste por qué cada resultado es correcto
  - Detectaste y analizaste cualquier error o caso edge

✓ **Experimentación independiente:**
  - Diseñaste 2-3 ejemplos propios explorando shadowing
  - Cada ejemplo demuestra un aspecto diferente
  - Ejecutaste y analizaste resultados

✓ **Comprensión conceptual profunda:**
  - Puedes explicar cómo la pila de scopes soluciona visibilidad
  - Entiendes por qué la búsqueda es "hacia afuera"
  - Analizaste casos útiles y confusos de shadowing
  - Conectaste con compiladores reales y problemas semánticos

✓ **Código limpio y modificaciones mínimas:**
  - Tu implementación en symbols.py es clara y legible
  - El parser solo fue modificado en parse_block()
  - No hay cambios innecesarios
  - Los comandos de compilación siguen siendo los mismos

**Cuando alcances estos criterios, habrás completado exitosamente el laboratorio.**




---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)