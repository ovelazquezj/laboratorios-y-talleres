# Laboratorio — Semana 3: Objetos, controles/componentes + módulos/imports

## 1) Encabezado

**Materia:** Programación II (Ing. TICs)
**Semana–Tema:** Semana 3 — Objetos, controles y componentes + espacios de nombres (módulos/imports/paquetes)
**IDE obligatorio:** Visual Studio Code

**Alumno:** <Nombre completo>
**Matrícula/Número de alumno:** <ID>
**Grupo:** <Grupo>
**Fecha:** <YYYY-MM-DD>

### Evidencias mínimas del laboratorio (obligatorias)

* Captura del **árbol de carpetas/módulos**.
* Capturas de UI mostrando **reutilización** (mismo componente/widget usado al menos 2 veces).
* Log/captura de ejecución mostrando el comando usado y que corre sin errores.
* Procedimiento reproducible para correr y verificar imports/módulos.

---

## 2) Objetivo técnico y criterios de aceptación

### Objetivo técnico

Construir una mini-aplicación con UI basada en **objetos/componentes**, organizada por **módulos**, demostrando:

* estructura mínima mantenible (no todo en un archivo),
* reutilización real de componentes/controles,
* un modelo de datos mínimo `Evento` usado para construir/mostrar información.

### Criterios de aceptación (medibles)

Debes cumplir TODO:

1. **Estructura del proyecto** con mínimo 3 módulos/carpetas:

   * `ui/` (UI),
   * `logic/` (lógica),
   * `models/` (modelo de datos).

2. **Modelo mínimo** `Evento` con 5 campos (contrato):

   * `timestamp`, `equipo`, `etapa`, `evento`, `valor`.

3. **Al menos 2 componentes/controles reutilizables**.

   * Ejemplo: `EventCard` y `CaptureForm` (o equivalentes).

4. **Evidencia de reutilización**:

   * el mismo componente/widget se usa **al menos 2 veces** en la UI.

5. **Procedimiento reproducible** para correr y verificar:

   * imports/módulos correctos,
   * componentes visibles,
   * reutilización funcionando.

---

## 3) Plataforma (rutas vigentes)

* **Ruta A:** Node.js + React (TypeScript opcional)
* **Ruta B:** Python + Tkinter

Elige UNA ruta y realiza el laboratorio completo solo con esa.

---

## 4) Prerrequisitos y fuentes (links directos)

### Fuentes oficiales

* React — Passing Props to a Component: [https://react.dev/learn/passing-props-to-a-component](https://react.dev/learn/passing-props-to-a-component)
* React — Your First Component / component model (ruta Learn): [https://react.dev/learn](https://react.dev/learn)
* Vite — Getting Started: [https://vite.dev/guide/](https://vite.dev/guide/)
* Python — import system (referencia): [https://docs.python.org/3/reference/import.html](https://docs.python.org/3/reference/import.html)
* Python — modules (tutorial): [https://docs.python.org/3/tutorial/modules.html](https://docs.python.org/3/tutorial/modules.html)
* Python — tkinter (oficial): [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)

### Foro experto (solo como apoyo; valida con evidencia)

* Stack Overflow — Reusable frame class in Tkinter: [https://stackoverflow.com/questions/54223587/how-to-use-a-re-usable-frame-class-in-tkinter](https://stackoverflow.com/questions/54223587/how-to-use-a-re-usable-frame-class-in-tkinter)

---

## 5) Glosario mínimo

* **Módulo:** archivo importable (ej. `models/event.ts` o `models/event.py`).
* **Paquete:** carpeta con módulos (en Python, típicamente con `__init__.py`; en JS/TS, carpeta de módulos).
* **Espacio de nombres:** “zona” donde viven nombres; evita choques y organiza el código.
* **Componente (React):** función que recibe props y devuelve UI.
* **Control/Widget (Tkinter):** objeto UI (Entry, Button, Frame, Label) que puede componerse y reutilizarse.

---

## 6) Estructura del proyecto (obligatoria)

### Plantilla mínima

#### Ruta A (React)

```text
semana3-ui/
  src/
    models/
      Event.ts
    logic/
      eventService.ts
    ui/
      components/
        EventCard.tsx
        CaptureForm.tsx
      AppShell.tsx
    App.tsx
```

#### Ruta B (Tkinter)

```text
semana3-tk/
  app/
    models/
      event.py
    logic/
      event_service.py
    ui/
      widgets/
        event_card.py
        capture_form.py
      app_shell.py
  main.py
```

**Evidencia obligatoria**

* Captura del árbol de carpetas (VS Code Explorer).

---

## 7) Contrato del modelo (obligatorio)

Tu modelo `Evento` debe representar este contrato mínimo:

* `timestamp`: string (ISO) o datetime (según ruta)
* `equipo`: string
* `etapa`: string
* `evento`: string
* `valor`: string

Regla: la UI debe construir al menos 1 `Evento` y mostrarlo usando un componente/widget.

---

## 8) Desarrollo guiado — Ruta A (React)

### 8.1 Crear (o reutilizar) proyecto

Si vienes de Semana 2, puedes **copiar** tu proyecto y renombrar carpeta a `semana3-ui`.

Si necesitas crear desde cero:

```bash
npm create vite@latest semana3-ui -- --template react-ts
cd semana3-ui
npm install
npm run dev
```

**Evidencia**

* Log/captura con `npm run dev` y la app corriendo.

---

### 8.2 Paso 1 — Crear el modelo `Evento`

Crea `src/models/Event.ts`:

```ts
export type Evento = {
  timestamp: string; // ISO
  equipo: string;
  etapa: string;
  evento: string;
  valor: string;
};
```

**Qué está pasando y por qué**

* Extraes el “contrato” a un módulo para que UI y lógica dependan del mismo tipo.

---

### 8.3 Paso 2 — Crear lógica (servicio) separada

Crea `src/logic/eventService.ts`:

```ts
import type { Evento } from "../models/Event";

export function makeEvento(input: {
  equipo: string;
  etapa: string;
  evento: string;
  valor: string;
}): Evento {
  return {
    timestamp: new Date().toISOString(),
    equipo: input.equipo.trim(),
    etapa: input.etapa.trim(),
    evento: input.evento.trim(),
    valor: input.valor.trim(),
  };
}

export function formatEvento(e: Evento): string {
  return `${e.timestamp} | ${e.equipo} | ${e.etapa} | ${e.evento} | ${e.valor}`;
}
```

**Qué está pasando y por qué**

* `logic/` concentra reglas y transformaciones (UI no debería formatear strings complejos ni construir timestamps directamente).

---

### 8.4 Paso 3 — Componente reutilizable 1: `EventCard`

Crea `src/ui/components/EventCard.tsx`:

```tsx
import type { Evento } from "../../models/Event";
import { formatEvento } from "../../logic/eventService";

export function EventCard(props: { title: string; evento: Evento | null }) {
  const { title, evento } = props;

  return (
    <div style={{ border: "1px solid #ccc", padding: 12, borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <pre style={{ whiteSpace: "pre-wrap" }}>
        {evento ? formatEvento(evento) : "(sin eventos)"}
      </pre>
    </div>
  );
}
```

**Qué está pasando y por qué**

* `EventCard` recibe datos por **props** y puede usarse varias veces sin duplicar UI.

---

### 8.5 Componente reutilizable 2: `CaptureForm`

Crea `src/ui/components/CaptureForm.tsx`:

```tsx
import { useState } from "react";

export function CaptureForm(props: {
  onCreate: (input: { equipo: string; etapa: string; evento: string; valor: string }) => void;
}) {
  const { onCreate } = props;

  const [equipo, setEquipo] = useState("");
  const [etapa, setEtapa] = useState("");
  const [evento, setEvento] = useState("");
  const [valor, setValor] = useState("");

  function submit() {
    onCreate({ equipo, etapa, evento, valor });
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: 12, borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>Formulario de captura</h3>

      <label>
        Equipo
        <input value={equipo} onChange={(e) => setEquipo(e.target.value)} />
      </label>
      <br />

      <label>
        Etapa
        <input value={etapa} onChange={(e) => setEtapa(e.target.value)} />
      </label>
      <br />

      <label>
        Evento
        <input value={evento} onChange={(e) => setEvento(e.target.value)} />
      </label>
      <br />

      <label>
        Valor
        <input value={valor} onChange={(e) => setValor(e.target.value)} />
      </label>
      <br />

      <button type="button" onClick={submit} style={{ marginTop: 8 }}>
        Crear Evento
      </button>
    </div>
  );
}
```

**Qué está pasando y por qué**

* `CaptureForm` encapsula la captura; se reutiliza en el futuro sin mezclar lógica con `App`.

---

### 8.6 AppShell: separar “pantalla” de composición

Crea `src/ui/AppShell.tsx`:

```tsx
import { useState } from "react";
import type { Evento } from "../models/Event";
import { makeEvento } from "../logic/eventService";
import { EventCard } from "./components/EventCard";
import { CaptureForm } from "./components/CaptureForm";

export function AppShell() {
  const [last, setLast] = useState<Evento | null>(null);
  const [list, setList] = useState<Evento[]>([]);

  function onCreate(input: { equipo: string; etapa: string; evento: string; valor: string }) {
    const e = makeEvento(input);
    setLast(e);
    setList((prev) => [e, ...prev].slice(0, 5));
  }

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <h1>Semana 3 — Componentes + Módulos</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <CaptureForm onCreate={onCreate} />

        {/* Reutilización #1: misma tarjeta para “último evento” */}
        <EventCard title="Último evento" evento={last} />
      </div>

      <h2 style={{ marginTop: 16 }}>Eventos recientes</h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {/* Reutilización #2+: misma tarjeta usada múltiples veces */}
        {list.slice(0, 2).map((e, idx) => (
          <EventCard key={idx} title={`Evento #${idx + 1}`} evento={e} />
        ))}
      </div>
    </div>
  );
}
```

Actualiza `src/App.tsx` para usar `AppShell`:

```tsx
import { AppShell } from "./ui/AppShell";

export default function App() {
  return <AppShell />;
}
```

**Evidencia obligatoria (reutilización)**

* Captura donde se ve `EventCard` al menos 2 veces (por ejemplo “Último evento” y “Evento #1”).

---

### 8.7 Verificación de imports/módulos (procedimiento reproducible)

**Acción**

1. Asegura que corre:

```bash
npm run dev
```

2. Verifica que no hay errores de imports en terminal/consola.

**Prueba de robustez (módulos) — falla inducida y corrección**

* Induce: cambia un import de `../models/Event` a `../models/Events`.
* Evidencia: error en build/consola.
* Corrige: regresa el nombre correcto.
* Evidencia final: vuelve a compilar y correr.

---

## 9) Desarrollo guiado — Ruta B (Python + Tkinter)

### 9.1 Preparar proyecto

Crea la estructura `semana3-tk/` como se muestra en la sección 6.

(1) Verifica Python:

```bash
python --version
```

(2) Verifica Tkinter:

```bash
python -m tkinter
```

---

### 9.2 Paso 1 — Modelo `Evento`

Crea `app/models/event.py`:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Evento:
    timestamp: str
    equipo: str
    etapa: str
    evento: str
    valor: str


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
```

---

### 9.3 Paso 2 — Lógica separada

Crea `app/logic/event_service.py`:

```python
from app.models.event import Evento, now_iso


def make_evento(equipo: str, etapa: str, evento: str, valor: str) -> Evento:
    return Evento(
        timestamp=now_iso(),
        equipo=equipo.strip(),
        etapa=etapa.strip(),
        evento=evento.strip(),
        valor=valor.strip(),
    )


def format_evento(e: Evento) -> str:
    return f"{e.timestamp} | {e.equipo} | {e.etapa} | {e.evento} | {e.valor}"
```

---

### 9.4 Widget reutilizable 1: `EventCardFrame`

Crea `app/ui/widgets/event_card.py`:

```python
import tkinter as tk

from app.logic.event_service import format_evento
from app.models.event import Evento


class EventCardFrame(tk.Frame):
    def __init__(self, master, title: str):
        super().__init__(master, bd=1, relief="solid", padx=10, pady=10)
        self._title = tk.Label(self, text=title, font=("Arial", 11, "bold"))
        self._title.pack(anchor="w")

        self._text = tk.StringVar(value="(sin eventos)")
        self._body = tk.Label(self, textvariable=self._text, justify="left")
        self._body.pack(anchor="w", pady=(6, 0))

    def set_evento(self, e: Evento | None):
        self._text.set(format_evento(e) if e else "(sin eventos)")
```

**Qué está pasando y por qué**

* Definir un Frame como clase lo hace reutilizable y componible.

---

### 9.5 Widget reutilizable 2: `CaptureFormFrame`

Crea `app/ui/widgets/capture_form.py`:

```python
import tkinter as tk


class CaptureFormFrame(tk.Frame):
    def __init__(self, master, on_create):
        super().__init__(master, bd=1, relief="solid", padx=10, pady=10)
        self._on_create = on_create

        tk.Label(self, text="Formulario de captura", font=("Arial", 11, "bold")).pack(anchor="w")

        self.equipo = tk.StringVar(value="")
        self.etapa = tk.StringVar(value="")
        self.evento = tk.StringVar(value="")
        self.valor = tk.StringVar(value="")

        self._row("Equipo", self.equipo)
        self._row("Etapa", self.etapa)
        self._row("Evento", self.evento)
        self._row("Valor", self.valor)

        tk.Button(self, text="Crear Evento", command=self._submit).pack(anchor="w", pady=(8, 0))

    def _row(self, label, var):
        tk.Label(self, text=label).pack(anchor="w")
        tk.Entry(self, textvariable=var, width=40).pack(anchor="w", pady=(0, 6))

    def _submit(self):
        self._on_create(
            self.equipo.get(),
            self.etapa.get(),
            self.evento.get(),
            self.valor.get(),
        )
```

---

### 9.6 AppShell: componer pantalla con reutilización

Crea `app/ui/app_shell.py`:

```python
import tkinter as tk

from app.logic.event_service import make_evento
from app.models.event import Evento
from app.ui.widgets.capture_form import CaptureFormFrame
from app.ui.widgets.event_card import EventCardFrame


class AppShell(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._last: Evento | None = None
        self._list: list[Evento] = []

        tk.Label(self, text="Semana 3 — Componentes + Módulos", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        top = tk.Frame(self)
        top.pack(fill="x")

        self.form = CaptureFormFrame(top, on_create=self.on_create)
        self.form.pack(side="left", padx=(0, 10))

        # Reutilización #1
        self.card_last = EventCardFrame(top, title="Último evento")
        self.card_last.pack(side="left")

        tk.Label(self, text="Eventos recientes", font=("Arial", 12, "bold")).pack(anchor="w", pady=(12, 6))

        bottom = tk.Frame(self)
        bottom.pack(fill="x")

        # Reutilización #2 (otra instancia del MISMO widget)
        self.card_1 = EventCardFrame(bottom, title="Evento #1")
        self.card_1.pack(side="left", padx=(0, 10))

        self.card_2 = EventCardFrame(bottom, title="Evento #2")
        self.card_2.pack(side="left")

        self._render()

    def on_create(self, equipo: str, etapa: str, evento: str, valor: str):
        e = make_evento(equipo, etapa, evento, valor)
        self._last = e
        self._list = [e, *self._list][:5]
        self._render()

    def _render(self):
        self.card_last.set_evento(self._last)

        e1 = self._list[0] if len(self._list) > 0 else None
        e2 = self._list[1] if len(self._list) > 1 else None

        self.card_1.set_evento(e1)
        self.card_2.set_evento(e2)
```

Crea `main.py` en la raíz:

```python
import tkinter as tk

from app.ui.app_shell import AppShell


def main():
    root = tk.Tk()
    root.title("Semana 3 — Tkinter módulos")
    root.geometry("980x420")

    app = AppShell(root)
    app.pack(fill="both", expand=True, padx=12, pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()
```

**Evidencia obligatoria (reutilización)**

* Captura donde se ven al menos 2 instancias de `EventCardFrame` (por ejemplo “Último evento” y “Evento #1”).

---

### 9.7 Verificación de imports/módulos (procedimiento reproducible)

**Acción**
Ejecuta desde la raíz del proyecto:

```bash
python main.py
```

**Prueba de robustez (módulos) — falla inducida y corrección**

* Induce: cambia `from app.logic.event_service import make_evento` por `from app.logic.events_service import make_evento`.
* Evidencia: `ModuleNotFoundError`.
* Corrige: regresa el import correcto.
* Evidencia final: vuelve a ejecutar y corre.

---

## 10) Verificación y pruebas (mínimas)

### Casos mínimos

1. Completa los 4 campos y crea un evento → debe reflejarse en “Último evento”.
2. Crea 2 eventos → “Evento #1” y “Evento #2” deben mostrar eventos distintos.
3. Reinicia la app → vuelve a estado inicial (lista local, sin persistencia).

---

## 11) Checklist final (solo laboratorio)

* Estructura con `ui/`, `logic/`, `models/` (o equivalente) y evidencia del árbol.
* Modelo `Evento` con 5 campos (timestamp, equipo, etapa, evento, valor).
* 2 componentes/controles reutilizables implementados.
* Reutilización real: mismo componente/widget instanciado ≥ 2 veces.
* App corre sin errores y hay evidencia de ejecución.
* Procedimiento reproducible de ejecución.
* Prueba de robustez de imports (falla inducida y corrección) documentada con evidencia.


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)