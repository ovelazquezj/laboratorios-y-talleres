# Laboratorio — Semana 2: Programación orientada a eventos (POE) + Depuración en VS Code

## 1) Encabezado

**Materia:** Programación II (Ing. TICs)
**Semana–Tema:** Semana 2 — Programación orientada a eventos + Entorno integrado de desarrollo (IDE)
**IDE obligatorio:** Visual Studio Code

**Alumno:** <Nombre completo>
**Matrícula/Número de alumno:** <ID>
**Grupo:** <Grupo>
**Fecha:** <YYYY-MM-DD>

### Evidencias mínimas del laboratorio (obligatorias)

* Capturas o logs de ejecución (comandos y salida).
* Tabla de eventos completa (evento → acción → evidencia).
* Evidencia de depuración: **antes** (falla) y **después** (corrección), con explicación breve y reproducible.

---

## 2) Objetivo técnico y criterios de aceptación

### Objetivo técnico

Construir una mini-interfaz basada en eventos y demostrar el flujo:

**evento → manejador → cambio de estado → actualización de UI**

Además, usar el IDE (VS Code) para **depurar** un problema inducido y evidenciar la corrección.

### Criterios de aceptación (medibles)

Debes cumplir TODO:

1. **UI con al menos 3 controles** (por ejemplo: input, botón, etiqueta/área de salida).
2. **Al menos 3 eventos implementados**, por ejemplo:

   * click de botón,
   * cambio en un input,
   * submit/enter o equivalente.
3. **Cada evento**:

   * actualiza una variable de estado (contador, texto, bandera),
   * refleja el cambio en UI,
   * deja evidencia por log/console o mensaje visible.
4. **Depuración obligatoria**:

   * provocar un error (entrada inválida o evento mal enlazado),
   * mostrar cómo lo detectaste,
   * corregirlo y evidenciar la corrección.
5. Evidencia obligatoria:

   * capturas/logs de ejecución,
   * tabla de eventos,
   * procedimiento reproducible para correr y probar.

---

## 3) Plataforma (rutas)

> En este curso, las rutas vigentes para laboratorio son:

* **Ruta A:** Node.js + React (TypeScript opcional)
* **Ruta B:** Python + Tkinter

Elige una ruta y realiza el laboratorio completo solo con esa.

---

## 4) Prerrequisitos y fuentes (con links)

### Fuentes oficiales

* React — Responding to Events: [https://react.dev/learn/responding-to-events](https://react.dev/learn/responding-to-events)
* React — Managing State: [https://react.dev/learn/managing-state](https://react.dev/learn/managing-state)
* Vite — Getting Started (create-vite): [https://vite.dev/guide/](https://vite.dev/guide/)
* VS Code — Browser debugging (Chrome/Edge): [https://code.visualstudio.com/docs/nodejs/browser-debugging](https://code.visualstudio.com/docs/nodejs/browser-debugging)
* Python — tkinter (oficial): [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
* Python — venv (oficial): [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
* VS Code — Python debugging: [https://code.visualstudio.com/docs/python/debugging](https://code.visualstudio.com/docs/python/debugging)

### Foros expertos (solo como apoyo; valida con evidencia)

* Stack Overflow (React submit / preventDefault): [https://stackoverflow.com/questions/39809943/react-preventing-form-submission](https://stackoverflow.com/questions/39809943/react-preventing-form-submission)

---

## 5) Glosario mínimo

* **Evento:** suceso disparado por interacción (click, change, submit, enter).
* **Manejador (handler):** función que corre cuando ocurre el evento.
* **Estado (state):** dato que cambia por eventos (contador, texto, bandera).
* **UI reactiva:** la interfaz se actualiza cuando cambia el estado.
* **Breakpoint (punto de interrupción):** pausa controlada para inspeccionar variables y flujo.

---

## 6) Tabla de eventos (obligatoria)

> Llénala para tu implementación real. Debe cubrir **mínimo 3 eventos**.

| # | Control | Evento | Manejador | Estado que cambia | Cambio visible en UI | Evidencia (log/captura) |
| - | ------- | ------ | --------- | ----------------- | -------------------- | ----------------------- |
| 1 |         |        |           |                   |                      |                         |
| 2 |         |        |           |                   |                      |                         |
| 3 |         |        |           |                   |                      |                         |

---

## 7) Desarrollo guiado — Ruta A (React)

### 7.1 Instalación/verificación de Node.js y npm

**Acción**

1. Instala Node.js LTS: [https://nodejs.org/en/download](https://nodejs.org/en/download)
2. En VS Code abre Terminal y valida:

```bash
node -v
npm -v
```

**Qué está pasando y por qué**

* Node.js ejecuta el tooling (Vite) y npm administra dependencias del proyecto.

**Evidencia**

* Captura o salida pegada con versiones.

---

### 7.2 Crear proyecto React (Vite)

**Acción**

```bash
npm create vite@latest semana2-ui -- --template react-ts
cd semana2-ui
npm install
npm run dev
```

**Qué está pasando y por qué**

* `create-vite` genera un proyecto base con React listo para correr.

**Resultado esperado**

* La terminal muestra una URL local (ej. `http://localhost:5173`).

**Evidencia**

* Captura del navegador con la app corriendo + salida del comando.

---

### 7.3 Construir la UI con 3 controles y 3 eventos

**Requisitos mínimos de UI (control obligatorio)**

* **Input**: texto (captura mínima)
* **Botón**: “Registrar evento”
* **Área de salida**: “último evento” + “contador de eventos”

**Eventos obligatorios (mínimo 3)**

1. `onChange` del input
2. `onClick` del botón
3. `onSubmit` del formulario (Enter)

#### Paso A1 — Estado y estructura base (sin eventos)

**Acción**
Edita `src/App.tsx` y reemplaza por este bloque (más legible y comentado):

```tsx
import { useState } from "react";

type LastEvent = {
  name: string;
  value: string;
  ts: string;
};

function formatLastEvent(e: LastEvent | null): string {
  if (!e) return "(sin eventos)";
  return `${e.name} | ${e.value} | ${e.ts}`;
}

export default function App() {
  // Estado (state) que cambia por eventos
  const [inputValue, setInputValue] = useState("");
  const [eventCount, setEventCount] = useState(0);
  const [lastEvent, setLastEvent] = useState<LastEvent | null>(null);

  return (
    <div style={{ padding: 24, maxWidth: 720 }}>
      <h1>Semana 2 — POE + Depuración</h1>

      <form>
        <label>
          Texto (input):
          <input
            style={{
              display: "block",
              width: "100%",
              marginTop: 8,
              padding: 8,
            }}
            value={inputValue}
            placeholder="Escribe algo..."
          />
        </label>

        <button style={{ marginTop: 12 }} type="button">
          Registrar evento
        </button>
      </form>

      <hr style={{ margin: "16px 0" }} />

      <h2>Centro de Control (base)</h2>
      <p>
        <b>Contador de eventos:</b> {eventCount}
      </p>
      <p>
        <b>Último evento:</b> {formatLastEvent(lastEvent)}
      </p>
    </div>
  );
}
```

**Qué está pasando y por qué**

* Declaras el estado que será modificado por eventos: `inputValue`, `eventCount`, `lastEvent`.
* Aún no conectas eventos: el objetivo es construir por incrementos.

**Evidencia**

* Captura de la UI corriendo con “(sin eventos)”.

---

#### Paso A2 — Evento 1: onChange (input)

**Acción**
En el `<input>`, agrega `onChange` de forma legible:

```tsx
onChange={(e) => {
  const v = e.target.value;

  // 1) Actualiza el estado del input
  setInputValue(v);

  // 2) Registra el último evento (evidencia visible)
  setLastEvent({
    name: "input_change",
    value: v,
    ts: new Date().toISOString(),
  });

  // 3) Evidencia adicional (consola)
  console.log("EVENT input_change", v);
}}
```

**Qué está pasando y por qué**

* `onChange` dispara el handler cada vez que cambia el input.
* Cambias estado y React re-renderiza la UI.

**Resultado esperado**

* Al escribir, “Último evento” cambia y en la consola se ven logs.

**Evidencia**

* Captura de consola (DevTools) o log pegado + captura de “Último evento”.

---

#### Paso A3 — Evento 2: onClick (botón)

**Acción**
Convierte el botón en evento que incrementa contador y registra el último evento:

```tsx
<button
  style={{ marginTop: 12 }}
  type="button"
  onClick={() => {
    // 1) Incrementa el contador
    setEventCount((c) => c + 1);

    // 2) Registra el último evento (evidencia visible)
    setLastEvent({
      name: "button_click",
      value: inputValue,
      ts: new Date().toISOString(),
    });

    // 3) Evidencia adicional
    console.log("EVENT button_click", inputValue);
  }}
>
  Registrar evento
</button>
```

**Qué está pasando y por qué**

* Click actualiza estado (`eventCount`, `lastEvent`).
* La UI se actualiza porque el estado cambió.

**Evidencia**

* Captura antes/después del contador y captura/log del console.

---

#### Paso A4 — Evento 3: onSubmit (Enter)

**Acción**
Agrega `onSubmit` al `<form>` y cambia el botón a `type="submit"`.

1. En `<form>`:

```tsx
<form
  onSubmit={(e) => {
    e.preventDefault();

    setEventCount((c) => c + 1);
    setLastEvent({
      name: "form_submit_enter",
      value: inputValue,
      ts: new Date().toISOString(),
    });

    console.log("EVENT form_submit_enter", inputValue);
  }}
>
```

2. En el botón:

```tsx
<button style={{ marginTop: 12 }} type="submit">
  Registrar evento
</button>
```

**Qué está pasando y por qué**

* `onSubmit` se dispara al presionar Enter en el input o al enviar el form.
* `e.preventDefault()` evita recarga de página.

**Evidencia**

* Captura o video corto presionando Enter y viendo el contador subir.

---

### 7.4 Depuración obligatoria (React) — error inducido y corrección

**Objetivo**
Provocar un error de enlace de evento y demostrar depuración reproducible en VS Code.

#### Paso D1 — Inducir el error

**Acción (solo para la prueba de depuración)**
Cambia el `onSubmit` del form a esto (nota el paréntesis):

```tsx
onSubmit={((e) => {
  e.preventDefault();
  setEventCount((c) => c + 1);
  setLastEvent({ name: "form_submit_enter", value: inputValue, ts: new Date().toISOString() });
  console.log("EVENT form_submit_enter", inputValue);
})()}
```

**Qué está pasando y por qué**

* Estás **ejecutando** la función en el render, no pasándola como handler.
* Esto rompe el flujo normal de eventos.

**Evidencia**

* Captura del error en consola o evidencia de comportamiento incorrecto.

#### Paso D2 — Depurar con VS Code (breakpoints)

**Acción**

1. Abre la vista **Run and Debug**.
2. Usa depuración de navegador según la guía oficial: [https://code.visualstudio.com/docs/nodejs/browser-debugging](https://code.visualstudio.com/docs/nodejs/browser-debugging)
3. Coloca un breakpoint dentro del handler (línea del `setEventCount`).
4. Reproduce el problema y documenta qué variable/flujo observaste.

**Evidencia**

* Captura del breakpoint alcanzado (o explicación si no se alcanza, y por qué).

#### Paso D3 — Corregir

**Acción**
Regrésalo a la forma correcta:

```tsx
onSubmit={(e) => {
  e.preventDefault();
  setEventCount((c) => c + 1);
  setLastEvent({ name: "form_submit_enter", value: inputValue, ts: new Date().toISOString() });
  console.log("EVENT form_submit_enter", inputValue);
}}
```

**Evidencia**

* Captura “después”: Enter vuelve a funcionar y el contador incrementa.

---

## 8) Desarrollo guiado — Ruta B (Python + Tkinter)

### 8.1 Instalación/verificación de Python, Tkinter y venv

#### Paso B0.1 — Verificar Python

**Acción**

```bash
python --version
```

**Evidencia**

* Captura o salida pegada.

#### Paso B0.2 — Verificar Tkinter

**Acción**

```bash
python -m tkinter
```

**Qué está pasando y por qué**

* Esto abre una ventana demo; confirma que Tkinter está instalado y funcional (oficial Python docs).

**Evidencia**

* Captura de la ventana demo o evidencia de que abrió.

#### Paso B0.3 — Crear y activar venv (recomendado)

**Acción**

```bash
python -m venv .venv
```

Activa:

* Windows (PowerShell):

```bash
.\.venv\Scripts\Activate.ps1
```

* macOS/Linux:

```bash
source .venv/bin/activate
```

**Qué está pasando y por qué**

* venv crea un Python aislado por proyecto.
* Evita choques de versiones y hace el proyecto más reproducible cuando instales dependencias más adelante.

**Evidencia**

* Captura del prompt con `.venv` o salida de:

```bash
python -c "import sys; print(sys.executable)"
```

---

### 8.2 Construir la UI con 3 controles y 3 eventos

**Controles obligatorios**

* `Entry` (input)
* `Button` (click)
* `Label` o `Text` (salida visible)

**Eventos obligatorios (mínimo 3)**

1. Click de botón (`command=...`)
2. Cambio en input (bind `"<KeyRelease>"`)
3. Enter/Submit (bind `"<Return>"`)

#### Paso B1 — Estructura base (ventana + layout)

**Acción**
Crea `main.py`:

```python
import tkinter as tk

root = tk.Tk()
root.title("Semana 2 — POE + Depuración (Tkinter)")
root.geometry("520x260")

root.mainloop()
```

**Qué está pasando y por qué**

* `Tk()` crea la ventana.
* `mainloop()` mantiene viva la UI y despacha eventos.

**Evidencia**

* Captura de la ventana abierta.

---

#### Paso B2 — Estado y controles (sin eventos)

**Acción**
Reemplaza `main.py` por este bloque (más legible y comentado):

```python
import tkinter as tk

root = tk.Tk()
root.title("Semana 2 — POE + Depuración (Tkinter)")
root.geometry("520x260")

# Estado
input_value = tk.StringVar(value="")
last_event = tk.StringVar(value="(sin eventos)")

# En Tkinter también podemos tener estado numérico.
# Para esta semana lo iniciamos como entero simple.
event_count = 0

# Controles (widgets)
header = tk.Label(
    root,
    text="Semana 2 — POE + Depuración",
    font=("Arial", 14, "bold"),
)
header.pack(pady=(10, 6))

entry = tk.Entry(root, textvariable=input_value, width=50)
entry.pack(pady=6)

btn = tk.Button(root, text="Registrar evento")
btn.pack(pady=6)

out = tk.Label(root, textvariable=last_event)
out.pack(pady=6)

counter = tk.Label(root, text=f"Contador de eventos: {event_count}")
counter.pack(pady=6)

root.mainloop()
```

**Qué está pasando y por qué**

* `StringVar` facilita actualizar texto visible (`last_event`) sin manipular strings en varios lugares.
* Aún no hay eventos conectados: solo estructura.

**Evidencia**

* Captura de UI mostrando “(sin eventos)”.

---

#### Paso B3 — Evento 1: cambio en input (KeyRelease)

**Acción**
Agrega este handler y el `bind` (con comentarios):

```python
def on_input_change(event):
    """Evento: el usuario soltó una tecla dentro del Entry."""
    v = input_value.get()

    # Evidencia visible
    last_event.set(f"input_change | value='{v}'")

    # Evidencia adicional (terminal)
    print("EVENT input_change", v)

# Conectamos el evento del widget a nuestro handler
entry.bind("<KeyRelease>", on_input_change)
```

**Qué está pasando y por qué**

* `bind` asocia un evento del widget con una función.
* Cada tecla soltada actualiza estado visible y deja log.

**Evidencia**

* Captura del label cambiando y log en terminal.

---

#### Paso B4 — Evento 2: click de botón (command)

**Acción**
Define handler y asigna `command` al botón (forma legible):

```python
def on_button_click():
    """Evento: click del botón."""
    global event_count

    event_count += 1
    v = input_value.get()

    # Evidencia visible
    last_event.set(f"button_click | value='{v}'")
    counter.config(text=f"Contador de eventos: {event_count}")

    # Evidencia adicional
    print("EVENT button_click", v)

# Conectamos el evento click del botón
btn.config(command=on_button_click)
```

**Qué está pasando y por qué**

* Click cambia estado (`event_count`, `last_event`) y actualiza UI.

**Evidencia**

* Captura antes/después del contador + log.

---

#### Paso B5 — Evento 3: Enter (Return) como submit

**Acción**
Agrega handler y `bind` a Enter:

```python
def on_submit_enter(event):
    """Evento: Enter dentro del Entry (simula submit)."""
    on_button_click()  # Reutiliza la lógica del click

    v = input_value.get()
    last_event.set(f"submit_enter | value='{v}'")
    print("EVENT submit_enter", v)

# Conectamos Enter del Entry
entry.bind("<Return>", on_submit_enter)
```

**Qué está pasando y por qué**

* Enter ejecuta un flujo equivalente a submit.

**Evidencia**

* Captura o video corto mostrando Enter incrementando contador.

---

### 8.3 Depuración obligatoria (Tkinter) — error inducido y corrección

#### Paso D1 — Inducir el error (evento mal enlazado)

**Acción (solo para la prueba de depuración)**
Cambia el `command` del botón a esto (nota los paréntesis):

```python
btn.config(command=on_button_click())
```

**Qué está pasando y por qué**

* Estás **ejecutando** la función al configurar el botón.
* El botón ya no tiene un handler válido para el click.

**Evidencia**

* Captura del comportamiento incorrecto (contador cambia al inicio o click no hace nada) + log.

#### Paso D2 — Depurar en VS Code

**Acción**

1. Instala/activa extensiones de Python y depuración según la guía oficial: [https://code.visualstudio.com/docs/python/debugging](https://code.visualstudio.com/docs/python/debugging)
2. Coloca breakpoint dentro de `on_button_click`.
3. Ejecuta en modo Debug (F5) y observa:

   * ¿cuándo se ejecuta `on_button_click`?
   * ¿qué valor tiene `event_count`?

**Evidencia**

* Captura del breakpoint y variables inspeccionadas.

#### Paso D3 — Corregir

**Acción**
Cambia a la forma correcta:

```python
btn.config(command=on_button_click)
```

**Evidencia**

* Captura “después”: click vuelve a incrementar y actualizar UI.

---

## 9) Verificación y pruebas (mínimas)

### Casos mínimos

1. **Input change:** escribe 5 caracteres → el “último evento” cambia y hay log.
2. **Button click:** click 2 veces → contador sube y “último evento” cambia.
3. **Enter/submit:** presiona Enter → contador sube y “último evento” cambia.

### Validación

* Debes poder repetir los casos 1–3 siguiendo tu procedimiento reproducible.

---

## 10) Etapa 5: Implementación en el proyecto (base UI)

> Esta parte es obligatoria dentro del laboratorio de la Semana 2.

Tu UI debe incluir una “pantalla base” del **Centro de Control** con:

* Encabezado
* Sección de “último evento recibido” (por ahora simulado con `lastEvent`/`last_event`)
* Contador de eventos (por ahora local)

Esto ya está integrado en los ejemplos de React y Tkinter (sección “Centro de Control (base)” / labels equivalentes).

---

## 11) Checklist final (solo laboratorio)

* UI con ≥ 3 controles.
* ≥ 3 eventos: click + change + enter/submit (o equivalente).
* Cada evento cambia estado y actualiza UI.
* Evidencia por log/console o mensaje visible para cada evento.
* Tabla de eventos completa (mínimo 3 filas).
* Depuración: error inducido + detección + corrección + evidencia antes/después.
* Procedimiento reproducible para correr y probar.

---

## Referencias (APA, con links)

Ajusta “Retrieved” a tu fecha real.

* React. (n.d.). *Responding to Events*. Retrieved 2026-01-25, from [https://react.dev/learn/responding-to-events](https://react.dev/learn/responding-to-events)
* React. (n.d.). *Managing State*. Retrieved 2026-01-25, from [https://react.dev/learn/managing-state](https://react.dev/learn/managing-state)
* Vite. (n.d.). *Getting Started*. Retrieved 2026-01-25, from [https://vite.dev/guide/](https://vite.dev/guide/)
* Visual Studio Code. (n.d.). *Browser debugging in VS Code*. Retrieved 2026-01-25, from [https://code.visualstudio.com/docs/nodejs/browser-debugging](https://code.visualstudio.com/docs/nodejs/browser-debugging)
* Python. (n.d.). *tkinter — Python interface to Tcl/Tk*. Retrieved 2026-01-25, from [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
* Python. (n.d.). *venv — Creation of virtual environments*. Retrieved 2026-01-25, from [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
* Visual Studio Code. (n.d.). *Python debugging in VS Code*. Retrieved 2026-01-25, from [https://code.visualstudio.com/docs/python/debugging](https://code.visualstudio.com/docs/python/debugging)
* Stack Overflow. (2016). *React - Preventing Form Submission*. Retrieved 2026-01-25, from [https://stackoverflow.com/questions/39809943/react-preventing-form-submission](https://stackoverflow.com/questions/39809943/react-preventing-form-submission)


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)