/*
  Dimmer AC con RBDdimmer: 5 niveles fijos (0,25,50,75,100) por 10 s
  - Hardware típico Arduino UNO (AVR):
      D2 = entrada ZC del módulo dimmer (lo maneja la librería)
      D3 = salida de disparo TRIAC (gate)
  - Telemetría didáctica para Serial Plotter:
      zc_dbg  : pulso corto al inicio de cada semiciclo
      gate_dbg: pulso alrededor del instante de disparo (calculado a partir de PCT)
      pct     : porcentaje de potencia aplicado por RBDdimmer
*/

#include <RBDdimmer.h>

// ===================== Pines y objetos =====================
const uint8_t PIN_DIM = 3;   // Gate del TRIAC (salida)
const uint8_t PIN_ZC  = 2;   // ZC del módulo (documentativo; la librería lo usa en UNO)

dimmerLamp dimmer(PIN_DIM);  // En UNO: ZC = D2 (INT0), Gate = PIN_DIM

// ===================== Config AC y visualización =====================
// Ajusta a 50 si estás en 50 Hz:
const uint8_t  MAINS_HZ   = 60;
const uint32_t HALF_US    = (uint32_t)(1000000UL / (MAINS_HZ * 2));  // ~8333 us a 60 Hz
const uint32_t ZC_VIS_US  = 1000;   // duración del pulso "zc_dbg" (1 ms)
const uint32_t GATE_VIS_US= 2000;   // duración del pulso "gate_dbg" (2 ms)
const uint16_t SAMPLE_MS  = 10;     // muestreo para Plotter (100 Hz)

// ===================== Niveles fijos =====================
const uint8_t  LEVELS[]   = {0, 25, 50, 75, 100};
const uint8_t  N_LEVELS   = sizeof(LEVELS) / sizeof(LEVELS[0]);
const uint32_t HOLD_MS    = 10000;  // 10 s por nivel

volatile uint8_t pct      = 0;      // % de potencia actual
uint8_t  level_idx        = 0;      // índice de nivel actual
uint32_t next_level_ms    = 0;      // cuándo saltar al siguiente nivel

// ===================== Relojes didácticos =====================
uint32_t zc_t0_us         = 0;      // ancla del semiciclo actual (para zc_dbg/gate_dbg)
uint32_t last_plot_ms     = 0;      // último envío al Plotter

// ===================== Utilitarios =====================
static inline uint32_t u32_diff(uint32_t a, uint32_t b) {
  // diferencia con wrap-around (micros/millis unsigned)
  return (uint32_t)(a - b);
}

void setup() {
  Serial.begin(115200);
  delay(1500); // da tiempo a que el Plotter enganche tras el reset
  Serial.println("zc_dbg,gate_dbg,pct");

  dimmer.begin(NORMAL_MODE, ON);

  // Arranca en el primer nivel fijo
  pct = LEVELS[level_idx];
  dimmer.setPower(pct);

  // Inicializa anclas de tiempo
  zc_t0_us      = micros();
  next_level_ms = millis() + HOLD_MS;
  last_plot_ms  = millis();
}

void loop() {
  const uint32_t now_ms = millis();
  const uint32_t now_us = micros();

  // -------- 1) Escalonador: cambiar de nivel cada 10 s --------
  if ((int32_t)(now_ms - next_level_ms) >= 0) {
    level_idx = (uint8_t)((level_idx + 1) % N_LEVELS);
    pct = LEVELS[level_idx];
    dimmer.setPower(pct);
    next_level_ms = now_ms + HOLD_MS;

    // Marcador útil para ubicar los cambios en el Monitor/Plotter
    Serial.print("# Cambio de nivel -> PCT = ");
    Serial.println(pct);
  }

  // -------- 2) Reloj de semiciclos (didáctico p/ telemetría) --------
  // Si se completó el semiciclo, avanza el ancla zc_t0_us.
  // Usamos while por si el loop perdió más de un semiciclo.
  while (u32_diff(now_us, zc_t0_us) >= HALF_US) {
    zc_t0_us += HALF_US;
  }

  // zc_dbg: 1 durante ZC_VIS_US tras cada cruce por cero
  const uint32_t t_from_zc = u32_diff(now_us, zc_t0_us);
  const int zc_dbg  = (t_from_zc < ZC_VIS_US) ? 1 : 0;

  // gate_dbg: 1 durante GATE_VIS_US alrededor del instante de disparo
  // fire_delay_us -> (100 - pct)% del semiciclo: pct alto => disparo temprano
  const uint32_t fire_delay_us = (uint32_t)((100UL - pct) * HALF_US / 100UL);
  const int gate_dbg = (t_from_zc >= fire_delay_us && t_from_zc < (fire_delay_us + GATE_VIS_US)) ? 1 : 0;

  // -------- 3) Telemetría para Serial Plotter --------
  if ((uint32_t)(now_ms - last_plot_ms) >= SAMPLE_MS) {
    last_plot_ms = now_ms;
    // Formato CSV: zc_dbg,gate_dbg,pct
    Serial.print(zc_dbg);
    Serial.print(',');
    Serial.print(gate_dbg);
    Serial.print(',');
    Serial.println(pct);
  }
}
