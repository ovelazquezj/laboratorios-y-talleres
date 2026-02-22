#include <Wire.h>
#include <U8g2lib.h>
#include <SPI.h>
#define hal_init LMICHAL_init
#include <lmic.h>
#include <hal/hal.h>

// ---------------- OLED ----------------
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// ---------------- HC-SR04 ALIMENTADO CON 5V ----------------
#define TRIG_PIN 25 // GPIO 25 - Libre
#define ECHO_PIN 34 // GPIO 34 - Input-only
// ALIMENTACIÓN: 5V (VIN del ESP32)
// ECHO: Divisor de voltaje (1kΩ + 1.2kΩ) para reducir 5V a 2.73V
// VENTAJA: Rango completo ~2-4m

// ---------------- LoRa Pins TTGO T3 v1.6.1 ----------------
#define LORA_SCK 5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_SS 18
#define LORA_RST 14
#define LORA_DIO0 26
#define LORA_DIO1 33
#define LORA_DIO2 32

// ---------------- LoRaWAN Credenciales ChirpStack ----------------
// OTAA - Over The Air Activation
// DevEUI: 02389205358E71DB (LSB format para LMIC)
static const u1_t PROGMEM DEVEUI[8] = { 0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x02 };

// JoinEUI (AppEUI): 505246F87143FD8A (LSB format para LMIC)
static const u1_t PROGMEM APPEUI[8] = { 0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x50 };

// AppKey: 8AC583DFEEC76C81FFD19CCFE76B73BF (MSB format para LMIC)
static const u1_t PROGMEM APPKEY[16] = { 0x8A, 0xC5, 0x83, 0xDF, 0xEE, 0xC7, 0x6C, 0x81, 
                                          0xFF, 0xD1, 0x9C, 0xCF, 0xE7, 0x6B, 0x73, 0xBF };

void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

// ---------------- Variables de estado ----------------
static osjob_t sendjob;
const unsigned MEASUREMENT_INTERVAL = 10; // Medir cada 10 segundos
const unsigned TX_INTERVAL = 60; // Enviar cada 60 segundos
bool deviceJoined = false;
float currentDistance = 0.0;
unsigned long lastMeasurement = 0;
unsigned long measurementCount = 0;

// Buffer offline
#define MAX_OFFLINE_MEASUREMENTS 50
struct Measurement {
    float distance;
    unsigned long timestamp;
    bool sent;
};
Measurement offlineBuffer[MAX_OFFLINE_MEASUREMENTS];
int bufferIndex = 0;
int pendingMeasurements = 0;

// Pinmap LMIC
const lmic_pinmap lmic_pins = {
    .nss = LORA_SS,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = LORA_RST,
    .dio = { LORA_DIO0, LORA_DIO1, LORA_DIO2 }
};

// ---------------- Función para leer HC-SR04 ----------------
float readDistance() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10); // 10µs para 5V
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
    if (duration == 0) {
        return -1.0; // Error o fuera de rango
    }
    return (duration * 0.034) / 2;
}

// ---------------- Almacenar medición ----------------
void storeMeasurement(float distance) {
    measurementCount++;
    Serial.print("[");
    Serial.print(measurementCount);
    Serial.print("] ");
    Serial.print("Distancia: ");
    if (distance >= 0) {
        Serial.print(distance);
        Serial.println(" cm");
    } else {
        Serial.println("Fuera de rango");
    }

    // Almacenar en buffer offline
    if (pendingMeasurements < MAX_OFFLINE_MEASUREMENTS) {
        offlineBuffer[bufferIndex].distance = distance;
        offlineBuffer[bufferIndex].timestamp = millis();
        offlineBuffer[bufferIndex].sent = false;
        bufferIndex = (bufferIndex + 1) % MAX_OFFLINE_MEASUREMENTS;
        if (pendingMeasurements < MAX_OFFLINE_MEASUREMENTS) {
            pendingMeasurements++;
        }
    }
}

// ---------------- Actualizar display ----------------
void updateDisplay() {
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x12_tf);

    // Estado LoRaWAN
    if (deviceJoined) {
        u8g2.drawStr(0, 12, "LoRaWAN: CONECTADO");
    } else {
        u8g2.drawStr(0, 12, "LoRaWAN: JOINING...");
    }

    // Distancia
    if (currentDistance >= 0) {
        char distStr[32];
        sprintf(distStr, "Dist: %.1f cm", currentDistance);
        u8g2.drawStr(0, 28, distStr);
    } else {
        u8g2.drawStr(0, 28, "Fuera de rango");
    }

    // Contadores
    char infoStr[32];
    sprintf(infoStr, "Med:%lu Pend:%d", measurementCount, pendingMeasurements);
    u8g2.drawStr(0, 44, infoStr);

    // Info Gateway
    u8g2.drawStr(0, 60, "GW: US915 SubBand2");

    u8g2.sendBuffer();
}

// ---------------- Eventos LoRaWAN ----------------
void onEvent (ev_t ev) {
    Serial.print(os_getTime());
    Serial.print(": ");
    switch(ev) {
        case EV_SCAN_TIMEOUT:
            Serial.println(F("EV_SCAN_TIMEOUT"));
            break;
        case EV_BEACON_FOUND:
            Serial.println(F("EV_BEACON_FOUND"));
            break;
        case EV_BEACON_MISSED:
            Serial.println(F("EV_BEACON_MISSED"));
            break;
        case EV_BEACON_TRACKED:
            Serial.println(F("EV_BEACON_TRACKED"));
            break;
        case EV_JOINING:
            Serial.println(F("EV_JOINING - Intentando unirse..."));
            deviceJoined = false;
            break;
        case EV_JOINED:
            Serial.println(F("EV_JOINED - ¡Conectado a ChirpStack!"));
            {
                u4_t netid = 0;
                devaddr_t devaddr = 0;
                u1_t nwkKey[16];
                u1_t artKey[16];
                LMIC_getSessionKeys(&netid, &devaddr, nwkKey, artKey);
                Serial.print("netid: ");
                Serial.println(netid, DEC);
                Serial.print("devaddr: ");
                Serial.println(devaddr, HEX);
                Serial.print("AppSKey: ");
                for (size_t i=0; i<sizeof(artKey); ++i) {
                    if (i != 0)
                        Serial.print("-");
                    Serial.print(artKey[i], HEX);
                }
                Serial.println();
                Serial.print("NwkSKey: ");
                for (size_t i=0; i<sizeof(nwkKey); ++i) {
                    if (i != 0)
                        Serial.print("-");
                    Serial.print(nwkKey[i], HEX);
                }
                Serial.println();
            }
            LMIC_setLinkCheckMode(0);
            deviceJoined = true;
            if (pendingMeasurements > 0) {
                Serial.print("Enviando datos pendientes: ");
                Serial.println(pendingMeasurements);
                os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(2), do_send);
            }
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("EV_JOIN_FAILED - Reintentando..."));
            deviceJoined = false;
            break;
        case EV_REJOIN_FAILED:
            Serial.println(F("EV_REJOIN_FAILED"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE (incluye espera de ventanas RX)"));
            if (LMIC.txrxFlags & TXRX_ACK)
                Serial.println(F("ACK recibido"));
            if (LMIC.dataLen) {
                Serial.print(F("Datos recibidos: "));
                Serial.write(LMIC.frame+LMIC.dataBeg, LMIC.dataLen);
                Serial.println();
            }
            
            if (pendingMeasurements > 0) {
                for (int i = 0; i < MAX_OFFLINE_MEASUREMENTS; i++) {
                    if (!offlineBuffer[i].sent) {
                        offlineBuffer[i].sent = true;
                        pendingMeasurements--;
                        break;
                    }
                }
            }
            if (deviceJoined && pendingMeasurements > 0) {
                os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(5), do_send);
            } else if (deviceJoined) {
                os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(TX_INTERVAL), do_send);
            }
            break;
        case EV_LOST_TSYNC:
            Serial.println(F("EV_LOST_TSYNC"));
            break;
        case EV_RESET:
            Serial.println(F("EV_RESET"));
            break;
        case EV_RXCOMPLETE:
            Serial.println(F("EV_RXCOMPLETE"));
            break;
        case EV_LINK_DEAD:
            Serial.println(F("EV_LINK_DEAD"));
            break;
        case EV_LINK_ALIVE:
            Serial.println(F("EV_LINK_ALIVE"));
            break;
        case EV_TXSTART:
            Serial.println(F("EV_TXSTART - Transmitiendo..."));
            break;
        case EV_TXCANCELED:
            Serial.println(F("EV_TXCANCELED"));
            break;
        case EV_RXSTART:
            break;
        case EV_JOIN_TXCOMPLETE:
            Serial.println(F("EV_JOIN_TXCOMPLETE: sin respuesta de Join"));
            break;
        default:
            Serial.print(F("Evento desconocido: "));
            Serial.println((unsigned) ev);
            break;
    }
    updateDisplay();
}

// ---------------- Envío de datos ----------------
void do_send(osjob_t* j) {
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, no enviando"));
        return;
    }

    // Buscar medición pendiente
    float distanceToSend = -1;
    unsigned long timestampToSend = 0;
    for (int i = 0; i < MAX_OFFLINE_MEASUREMENTS; i++) {
        if (!offlineBuffer[i].sent) {
            distanceToSend = offlineBuffer[i].distance;
            timestampToSend = offlineBuffer[i].timestamp;
            break;
        }
    }
    if (distanceToSend == -1) {
        distanceToSend = currentDistance;
        timestampToSend = millis();
    }

    // Preparar payload
    uint8_t payload[10];
    uint16_t distanceInt;
    if (distanceToSend >= 0) {
        distanceInt = (uint16_t)(distanceToSend * 10);
        Serial.print("TX: ");
        Serial.print(distanceToSend);
        Serial.println(" cm");
    } else {
        distanceInt = 0xFFFF;
        Serial.println("TX: Fuera de rango");
    }

    payload[0] = 0x01; // Tipo sensor: ultrasónico
    payload[1] = distanceInt & 0xFF;
    payload[2] = (distanceInt >> 8) & 0xFF;
    payload[3] = 0x05; // Versión: 5V con divisor
    
    uint32_t measurementTime = timestampToSend / 1000;
    payload[4] = measurementTime & 0xFF;
    payload[5] = (measurementTime >> 8) & 0xFF;
    payload[6] = (measurementTime >> 16) & 0xFF;
    payload[7] = (measurementTime >> 24) & 0xFF;
    payload[8] = pendingMeasurements & 0xFF;
    payload[9] = measurementCount & 0xFF;

    LMIC_setTxData2(1, payload, sizeof(payload), 0);
    
    Serial.print("Payload: ");
    for (int i = 0; i < sizeof(payload); i++) {
        if (payload[i] < 0x10) Serial.print("0");
        Serial.print(payload[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
}

// ---------------- Setup ----------------
void setup() {
    Serial.begin(115200);
    delay(2000);
    Serial.println("\n=== TTGO T3 + HC-SR04 (5V) + ChirpStack ===");
    Serial.println("✅ Alimentación: 5V con divisor de voltaje");
    Serial.println("✅ Divisor: 1kΩ + 1.2kΩ = 2.73V en ECHO");
    Serial.println("✅ Gateway: US915 SubBand 2");
    Serial.println();

    // GPIOs seguros
    pinMode(0, INPUT_PULLUP);
    pinMode(2, OUTPUT);
    digitalWrite(2, LOW);

    // Configurar sensor
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);
    
    Serial.println("HC-SR04 configurado:");
    Serial.print("- TRIG: GPIO ");
    Serial.println(TRIG_PIN);
    Serial.print("- ECHO: GPIO ");
    Serial.println(ECHO_PIN);
    Serial.println("- VCC: 5V (VIN)");
    Serial.println("- GND: GND");
    Serial.println();

    // Test inicial
    Serial.println("Probando sensor...");
    currentDistance = readDistance();
    if (currentDistance >= 0) {
        Serial.print("✅ Sensor OK: ");
        Serial.print(currentDistance);
        Serial.println(" cm");
    } else {
        Serial.println("⚠️ Sin objeto detectado (normal)");
    }

    // OLED
    Serial.println("Configurando OLED...");
    Wire.begin(21, 22);
    Wire.setClock(100000);
    u8g2.begin();
    updateDisplay();
    Serial.println("✅ OLED funcionando");

    // LoRa
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    os_init();
    LMIC_reset();
    
    #ifdef CFG_us915
    LMIC_selectSubBand(0); 
    Serial.println("✅ LoRa US915 SubBand 1 configurado");
    #endif
    
    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
    LMIC_startJoining();

    lastMeasurement = millis();
    storeMeasurement(currentDistance);
    
    Serial.println("🚀 Sistema iniciado - Conectando a ChirpStack...");
}

// ---------------- Loop ----------------
void loop() {
    os_runloop_once();

    // Medición continua
    if (millis() - lastMeasurement >= (MEASUREMENT_INTERVAL * 1000)) {
        currentDistance = readDistance();
        storeMeasurement(currentDistance);
        lastMeasurement = millis();
        updateDisplay();
    }

    // Actualizar display
    static unsigned long lastDisplayUpdate = 0;
    if (millis() - lastDisplayUpdate >= 1000) {
        updateDisplay();
        lastDisplayUpdate = millis();
    }
}
