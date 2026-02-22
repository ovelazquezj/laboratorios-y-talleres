# EXP1 – Laboratorio de Parser Aritmético (MiniGUs)

## 1. Introducción

En el laboratorio anterior (EXP0), implementaste un **lexer** capaz de reconocer tokens válidos dentro de programas simples escritos en MiniGUs. Esta vez extenderás esa funcionalidad construyendo tu propio **parser recursivo** que te permitirá **interpretar la estructura sintáctica** de expresiones aritméticas.

Este parser será una implementación didáctica de un **analizador descendente recursivo** (top-down parser) inspirado en el funcionamiento de `parser.py`, el cual forma parte del compilador MiniGUs.

A diferencia del parser completo del compilador, tu parser no generará código ni manipulará símbolos, sino que validará expresiones aritméticas como:

```txt
3 + 4 * (2 - 1)
7 * (5 + 9) / 2
```

El objetivo no es generar árboles abstractos ni compilar, sino comprobar que la secuencia de tokens cumple con la **estructura gramatical correcta**.

---

**Prerrequisitos:**

* Haber completado el EXP0 con un lexer funcional.
* Comprender cómo se generan los tokens con `lexer.py`.
* Observar la estructura del archivo `parser.py` del compilador.

**Archivos necesarios:**

* `src/lexer.py`
* `src/parser.py` (referencia)
* `parser_aritmetico.py` (archivo nuevo que tú crearás)

**Recomendación:** No edites `parser.py`. Solo estúdialo y replica su estructura base en tu propio archivo.

**Uso de IA:** Puedes utilizar herramientas como **Claude** u otro modelo de lenguaje para analizar o ayudarte a estructurar tu código. Si lo haces, deberás:

* **Incluir el prompt exacto que usaste**
* **Citar la fuente en formato APA (7ª ed.)** indicando el modelo, fecha y plataforma

Ejemplo:

> Prompt usado: "Diseña una clase en Python que implemente un parser recursivo para expresiones aritméticas."
> Referencia: Anthropic. (2025). *Claude 3.0 \[Large language model]*. [https://claude.ai](https://claude.ai)

---

## 2. Objetivo del laboratorio

Diseñar e implementar un parser aritmético simple que reconozca expresiones con suma, resta, multiplicación, división y paréntesis, usando el patrón de análisis descendente observado en `parser.py`.

Al finalizar este laboratorio, deberás ser capaz de:

* Comprender la estructura modular de un parser.
* Replicar los métodos `match()`, `eat()`, `abort()` en tu propia clase.
* Implementar `expr()`, `term()` y `factor()` para procesar expresiones.
* Probar tu parser con entradas manuales o desde archivo.
* Documentar correctamente el uso de herramientas de apoyo como IA.

---

## 3. Actividades paso a paso

### Paso 1: Estudia `parser.py`

Abre el archivo `src/parser.py` y enfócate en estas funciones:

* `cur()`, `at()`, `match()`, `eat()` → manejo de tokens
* `parse_expr()`, `parse_term()`, `parse_factor()` si existen, o imagina cómo los construirías
* Observa cómo se procesan tokens paso a paso y se validan estructuras

No edites este archivo.

### Paso 2: Crea tu propio archivo `parser_aritmetico.py`

* Dentro del mismo proyecto, crea el archivo `parser_aritmetico.py`
* Define tu clase `ParserAritmetico`
* Agrega métodos auxiliares: `cur_token`, `next_token`, `match`, `abort`

### Paso 3: Implementa la gramática aritmética

Tu parser debe implementar esta gramática:

```bnf
expr   → term ( ( "+" | "-" ) term )*
term   → factor ( ( "*" | "/" ) factor )*
factor → NUMBER | "(" expr ")"
```

### Paso 4: Programa y prueba tu parser

Ejecuta tu parser desde un script de prueba, o desde `main.py` si lo adaptas.

```python
parser = ParserAritmetico(tokens)
parser.expr()
print("Expresión válida")
```

---

## 4. Pruebas y validación

### Casos válidos:

* `2 + 3`
* `4 * (1 + 6)`
* `(8 + 2) * (3 - 1)`

### Casos inválidos:

* `5 +`
* `2 * (3 + )`
* `((7 - 2)`

### Actividad:

* Crea un archivo de prueba con una expresión válida y otra con error
* Captura el resultado o mensaje del parser

### Reflexión:

* ¿Qué estructura usaste como guía?
* ¿Qué diferencias hay entre tu parser y el original?
* ¿Qué errores fueron los más difíciles de manejar?

---

## 5. Entregables y cierre

### Entregables obligatorios:

1. Archivo `parser_aritmetico.py` con la clase implementada
2. Captura de ejecución con expresión válida e inválida
3. Bitácora técnica (si se solicita en clase)
4. Prompt usado con la IA (si aplica) y referencia en formato APA

---

Fin del laboratorio EXP1 – Parser Aritmético



---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)