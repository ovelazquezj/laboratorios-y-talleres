 # Semana 2 – Máquinas de estados (FSM)

Laboratorio 2: Implementación de una FSM no bloqueante en ESP32 con Arduino IDE y Wokwi

## 1) Objetivo técnico

Implementar una máquina de estados finitos (FSM) en ESP32 que cumpla:

* Mínimo 4 estados.
* Mínimo 5 transiciones documentadas.
* Evidencia observable de estados y transiciones por Serial Monitor.
* Implementación no bloqueante: el ciclo principal no debe depender de esperas largas.
* Código organizado con:

  * una función `updateFsm(...)`
  * funciones auxiliares por acción o por estado.

El laboratorio entrega una FSM base reproducible. Al final, deberás presentar también la representación de la FSM en tabla y/o diagrama.

---

## 2) Reporte

Tu reporte debe iniciar con:

* Nombre completo
* Número de alumno
* Semana–Tema: Semana 2 – Máquinas de estados
* Grupo
* Fecha

Tu reporte debe incluir:

* Objetivo.
* Procedimiento reproducible.
* FSM en representación clara: tabla o diagrama.
* Evidencia: capturas/logs del Serial Monitor, capturas del circuito en Wokwi, enlace del proyecto.
* Conclusión técnica.
* Referencias APA cuando uses fuentes externas.
* Declaración de uso de IA: qué usaste, para qué, y cómo validaste.

---

## 3) Documentación en línea

Herramientas:

* Arduino IDE 2
  [https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing](https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing)
* Soporte ESP32 en Arduino IDE (Arduino-ESP32 / Espressif)
  [https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
* Wokwi ESP32
  [https://docs.wokwi.com/guides/esp32](https://docs.wokwi.com/guides/esp32)

Referencias técnicas usadas en este laboratorio:

* `Serial`
  [https://docs.arduino.cc/language-reference/en/functions/communication/serial/](https://docs.arduino.cc/language-reference/en/functions/communication/serial/)
* `pinMode`
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/pinmode/](https://docs.arduino.cc/language-reference/en/functions/digital-io/pinmode/)
* `digitalWrite`
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalwrite/](https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalwrite/)
* `digitalRead`
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalread/](https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalread/)
* `millis`
  [https://docs.arduino.cc/language-reference/en/functions/time/millis/](https://docs.arduino.cc/language-reference/en/functions/time/millis/)
* Debounce (patrón con `millis`)
  [https://docs.arduino.cc/built-in-examples/digital/Debounce/](https://docs.arduino.cc/built-in-examples/digital/Debounce/)
* Blink Without Delay (patrón no bloqueante)
  [https://www.arduino.cc/en/Tutorial/BlinkWithoutDelay](https://www.arduino.cc/en/Tutorial/BlinkWithoutDelay)

---

## 3.1) Glosario mínimo del core Arduino-ESP32

Este laboratorio usa constantes, tipos y funciones que ya existen en el core de Arduino para ESP32. Debes reconocerlas porque aparecerán en muchos ejemplos oficiales.

### 3.1.1 `#include <Arduino.h>`

* Inserta las declaraciones del core de Arduino.
* Desde ahí provienen símbolos como `HIGH`, `LOW`, `INPUT_PULLUP`, `OUTPUT`, `pinMode`, `digitalWrite`, `digitalRead`, `millis`, y el objeto global `Serial`.

### 3.1.2 `HIGH`, `LOW`, `OUTPUT`, `INPUT`, `INPUT_PULLUP`

* `OUTPUT`: configura un GPIO como salida digital.
* `INPUT`: configura un GPIO como entrada digital.
* `INPUT_PULLUP`: configura un GPIO como entrada e integra una resistencia pull-up interna. En reposo la lectura suele ser `HIGH`. Si conectas el botón a GND, al presionarlo la lectura pasa a `LOW`.
* `HIGH` y `LOW`: niveles lógicos usados por `digitalWrite` y devueltos por `digitalRead`.

### 3.1.3 Por qué usamos `INPUT_PULLUP` en el botón

* Evita que el pin quede “flotando” cuando el botón no está presionado.
* Reduce ruido eléctrico y lecturas aleatorias.
* Simplifica el circuito: no necesitas resistencia externa.

### 3.1.4 `enum class` y el prefijo `State::`

* `enum class` define un conjunto de valores con tipado fuerte.
* Si el tipo se llama `State`, sus valores se acceden como `State::IDLE`, `State::RUNNING`, etc.
* Este prefijo evita colisiones con otros nombres y obliga a escribir el tipo explícito, lo cual mejora legibilidad.

---

## 4) Evidencias mínimas

Adjunta al reporte:

* E1. Enlace del proyecto Wokwi.
* E2. Captura del circuito en Wokwi (LED + botón).
* E3. Captura del Serial Monitor mostrando:

  * arranque
  * estado actual
  * mínimo 5 transiciones, cada una con evento y cambio de estado
* E4. FSM en tabla o diagrama, consistente con el código.
* E5. Bitácora breve de pruebas: qué hiciste para provocar cada transición.

---

## 5) Circuito en Wokwi

Crea un proyecto nuevo de ESP32 y arma este circuito:

* LED con resistencia en serie

  * Ánodo del LED a GPIO 2
  * Cátodo del LED a GND
* Botón (pushbutton)

  * Un lado a GPIO 4
  * El otro lado a GND

### 5.1) Qué implica `INPUT_PULLUP` en el circuito

En el código configuraremos el botón como `INPUT_PULLUP`:

* El microcontrolador activa una resistencia pull-up interna hacia Vcc.
* Sin presionar, el pin tiende a `HIGH`.
* Al presionar, conectas el pin a GND y la lectura pasa a `LOW`.

Consecuencia directa:

* En este laboratorio, “botón presionado” se detecta como `LOW`.

---

## 6) FSM base del laboratorio

Implementarás esta FSM base. Si la implementas correctamente, cumples requisitos mínimos.

### 6.1 Estados

* `IDLE`: sistema inactivo.
* `ARMED`: sistema armado, listo para iniciar.
* `RUNNING`: ejecutando una tarea simulada.
* `WAIT_COND`: esperando una condición simulada por tiempo.
* `DONE`: ciclo completado.
* `ERROR`: estado de falla controlada.

### 6.2 Eventos

* `EVT_BTN_SHORT`: pulsación corta.
* `EVT_BTN_LONG`: pulsación larga.
* `EVT_TIMEOUT`: vencimiento de temporizador.
* `EVT_FAULT`: falla inducida.

### 6.3 Transiciones mínimas (tabla de referencia)

Esta tabla debe aparecer en tu reporte.

| Origen    | Evento    | Destino   | Acción principal  |
| --------- | --------- | --------- | ----------------- |
| IDLE      | BTN_SHORT | ARMED     | Preparar ciclo    |
| ARMED     | BTN_SHORT | RUNNING   | Iniciar ejecución |
| RUNNING   | TIMEOUT   | WAIT_COND | Pasar a espera    |
| WAIT_COND | TIMEOUT   | DONE      | Finalizar ciclo   |
| DONE      | BTN_SHORT | IDLE      | Reset lógico      |
| ARMED     | BTN_LONG  | IDLE      | Desarmar          |
| RUNNING   | BTN_LONG  | ERROR     | Falla inducida    |
| ERROR     | BTN_SHORT | IDLE      | Recuperación      |

Se permite implementar más transiciones, pero estas deben existir y demostrarse con evidencia.

---

## 7) Tipos de datos que usaremos

En embebidos, el tipo de dato es parte del diseño. En este laboratorio:

* `uint8_t` para GPIO: identificadores pequeños sin signo.
* `uint32_t` para tiempo: compatible con `millis()` y comparaciones por diferencia.
* `bool` para estados lógicos.
* `enum class` para estados y eventos: evita colisiones de nombres y mejora legibilidad.

---

## 8) Implementación incremental guiada con código

Regla de trabajo:

* En cada paso reemplaza tu archivo `sketch.ino` por el bloque completo indicado.
* Compila y ejecuta en Wokwi.
* No avances sin cumplir el resultado esperado.
* Captura evidencia y registra cómo provocaste cada transición.

### 8.1) Antes de empezar: qué significa lo que estás usando

En esta sección vas a ver símbolos del core Arduino. Cada vez que aparezca uno nuevo, debes poder responder dos preguntas:

* Qué hace a nivel de plataforma.
* Por qué se usa en este diseño.

Checklist técnico de símbolos que aparecerán:

* `Serial`: objeto global para comunicación serial.
* `Serial.begin(baud)`: inicializa la UART a un baud rate.
* `pinMode(pin, modo)`: configura un GPIO como entrada o salida.
* `digitalWrite(pin, nivel)`: escribe `HIGH/LOW` en un GPIO configurado como salida.
* `digitalRead(pin)`: lee `HIGH/LOW` en un GPIO configurado como entrada.
* `millis()`: contador de tiempo desde arranque en milisegundos.
* `INPUT_PULLUP`: activa pull-up interna en una entrada.
* `enum class`: estados y eventos con tipado fuerte.
* `State::IDLE`: acceso a un valor de un `enum class`.

Si un símbolo no te queda claro, consulta la referencia de Arduino en la sección 3.

### Paso 8.1: Arranque y GPIO

Acción:

1. Pega el código.
2. Ejecuta.
3. Abre Serial Monitor.

Resultado esperado:

* Mensaje de arranque.
* LED apagado.

Código:

```cpp
/*
  Semana 2 - FSM
  Paso 8.1: Arranque, Serial, GPIO de LED y botón.

  LED: GPIO 2
  Botón: GPIO 4 (INPUT_PULLUP). Presionado = LOW.
*/

#include <Arduino.h>

const uint8_t LED_GPIO = 2;
const uint8_t BTN_GPIO = 4;

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 2 - FSM");

  pinMode(LED_GPIO, OUTPUT);
  digitalWrite(LED_GPIO, LOW);

  pinMode(BTN_GPIO, INPUT_PULLUP);
}

void loop() {
  // En el siguiente paso agregaremos tipos de estado y logging estructurado.
}
```

Evidencia:

* Captura del Serial Monitor con el arranque.
* Captura del circuito en Wokwi.

---

### Paso 8.2: Definir estados y logging

Acción:

1. Pega el código.
2. Ejecuta.

Resultado esperado:

* Se imprime el estado actual cada 1 s.

Código:

```cpp
/*
  Paso 8.2: Estados como enum class y logging del estado actual.

  enum class State:
    - Tipado fuerte para estados.
*/

#include <Arduino.h>

const uint8_t LED_GPIO = 2;
const uint8_t BTN_GPIO = 4;

enum class State : uint8_t {
  IDLE,
  ARMED,
  RUNNING,
  WAIT_COND,
  DONE,
  ERROR
};

static State current_state = State::IDLE;
static uint32_t last_state_print_ms = 0;

const char* stateToStr(State s) {
  switch (s) {
    case State::IDLE:      return "IDLE";
    case State::ARMED:     return "ARMED";
    case State::RUNNING:   return "RUNNING";
    case State::WAIT_COND: return "WAIT_COND";
    case State::DONE:      return "DONE";
    case State::ERROR:     return "ERROR";
    default:               return "UNKNOWN";
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 2 - FSM");

  pinMode(LED_GPIO, OUTPUT);
  digitalWrite(LED_GPIO, LOW);

  pinMode(BTN_GPIO, INPUT_PULLUP);
}

void loop() {
  uint32_t now_ms = millis();

  if ((now_ms - last_state_print_ms) >= 1000) {
    last_state_print_ms = now_ms;
    Serial.print("STATE=");
    Serial.println(stateToStr(current_state));
  }
}
```

Evidencia:

* Captura del Serial Monitor mostrando `STATE=IDLE` repetido.

---

### Paso 8.3: Lectura del botón con debounce y detección de pulsación corta/larga

Acción:

1. Pega el código.
2. Ejecuta.
3. Presiona el botón en Wokwi.

Resultado esperado:

* En Serial Monitor aparecen eventos `BTN_SHORT` y `BTN_LONG`.

Código:

```cpp
/*
  Paso 8.3: Debounce y detección de pulsación.

  INPUT_PULLUP:
    - Sin presionar: HIGH
    - Presionado: LOW

  Se implementa debounce por tiempo y detección de duración:
    - Short: 50 ms a 600 ms
    - Long:  800 ms o más

  Tipos:
    - uint32_t para tiempos de millis()
    - bool para estados lógicos de lectura
*/

#include <Arduino.h>

const uint8_t LED_GPIO = 2;
const uint8_t BTN_GPIO = 4;

enum class State : uint8_t { IDLE, ARMED, RUNNING, WAIT_COND, DONE, ERROR };
static State current_state = State::IDLE;

const char* stateToStr(State s) {
  switch (s) {
    case State::IDLE:      return "IDLE";
    case State::ARMED:     return "ARMED";
    case State::RUNNING:   return "RUNNING";
    case State::WAIT_COND: return "WAIT_COND";
    case State::DONE:      return "DONE";
    case State::ERROR:     return "ERROR";
    default:               return "UNKNOWN";
  }
}

enum class Event : uint8_t {
  NONE,
  EVT_BTN_SHORT,
  EVT_BTN_LONG,
  EVT_TIMEOUT,
  EVT_FAULT
};

const char* eventToStr(Event e) {
  switch (e) {
    case Event::EVT_BTN_SHORT: return "BTN_SHORT";
    case Event::EVT_BTN_LONG:  return "BTN_LONG";
    case Event::EVT_TIMEOUT:   return "TIMEOUT";
    case Event::EVT_FAULT:     return "FAULT";
    case Event::NONE:          return "NONE";
    default:                   return "UNKNOWN";
  }
}

static uint32_t last_state_print_ms = 0;

// Debounce
static bool btn_stable_level = HIGH;
static bool btn_last_raw_level = HIGH;
static uint32_t btn_last_change_ms = 0;
static const uint32_t DEBOUNCE_MS = 30;

// Detección de duración
static bool btn_is_pressed = false;
static uint32_t btn_press_start_ms = 0;
static const uint32_t SHORT_MIN_MS = 50;
static const uint32_t SHORT_MAX_MS = 600;
static const uint32_t LONG_MIN_MS  = 800;

Event readButtonEvent(uint32_t now_ms) {
  bool raw_level = digitalRead(BTN_GPIO);

  if (raw_level != btn_last_raw_level) {
    btn_last_raw_level = raw_level;
    btn_last_change_ms = now_ms;
  }

  if ((now_ms - btn_last_change_ms) >= DEBOUNCE_MS) {
    if (btn_stable_level != raw_level) {
      btn_stable_level = raw_level;

      // Transición estable detectada
      if (btn_stable_level == LOW) {
        // Presionado
        btn_is_pressed = true;
        btn_press_start_ms = now_ms;
      } else {
        // Liberado
        if (btn_is_pressed) {
          btn_is_pressed = false;
          uint32_t press_ms = now_ms - btn_press_start_ms;

          if (press_ms >= LONG_MIN_MS) {
            return Event::EVT_BTN_LONG;
          }
          if (press_ms >= SHORT_MIN_MS && press_ms <= SHORT_MAX_MS) {
            return Event::EVT_BTN_SHORT;
          }
        }
      }
    }
  }

  return Event::NONE;
}

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 2 - FSM");

  pinMode(LED_GPIO, OUTPUT);
  digitalWrite(LED_GPIO, LOW);

  pinMode(BTN_GPIO, INPUT_PULLUP);
}

void loop() {
  uint32_t now_ms = millis();

  if ((now_ms - last_state_print_ms) >= 1000) {
    last_state_print_ms = now_ms;
    Serial.print("STATE=");
    Serial.println(stateToStr(current_state));
  }

  Event e = readButtonEvent(now_ms);
  if (e != Event::NONE) {
    Serial.print("EVENT=");
    Serial.println(eventToStr(e));
  }
}
```

Evidencia:

* Captura del Serial Monitor mostrando al menos un `EVENT=BTN_SHORT` y un `EVENT=BTN_LONG`.

---

### Paso 8.4: Implementar la FSM con `updateFsm` y transiciones

Acción:

1. Pega el código.
2. Ejecuta.
3. Provoca transiciones con el botón.

Resultado esperado:

* El Serial Monitor imprime transiciones en formato `TRANSITION: ORIGEN --EVENTO--> DESTINO`.
* La FSM cambia de estado realmente.

Código:

```cpp
/*
  Paso 8.4: FSM completa con updateFsm.

  Diseño:
    - readButtonEvent genera eventos.
    - updateFsm consume eventos y produce transiciones.
    - El cambio de estado se registra con logging consistente.
*/

#include <Arduino.h>

const uint8_t LED_GPIO = 2;
const uint8_t BTN_GPIO = 4;

enum class State : uint8_t { IDLE, ARMED, RUNNING, WAIT_COND, DONE, ERROR };

enum class Event : uint8_t {
  NONE,
  EVT_BTN_SHORT,
  EVT_BTN_LONG,
  EVT_TIMEOUT,
  EVT_FAULT
};

const char* stateToStr(State s) {
  switch (s) {
    case State::IDLE:      return "IDLE";
    case State::ARMED:     return "ARMED";
    case State::RUNNING:   return "RUNNING";
    case State::WAIT_COND: return "WAIT_COND";
    case State::DONE:      return "DONE";
    case State::ERROR:     return "ERROR";
    default:               return "UNKNOWN";
  }
}

const char* eventToStr(Event e) {
  switch (e) {
    case Event::EVT_BTN_SHORT: return "BTN_SHORT";
    case Event::EVT_BTN_LONG:  return "BTN_LONG";
    case Event::EVT_TIMEOUT:   return "TIMEOUT";
    case Event::EVT_FAULT:     return "FAULT";
    case Event::NONE:          return "NONE";
    default:                   return "UNKNOWN";
  }
}

static State current_state = State::IDLE;
static uint32_t last_state_print_ms = 0;

// Debounce
static bool btn_stable_level = HIGH;
static bool btn_last_raw_level = HIGH;
static uint32_t btn_last_change_ms = 0;
static const uint32_t DEBOUNCE_MS = 30;

// Duración
static bool btn_is_pressed = false;
static uint32_t btn_press_start_ms = 0;
static const uint32_t SHORT_MIN_MS = 50;
static const uint32_t SHORT_MAX_MS = 600;
static const uint32_t LONG_MIN_MS  = 800;

// Temporizadores por estado
static uint32_t state_enter_ms = 0;
static const uint32_t RUNNING_MS   = 2000;
static const uint32_t WAIT_COND_MS = 1500;

void logTransition(State from, Event e, State to) {
  Serial.print("TRANSITION: ");
  Serial.print(stateToStr(from));
  Serial.print(" --");
  Serial.print(eventToStr(e));
  Serial.print("--> ");
  Serial.println(stateToStr(to));
}

void enterState(State next, uint32_t now_ms) {
  current_state = next;
  state_enter_ms = now_ms;
  Serial.print("ENTER_STATE: ");
  Serial.println(stateToStr(current_state));
}

Event readButtonEvent(uint32_t now_ms) {
  bool raw_level = digitalRead(BTN_GPIO);

  if (raw_level != btn_last_raw_level) {
    btn_last_raw_level = raw_level;
    btn_last_change_ms = now_ms;
  }

  if ((now_ms - btn_last_change_ms) >= DEBOUNCE_MS) {
    if (btn_stable_level != raw_level) {
      btn_stable_level = raw_level;

      if (btn_stable_level == LOW) {
        btn_is_pressed = true;
        btn_press_start_ms = now_ms;
      } else {
        if (btn_is_pressed) {
          btn_is_pressed = false;
          uint32_t press_ms = now_ms - btn_press_start_ms;

          if (press_ms >= LONG_MIN_MS) {
            return Event::EVT_BTN_LONG;
          }
          if (press_ms >= SHORT_MIN_MS && press_ms <= SHORT_MAX_MS) {
            return Event::EVT_BTN_SHORT;
          }
        }
      }
    }
  }

  return Event::NONE;
}

Event readTimeoutEvent(uint32_t now_ms) {
  switch (current_state) {
    case State::RUNNING:
      if ((now_ms - state_enter_ms) >= RUNNING_MS) return Event::EVT_TIMEOUT;
      break;
    case State::WAIT_COND:
      if ((now_ms - state_enter_ms) >= WAIT_COND_MS) return Event::EVT_TIMEOUT;
      break;
    default:
      break;
  }
  return Event::NONE;
}

void updateFsm(Event e, uint32_t now_ms) {
  if (e == Event::NONE) return;

  State from = current_state;
  State to = current_state;

  switch (current_state) {
    case State::IDLE:
      if (e == Event::EVT_BTN_SHORT) to = State::ARMED;
      break;

    case State::ARMED:
      if (e == Event::EVT_BTN_SHORT) to = State::RUNNING;
      else if (e == Event::EVT_BTN_LONG) to = State::IDLE;
      break;

    case State::RUNNING:
      if (e == Event::EVT_TIMEOUT) to = State::WAIT_COND;
      else if (e == Event::EVT_BTN_LONG) to = State::ERROR;
      break;

    case State::WAIT_COND:
      if (e == Event::EVT_TIMEOUT) to = State::DONE;
      break;

    case State::DONE:
      if (e == Event::EVT_BTN_SHORT) to = State::IDLE;
      break;

    case State::ERROR:
      if (e == Event::EVT_BTN_SHORT) to = State::IDLE;
      break;
  }

  if (to != from) {
    logTransition(from, e, to);
    enterState(to, now_ms);
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 2 - FSM");

  pinMode(LED_GPIO, OUTPUT);
  digitalWrite(LED_GPIO, LOW);

  pinMode(BTN_GPIO, INPUT_PULLUP);

  enterState(State::IDLE, millis());
}

void loop() {
  uint32_t now_ms = millis();

  if ((now_ms - last_state_print_ms) >= 1000) {
    last_state_print_ms = now_ms;
    Serial.print("STATE=");
    Serial.println(stateToStr(current_state));
  }

  Event e_btn = readButtonEvent(now_ms);
  if (e_btn != Event::NONE) {
    Serial.print("EVENT=");
    Serial.println(eventToStr(e_btn));
    updateFsm(e_btn, now_ms);
  }

  Event e_tmo = readTimeoutEvent(now_ms);
  if (e_tmo != Event::NONE) {
    Serial.print("EVENT=");
    Serial.println(eventToStr(e_tmo));
    updateFsm(e_tmo, now_ms);
  }

  // Acciones por estado se agregan en el siguiente paso.
}
```

Evidencia:

* Captura del Serial Monitor mostrando al menos 3 transiciones.
* Registro en el reporte: qué acción realizaste para causar cada transición.

---

### Paso 8.5: Acciones por estado y evidencia de comportamiento real

Acción:

1. Pega el código.
2. Ejecuta.
3. Verifica que el LED cambia de patrón según el estado.

Patrón del LED por estado:

* IDLE: apagado.
* ARMED: parpadeo lento.
* RUNNING: encendido fijo.
* WAIT_COND: parpadeo rápido.
* DONE: 2 destellos rápidos y queda apagado.
* ERROR: parpadeo doble repetitivo.

Código:

```cpp
/*
  Paso 8.5: Acciones por estado.

  Diseño:
    - La FSM decide el estado.
    - Una capa de "actuación" implementa el comportamiento observable.

  Importante:
    - Las acciones se ejecutan sin bloquear el loop.
*/

#include <Arduino.h>

const uint8_t LED_GPIO = 2;
const uint8_t BTN_GPIO = 4;

enum class State : uint8_t { IDLE, ARMED, RUNNING, WAIT_COND, DONE, ERROR };

enum class Event : uint8_t { NONE, EVT_BTN_SHORT, EVT_BTN_LONG, EVT_TIMEOUT, EVT_FAULT };

const char* stateToStr(State s) {
  switch (s) {
    case State::IDLE:      return "IDLE";
    case State::ARMED:     return "ARMED";
    case State::RUNNING:   return "RUNNING";
    case State::WAIT_COND: return "WAIT_COND";
    case State::DONE:      return "DONE";
    case State::ERROR:     return "ERROR";
    default:               return "UNKNOWN";
  }
}

const char* eventToStr(Event e) {
  switch (e) {
    case Event::EVT_BTN_SHORT: return "BTN_SHORT";
    case Event::EVT_BTN_LONG:  return "BTN_LONG";
    case Event::EVT_TIMEOUT:   return "TIMEOUT";
    case Event::EVT_FAULT:     return "FAULT";
    case Event::NONE:          return "NONE";
    default:                   return "UNKNOWN";
  }
}

static State current_state = State::IDLE;
static uint32_t last_state_print_ms = 0;

// Debounce
static bool btn_stable_level = HIGH;
static bool btn_last_raw_level = HIGH;
static uint32_t btn_last_change_ms = 0;
static const uint32_t DEBOUNCE_MS = 30;

// Duración
static bool btn_is_pressed = false;
static uint32_t btn_press_start_ms = 0;
static const uint32_t SHORT_MIN_MS = 50;
static const uint32_t SHORT_MAX_MS = 600;
static const uint32_t LONG_MIN_MS  = 800;

// Temporizadores por estado
static uint32_t state_enter_ms = 0;
static const uint32_t RUNNING_MS   = 2000;
static const uint32_t WAIT_COND_MS = 1500;

// Señales para patrones
static uint32_t led_pattern_last_ms = 0;
static bool led_level = false;

void logTransition(State from, Event e, State to) {
  Serial.print("TRANSITION: ");
  Serial.print(stateToStr(from));
  Serial.print(" --");
  Serial.print(eventToStr(e));
  Serial.print("--> ");
  Serial.println(stateToStr(to));
}

void enterState(State next, uint32_t now_ms) {
  current_state = next;
  state_enter_ms = now_ms;
  led_pattern_last_ms = now_ms;
  led_level = false;

  Serial.print("ENTER_STATE: ");
  Serial.println(stateToStr(current_state));
}

Event readButtonEvent(uint32_t now_ms) {
  bool raw_level = digitalRead(BTN_GPIO);

  if (raw_level != btn_last_raw_level) {
    btn_last_raw_level = raw_level;
    btn_last_change_ms = now_ms;
  }

  if ((now_ms - btn_last_change_ms) >= DEBOUNCE_MS) {
    if (btn_stable_level != raw_level) {
      btn_stable_level = raw_level;

      if (btn_stable_level == LOW) {
        btn_is_pressed = true;
        btn_press_start_ms = now_ms;
      } else {
        if (btn_is_pressed) {
          btn_is_pressed = false;
          uint32_t press_ms = now_ms - btn_press_start_ms;

          if (press_ms >= LONG_MIN_MS) return Event::EVT_BTN_LONG;
          if (press_ms >= SHORT_MIN_MS && press_ms <= SHORT_MAX_MS) return Event::EVT_BTN_SHORT;
        }
      }
    }
  }

  return Event::NONE;
}

Event readTimeoutEvent(uint32_t now_ms) {
  switch (current_state) {
    case State::RUNNING:
      if ((now_ms - state_enter_ms) >= RUNNING_MS) return Event::EVT_TIMEOUT;
      break;
    case State::WAIT_COND:
      if ((now_ms - state_enter_ms) >= WAIT_COND_MS) return Event::EVT_TIMEOUT;
      break;
    default:
      break;
  }
  return Event::NONE;
}

void updateFsm(Event e, uint32_t now_ms) {
  if (e == Event::NONE) return;

  State from = current_state;
  State to = current_state;

  switch (current_state) {
    case State::IDLE:
      if (e == Event::EVT_BTN_SHORT) to = State::ARMED;
      break;

    case State::ARMED:
      if (e == Event::EVT_BTN_SHORT) to = State::RUNNING;
      else if (e == Event::EVT_BTN_LONG) to = State::IDLE;
      break;

    case State::RUNNING:
      if (e == Event::EVT_TIMEOUT) to = State::WAIT_COND;
      else if (e == Event::EVT_BTN_LONG) to = State::ERROR;
      break;

    case State::WAIT_COND:
      if (e == Event::EVT_TIMEOUT) to = State::DONE;
      break;

    case State::DONE:
      if (e == Event::EVT_BTN_SHORT) to = State::IDLE;
      break;

    case State::ERROR:
      if (e == Event::EVT_BTN_SHORT) to = State::IDLE;
      break;
  }

  if (to != from) {
    logTransition(from, e, to);
    enterState(to, now_ms);
  }
}

void setLed(bool on) {
  digitalWrite(LED_GPIO, on ? HIGH : LOW);
}

void applyStateActions(uint32_t now_ms) {
  switch (current_state) {
    case State::IDLE:
      setLed(false);
      break;

    case State::ARMED: {
      // Parpadeo lento 500 ms
      if ((now_ms - led_pattern_last_ms) >= 500) {
        led_pattern_last_ms = now_ms;
        led_level = !led_level;
        setLed(led_level);
      }
      break;
    }

    case State::RUNNING:
      setLed(true);
      break;

    case State::WAIT_COND: {
      // Parpadeo rápido 150 ms
      if ((now_ms - led_pattern_last_ms) >= 150) {
        led_pattern_last_ms = now_ms;
        led_level = !led_level;
        setLed(led_level);
      }
      break;
    }

    case State::DONE: {
      // Dos destellos rápidos al entrar a DONE y luego apagado.
      // Se usa el tiempo relativo a la entrada al estado.
      uint32_t t = now_ms - state_enter_ms;
      if (t < 100) setLed(true);
      else if (t < 200) setLed(false);
      else if (t < 300) setLed(true);
      else if (t < 400) setLed(false);
      else setLed(false);
      break;
    }

    case State::ERROR: {
      // Patrón doble: ON 100, OFF 100, ON 100, OFF 700 (ciclo 1000)
      uint32_t t = (now_ms - state_enter_ms) % 1000;
      if (t < 100) setLed(true);
      else if (t < 200) setLed(false);
      else if (t < 300) setLed(true);
      else if (t < 1000) setLed(false);
      break;
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 2 - FSM");

  pinMode(LED_GPIO, OUTPUT);
  setLed(false);

  pinMode(BTN_GPIO, INPUT_PULLUP);

  enterState(State::IDLE, millis());
}

void loop() {
  uint32_t now_ms = millis();

  if ((now_ms - last_state_print_ms) >= 1000) {
    last_state_print_ms = now_ms;
    Serial.print("STATE=");
    Serial.println(stateToStr(current_state));
  }

  Event e_btn = readButtonEvent(now_ms);
  if (e_btn != Event::NONE) {
    Serial.print("EVENT=");
    Serial.println(eventToStr(e_btn));
    updateFsm(e_btn, now_ms);
  }

  Event e_tmo = readTimeoutEvent(now_ms);
  if (e_tmo != Event::NONE) {
    Serial.print("EVENT=");
    Serial.println(eventToStr(e_tmo));
    updateFsm(e_tmo, now_ms);
  }

  applyStateActions(now_ms);
}
```

Evidencia:

* Captura del Serial Monitor mostrando al menos 5 transiciones.
* Captura/nota de que el patrón del LED cambia por estado.

---

## 9) Pruebas obligatorias

Ejecuta y documenta un plan mínimo de pruebas. Debe quedar en tu bitácora del reporte:

1. IDLE -> ARMED con pulsación corta.
2. ARMED -> RUNNING con pulsación corta.
3. RUNNING -> WAIT_COND por timeout.
4. WAIT_COND -> DONE por timeout.
5. DONE -> IDLE con pulsación corta.
6. RUNNING -> ERROR con pulsación larga.
7. ERROR -> IDLE con pulsación corta.
8. ARMED -> IDLE con pulsación larga.

---

## 10) Reflejo en el proyecto

Incluye en la bitácora de equipo una FSM de tu etapa del proyecto en dos formatos:

* Tabla o diagrama con estados, transiciones y eventos.
* Código base reutilizable: una función `updateFsm` y una función de acciones.

---

## 11) Depuración con IA (obligatorio)

Documenta dos casos reales. En cada caso incluye:

* Error exacto copiado.
* Prompt enviado a la IA.
* Respuesta de la IA.
* Cambio aplicado.
* Evidencia de validación: compila y ejecuta, más el log esperado.

Sugerencias de fallas inducidas:

* Romper el `switch` de estados omitiendo un `case` y observar comportamiento.
* Cambiar un tipo (`uint32_t` a `int`) y analizar consecuencias en comparaciones de tiempo.

Declaración de uso de IA:

* Herramienta utilizada.
* Propósito.
* Qué se validó.
* Evidencia de validación.

---

## 12) Preguntas obligatorias para el reporte

1. Define FSM usando términos: estado, evento, transición, acción.
2. Diferencia evento vs estado con un ejemplo de tu ejecución.
3. Justifica por qué `enum class` es preferible a constantes sueltas para estados.
4. Justifica el uso de `uint32_t` para `millis()` y comparación por diferencia.
5. Identifica la función que implementa la lógica de transición y explica su contrato.
6. Explica cómo garantizas que el programa es no bloqueante.
7. Explica cómo verificas que la FSM transita realmente y no solo imprime texto.
8. Adjunta tu tabla/diagrama y demuestra que coincide con el código.

---

## 13) Checklist final

* Encabezado completo del reporte.
* Enlace Wokwi.
* Circuito y capturas.
* Logs con estados y transiciones.
* FSM en tabla/diagrama.
* Plan de pruebas documentado.
* Referencias APA cuando aplique.
* Declaración de uso de IA.


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)