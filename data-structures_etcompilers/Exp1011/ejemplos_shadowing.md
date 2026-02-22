# Ejemplos de Código MiniGUS para Pruebas de Shadowing

Este archivo proporciona los ejemplos de código `.ms` propuestos en la guía del laboratorio.
Copia cada sección en su propio archivo dentro de `examples/`.

---

## Prueba 1: Shadowing Simple

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
- Declara `x` global = 100.
- Dentro del bloque `if`, declara un nuevo `x` local = 50.
- Al salir del bloque, el `x` local desaparece del alcance.
- Se imprime el `x` global = 100.

**Salida esperada:**
```
100
```

---

## Prueba 2: Múltiples Niveles de Anidamiento

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
    print(x);
  }
  print(x);
}
print(x);
```

**Comportamiento esperado:**
- Tres niveles diferentes de `x`:
  - Nivel 0 (global): x = 1
  - Nivel 1 (primer if): x = 2
  - Nivel 2 (segundo if anidado): x = 3
- Imprime 3 (el x del nivel 2).
- Imprime 2 (el x del nivel 1).
- Imprime 1 (el x del global).

**Salida esperada:**
```
3
2
1
```

---

## Prueba 3: Sin Shadowing (Referencias al Scope Global)

**Archivo:** `examples/no_shadow.ms`

```c
int x;
int y;
x = 10;
y = 20;
if (true) {
  int z;
  z = x + y;
  print(z);
}
```

**Comportamiento esperado:**
- `x` e `y` se declaran en el scope global.
- Dentro del bloque `if`, se declara `z` localmente.
- `z` se calcula como x + y, donde x e y se resuelven al buscar hacia afuera.
- Se imprime 30.

**Salida esperada:**
```
30
```

---

## Prueba 4: Error - Redeclaración en el Mismo Scope

**Archivo:** `examples/error_redecl.ms`

```c
int x;
if (true) {
  int x;
  int x;
}
```

**Comportamiento esperado:**
- Primera declaración de `x` en el scope global: OK.
- Primera declaración de `x` en el scope local (if): OK (shadowing).
- Segunda declaración de `x` en el scope local: ERROR - redeclaración en el mismo scope.

**Salida esperada (error):**
```
[Semantics] Redeclaración de 'x'
```

---

## Prueba 5: Shadowing Útil - Contadores en Contextos Diferentes

**Archivo:** `examples/shadow_useful.ms`

```c
int count;
count = 0;

if (true) {
  int count;
  count = 0;
  while (count < 3) {
    print(count);
    count = count + 1;
  }
}

print(count);
```

**Comportamiento esperado:**
- `count` global se mantiene en 0.
- `count` local dentro del bloque se usa para el loop (0, 1, 2).
- Al salir del bloque, se imprime el `count` global nuevamente = 0.
- Útil para reutilizar nombres de contadores sin contaminar el scope global.

**Salida esperada:**
```
0
1
2
0
```

---

## Prueba 6: Shadowing Confuso - Muchos Niveles

**Archivo:** `examples/shadow_confusing.ms`

```c
int x;
int y;
int z;
x = 1; y = 2; z = 3;

if (true) {
  int x;
  x = 10;
  if (true) {
    int y;
    y = 20;
    if (true) {
      int z;
      z = 30;
      print(x);
      print(y);
      print(z);
    }
    print(y);
  }
  print(x);
}

print(z);
```

**Comportamiento esperado:**
- Nivel 0 (global): x=1, y=2, z=3
- Nivel 1 (if 1): x=10 (shadows global x), y,z no redeclarados
- Nivel 2 (if 2): y=20 (shadows global y), x,z no redeclarados
- Nivel 3 (if 3): z=30 (shadows global z), x,y no redeclarados
- Primera serie de prints (nivel 3): 10, 20, 30 (locals más profundos)
- Segunda serie (nivel 2): 20, 10 (y local, x nivel 1)
- Tercera serie (nivel 0): 3 (z global)

**Salida esperada:**
```
10
20
30
20
10
3
```

---

## Prueba 7: Combinación de Bloques - If + While Anidados

**Archivo:** `examples/shadow_complex.ms`

```c
int i;
i = 0;

if (true) {
  int i;
  i = 0;
  while (i < 2) {
    int j;
    j = i * 10;
    print(j);
    i = i + 1;
  }
}

print(i);
```

**Comportamiento esperado:**
- `i` global se inicializa en 0.
- `i` local en el bloque if se usa para el loop.
- Dentro del while, `j` es local a cada iteración (pero reutilizado).
- Se imprime: 0, 10 (valores de j).
- Finalmente se imprime `i` global = 0.

**Salida esperada:**
```
0
10
0
```

---

## Prueba 8: Sin Redeclaración - Solo Uso

**Archivo:** `examples/no_redecl_use_only.ms`

```c
int x;
x = 5;

if (true) {
  x = x + 1;
  print(x);
}

print(x);
```

**Comportamiento esperado:**
- `x` se declara globalmente = 5.
- Dentro del if, se modifica el mismo `x` global = 6.
- Se imprime 6 dos veces (dentro y fuera del bloque).

**Salida esperada:**
```
6
6
```

---

## Notas de Implementación

1. **Copiar cada programa:** Crea archivos separados con estos nombres exactos en la carpeta `examples/`.

2. **Ejecutar las pruebas:**
   ```bash
   python3 main.py examples/shadow_simple.ms
   python3 main.py examples/shadow_nested.ms
   # ... etc
   ```

3. **Casos de error:** Las pruebas 4 deben fallar con errores semánticos. Es el comportamiento esperado.

4. **Comparar con predicciones:** Antes de ejecutar cada una, predice el resultado. Luego compara.

5. **Documentar en el reporte:** Incluye:
   - El código del ejemplo.
   - Tu predicción del comportamiento.
   - La salida real del compilador.
   - Explicación de por qué coinciden (o no).


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)