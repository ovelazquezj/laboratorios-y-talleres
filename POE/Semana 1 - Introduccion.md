# Laboratorio — Semana 1: Arranque de entorno + primer evento UI

## 1) Encabezado

**Materia:** Programación II (Ing. TICs)
**Semana–Tema:** Semana 1 — Inducción y forma de trabajo + Arranque de entorno + primer evento UI
**IDE obligatorio:** Visual Studio Code

**Alumno:** <Nombre completo>
**Matrícula/Número de alumno:** <ID>
**Grupo:** <Grupo>
**Fecha:** <YYYY-MM-DD>

### Evidencias mínimas del laboratorio (obligatorias)

* 1 captura (screenshot) de la interfaz corriendo.
* 1 evidencia de ejecución (salida de terminal o log) mostrando el comando usado.
* 1 evidencia del evento funcionando (antes/después del click o mini-video corto).
* Pasos reproducibles para correr el proyecto (comandos exactos).

---

## 2) Objetivo técnico y criterios de aceptación

### Objetivo técnico (Semana 1)

Dejar lista la **ruta elegida** y demostrar un programa mínimo con:

* una interfaz (ventana/página),
* un control (botón o equivalente),
* un evento (click) que cambie un estado visible (texto/contador),
  con evidencia reproducible de ejecución.

### Criterios de aceptación (medibles)

Debes cumplir TODO:

1. **Ruta elegida documentada** (A o B) y evidencia de versión:

   * Ruta A: `node -v` y `npm -v` (captura o pegado de salida en el reporte).
   * Ruta B: `python --version` y evidencia de venv activo (captura o pegado de salida).

2. **Proyecto creado y ejecutando**:

   * Debe iniciar sin errores y mostrar interfaz.

3. **Evento funcional**:

   * El click en el botón provoca un **cambio verificable** (texto o contador) en la interfaz.

4. **Evidencia mínima obligatoria**:

   * 1 captura (o screenshot) de la interfaz corriendo,
   * 1 evidencia de ejecución (log/terminal),
   * pasos reproducibles para correrlo (comandos exactos).

5. **Falla inducida (robustez mínima)**:

   * Debes provocar 1 falla controlada (definida abajo) y documentar: hipótesis → prueba mínima → evidencia del error → corrección → evidencia de que quedó funcionando.

---

## 3) Prerrequisitos y fuentes

### Rutas permitidas

* **Ruta A:** Node.js + React (TypeScript opcional)
* **Ruta B:** Python + Tkinter

### Prerrequisitos (software) — instalación guiada

#### Ruta A: instalar Node.js y npm (para correr React)

**Paso A0.1 — Instalar Node.js (LTS)**

**Acción**

1. Descarga e instala **Node.js LTS** desde el sitio oficial: [https://nodejs.org/en/download](https://nodejs.org/en/download)
2. Cierra y vuelve a abrir VS Code para que la terminal detecte los comandos.

**Qué está pasando y por qué**

* Node.js es el runtime que ejecuta herramientas del ecosistema React (por ejemplo Vite) y scripts de desarrollo.
* npm se instala junto con Node.js y gestiona dependencias (bibliotecas) de tu proyecto.

**Validación**
En la terminal de VS Code:

```bash
node -v
npm -v
```

**Resultado esperado**

* Debes ver versiones (por ejemplo `v20.x.x` y `10.x.x`).

**Evidencia**

* Copia/pega la salida o captura.

#### Ruta B: instalar Python y verificar Tkinter

**Paso B0.1 — Instalar Python 3**

**Acción**

1. Instala Python desde una fuente confiable:

   * Windows/macOS: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   * (Opcional) Microsoft Store en Windows, si tu institución lo permite.
2. En Windows, asegúrate de marcar la opción **Add Python to PATH** durante la instalación.

**Qué está pasando y por qué**

* Python será tu runtime para Tkinter. Si PATH no está configurado, `python` no se reconoce en terminal.

**Validación**

```bash
python --version
```

**Resultado esperado**

* Debes ver `Python 3.x.y`.

**Evidencia**

* Copia/pega la salida o captura.

### Fuentes oficiales (links directos)

* Node.js (descarga): [https://nodejs.org/en/download](https://nodejs.org/en/download)
* npm (instalación/uso): [https://docs.npmjs.com/downloading-and-installing-node-js-and-npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* React (estado y eventos): [https://react.dev/learn/managing-state](https://react.dev/learn/managing-state)
* React (crear app con build tool): [https://react.dev/learn/build-a-react-app-from-scratch](https://react.dev/learn/build-a-react-app-from-scratch)
* Vite (scaffolding): [https://vite.dev/guide/](https://vite.dev/guide/)
* Python (tkinter): [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
* Python (venv): [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

---

## 4) Glosario mínimo

* **Evento (UI):** suceso disparado por interacción (ej. click).
* **Handler/Callback:** función que se ejecuta cuando ocurre el evento.
* **Estado visible:** valor que se refleja en pantalla (texto/contador).
* **Main loop (bucle de eventos):** ciclo que mantiene viva la interfaz y despacha eventos.
* **Widget (Tkinter):** componente visual (Label, Button, Entry, etc.).

---

## 5) Materiales y entorno

### Software obligatorio

* Visual Studio Code

### Según ruta elegida

**Ruta A**

* Node.js + npm
* UI: React (con Vite)

**Ruta B**

* Python 3.x
* Tkinter (incluido con Python en la mayoría de distribuciones)
* (Recomendado) Entorno virtual (venv) para aislar dependencias del proyecto

---

## 6) Desarrollo guiado 

### 6.1 Paso 0 — Elegir ruta y registrar evidencia

**Acción**

* En el reporte, escribe: “Elegí Ruta A” o “Elegí Ruta B”.

**Resultado esperado**

* Ruta definida y justificada (1–3 líneas: por qué esa ruta para ti).

**Evidencia**

* Screenshot pegado en el reporte con:

  * Ruta A: `node -v` y `npm -v`
  * Ruta B: `python --version` y confirmación de venv (ver Paso 6.4)

---

### 6.2 Ruta A (Node.js + React; TypeScript opcional)

Tu demo debe cumplir: **ventana/página + botón + click cambia texto/contador**.

#### Opción A1 — React (con herramienta de build)

**Paso A1.1 — Crear proyecto**

**Acción (comandos)**

```bash
# 1) Crear proyecto (elige variante TS si tu ruta es TypeScript)
npm create vite@latest semana1-ui -- --template react-ts

# 2) Entrar a la carpeta
cd semana1-ui

# 3) Instalar dependencias
npm install

# 4) Ejecutar en modo desarrollo
npm run dev
```

**Resultado esperado**

* La terminal muestra la URL local (ej. `http://localhost:5173`) y el navegador abre la UI.

**Evidencia**

* Captura de la UI en el navegador.
* Copia de la salida de `npm run dev` (o captura).

**Paso A1.2 — Implementar botón + evento + estado visible**

**Acción**

* Edita `src/App.tsx` y deja un contador mínimo.

**Código (bloque incremental)**

```tsx
import { useState } from "react";

export default function App() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount((c) => c + 1);
  }

  return (
    <div style={{ padding: 24 }}>
      <h1>Semana 1 - Evento UI</h1>
      <p>Conteo actual: {count}</p>
      <button onClick={handleClick}>Click</button>
    </div>
  );
}
```

**Explicación técnica (qué pasa y por qué)**

* El botón dispara un evento `onClick`.
* El handler actualiza el state; React re-renderiza y el texto cambia.

**Resultado esperado**

* Cada click incrementa el contador en pantalla.

**Evidencia**

* Captura antes (count=0) y después (count>=1), o un video corto mostrando el cambio.

### 6.3 Ruta B (Python + Tkinter)

Tu demo debe cumplir: **ventana + botón + click cambia texto/contador**.

#### Paso B1 — Verificar Python y preparar el proyecto

**Acción**

1. Abre una terminal en VS Code (Terminal → New Terminal).
2. Verifica versión:

```bash
python --version
```

**Qué está pasando y por qué**

* Verificar versión asegura que tu runtime es consistente y que podrás reproducir el laboratorio en otra máquina.

**Resultado esperado**

* Debes ver algo como `Python 3.x.y`.

**Evidencia**

* Copia/pega la salida o captura.

#### Paso B2 — (Recomendado) Crear y activar un entorno virtual

**Acción**
En la carpeta del laboratorio:

```bash
python -m venv .venv
```

Actívalo:

* Windows (PowerShell):

```bash
.\.venv\Scripts\Activate.ps1
```

* macOS/Linux:

```bash
source .venv/bin/activate
```

**Qué está pasando y por qué**

* Un entorno virtual crea un Python “aislado” para tu proyecto.
* Problema que evita: cuando instalas librerías en el Python global, puedes romper otros proyectos o tener versiones incompatibles.
* En `.venv` quedan las dependencias de ESTE laboratorio; así, el proyecto es más reproducible y depurable.
* Aunque Tkinter suele venir incluido, el hábito de venv será obligatorio cuando avances a FastAPI y otras dependencias.

**Resultado esperado**

* Tu prompt de terminal cambia e indica `.venv` activo.

**Evidencia**

* Captura del prompt o salida de:

```bash
python -c "import sys; print(sys.executable)"
```

#### Paso B3 — Validar que Tkinter está disponible

**Acción**
Ejecuta:

```bash
python -c "import tkinter as tk; print('tkinter OK')"
```

**Qué está pasando y por qué**

* Confirmas que el módulo `tkinter` está disponible antes de escribir código. Si falla aquí, te ahorras perder tiempo depurando después.

**Resultado esperado**

* Imprime `tkinter OK`.

**Evidencia**

* Copia/pega la salida o captura.

#### Paso B4 — Crear tu primera UI (arranque mínimo)

**Acción**
Crea el archivo `main.py` con este primer bloque:

```python
import tkinter as tk

root = tk.Tk()
root.title("Semana 1 - Evento UI (Tkinter)")

root.mainloop()
```

Ejecuta:

```bash
python main.py
```

**Qué está pasando y por qué**

* `tk.Tk()` crea la ventana principal.
* `mainloop()` arranca el bucle de eventos: sin esto, la ventana se cierra inmediatamente.

**Resultado esperado**

* Aparece una ventana vacía con el título definido.

**Evidencia**

* Captura de la ventana abierta.

#### Paso B5 — Agregar estado visible (Label) y un botón

**Acción**
Reemplaza `main.py` por este bloque incremental:

```python
import tkinter as tk

root = tk.Tk()
root.title("Semana 1 - Evento UI (Tkinter)")

count = 0

label = tk.Label(root, text=f"Estado: {count}")
label.pack(padx=20, pady=10)

button = tk.Button(root, text="Click")
button.pack(padx=20, pady=10)

root.mainloop()
```

**Qué está pasando y por qué**

* `Label` es el estado visible: muestra el valor que vas a cambiar.
* `Button` existe, pero todavía no hace nada: falta conectar el evento.

**Resultado esperado**

* Ventana con texto `Estado: 0` y un botón.

**Evidencia**

* Captura de la ventana mostrando Label y Button.

#### Paso B6 — Conectar el evento (command) y actualizar el estado

**Acción**
Actualiza `main.py` a este bloque (con handler):

```python
import tkinter as tk

root = tk.Tk()
root.title("Semana 1 - Evento UI (Tkinter)")

count = 0

label = tk.Label(root, text=f"Estado: {count}")
label.pack(padx=20, pady=10)

def handle_click():
    global count
    count += 1
    label.config(text=f"Estado: {count}")

button = tk.Button(root, text="Click", command=handle_click)
button.pack(padx=20, pady=10)

root.mainloop()
```

**Qué está pasando y por qué**

* `handle_click` es el handler: se ejecuta cuando ocurre el evento.
* `command=handle_click` conecta el evento del botón con tu función.
* `label.config(...)` actualiza el texto en pantalla: esa es tu evidencia de evento + estado.

**Resultado esperado**

* Cada click incrementa el contador y el Label cambia.

**Evidencia**

* Captura antes (Estado: 0) y después (Estado: 1 o más) o mini-video.

---

## 7) Verificación y pruebas

### Plan mínimo de pruebas (obligatorio)

1. **Happy path:** ejecutar app → click 3 veces → verificar que el contador sube (0→1→2→3).

   * Evidencia: captura o video corto.

2. **Reinicio:** cerrar app → abrir de nuevo → verificar que inicia en 0 (estado inicial consistente).

   * Evidencia: captura de “Estado: 0”.

### Prueba de robustez (falla inducida) — elige 1 y documenta completo

Debes elegir UNA y hacer el ciclo: hipótesis → prueba mínima → error → fix → validación.

**Ruta A (React) — Falla inducida**

* Acción: cambia `onClick={handleClick}` por `onClick={handleClick()}`.
* Resultado esperado: comportamiento incorrecto (se ejecuta al render o genera error) y lo corriges regresando a `onClick={handleClick}`.

**Ruta B (Tkinter) — Falla inducida**

* Acción: cambia `command=handle_click` por `command=handle_click()`.
* Resultado esperado: el contador se incrementa al iniciar (o la UI se comporta mal) porque ejecutaste la función al crear el botón, en lugar de pasar la referencia.
* Corrección: vuelve a `command=handle_click`.

**Evidencia mínima de falla inducida**

* Captura del error o evidencia de “no cambia el estado”.
* Explicación corta: qué rompiste, por qué falló, cómo lo validaste, cómo lo corregiste.

---

## 8) Preguntas obligatorias para el reporte (responde todas)

1. ¿Qué ruta elegiste (A o B) y cuál fue tu criterio técnico para elegirla esta semana?
2. Define “programación orientada a eventos” usando tu demo: ¿cuál es el evento, cuál es el handler y cuál es el estado visible?
3. En tu implementación, ¿qué dato consideras “estado” y por qué debe ser visible para verificar aprendizaje?
4. Describe el flujo exacto de ejecución desde que corres el comando hasta que ves el cambio en UI (paso a paso).
5. ¿Qué falló en tu falla inducida? Da tu hipótesis inicial y explica la evidencia que la confirmó o descartó.
6. ¿Qué harías para que tu demo sea más “robusta” (validaciones, mensajes, manejo de errores) sin salirte del alcance de Semana 1?
7. ¿Qué parte del entorno fue la más frágil (instalación, versiones, dependencias) y cómo mitigaste el riesgo?
8. Si usaste IA, ¿qué verificaste tú manualmente para asegurar reproducibilidad (comandos, versiones, ejecución, evidencia)?

---

## 9) Uso de IA (obligatorio si la usaste)

Regla central: la IA no sustituye la prueba; todo debe ser reproducible y comprobado con evidencia.

Incluye en tu reporte una tabla (mínimo 1 fila si usaste IA):

* Error/objetivo (qué pasó o qué querías lograr)
* Prompt exacto
* Respuesta de IA (resumen)
* Cambio aplicado (qué modificaste exactamente)
* Evidencia de validación (captura/log de que ya funciona)
* Fuentes consultadas (APA)

---

## 10) Etapa 5: Implementación en el proyecto (Semana 1)

Esta semana solo establece base:

1. Repositorio/proyecto inicial creado según tu ruta (A o B).
2. Definir el objetivo general del proyecto integrador del curso (Centro de Control y Trazabilidad) solo como idea, sin desarrollo.

Evidencia:

* Un párrafo en el reporte con la idea general del proyecto integrador.
* Captura de estructura del repo.

---

## 11) Checklist final (antes de entregar)

* Ruta (A o B) declarada y evidencia de versiones incluida.
* Proyecto corre y muestra interfaz.
* Botón + click cambia estado visible (texto/contador).
* Evidencias mínimas: captura UI + log/terminal + pasos reproducibles.
* Falla inducida documentada con ciclo completo (hipótesis → prueba → evidencia → corrección → evidencia).
* Respuestas completas a preguntas obligatorias.
* APA incluida (si usaste fuentes) y declaración de IA incluida (si usaste IA).

---

## Referencias (formato APA, con links)

Ajusta “Retrieved” a tu fecha real.

* Node.js. (n.d.). *Download Node.js*. Retrieved 2026-01-25, from [https://nodejs.org/en/download](https://nodejs.org/en/download)
* npm Docs. (n.d.). *Downloading and installing Node.js and npm*. Retrieved 2026-01-25, from [https://docs.npmjs.com/downloading-and-installing-node-js-and-npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* TypeScript. (n.d.). *TypeScript Documentation*. Retrieved 2026-01-25, from [https://www.typescriptlang.org/docs/](https://www.typescriptlang.org/docs/)
* React. (n.d.). *Managing State*. Retrieved 2026-01-25, from [https://react.dev/learn/managing-state](https://react.dev/learn/managing-state)
* React. (n.d.). *Build a React app from Scratch*. Retrieved 2026-01-25, from [https://react.dev/learn/build-a-react-app-from-scratch](https://react.dev/learn/build-a-react-app-from-scratch)
* Vite. (n.d.). *Getting Started*. Retrieved 2026-01-25, from [https://vite.dev/guide/](https://vite.dev/guide/)
* Python. (n.d.). *tkinter — Python interface to Tcl/Tk*. Retrieved 2026-01-25, from [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
* Python. (n.d.). *venv — Creation of virtual environments*. Retrieved 2026-01-25, from [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)