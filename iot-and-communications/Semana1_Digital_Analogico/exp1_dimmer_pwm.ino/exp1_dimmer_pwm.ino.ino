#include <RBDdimmer.h>

// --- Pines Arduino UNO ---
#define PIN_ZC   2     // Zero-Cross -> D2 (INT0) ***OBLIGATORIO EN UNO***
#define PIN_DIM  3     // Disparo TRIAC -> D3

// En UNO/AVR el constructor recibe SOLO el pin DIM
dimmerLamp dimmer(PIN_DIM);

// --- Parámetros del fade triangular ---
const uint8_t  STEP_SIZE        = 1;      // cambio de potencia por paso (%)
const uint16_t STEP_MS          = 120;    // más alto = más lento (120 ms ≈ 12 s 0→100)
const uint16_t HOLD_TOP_MS      = 1500;   // pausa en 100%
const uint16_t HOLD_BOTTOM_MS   = 800;    // pausa en 0%

// Frecuencia de red (México 60 Hz; cambia a 50 si aplica)
const uint8_t  MAINS_HZ         = 60;
const unsigned long HALF_US     = 1000000UL / (2UL * MAINS_HZ); // ~8333 us a 60Hz

// “Anchos” visuales para graficar (no afectan al disparo real)
const unsigned long ZC_VIS_US    = 1000;  // 1 ms
const unsigned long GATE_VIS_US  = 2000;  // 2 ms
const uint16_t      SAMPLE_MS    = 10;    // 100 Hz de muestreo al Plotter

// --- Estado ---
uint8_t pct = 0;                 // 0..100 %
int8_t  dir = +1;                // +1 sube, -1 baja
unsigned long last_step_ms = 0;

// Reloj "virtual" para ZC
unsigned long zc_t0_us = 0;

// --- Utilidad: salida CSV para Plotter ---
inline void plotCSV(int zc_dbg, int gate_dbg, int pct_val) {
  Serial.print(zc_dbg);   Serial.print(',');
  Serial.print(gate_dbg); Serial.print(',');
  Serial.println(pct_val);
}

void setup() {
  Serial.begin(115200);

  // Espera a que el Plotter enganche tras el reset del UNO
  delay(1500);
  Serial.println("zc_dbg,gate_dbg,pct");   // encabezado (etiquetas)

  dimmer.begin(NORMAL_MODE, ON);
  dimmer.setPower(pct); // inicia en 0%

  zc_t0_us = micros();
  last_step_ms = millis(); // arranque de rampa
}

void loop() {
  unsigned long now_ms = millis();

  // --- Fade triangular: 0→100→0 en bucle con pausas en extremos ---
  if (now_ms - last_step_ms >= STEP_MS) {
    last_step_ms = now_ms;

    // Avanza potencia
    if (dir > 0) {
      if (pct < 100) { pct += STEP_SIZE; if (pct > 100) pct = 100; }
      if (pct == 100) { dir = -1; last_step_ms = now_ms + HOLD_TOP_MS - STEP_MS; }
    } else { // dir < 0
      if (pct > 0)   { pct -= STEP_SIZE; if (pct > 100) pct = 0; } // saturación
      if (pct == 0)  { dir = +1; last_step_ms = now_ms + HOLD_BOTTOM_MS - STEP_MS; }
    }

    dimmer.setPower(pct);
  }

  // --- Señales didácticas para el Plotter ---
  unsigned long now_us = micros();
  if (now_us - zc_t0_us >= HALF_US) {
    do { zc_t0_us += HALF_US; } while (now_us - zc_t0_us >= HALF_US);
  }

  // Tick visual de cruce por cero
  int zc_dbg = ((now_us - zc_t0_us) < ZC_VIS_US) ? 1 : 0;

  // Posición “didáctica” del disparo según % (lineal)
  unsigned long fire_delay_us = (unsigned long)((100UL - pct) * HALF_US / 100UL);
  unsigned long t_from_zc     = now_us - zc_t0_us;
  int gate_dbg = (t_from_zc >= fire_delay_us && t_from_zc < fire_delay_us + GATE_VIS_US) ? 1 : 0;

  // Enviar una línea al Plotter cada SAMPLE_MS
  static unsigned long last_plot_ms = 0;
  if (millis() - last_plot_ms >= SAMPLE_MS) {
    last_plot_ms = millis();
    plotCSV(zc_dbg, gate_dbg, pct);
  }
}
