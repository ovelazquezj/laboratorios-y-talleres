# Semana 1 – Funciones

Laboratorio 1: Implementación incremental de funciones con Arduino IDE, ESP32 y Wokwi

## 1) Objetivo técnico

Implementar un programa embebido que:

* Inicializa comunicación serial.
* Configura un GPIO como salida para un LED.
* Alterna el estado del LED de manera periódica usando temporización no bloqueante basada en `millis()`.
* Reporta el estado por serial con un formato consistente.

El objetivo didáctico es aprender a:

* Definir funciones con nombre, parámetros y tipo de retorno correctos.
* Elegir tipos de datos adecuados para variables de configuración y estado.
* Validar cada incremento por compilación y ejecución, generando evidencia para un reporte técnico.

---

## 2) Reporte

Tu reporte debe iniciar con:

* Nombre completo
* Número de alumno
* Semana–Tema: Semana 1 – Funciones
* Grupo
* Fecha

Tu reporte debe incluir:

* Evidencias de cada etapa.
* Respuestas a las preguntas de la sección 12.
* Referencias en formato APA cuando uses fuentes externas.
* Declaración de uso de IA con el formato de la sección 11.

---

## 3) Documentación en línea

Herramientas:

* Arduino IDE 2
  [https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing](https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing)
* Soporte ESP32 en Arduino IDE (Arduino-ESP32 / Espressif)
  [https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
* Wokwi ESP32
  [https://docs.wokwi.com/guides/esp32](https://docs.wokwi.com/guides/esp32)

Referencia técnica usada en este laboratorio:

* Serial
  [https://docs.arduino.cc/language-reference/en/functions/communication/serial/](https://docs.arduino.cc/language-reference/en/functions/communication/serial/)
* Serial.println
  [https://docs.arduino.cc/language-reference/en/functions/communication/serial/println/](https://docs.arduino.cc/language-reference/en/functions/communication/serial/println/)
* pinMode
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/pinmode/](https://docs.arduino.cc/language-reference/en/functions/digital-io/pinmode/)
* digitalWrite
  [https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalwrite/](https://docs.arduino.cc/language-reference/en/functions/digital-io/digitalwrite/)
* millis
  [https://docs.arduino.cc/language-reference/en/functions/time/millis/](https://docs.arduino.cc/language-reference/en/functions/time/millis/)
* Patrón no bloqueante (Blink Without Delay)
  [https://www.arduino.cc/en/Tutorial/BlinkWithoutDelay](https://www.arduino.cc/en/Tutorial/BlinkWithoutDelay)

Refuerzo C++:

* [https://www.w3schools.com/cpp/default.asp](https://www.w3schools.com/cpp/default.asp)

---

## 4) Evidencias mínimas

Adjunta al reporte:

E1. Captura de Arduino IDE abierto
E2. Captura de compilación exitosa en Arduino IDE
E3. Captura del soporte ESP32 instalado en Boards Manager
E4. Enlace del proyecto Wokwi o capturas mostrando la simulación corriendo
E5. Captura del monitor serial con al menos 6 eventos consecutivos reportados
E6. Dos casos de depuración con IA documentados y validados

---

## 5) Etapa 1: Arduino IDE 2

1. Instala Arduino IDE 2 desde la guía oficial.
2. Abre el IDE.
3. Crea un sketch nuevo.
4. Compila el sketch.

Criterio de aceptación:

* Compila sin errores.

Evidencias:

* E1 y E2.

---

## 6) Etapa 2: Soporte ESP32 en Arduino IDE

1. Abre Boards Manager.
2. Instala el paquete de Espressif para ESP32 siguiendo el procedimiento oficial.
3. Verifica que aparece como instalado.

Criterio de aceptación:

* El paquete ESP32 aparece instalado.

Evidencia:

* E3.

---

## 7) Etapa 3: Proyecto Wokwi y circuito del LED

1. Crea un proyecto nuevo de ESP32 en Wokwi.
2. Abre el diagrama del circuito.
3. Agrega un LED y una resistencia.
4. Conecta:

   * Ánodo del LED al GPIO 2
   * Cátodo del LED a GND
   * Resistencia en serie con el LED

Criterio de aceptación:

* La simulación ejecuta sin errores.

Evidencia:

* E4.

---

## 8) Etapa 4: Implementación incremental guiada con código

Regla de trabajo:

* En cada paso vas a reemplazar tu archivo `semana1-funciones.ino` por el bloque completo indicado.
* Después de pegar el código, compila y ejecuta en Wokwi.
* No avances si no obtienes el resultado esperado.
* Registra evidencia del resultado en tu reporte.

### Tipos de datos que usaremos

* `uint8_t` para pines GPIO: un GPIO es un identificador pequeño sin signo; `uint8_t` ocupa 1 byte y representa 0–255.
* `uint32_t` para tiempo en milisegundos: `millis()` devuelve un entero sin signo con rango amplio; `uint32_t` es compatible con comparaciones por diferencia.
* `bool` para estado lógico: un estado encendido/apagado es binario; `bool` expresa intención.

---

### Paso 8.1: Estructura mínima con `setup()` y `loop()`

Acción:

1. Reemplaza `semana1-funciones.ino` con este código.
2. Ejecuta la simulación.
3. Abre el monitor serial.

Resultado esperado:

* Mensaje de arranque aparece una sola vez.

Evidencia:

* Captura del monitor serial mostrando el mensaje.

Código:

```cpp
/*
  Semana 1 - Funciones
  Paso 8.1: Estructura mínima y verificación de Serial.

  setup():
    - Se ejecuta una sola vez al inicio.
  loop():
    - Se ejecuta de forma repetitiva.
*/

void setup() {
  // Inicializa la interfaz serial para telemetría y depuración.
  Serial.begin(115200);

  // Mensaje único de arranque para confirmar que setup() se ejecutó.
  Serial.println("BOOT: Semana 1 - Funciones");
}

void loop() {
  // Ciclo principal aún vacío.
  // En los siguientes pasos agregaremos temporización y lógica.
}
```

---

### Paso 8.2: Configuración y variables de estado

Acción:

1. Reemplaza `semana1-funciones.ino` con este código.
2. Ejecuta y confirma que sigue apareciendo el mensaje de arranque.

Resultado esperado:

* Compila y ejecuta.
* Mensaje de arranque aparece una sola vez.

Evidencia:

* Captura del código mostrando constantes y variables globales.

Código:

```cpp
/*
  Paso 8.2: Configuración y variables de estado.

  Constantes:
    LED_GPIO: pin donde está conectado el LED.
    PERIOD_MS: periodo de alternancia en ms.

  Variables de estado:
    led_state: estado lógico actual del LED.
    last_toggle_ms: marca de tiempo del último cambio.
*/

// Pin de salida. Tipo: uint8_t porque un GPIO es un identificador pequeño sin signo.
const uint8_t LED_GPIO = 2;

// Periodo en ms. Tipo: uint32_t porque se compara con millis() y puede crecer mucho.
const uint32_t PERIOD_MS = 500;

// Estado lógico actual. Tipo: bool porque es binario.
bool led_state = false;

// Marca de tiempo del último cambio. Tipo: uint32_t por compatibilidad con millis().
uint32_t last_toggle_ms = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 1 - Funciones");
}

void loop() {
  // Aún no usamos estas variables.
  // En el siguiente paso configuraremos el GPIO y validaremos el estado inicial.
}
```

---

### Paso 8.3: Configurar GPIO y estado inicial del LED

Acción:

1. Reemplaza `semana1-funciones.ino` con este código.
2. Ejecuta la simulación.
3. Observa el LED en el diagrama.

Resultado esperado:

* El LED inicia apagado y se mantiene apagado.

Evidencia:

* Captura del diagrama corriendo con el LED apagado al arranque.

Código:

```cpp
/*
  Paso 8.3: Configuración de GPIO para el LED.

  pinMode(LED_GPIO, OUTPUT):
    - Configura el pin como salida.
  digitalWrite(LED_GPIO, LOW):
    - Fuerza un estado inicial apagado.
*/

const uint8_t LED_GPIO = 2;
const uint32_t PERIOD_MS = 500;

bool led_state = false;
uint32_t last_toggle_ms = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 1 - Funciones");

  // Configura el GPIO del LED como salida.
  pinMode(LED_GPIO, OUTPUT);

  // Estado inicial apagado.
  digitalWrite(LED_GPIO, LOW);
}

void loop() {
  // En el siguiente paso haremos alternancia periódica con millis().
}
```

---

### Paso 8.4: Alternancia periódica no bloqueante con `millis()`

Acción:

1. Reemplaza `semana1-funciones.ino` con este código.
2. Ejecuta la simulación.
3. Abre el monitor serial y observa los eventos.

Resultado esperado:

* El LED alterna cada 500 ms.
* El monitor serial reporta eventos con `LED_STATE=ON` y `LED_STATE=OFF`.

Evidencia:

* Captura del monitor serial mostrando al menos 6 eventos consecutivos.

Código:

```cpp
/*
  Paso 8.4: Temporización no bloqueante.

  now_ms = millis():
    - Tiempo actual desde el arranque en milisegundos.

  Criterio:
    - Si (now_ms - last_toggle_ms) >= PERIOD_MS, entonces ocurrió un "evento" de tiempo.
    - Este patrón evita pausas bloqueantes y permite que loop() siga ejecutándose.

  Reporte:
    - Se imprime un mensaje por serial cada vez que ocurre el evento.
*/

const uint8_t LED_GPIO = 2;
const uint32_t PERIOD_MS = 500;

bool led_state = false;
uint32_t last_toggle_ms = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("BOOT: Semana 1 - Funciones");

  pinMode(LED_GPIO, OUTPUT);
  digitalWrite(LED_GPIO, LOW);
}

void loop() {
  uint32_t now_ms = millis();

  // Verifica si ya transcurrió el periodo.
  if ((now_ms - last_toggle_ms) >= PERIOD_MS) {
    last_toggle_ms = now_ms;

    // Alterna el estado lógico.
    led_state = !led_state;

    // Aplica el estado al GPIO.
    digitalWrite(LED_GPIO, led_state ? HIGH : LOW);

    // Reporta por serial con formato consistente.
    Serial.print("LED_STATE=");
    Serial.println(led_state ? "ON" : "OFF");
  }
}
```

---

### Paso 8.5: Refactorización a funciones con firmas técnicas

Meta:

* Mantener `setup()` y `loop()` como funciones estándar.
* Extraer responsabilidades a funciones auxiliares con parámetros y tipo de retorno correctos.

Acción:

1. Reemplaza `semana1-funciones.ino` con este código.
2. Ejecuta la simulación.
3. Verifica que el comportamiento sea el mismo que en el Paso 8.4.

Resultado esperado:

* Misma alternancia del LED.
* Misma telemetría por serial.

Evidencia:

* Captura del monitor serial mostrando al menos 6 eventos consecutivos.
* Captura del código donde se ve la lista de funciones.

Código:

```cpp
/*
  Paso 8.5: Refactorización a funciones.

  Funciones auxiliares:
    1) initSerial(baud) -> void
    2) initLedGpio(gpio) -> void
    3) computeNextState(current_state) -> bool
    4) applyStateAndReport(gpio, state) -> void
*/

const uint8_t LED_GPIO = 2;
const uint32_t PERIOD_MS = 500;

bool led_state = false;
uint32_t last_toggle_ms = 0;

void initSerial(uint32_t baud) {
  Serial.begin(baud);
  Serial.println("BOOT: Semana 1 - Funciones");
}

void initLedGpio(uint8_t gpio) {
  pinMode(gpio, OUTPUT);
  digitalWrite(gpio, LOW);
}

bool computeNextState(bool current_state) {
  return !current_state;
}

void applyStateAndReport(uint8_t gpio, bool state) {
  digitalWrite(gpio, state ? HIGH : LOW);

  Serial.print("LED_STATE=");
  Serial.println(state ? "ON" : "OFF");
}

void setup() {
  initSerial(115200);
  initLedGpio(LED_GPIO);
}

void loop() {
  uint32_t now_ms = millis();

  if ((now_ms - last_toggle_ms) >= PERIOD_MS) {
    last_toggle_ms = now_ms;

    led_state = computeNextState(led_state);
    applyStateAndReport(LED_GPIO, led_state);
  }
}
```

---

### Paso 8.6: Cambio controlado para evidencia adicional

Acción:

1. Cambia `PERIOD_MS` a 200.
2. Ejecuta de nuevo.

Resultado esperado:

* Aumenta la frecuencia de eventos en el monitor serial.

Evidencia:

* Captura del monitor serial donde se aprecie el cambio de frecuencia.

---

## 9) Extensión opcional en hardware

Si tienes placa ESP32-S3:

1. Selecciona una placa ESP32-S3 en el menú de placas del Arduino IDE.
2. Selecciona el puerto serial.
3. Carga el sketch.
4. Captura el monitor serial en Arduino IDE.

---

## 10) Checklist de evidencia para la Etapa 4

Incluye en el reporte:

* Captura del monitor serial del Paso 8.1.
* Captura del código del Paso 8.2.
* Captura del diagrama del Paso 8.3.
* Captura del monitor serial del Paso 8.4 con al menos 6 eventos.
* Captura del monitor serial del Paso 8.5 con al menos 6 eventos.
* Captura del monitor serial del Paso 8.6.

---

## 11) Depuración con IA: 2 casos con validación

Incluye dos casos completos. Cada caso debe contener:

* Error exacto copiado
* Prompt enviado a la IA
* Respuesta de la IA
* Cambio aplicado
* Evidencia de compilación y ejecución correcta

Caso 1: Error de sintaxis

1. Introduce un error de sintaxis en una línea.
2. Compila para obtener el error.
3. Usa IA para identificar la causa y corregir.
4. Compila y ejecuta para validar.

Caso 2: Error por firma o llamada incorrecta

1. Modifica una llamada a función para que falle por parámetros incorrectos o faltantes.
2. Compila para obtener el error.
3. Usa IA para corregir.
4. Compila y ejecuta para validar.

Formato sugerido para el reporte:

* Caso 1

  * Error:
  * Prompt:
  * Respuesta IA:
  * Cambio aplicado:
  * Evidencia:
* Caso 2

  * Error:
  * Prompt:
  * Respuesta IA:
  * Cambio aplicado:
  * Evidencia:

Declaración de uso de IA:

* Herramienta utilizada:
* Propósito:
* Qué se validó:
* Evidencia de validación:

---

## 12) Preguntas obligatorias para el reporte

### A) Funciones y firmas

1. Define función usando los términos: nombre, parámetros, tipo de retorno, cuerpo.
2. Explica por qué `computeNextState` retorna `bool` y no imprime por serial.
3. Enumera las funciones auxiliares del Paso 8.5 e indica sus parámetros y tipo de retorno.

### B) Tipos de datos y estado

4. Justifica el uso de `uint8_t` para el GPIO y `uint32_t` para tiempo.
5. Explica el propósito de `led_state` y por qué es `bool`.
6. Explica el propósito de `last_toggle_ms` y por qué se actualiza en el evento.

### C) Temporización no bloqueante

7. Describe el criterio exacto de decisión del evento usando `now_ms - last_toggle_ms`.
8. Describe un problema técnico que podría aparecer si usaras esperas bloqueantes en un sistema que después integrará sensores o comunicación.

### D) Evidencia y validación

9. Indica qué evidencia demuestra que tu simulación está ejecutando el programa correctamente.
10. Indica qué evidencia demuestra que el refactor a funciones no cambió el comportamiento.
11. En cada caso de IA, describe cómo verificaste la corrección sin confiar solo en la respuesta.

---

## 13) Checklist final

* Reporte con encabezado completo
* E1, E2, E3, E4, E5
* Evidencias de los pasos 8.1 a 8.6
* Dos casos de IA completos con evidencia
* Referencias APA cuando aplique
* Declaración de uso de IA


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)