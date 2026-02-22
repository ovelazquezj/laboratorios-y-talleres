# Semana 4 — Librería de Telemetría v1 (Cápsula: “7 minutos de terror”)

## 1) Contexto

En el proyecto de recuperación de cápsula, la telemetría es el “idioma común” del sistema durante todas las etapas, todos los módulos consumen datos (altitud, temperatura) y toman decisiones con base en ellos. Si cada equipo implementa lecturas y conversiones por su cuenta, aparecen fallos típicos:

* Unidades inconsistentes (m vs km, C vs F) y decisiones incorrectas.
* Duplicación de código que se vuelve imposible de mantener.
* Cambios de sensor que rompen múltiples archivos a la vez.

Esta semana construirás la **primera librería obligatoria para todos los equipos**: **Telemetry v1**, enfocada en dos responsabilidades iniciales:

* **Altitud** con BMP280 o BMP180.
* **Temperatura** con DHT11 o DHT22.

La librería debe poder usarse igual en simulación (Wokwi) y en la tarjeta real (ESP32-S3), sin reescribir lógica.

---

## 2) Objetivo del laboratorio

Al finalizar, podrás:

1. Diseñar una librería con una **API pequeña y estable**.
2. Separar interfaz y lógica en archivos **.h/.cpp**.
3. Leer sensores reales (BMP280/BMP180 y DHT11/DHT22) desde **ESP32‑S3**.
4. Entregar telemetría en **múltiples unidades** sin duplicar conversiones en el proyecto.
5. Demostrar funcionamiento con un **sketch de prueba** y una **matriz de evidencia**.
6. Integrar la librería al proyecto de la cápsula como dependencia.

---

## 3) Materiales

### Software

* Arduino IDE o PlatformIO
* Wokwi (ESP32-S3)

### Hardware

* 1× ESP32‑S3
* Sensor de altitud: **BMP280 o BMP180** (I2C)
* Sensor de temperatura: **DHT11 o DHT22** (pin digital)
* Protoboard y cables

---

## 4) Reglas del laboratorio (se evalúan)

1. Deben existir estos archivos:

   * `Telemetry.h`
   * `Telemetry.cpp`
   * `sketch_prueba.ino`
2. La librería **no imprime por Serial**. El que imprime es el sketch de prueba.
3. Debe existir un **contrato de estado/validez**: el consumidor debe saber si puede confiar en la lectura.
4. Proceso obligatorio:

   * Primero Wokwi
   * Después hardware real
5. Evidencia obligatoria:

   * Capturas y salidas del monitor serial (formato fijo)
   * Tabla de pruebas (esperado vs observado)
   * Evidencia de integración al proyecto

---

## 5) Requerimientos funcionales

### 5.1 Altitud (BMP280/BMP180)

La librería debe retornar altitud en:

* **metros**
* **kilómetros**
* **pies**
* **millas**

### 5.2 Temperatura (DHT11/DHT22)

La librería debe retornar temperatura en:

* **Celsius**
* **Fahrenheit**
* **Kelvin**

### 5.3 Contrato mínimo

La librería debe permitir responder dos preguntas:

* ¿Inicializó bien?
* ¿La última lectura es válida?

Puedes implementarlo con:

* `status()` (enum)
* `hasValidReading()` (bool)

---

## 6) Plantillas mínimas (importantes)

Estas plantillas no son “para copiar y pegar sin pensar”. Son el mapa del terreno: muestran la forma correcta del módulo.

### 6.1 Plantilla de cabecera (`Telemetry.h`)

Crea este archivo y completa los TODO.

```cpp
#pragma once

#include <Arduino.h>

// Esta cabecera define el “contrato” de la librería.
// Si otro módulo la usa, debería poder hacerlo leyendo solo este archivo.
// Mantener el contrato pequeño evita que el proyecto se vuelva frágil.

// Librería Telemetry v1
// - Encapsula sensores (BMP + DHT)
// - Entrega magnitudes en unidades solicitadas
// - Expone contrato de validez para que el proyecto no “adivine”

class Telemetry {
public:
  // Status permite distinguir:
  // - No iniciado
  // - OK
  // - Falla al inicializar sensores
  // - Falla al leer (p. ej., NaN en DHT o lectura inválida en BMP)
  // Esta distinción sirve para depuración y evidencia.
  enum class Status : uint8_t {
    NOT_STARTED = 0,
    OK,
    SENSOR_INIT_FAIL,
    READ_FAIL
  };

  // Constructor: deja al objeto en estado “seguro” (sin lecturas válidas).
  // No inicialices hardware aquí: aún no sabes pines ni tipo de sensor.
  Telemetry();

  // begin() debe:
  // - Guardar configuración
  // - Inicializar hardware
  // - Dejar el módulo listo para llamar update() desde loop()
  //
  // useBMP280:
  // - true  -> inicializa BMP280
  // - false -> inicializa BMP180
  // dhtType: 11 o 22
  // dhtPin: GPIO para DHT
  bool begin(bool useBMP280, uint8_t dhtType, uint8_t dhtPin);

  // update() es el corazón del módulo.
  // Se llama periódicamente y actualiza lecturas internas.
  // Retorna true solo si obtuvo lecturas válidas.
  // Si falla, el consumidor NO debe usar los valores.
  bool update();

  // hasValidReading() responde: “¿Puedo confiar en los datos ahora mismo?”
  // Esto evita decisiones basadas en basura/NaN.
  bool hasValidReading() const;

  // status() da una razón rápida del estado actual.
  Status status() const;

  // Altitud (base interna: metros)
  // La librería ofrece distintas unidades para que el proyecto NO repita conversiones.
  float altitudeMeters() const;
  float altitudeKilometers() const;
  float altitudeFeet() const;
  float altitudeMiles() const;

  // Temperatura (base interna: Celsius)
  float tempC() const;
  float tempF() const;
  float tempK() const;

private:
  // Estado del módulo
  bool _started;
  bool _useBMP280;
  uint8_t _dhtType;
  uint8_t _dhtPin;

  Status _status;
  bool _valid;

  // Valores internos base (una sola fuente de verdad)
  // Guardar una sola unidad base reduce errores por conversiones repetidas.
  float _alt_m;
  float _temp_c;

  // Conversiones centralizadas
  // Estas funciones no leen sensores: solo convierten unidades.
  // Si hay un bug aquí, se corrige una vez y se arregla todo el proyecto.
  static float m_to_km(float m);
  static float m_to_ft(float m);
  static float m_to_mi(float m);

  static float c_to_f(float c);
  static float c_to_k(float c);

  // Lectura encapsulada por sensor
  // Encapsular la lectura permite cambiar librerías/sensores sin romper el resto.
  bool readAltitudeBMP(float &out_alt_m);
  bool readTempDHT(float &out_temp_c);
};
```

### 6.2 Plantilla de implementación (`Telemetry.cpp`)

Crea este archivo y completa los TODO. Observa cómo se decide validez sin “inventar” datos.

```cpp
#include "Telemetry.h"

// Este archivo contiene la implementación.
// La regla de oro: si cambias de sensor o librería, idealmente solo tocas aquí.

// Instalación de librerías (Arduino Library Manager)
// 1) Adafruit BMP280 Library (si usas BMP280)
// 2) Adafruit BMP085 Library (si usas BMP180)
// 3) DHT sensor library (Adafruit) + Adafruit Unified Sensor
//
// Nota práctica: esta semana puedes fijar una ruta oficial para la clase.
// Si el equipo usa un sensor distinto, debe documentar qué cambió.

// TODO: incluye headers de las librerías elegidas.
// #include <Wire.h>
// #include <Adafruit_BMP280.h>
// #include <Adafruit_BMP085.h>
// #include <DHT.h>

Telemetry::Telemetry()
: _started(false),
  _useBMP280(true),
  _dhtType(22),
  _dhtPin(0),
  _status(Status::NOT_STARTED),
  _valid(false),
  _alt_m(NAN),
  _temp_c(NAN) {
  // Al crear el objeto:
  // - No hay hardware inicializado.
  // - No hay lecturas válidas.
  // - Los valores base se dejan en NAN para detectar uso indebido.
}

bool Telemetry::begin(bool useBMP280, uint8_t dhtType, uint8_t dhtPin) {
  _useBMP280 = useBMP280;
  _dhtType = dhtType;
  _dhtPin = dhtPin;

  _started = true;
  _valid = false;
  _status = Status::OK;

  // 1) Inicialización del BMP
  // Aquí decides la librería concreta.
  // Puntos que deben quedar claros en tu reporte:
  // - Dirección I2C (BMP280 suele ser 0x76 o 0x77)
  // - Si tu BMP180 usa otra lib (BMP085) y cómo lo inicializas
  // Si falla, se marca SENSOR_INIT_FAIL y se aborta, porque sin altitud el sistema queda incompleto.

  bool bmpOk = true;
  // TODO: reemplaza el placeholder por inicialización real.

  // 2) Inicialización del DHT
  // Algunas librerías de DHT no “fallan” en begin(); la falla aparece al leer (devuelve NaN).
  // Aun así, aquí debes dejar el objeto listo.
  // TODO: inicializa el DHT real.

  if (!bmpOk) {
    _status = Status::SENSOR_INIT_FAIL;
    return false;
  }

  return true;
}

bool Telemetry::update() {
  if (!_started) {
    // update() sin begin() es un uso incorrecto.
    // El contrato lo marca como NOT_STARTED para que sea visible en evidencia.
    _status = Status::NOT_STARTED;
    _valid = false;
    return false;
  }

  float alt_m = NAN;
  float temp_c = NAN;

  // Se leen por separado para poder detectar cuál falló.
  // La decisión de “aceptar o rechazar” ocurre después.
  bool okAlt = readAltitudeBMP(alt_m);
  bool okTemp = readTempDHT(temp_c);

  // Contrato:
  // - Solo “acepta” lecturas cuando ambas son válidas.
  // - Si una falla, no actualiza valores internos.
  // Esto evita estados mezclados (altitud nueva con temperatura vieja).
  if (okAlt && okTemp) {
    _alt_m = alt_m;
    _temp_c = temp_c;
    _valid = true;
    _status = Status::OK;
    return true;
  }

  // Si falló una lectura:
  // - _valid = false
  // - _status = READ_FAIL
  // - se conservan los últimos valores internos (pero no deben usarse si valid=0)
  _valid = false;
  _status = Status::READ_FAIL;
  return false;
}

bool Telemetry::hasValidReading() const { return _valid; }
Telemetry::Status Telemetry::status() const { return _status; }

// Las funciones “getters” no leen sensores.
// Solo convierten/entregan los últimos valores internos.
float Telemetry::altitudeMeters() const { return _alt_m; }
float Telemetry::altitudeKilometers() const { return m_to_km(_alt_m); }
float Telemetry::altitudeFeet() const { return m_to_ft(_alt_m); }
float Telemetry::altitudeMiles() const { return m_to_mi(_alt_m); }

float Telemetry::tempC() const { return _temp_c; }
float Telemetry::tempF() const { return c_to_f(_temp_c); }
float Telemetry::tempK() const { return c_to_k(_temp_c); }

// Conversiones: pequeñas, deterministas, fáciles de probar.
float Telemetry::m_to_km(float m) { return m / 1000.0f; }
float Telemetry::m_to_ft(float m) { return m * 3.28084f; }
float Telemetry::m_to_mi(float m) { return m / 1609.344f; }

float Telemetry::c_to_f(float c) { return (c * 9.0f / 5.0f) + 32.0f; }
float Telemetry::c_to_k(float c) { return c + 273.15f; }

bool Telemetry::readAltitudeBMP(float &out_alt_m) {
  // Altitud desde presión requiere presión de referencia (nivel del mar).
  // Esta semana se usa un valor fijo para probar el flujo.
  // En el proyecto, se discute calibración/compensación y cómo afecta precisión.

  const float seaLevel_hPa = 1013.25f;

  // TODO: lee altitud con la librería BMP elegida.
  // Ejemplo típico BMP280 (Adafruit): out_alt_m = bmp280.readAltitude(seaLevel_hPa);
  // Si tu librería usa Pa en lugar de hPa, documenta la conversión.

  out_alt_m = NAN;

  // Validación mínima:
  // - Si es NaN, es lectura inválida.
  // - Si quieres, agrega un rango razonable para evitar picos absurdos.
  if (isnan(out_alt_m)) return false;
  return true;
}

bool Telemetry::readTempDHT(float &out_temp_c) {
  // DHT devuelve NaN cuando falla.
  // Si el pin está mal, si el sensor está desconectado o si el timing falla.
  // Este laboratorio exige que esa falla NO congele el sistema.

  // TODO: lee temperatura en Celsius.
  // Ejemplo típico: out_temp_c = dht.readTemperature();

  out_temp_c = NAN;

  if (isnan(out_temp_c)) return false;
  return true;
}
```

### 6.3 Plantilla de sketch de prueba (`sketch_prueba.ino`)

Este archivo genera toda la evidencia del laboratorio.

```cpp
#include <Arduino.h>
#include "Telemetry.h"

// Este sketch es un banco de pruebas.
// Su trabajo es generar evidencia clara y comparable.
// No “resuelve el proyecto”; valida que el módulo funciona y se comporta bien ante fallas.

// Ajusta estos parámetros según tu hardware.
// Si usas Wokwi, documenta los pines elegidos.
static const bool USE_BMP280 = true;   // false si usas BMP180
static const uint8_t DHT_TYPE = 22;    // 11 o 22
static const uint8_t DHT_PIN  = 6;     // elige un GPIO válido

Telemetry tel;

static void printStatus(Telemetry::Status s) {
  // Imprimir texto (y no solo números) ayuda a detectar rápidamente el tipo de falla.
  // Mantén estos labels estables para que la evidencia sea comparable.
  switch (s) {
    case Telemetry::Status::NOT_STARTED:      Serial.print("NOT_STARTED"); break;
    case Telemetry::Status::OK:               Serial.print("OK"); break;
    case Telemetry::Status::SENSOR_INIT_FAIL: Serial.print("SENSOR_INIT_FAIL"); break;
    case Telemetry::Status::READ_FAIL:        Serial.print("READ_FAIL"); break;
    default:                                  Serial.print("UNKNOWN"); break;
  }
}

void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("[TEST] start");

  // Si necesitas pines I2C específicos en tu placa, configúralos aquí.
  // Si no los configuras, algunas placas usan pines por defecto.
  // Documenta en el reporte qué pines SDA/SCL usaste.
  // Ejemplo:
  // Wire.begin(SDA_PIN, SCL_PIN);

  const bool ok = tel.begin(USE_BMP280, DHT_TYPE, DHT_PIN);

  // begin() se reporta una sola vez.
  // Si begin falla, aún puedes imprimir el status para explicar la causa.
  Serial.print("[TEST] begin ok=");
  Serial.println(ok ? 1 : 0);
}

void loop() {
  // update() debe ser llamado continuamente.
  // El contrato indica si la lectura es válida en este ciclo.
  const bool ok = tel.update();

  // Formato fijo para comparar evidencia entre equipos.
  // Mantener orden fijo simplifica revisar logs y construir tablas de pruebas.
  Serial.print("[TEST] ok=");
  Serial.print(ok ? 1 : 0);

  Serial.print(" status=");
  printStatus(tel.status());

  Serial.print(" valid=");
  Serial.print(tel.hasValidReading() ? 1 : 0);

  // Si valid=0, estas magnitudes no deben usarse para decisiones.
  // Aun así, imprimirlas ayuda a detectar si alguien está usando valores sin validar.
  Serial.print(" alt_m=");
  Serial.print(tel.altitudeMeters(), 3);

  Serial.print(" alt_km=");
  Serial.print(tel.altitudeKilometers(), 6);

  Serial.print(" alt_ft=");
  Serial.print(tel.altitudeFeet(), 2);

  Serial.print(" alt_mi=");
  Serial.print(tel.altitudeMiles(), 6);

  Serial.print(" temp_c=");
  Serial.print(tel.tempC(), 2);

  Serial.print(" temp_f=");
  Serial.print(tel.tempF(), 2);

  Serial.print(" temp_k=");
  Serial.print(tel.tempK(), 2);

  Serial.println();

  // Prueba de borde: muestreo rápido.
  // Si el sistema se congela aquí, hay bloqueos o lecturas mal manejadas.
  delay(200);
}
```

---

## 7) Actividad principal (paso a paso)

### Paso 1 — Define tu ruta de sensores

Elige y documenta:

* BMP280 o BMP180
* DHT11 o DHT22


### Paso 2 — Crea la carpeta del módulo

Crea `TelemetryV1/` con:

* `Telemetry.h`
* `Telemetry.cpp`
* `sketch_prueba.ino`

Compila desde el inicio aunque haya TODOs: la estructura correcta reduce errores de “última hora”.

### Paso 3 — Completa inicialización de sensores

En `begin()`:

* Inicializa BMP (I2C).
* Inicializa DHT.

El contrato no exige que DHT “falle en begin”; la validación ocurre en `update()`.

### Paso 4 — Implementa lecturas

En `update()`:

* Lee altitud y temperatura.
* Acepta valores solo si ambas lecturas fueron válidas.

Evita dos errores clásicos:

* Guardar NaN como si fuera dato.
* Actualizar una variable sí y la otra no (deja el sistema en un estado mezclado).

### Paso 5 — Centraliza conversiones

Implementa conversiones dentro de la librería.
Cuando el proyecto necesite “pies”, pedirá pies; cuando necesite “Kelvin”, pedirá Kelvin.

---

## 8) Pruebas obligatorias y evidencia

### Prueba 1 — Nominal

* Sensores conectados
* `begin ok=1`
* `valid=1` en lecturas
* Valores razonables

**Evidencia:** al menos 5 líneas consecutivas del monitor serial.

### Prueba 2 — Borde (estabilidad)

* Ejecuta 10 ciclos seguidos (ya lo hace `delay(200)`)
* Los valores no deben aparecer como NaN
* El sistema no debe congelarse

**Evidencia:** al menos 10 líneas consecutivas.

### Prueba 3 — Inválida (sobrevivir a falla)

Simula fallo:

* En Wokwi: desconecta el sensor o cambia configuración para forzar lectura inválida
* En físico: desconecta DHT o BMP durante unos segundos

Esperado:

* El sistema sigue corriendo e imprimiendo
* `valid=0`
* `status=READ_FAIL` (o equivalente)

**Evidencia:** al menos 5 líneas donde se observe el estado inválido.

---

## 9) Wokwi primero (obligatorio)

1. Monta el circuito ESP32‑S3 + BMP + DHT.
2. Corre pruebas 1, 2 y 3.
3. Captura:

   * Screenshot del circuito
   * Screenshot del monitor serial

---

## 10) Hardware real después (obligatorio)

1. Cablea sensores en la ESP32‑S3.
2. Repite pruebas 1, 2 y 3.
3. Captura:

   * Foto del montaje real
   * Captura del monitor serial

---

## 11) Integración al proyecto de la cápsula (obligatoria)

Crea una demostración mínima dentro del proyecto:

* `telemetry_integration_demo.ino` (o equivalente)

Debe mostrar:

* Uso de `Telemetry`
* Lectura en unidades distintas (por ejemplo: altitud en pies y temperatura en Kelvin)
* Ninguna conversión manual fuera de la librería

**Evidencia:** captura del código + salida serial corriendo desde el proyecto.

---

## 12) Entregables

1. Código

* `Telemetry.h`
* `Telemetry.cpp`
* `sketch_prueba.ino`
* `telemetry_integration_demo.ino` (o equivalente)

2. Reporte (PDF o Markdown)

* Responsabilidad en 1 frase
* API definida (funciones + contrato)
* Tabla de pruebas (esperado vs observado)
* Evidencia Wokwi
* Evidencia hardware real
* Evidencia integración al proyecto

3. Bitácora

* Qué falló
* Cómo lo resolvieron
* Decisiones tomadas

4. Video 3 minutos

* Qué problema resuelve Telemetry v1
* Cómo se usa
* Qué prueba demuestra que funciona

---

## 13) Preguntas guía (obligatorias)

1. Qué tipo de error se evita al centralizar conversiones en la librería.
2. Qué significa “contrato” en tu implementación: cómo sabe el proyecto si confiar.
3. Qué unidad base usas internamente para altitud y por qué.
4. Qué unidad base usas internamente para temperatura y por qué.
5. Qué evidencia muestra que el sistema sobrevive a falla de sensor.
6. En el proyecto de la cápsula, qué módulo se beneficiará primero de Telemetry v1.
7. Qué mejorarías para Telemetry v2 (solo ideas, sin implementarlas).

---

## 14) Checklist de evaluación

* Compila
* Wokwi: circuito + serial con pruebas 1–3
* Hardware: foto + serial con pruebas 1–3
* Contrato de validez implementado y usado
* Conversiones dentro de la librería
* Integración demostrada dentro del proyecto
* Evidencia clara y comparable


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)