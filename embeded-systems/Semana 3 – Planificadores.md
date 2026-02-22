# Semana 3 – Planificadores

Laboratorio 3: Planificador cooperativo no bloqueante en ESP32 (Arduino IDE + Wokwi)

## 1) Objetivo técnico

Implementar un planificador en un sistema embebido para ejecutar tareas sin bloquear, con tareas periódicas y por evento en ESP32, manteniendo el control del flujo.

Al final debes demostrar, con evidencia, que:

* Tienes **mínimo 3 tareas** ejecutándose en el mismo programa: una periódica rápida, una periódica lenta y una por evento/condición.
* Existe evidencia de que el sistema **no se bloquea**, mostrando por Serial cuándo corre cada tarea y que la rápida no se “congela” por la lenta.
* Documentas el criterio de planificación: cuándo se ejecuta cada tarea, cómo se decide, y cómo evitas el bloqueo.

---

## 2) Reporte

Tu reporte debe iniciar con:

* Nombre completo
* Número de alumno
* Semana–Tema: Semana 3 – Planificadores
* Grupo
* Fecha

Tu reporte debe incluir:

* Objetivo.
* Procedimiento reproducible.
* Lista de tareas (nombre, tipo: periódica/evento, periodo/condición, propósito: leer/decidir/actuar/reportar).
* Evidencia: logs/capturas del Serial Monitor con marcas de tiempo y conteos.
* Conclusión técnica.
* Referencias APA cuando uses fuentes externas.
* Declaración explícita de uso de IA: qué usaste, para qué, y cómo validaste.

---

## 3) Documentación en línea

Herramientas:

* Arduino IDE 2
  [https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing](https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing)
* Soporte ESP32 en Arduino IDE (Arduino-ESP32 / Espressif)
  [https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
* Wokwi ESP32
  [https://docs.wokwi.com/guides/esp32](https://docs.wokwi.com/guides/esp32)

Referencias técnicas (no bloqueo y temporización):

* `millis()`
  [https://docs.arduino.cc/language-reference/en/functions/time/millis/](https://docs.arduino.cc/language-reference/en/functions/time/millis/)
* Blink Without Delay (por qué evitar `delay()`)
  [https://www.arduino.cc/en/Tutorial/BlinkWithoutDelay](https://www.arduino.cc/en/Tutorial/BlinkWithoutDelay)
* Multi-tasking con `millis()` (explicación didáctica de “revisar el reloj”)
  [https://learn.adafruit.com/multi-tasking-the-arduino-part-1/using-millis-for-timing](https://learn.adafruit.com/multi-tasking-the-arduino-part-1/using-millis-for-timing)

GPIO y entradas:

* `pinMode`, `digitalRead`, `digitalWrite`
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/pinmode/](https://docs.arduino.cc/language-reference/en/functions/digital-io/pinmode/)
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalread/](https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalread/)
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalwrite/](https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalwrite/)
* Debounce (patrón con tiempo)
  [https://docs.arduino.cc/built-in-examples/digital/Debounce/](https://docs.arduino.cc/built-in-examples/digital/Debounce/)

Wokwi:

* GPIO pins API / modos como `INPUT_PULLUP`
  [https://docs.wokwi.com/chips-api/gpio](https://docs.wokwi.com/chips-api/gpio)

---

## 4) Lista de materiales

En esta semana se asume que ya cuentas con tu **ESP32-S3**. El laboratorio debe validarse en **dos modalidades**:

* Modalidad A: Simulación en Wokwi.
* Modalidad B: Ejecución real en la placa ESP32-S3 con Arduino IDE (carga por USB y validación con Serial Monitor).

### 4.1 Material obligatorio

1. Placa ESP32-S3 (dev board)
2. Cable USB de datos
3. Protoboard
4. Jumpers (macho-macho)
5. 1 LED (cualquier color)
6. 1 resistencia 220–330 Ω
7. 1 botón (pushbutton)

### 4.2 Material opcional

* 1 resistencia 10 kΩ (solo si decides no usar `INPUT_PULLUP` y prefieres pull-down externo)

---

## 5) Validación obligatoria en simulador y en placa

Este laboratorio requiere evidencia en ambas modalidades.

### 5.1 Modalidad A: Wokwi

* Crea el circuito en Wokwi.
* Ejecuta el sketch.
* Captura el Serial Monitor.
* Adjunta el enlace del proyecto.

### 5.2 Modalidad B: ESP32-S3 físico

* Selecciona tu placa ESP32-S3 en Arduino IDE.
* Selecciona el puerto USB correcto.
* Carga el sketch.
* Abre el Serial Monitor en Arduino IDE y captura evidencia.

Evidencia mínima de modalidad B:

* Captura de compilación/carga exitosa.
* Captura del Serial Monitor mostrando ejecución de tareas.
* Foto o captura del montaje físico (LED + botón).

---

## 6) Circuito (hardware y Wokwi)

Usaremos **un LED** y **un botón**.

### 5.1 LED (salida)

* GPIO_LED: GPIO 2
* Conexión:

  * GPIO 2 → resistencia (220–330 Ω) → ánodo del LED
  * cátodo del LED → GND

### 5.2 Botón (entrada)

* GPIO_BTN: GPIO 4
* Conexión:

  * un lado del botón → GPIO 4
  * otro lado del botón → GND

### 5.3 Por qué `INPUT_PULLUP`

En el código configuraremos el botón como `INPUT_PULLUP`:

* El MCU activa una resistencia pull-up interna.
* En reposo, el pin tiende a `HIGH`.
* Al presionar (conectas a GND) se lee `LOW`.

Resultado: en este laboratorio, **presionado = `LOW`**.

---

## 6) Modelo de planificador usado en este laboratorio

Este laboratorio implementa un planificador **cooperativo** (no RTOS) con:

* Una tabla de tareas periódicas (cada tarea tiene un periodo y su “última ejecución”).
* Una tarea por evento (se ejecuta cuando una condición se vuelve verdadera).

Este enfoque se basa en revisar el tiempo con `millis()` y evitar esperas bloqueantes como `delay()`. La idea central es: el sistema no “se duerme”; solo decide si ya es momento de ejecutar una tarea. (Ver Blink Without Delay y Adafruit multi-tasking en la sección 3.)

---

## 7) Evidencias mínimas

Adjunta al reporte:

* E1. Enlace del proyecto Wokwi (con LED y botón).
* E2. Captura del circuito en Wokwi.
* E3. Captura del Serial Monitor en Wokwi mostrando:

  * arranque
  * ejecución de 3 tareas (rápida, lenta y evento)
  * marcas de tiempo y conteos por tarea
* E4. Captura de compilación y carga exitosa en ESP32-S3 (Arduino IDE).
* E5. Foto/captura del montaje físico (LED + botón) en protoboard.
* E6. Captura del Serial Monitor en Arduino IDE (placa real) mostrando ejecución de tareas.
* E7. Tabla de tareas (nombre, periodo/condición, propósito).
* E8. Prueba de “no bloqueo”: evidencia comparativa de comportamiento con y sin bloqueo inducido.

---

## 8) Implementación incremental guiada con código

Regla de trabajo:

* En cada paso reemplaza tu archivo `sketch.ino` por el bloque completo indicado.
* Compila y ejecuta.
* No avances si no obtienes el resultado esperado.
* Guarda evidencia (captura o log) por paso.

### 8.1 Glosario mínimo de símbolos (para no programar “a ciegas”)

* `Serial`: objeto global del core Arduino para comunicación serial.
* `pinMode(pin, modo)`: configura un GPIO.
* `OUTPUT`, `INPUT_PULLUP`: constantes del core Arduino (provienen de `Arduino.h`).
* `digitalWrite(pin, HIGH/LOW)`: escribe nivel lógico.
* `digitalRead(pin)`: lee nivel lógico.
* `millis()`: tiempo desde el arranque en ms (contador 32-bit sin signo).

---

### Paso 8.1: Arranque, GPIO y telemetría base

Acción:

1. Pega el código.
2. Ejecuta.
3. Abre Serial Monitor.

Resultado esperado:

* Mensaje de arranque.
* LED apagado.

Código:

```cpp
#include <Arduino.h>

const uint8_t GPIO_LED = 2;
const uint8_t GPIO_BTN = 4;

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 3 - Planificadores");

  pinMode(GPIO_LED, OUTPUT);
  digitalWrite(GPIO_LED, LOW);

  // INPUT_PULLUP: el pin se mantiene en HIGH en reposo y pasa a LOW al presionar (conectado a GND)
  pinMode(GPIO_BTN, INPUT_PULLUP);
}

void loop() {
  // En el siguiente paso agregamos tareas y temporización.
}
```

Evidencia:

* Captura del Serial Monitor con el arranque.

---

### Paso 8.2: Temporización no bloqueante (función helper)

Meta:

* Crear una función que responda: “¿ya toca ejecutar?” sin usar `delay()`.

Acción:

1. Pega el código.
2. Observa que imprime un “tick” cada 1000 ms.

Resultado esperado:

* Aparece `TICK_1S` aproximadamente cada segundo.

Código:

```cpp
#include <Arduino.h>

const uint8_t GPIO_LED = 2;
const uint8_t GPIO_BTN = 4;

bool isDue(uint32_t now_ms, uint32_t &last_ms, uint32_t period_ms) {
  // Comparación por diferencia: soporta rollover de millis() en aritmética modular.
  if ((now_ms - last_ms) >= period_ms) {
    last_ms = now_ms;
    return true;
  }
  return false;
}

uint32_t last_tick_ms = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 3 - Planificadores");

  pinMode(GPIO_LED, OUTPUT);
  digitalWrite(GPIO_LED, LOW);

  pinMode(GPIO_BTN, INPUT_PULLUP);
}

void loop() {
  uint32_t now_ms = millis();

  if (isDue(now_ms, last_tick_ms, 1000)) {
    Serial.println("TICK_1S");
  }
}
```

Evidencia:

* Captura del Serial Monitor mostrando varios `TICK_1S`.

---

### Paso 8.3: Definir una tarea como estructura

Meta:

* Definir el “contrato” de una tarea: nombre, periodo, última ejecución y función.

Acción:

1. Pega el código.
2. Ejecuta y valida que compila.

Resultado esperado:

* Compila (aunque todavía no ejecuta tareas).

Código:

```cpp
#include <Arduino.h>

const uint8_t GPIO_LED = 2;
const uint8_t GPIO_BTN = 4;

// Firma de una tarea periódica: recibe el tiempo actual
using TaskFn = void (*)(uint32_t now_ms);

struct Task {
  const char* name;      // Identificador para logs
  uint32_t period_ms;    // Periodo de ejecución
  uint32_t last_run_ms;  // Última ejecución registrada
  TaskFn fn;             // Función a ejecutar
};

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 3 - Planificadores");

  pinMode(GPIO_LED, OUTPUT);
  digitalWrite(GPIO_LED, LOW);

  pinMode(GPIO_BTN, INPUT_PULLUP);
}

void loop() {
  // En el siguiente paso instanciamos tareas y las planificamos.
}
```

Evidencia:

* Captura de compilación exitosa.

---

### Paso 8.4: 2 tareas periódicas (rápida y lenta) con conteos

Meta:

* Tarea rápida: heartbeat cada 100 ms (actuar: alterna LED).
* Tarea lenta: telemetría cada 1000 ms (reportar: imprime conteos y marca de tiempo).

Acción:

1. Pega el código.
2. Ejecuta.
3. Observa que el LED parpadea y el Serial imprime telemetría cada 1 s.

Resultado esperado:

* LED alterna aproximadamente cada 100 ms.
* Log `SLOW` cada 1000 ms con conteos.

Código:

```cpp
#include <Arduino.h>

const uint8_t GPIO_LED = 2;
const uint8_t GPIO_BTN = 4;

using TaskFn = void (*)(uint32_t now_ms);

struct Task {
  const char* name;
  uint32_t period_ms;
  uint32_t last_run_ms;
  TaskFn fn;
};

bool isDue(uint32_t now_ms, uint32_t &last_ms, uint32_t period_ms) {
  if ((now_ms - last_ms) >= period_ms) {
    last_ms = now_ms;
    return true;
  }
  return false;
}

// Contadores de evidencia
uint32_t fast_count = 0;
uint32_t slow_count = 0;

bool led_level = false;

void taskFast(uint32_t now_ms) {
  (void)now_ms;
  fast_count++;
  led_level = !led_level;
  digitalWrite(GPIO_LED, led_level ? HIGH : LOW);
}

void taskSlow(uint32_t now_ms) {
  slow_count++;
  Serial.print("SLOW now_ms=");
  Serial.print(now_ms);
  Serial.print(" fast_count=");
  Serial.print(fast_count);
  Serial.print(" slow_count=");
  Serial.println(slow_count);
}

Task tasks[] = {
  {"FAST", 100, 0, taskFast},
  {"SLOW", 1000, 0, taskSlow},
};

const uint8_t TASKS_LEN = sizeof(tasks) / sizeof(tasks[0]);

void runScheduler(uint32_t now_ms) {
  for (uint8_t i = 0; i < TASKS_LEN; i++) {
    if (isDue(now_ms, tasks[i].last_run_ms, tasks[i].period_ms)) {
      tasks[i].fn(now_ms);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 3 - Planificadores");

  pinMode(GPIO_LED, OUTPUT);
  digitalWrite(GPIO_LED, LOW);

  pinMode(GPIO_BTN, INPUT_PULLUP);
}

void loop() {
  uint32_t now_ms = millis();
  runScheduler(now_ms);
}
```

Evidencia:

* Captura del Serial Monitor mostrando al menos 5 líneas `SLOW ...`.
* Captura del circuito con el LED alternando.

---

### Paso 8.5: 3ra tarea por evento (botón) con debounce

Meta:

* Tarea por evento: cuando detectes un “click” (presión+liberación estable) incrementa `event_count` y reporta.

Acción:

1. Pega el código.
2. Ejecuta.
3. Presiona el botón varias veces.

Resultado esperado:

* Se imprime `EVENT click_count=...` por cada click.
* No se generan múltiples clicks por rebotes.

Código:

```cpp
#include <Arduino.h>

const uint8_t GPIO_LED = 2;
const uint8_t GPIO_BTN = 4;

using TaskFn = void (*)(uint32_t now_ms);

struct Task {
  const char* name;
  uint32_t period_ms;
  uint32_t last_run_ms;
  TaskFn fn;
};

bool isDue(uint32_t now_ms, uint32_t &last_ms, uint32_t period_ms) {
  if ((now_ms - last_ms) >= period_ms) {
    last_ms = now_ms;
    return true;
  }
  return false;
}

// Contadores de evidencia
uint32_t fast_count = 0;
uint32_t slow_count = 0;
uint32_t event_count = 0;

bool led_level = false;

// Debounce básico
bool btn_stable_level = HIGH;
bool btn_last_raw_level = HIGH;
uint32_t btn_last_change_ms = 0;
const uint32_t DEBOUNCE_MS = 30;

// Bandera de evento
bool click_event = false;

void taskFast(uint32_t now_ms) {
  (void)now_ms;
  fast_count++;
  led_level = !led_level;
  digitalWrite(GPIO_LED, led_level ? HIGH : LOW);
}

void taskSlow(uint32_t now_ms) {
  slow_count++;
  Serial.print("SLOW now_ms=");
  Serial.print(now_ms);
  Serial.print(" fast_count=");
  Serial.print(fast_count);
  Serial.print(" slow_count=");
  Serial.print(slow_count);
  Serial.print(" event_count=");
  Serial.println(event_count);
}

void sampleButton(uint32_t now_ms) {
  // Lectura cruda
  bool raw_level = digitalRead(GPIO_BTN);

  // Detecta cambio crudo
  if (raw_level != btn_last_raw_level) {
    btn_last_raw_level = raw_level;
    btn_last_change_ms = now_ms;
  }

  // Si se mantiene estable, acepta el cambio
  if ((now_ms - btn_last_change_ms) >= DEBOUNCE_MS) {
    if (btn_stable_level != raw_level) {
      bool prev = btn_stable_level;
      btn_stable_level = raw_level;

      // Detecta un click: transición estable de LOW->HIGH (liberación)
      // Recuerda: con INPUT_PULLUP, presionado=LOW, liberado=HIGH
      if (prev == LOW && btn_stable_level == HIGH) {
        click_event = true;
      }
    }
  }
}

void taskEvent(uint32_t now_ms) {
  (void)now_ms;
  if (click_event) {
    click_event = false;
    event_count++;
    Serial.print("EVENT click_count=");
    Serial.println(event_count);
  }
}

Task tasks[] = {
  {"FAST", 100, 0, taskFast},
  {"SLOW", 1000, 0, taskSlow},
  // Esta tarea revisa si existe un evento ya detectado
  {"EVENT", 10, 0, taskEvent},
};

const uint8_t TASKS_LEN = sizeof(tasks) / sizeof(tasks[0]);

void runScheduler(uint32_t now_ms) {
  // Primero muestrea entradas (leer)
  sampleButton(now_ms);

  // Luego ejecuta tareas (decidir/actuar/reportar)
  for (uint8_t i = 0; i < TASKS_LEN; i++) {
    if (isDue(now_ms, tasks[i].last_run_ms, tasks[i].period_ms)) {
      tasks[i].fn(now_ms);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 3 - Planificadores");

  pinMode(GPIO_LED, OUTPUT);
  digitalWrite(GPIO_LED, LOW);

  pinMode(GPIO_BTN, INPUT_PULLUP);
}

void loop() {
  uint32_t now_ms = millis();
  runScheduler(now_ms);
}
```

Evidencia:

* Captura del Serial Monitor mostrando `EVENT click_count=...`.

---

### Paso 8.6: Prueba de “no bloqueo” (falla inducida y medición)

Esta prueba es didáctica: vas a inducir un bloqueo y comprobar que el planificador sufre.

Acción:

1. En `taskSlow`, agrega intencionalmente un `delay(300)`.
2. Ejecuta y observa el efecto en:

   * `fast_count` por segundo
   * regularidad del parpadeo
3. Quita el `delay(300)` y repite.

Qué debes observar:

* Con `delay(300)`, la tarea rápida pierde ejecuciones (se “congela” por ráfagas).
* Sin `delay(300)`, la tarea rápida mantiene su ritmo.

Evidencia:

* Dos capturas comparativas del Serial Monitor (con y sin el `delay`).

---

## 9) Plan de pruebas (obligatorio)

Documenta en tu reporte:

1. Tarea rápida: periodo configurado y evidencia de ejecución constante.
2. Tarea lenta: periodo configurado y evidencia de logs cada ~1 s.
3. Tarea por evento: qué condición la dispara y evidencia de clicks.
4. Prueba de no bloqueo: comparativo con/ sin bloqueo inducido.

---

## 10) Implementación en el proyecto

Esta semana debes integrar el planificador con la FSM de tu etapa (Semana 2) y entregar:

* Lista de tareas (3 o más) de tu etapa con periodicidad/condición y propósito.
* Implementación en ESP32 donde:

  * la FSM se actualiza sin bloquear
  * las tareas se ejecutan bajo el planificador

Guía mínima:

* Define una tarea `FSM_UPDATE` periódica (por ejemplo cada 20–50 ms) que llame tu función de actualización de FSM.
* Mantén todas las acciones por estado no bloqueantes.

---

## 11) Depuración con IA (obligatorio)

Documenta dos casos reales. Cada caso debe incluir:

* Error exacto copiado.
* Prompt enviado.
* Respuesta de IA.
* Cambio aplicado.
* Evidencia de validación: compila, ejecuta y produce el log esperado.

Sugerencias de fallas inducidas:

* Cambiar un `uint32_t` de tiempo a `int` y analizar efectos en comparación por diferencia.
* Romper el periodo de una tarea (poner 0 o un valor extremo) y documentar consecuencias.

---

## 12) Preguntas obligatorias para el reporte

1. Define “planificador” en embebidos y explica por qué se usa.
2. Explica por qué `delay()` es bloqueo y por qué es un problema para varias tareas.
3. Describe tus 3 tareas (rápida, lenta y evento): propósito y disparo (tiempo/condición).
4. Explica el criterio de decisión: cómo tu código decide que una tarea “ya toca”.
5. ¿Cómo verificas con evidencia que la tarea rápida no se congela por la lenta?
6. Explica por qué `uint32_t` es el tipo correcto para tiempos basados en `millis()`.
7. Describe cómo integrarías `FSM_UPDATE` en tu planificador sin bloquear.

---

## 13) Checklist final

* Reporte con encabezado (nombre, número de alumno, semana–tema).
* Enlace Wokwi + captura del circuito.
* Logs con marcas de tiempo y conteos por tarea.
* Tabla de tareas (nombre, periodo/condición, propósito).
* Prueba de no bloqueo (comparativo).
* Referencias APA cuando aplique.
* Declaración de uso de IA.


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)