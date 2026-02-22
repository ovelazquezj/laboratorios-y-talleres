# Laboratorio Semana 4 — Tipos de proyecto + estructuras base (aplicado en POE con try/assert y logs)

## 0) Qué estás construyendo (sin inventos)

Vas a construir una mini‑aplicación orientada a eventos (POE) con UI (formulario) que capture un **Evento** y lo procese con un **motor**.

El **tema de la semana** sigue siendo:

* **Tipos de proyectos** (cómo se organiza/arranca una app según la ruta)
* **Estructuras base del lenguaje** aplicadas (modelo, funciones, colección, normalización, manejo de estados)

**Restricción técnica del laboratorio (la herramienta, no el tema):**

* Las validaciones y garantías de estado NO se implementan con cadenas de `if/else`.
* En su lugar se usa el patrón en POE:

  * **assert** para validar condiciones previas/posteriores (incondicionales)
  * **try…except / try…catch** para capturar AssertionError u otras excepciones y evitar que la app se detenga
  * **logs** para evidencia y depuración (prohibido `print`)

---

## 1) Objetivo (medible)

Al final del laboratorio debes poder demostrar con evidencia que:

1. El proyecto tiene estructura mínima correcta para tu **tipo de proyecto** (según ruta)
2. Existe un **motor** separado de la UI
3. Al presionar “Agregar”, la app:

   * procesa el evento dentro de `try`
   * usa `assert` para verificar estados críticos
   * registra en logs: intento, aceptación o rechazo
   * NO se cae ante entradas inválidas
4. La colección local `eventos` contiene solo eventos válidos

---

## 2) Producto final esperado (lo que debe verse)

### En pantalla

* Formulario con 5 campos: `timestamp, equipo, etapa, evento, valor`
* Botón: **Agregar**
* Área de mensajes (éxito/error)
* Lista/tabla de eventos aceptados
* Botón: **Limpiar** (resetea colección y UI)

### En evidencia

* Logs con niveles (INFO/DEBUG/WARN/ERROR)
* Matriz de casos (6 intentos): 3 aceptados, 3 rechazados

---

## 3) Tipo de proyecto (elige UNA ruta)

### Opción A — Python + Tkinter

Tipo de proyecto: **Aplicación de escritorio con UI**.

* Tiene un punto de entrada que levanta la ventana.
* El programa vive en un bucle de eventos (event loop).

### Opción B — Node.js + React

Tipo de proyecto: **Aplicación UI basada en componentes**.

* Tiene un punto de arranque (arranque del front) y un ciclo de render/eventos.
* El estado (colección `eventos`) vive en memoria del front (estado local).

**Pregunta 1 (para tu reporte):**

* ¿Cuál es el “punto de entrada” de tu tipo de proyecto y qué responsabilidad tiene?

---

## 4) Contrato de datos (estructura base)

Define el contrato **Evento** con 5 campos:

* `timestamp` (texto)
* `equipo` (texto)
* `etapa` (número)
* `evento` (texto)
* `valor` (número)

**Pregunta 2:**

### Ejemplo de código (A: Python + Tkinter)

```python
# modelo.py
# Un contrato explícito evita “campos fantasma” y ayuda a validar entradas.
from dataclasses import dataclass

@dataclass
class Evento:
    timestamp: str
    equipo: str
    etapa: int
    evento: str
    valor: float
```

### Ejemplo de código (B: Node.js + React)

```ts
// modelo.ts
// Un type/interface define el contrato que la UI y el motor deben respetar.
export type Evento = {
  timestamp: string;
  equipo: string;
  etapa: number;
  evento: string;
  valor: number;
};
```

* ¿Qué falla se vuelve más probable si NO defines un contrato claro y solo manejas “campos sueltos”?

---

## 5) Colección local `eventos` (estructura base)

Mantén una colección local `eventos`.

* Contiene SOLO eventos aceptados.
* Se muestra en la UI.

**Postcondición clave (se verificará con assert):**

* Si un evento fue aceptado, entonces el tamaño de `eventos` aumenta en 1.

**Pregunta 3:**

* ¿Por qué “solo aceptar válidos” reduce el costo de mantenimiento (menciona 2 razones)?

---

## 6) Logger (obligatorio: evidencia verificable)

Configura un logger (prohibido `print`).

### Formato mínimo de línea

* `fecha-hora | nivel | módulo | acción | resultado | detalle`

### Eventos mínimos a registrar

* INFO: “Intento de agregar” (con un identificador breve del intento)
* DEBUG: “Texto normalizado” (antes/después)
* INFO: “Evento aceptado y agregado” (tamaño antes/después)
* WARN: “Evento rechazado” (razón)
* ERROR: “Excepción inesperada capturada” (tipo)

**Pregunta 4:**

### Ejemplo de código (A: Python)

```python
# logging_setup.py
# Logger con nivel y formato consistente: evidencia reproducible.
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()  # o FileHandler("app.log")
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
handler.setFormatter(formatter)

# Evita handlers duplicados si se reimporta el módulo.
if not logger.handlers:
    logger.addHandler(handler)
```

### Ejemplo de código (B: Node.js/React)

```ts
// logger.ts
// Wrapper didáctico de logging con niveles (puedes reemplazarlo por un logger real después).
export type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR";

export function log(level: LogLevel, modulo: string, accion: string, resultado: string, detalle: string) {
  const ts = new Date().toISOString();
  console.log(`${ts} | ${level} | ${modulo} | ${accion} | ${resultado} | ${detalle}`);
}
```

* ¿Qué parte de los logs te permite comprobar que el sistema NO se detuvo pese a un error?

---

## 7) Motor (separado de la UI)

Tu motor es un conjunto de funciones/procedimientos SIN UI.

### 7.1 Normalización (mínimo)

Normaliza el texto `evento`:

* Quitar espacios al inicio y final
* Convertir múltiples espacios internos en uno
* Opcional: convertir a minúsculas

**Pregunta 5:**

* ¿Por qué normalizar texto puede reducir bugs aunque “no cambie el significado”?

### 7.2 Validación con assert (sin if/else en cascada)

Aquí está la idea exacta que debes aplicar (sin convertirlo en “tema”):

* Usa **assert** como validación de invariantes:

  * Precondiciones: antes de aceptar
  * Postcondiciones: después de agregar

**Ejemplos de invariantes (debes implementar al menos 3):**

* Pre: `timestamp` no está vacío
* Pre: `equipo` no está vacío
* Pre: `etapa` está en 1..4
* Pre: `evento` (ya normalizado) no está vacío
* Pre: `valor` es numérico
* Post: si acepté, `len(eventos)` aumentó exactamente 1

Nota didáctica:

* `assert` no es “si falla entonces…”. Es: “esto DEBE ser verdad”.

### Ejemplo de código (A: Python) — motor

```python
# motor.py
# Motor sin UI: fácil de probar y reutilizar.
from typing import List
from modelo import Evento
from logging_setup import logger

def normalizar_texto(s: str) -> str:
    # 1) strip: elimina espacios extremos
    # 2) split/join: colapsa múltiples espacios internos a uno
    s2 = " ".join(s.strip().split())
    # 3) opcional: estandarizar a minúsculas
    return s2.lower()

def procesar_evento(candidato: Evento) -> Evento:
    # Precondiciones: si fallan, AssertionError
    assert isinstance(candidato.timestamp, str) and candidato.timestamp.strip(), "timestamp es obligatorio"
    assert isinstance(candidato.equipo, str) and candidato.equipo.strip(), "equipo es obligatorio"
    assert isinstance(candidato.etapa, int), "etapa debe ser int"
    assert 1 <= candidato.etapa <= 4, "etapa fuera de rango (1–4)"

    evento_norm = normalizar_texto(candidato.evento)
    logger.debug(
        f"motor | normalizar | ok | antes='{candidato.evento}' despues='{evento_norm}'"
    )

    assert evento_norm, "evento es obligatorio (tras normalización)"
    assert isinstance(candidato.valor, (int, float)), "valor debe ser numérico"

    # Construcción del objeto final (ya normalizado)
    return Evento(
        timestamp=candidato.timestamp.strip(),
        equipo=candidato.equipo.strip(),
        etapa=candidato.etapa,
        evento=evento_norm,
        valor=float(candidato.valor),
    )

def agregar_a_coleccion(eventos: List[Evento], evento_ok: Evento) -> None:
    antes = len(eventos)
    eventos.append(evento_ok)
    # Postcondición: si se aceptó, la colección crece exactamente 1
    assert len(eventos) == antes + 1, "postcondición falló: la colección no creció"
```

### Ejemplo de código (B: Node.js/React) — motor

```ts
// motor.ts
import { Evento } from "./modelo";
import { log } from "./logger";

export function normalizarTexto(s: string): string {
  // trim + colapsar espacios + minúsculas (opcional)
  const s2 = s.trim().split(/\s+/).join(" ").toLowerCase();
  return s2;
}

export function procesarEvento(candidato: Evento): Evento {
  // Precondiciones con assert: lanzan Error si no se cumplen.
  assert(!!candidato.timestamp?.trim(), "timestamp es obligatorio");
  assert(!!candidato.equipo?.trim(), "equipo es obligatorio");
  assert(Number.isInteger(candidato.etapa), "etapa debe ser entero");
  assert(candidato.etapa >= 1 && candidato.etapa <= 4, "etapa fuera de rango (1–4)");

  const eventoNorm = normalizarTexto(candidato.evento);
  log("DEBUG", "motor", "normalizar", "ok", `antes='${candidato.evento}' despues='${eventoNorm}'`);

  assert(!!eventoNorm, "evento es obligatorio (tras normalización)");
  assert(Number.isFinite(candidato.valor), "valor debe ser numérico");

  return {
    timestamp: candidato.timestamp.trim(),
    equipo: candidato.equipo.trim(),
    etapa: candidato.etapa,
    evento: eventoNorm,
    valor: Number(candidato.valor),
  };
}

export function agregarAColeccion(eventos: Evento[], eventoOk: Evento): void {
  const antes = eventos.length;
  eventos.push(eventoOk);
  // Postcondición
  assert(eventos.length === antes + 1, "postcondición falló: la colección no creció");
}

function assert(cond: boolean, msg: string): asserts cond {
  if (!cond) throw new Error(msg);
}
```

---

## 8) El evento crítico: botón “Agregar” (guía paso a paso)

Esta es la parte POE: cuando ocurre el evento (click/submit), tu app debe manejarlo de forma controlada.

### Paso 0 — Preparación

* Ten una colección `eventos` inicial vacía
* Ten un área de mensajes en UI
* Ten el logger listo

### Paso 1 — Captura

* Lee los 5 campos del formulario y construye un “Evento candidato”

### Paso 2 — Try (envolver el manejo del evento)

* Entra a un bloque `try` que contiene TODO el procesamiento

### Paso 3 — Assert de precondiciones (antes de aceptar)

* Ejecuta asserts para garantizar invariantes
* Si un assert falla, se lanza AssertionError

### Paso 4 — Normaliza

* Normaliza el texto `evento`
* Registra en DEBUG el antes/después

### Paso 5 — Construye Evento normalizado

* Construye el Evento final (ya normalizado) que SÍ puede guardarse

### Paso 6 — Agrega a colección

* Guarda el evento en `eventos`

### Paso 7 — Assert de postcondición

* Verifica con assert que la colección cambió como se esperaba

### Paso 8 — UI y logs en éxito

* Muestra confirmación en UI
* Log INFO: aceptado + tamaño antes/después

### Paso 9 — Except (captura de errores)

* `except AssertionError`:

  * No se agrega el evento
  * UI muestra mensaje entendible
  * Log WARN con razón
* `except/ catch (Exception general)`:

  * UI muestra “Error inesperado controlado” (sin crashear)
  * Log ERROR con tipo

### Paso 10 — Estado consistente

* La aplicación sigue viva
* La lista/tabla solo muestra aceptados

**Pregunta 6:**

### Ejemplo de código (A: Python + Tkinter) — handler del botón Agregar

```python
# ui.py (fragmento)
# El handler NO contiene reglas complejas: solo orquesta y muestra.
from modelo import Evento
from motor import procesar_evento, agregar_a_coleccion
from logging_setup import logger

eventos = []  # colección local

def on_agregar_click(entry_timestamp, entry_equipo, entry_etapa, entry_evento, entry_valor, label_mensaje):
    logger.info("ui | agregar | intento | click en Agregar")

    # Captura: convierte inputs UI a un Evento candidato
    candidato = Evento(
        timestamp=entry_timestamp.get(),
        equipo=entry_equipo.get(),
        etapa=int(entry_etapa.get()),
        evento=entry_evento.get(),
        valor=float(entry_valor.get()),
    )

    antes = len(eventos)

    try:
        evento_ok = procesar_evento(candidato)
        agregar_a_coleccion(eventos, evento_ok)

        label_mensaje.config(text="Evento agregado correctamente")
        logger.info(f"ui | agregar | ok | tam {antes}->{len(eventos)}")

        # Aquí actualizas tu tabla/lista en pantalla
        # refrescar_tabla_eventos(eventos)

    except AssertionError as e:
        # Error esperado: violación de invariante (dato inválido)
        label_mensaje.config(text=str(e))
        logger.warning(f"ui | agregar | rechazado | {e}")

    except Exception as e:
        # Error inesperado: NO crashear la app
        label_mensaje.config(text="Error inesperado controlado")
        logger.error(f"ui | agregar | exception | {type(e).__name__}: {e}")
```

### Ejemplo de código (B: React) — handler del submit

```tsx
// App.tsx (fragmento)
import React, { useState } from "react";
import { Evento } from "./modelo";
import { procesarEvento, agregarAColeccion } from "./motor";
import { log } from "./logger";

export function App() {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [msg, setMsg] = useState<string>("");

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    log("INFO", "ui", "agregar", "intento", "submit del formulario");

    const antes = eventos.length;

    const candidato: Evento = {
      timestamp: (document.getElementById("timestamp") as HTMLInputElement).value,
      equipo: (document.getElementById("equipo") as HTMLInputElement).value,
      etapa: Number((document.getElementById("etapa") as HTMLInputElement).value),
      evento: (document.getElementById("evento") as HTMLInputElement).value,
      valor: Number((document.getElementById("valor") as HTMLInputElement).value),
    };

    try {
      const eventoOk = procesarEvento(candidato);

      // En React, evitamos mutar el arreglo original
      const copia = [...eventos];
      agregarAColeccion(copia, eventoOk);

      setEventos(copia);
      setMsg("Evento agregado correctamente");
      log("INFO", "ui", "agregar", "ok", `tam ${antes}->${copia.length}`);

    } catch (err: any) {
      const mensaje = err?.message ?? "Error inesperado controlado";
      setMsg(mensaje);
      log("WARN", "ui", "agregar", "rechazado", mensaje);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <div>{msg}</div>
      {/* inputs + tabla */}
    </form>
  );
}
```

* ¿Cuál es la diferencia entre capturar AssertionError vs capturar una excepción general?

---

## 9) Botón “Limpiar” (estado)

Guía:

* Resetea `eventos` a vacío
* Limpia la tabla/lista
* Limpia el área de mensajes
* Log INFO: “colección limpiada”

**Pregunta 7:**

### Ejemplo de código (A: Python) — limpiar

```python
from logging_setup import logger

def on_limpiar_click(label_mensaje):
    global eventos
    antes = len(eventos)
    eventos = []

    label_mensaje.config(text="")
    # limpiar_tabla_eventos()

    logger.info(f"ui | limpiar | ok | tam {antes}->0")
```

### Ejemplo de código (B: React) — limpiar

```tsx
function onLimpiar() {
  const antes = eventos.length;
  setEventos([]);
  setMsg("");
  log("INFO", "ui", "limpiar", "ok", `tam ${antes}->0`);
}
```

* ¿Qué problema de POE aparece si limpias la UI pero NO limpias el estado (`eventos`)?

---

## 10) Matriz de evidencia (6 intentos obligatorios)

Debes ejecutar 6 intentos y registrar evidencia.

### Tabla obligatoria en tu reporte

| # | Entrada (resumen)         | Esperado            | ¿Se agregó? | Tamaño antes→después | Extracto de log (nivel + razón) |
| - | ------------------------- | ------------------- | ----------- | -------------------- | ------------------------------- |
| 1 | Válido #1                 | Aceptar             | Sí          |                      |                                 |
| 2 | Válido #2                 | Aceptar             | Sí          |                      |                                 |
| 3 | Válido #3 (normalización) | Aceptar + normaliza | Sí          |                      |                                 |
| 4 | Inválido #1 (faltante)    | Rechazar            | No          |                      |                                 |
| 5 | Inválido #2 (etapa)       | Rechazar            | No          |                      |                                 |
| 6 | Inválido #3 (valor)       | Rechazar            | No          |                      |                                 |

### Casos sugeridos (puedes adaptar)

* Válido #1: campos completos, etapa=1, valor numérico
* Válido #2: campos completos, etapa=4, valor numérico
* Válido #3: `evento` con espacios múltiples, se normaliza y se acepta
* Inválido #1: `timestamp` vacío
* Inválido #2: `etapa=7`
* Inválido #3: `valor` no numérico

**Regla de evidencia:**

* Cada fila debe poder validarse con:

  * lo que se ve en la UI (agregado/no agregado)
  * el cambio de tamaño de la colección
  * el extracto de log

---

## 11) Entregables (lo mínimo)

1. Evidencia de estructura del proyecto (carpetas/módulos) según tu ruta
2. Capturas de UI (antes y después de ejecutar los 6 intentos)
3. Logs (archivo o consola con formato y niveles)
4. Reporte con respuestas a Preguntas 1–7 + matriz de evidencia

---

## 12) Guía de implementación por ruta 

### Opción A — Python + Tkinter

* Define módulos: `ui`, `motor`, `modelo`, `logging`
* En `ui`, en el handler del botón “Agregar”, sigue los pasos 0–10
* En `motor`, coloca normalización y asserts (invariantes)
* En `ui`, captura AssertionError y Exception para mantener la app viva

### Opción B — Node.js + React

* Define carpetas: `ui`, `motor`, `modelo`, `logging`
* En React, el handler del submit sigue los pasos 0–10
* El estado `eventos` vive en memoria del componente (o store local)
* El motor normaliza y ejecuta asserts/invariantes
* El handler captura errores para mostrar mensaje y registrar logs sin romper el render

Fin del laboratorio.


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)