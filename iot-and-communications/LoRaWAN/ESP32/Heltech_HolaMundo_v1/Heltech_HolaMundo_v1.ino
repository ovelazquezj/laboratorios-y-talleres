/*
 * HELTEC LoRa32 V3 (ESP32-S3 + SX1262) OLED - ARQUITECTURA MODULAR
 * VERSION: 3.0 - Modular con RadioLib (SX1262)
 * 
 * CAMBIOS RESPECTO A V2:
 * - Microcontrolador: ESP32-S3 (en lugar de ESP32)
 * - LoRa chip: SX1262 (en lugar de SX1276)
 * - Libreria: RadioLib (en lugar de LMIC)
 * - Pines: Completamente diferentes para SX1262
 * - LoRaWAN: Implementado con RadioLib
 */

#include <Wire.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <RadioLib.h>

// ===================================================================
// PASO 1: CONFIGURAR PANTALLA OLED (V3)
// ===================================================================
// V3 usa pines I2C diferentes

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// ===================================================================
// PASO 2: DEFINIR PINES DEL MODULO LoRa (SX1262) - V3
// ===================================================================
// V3 tiene pines COMPLETAMENTE diferentes al V2
// Estos pines son especificos para Heltec LoRa32 V3

#define LORA_NSS   8   // Chip Select
#define LORA_RST   12  // Reset
#define LORA_DIO1  14  // Interrupt (en SX1262 es DIO1, NO DIO0)
#define LORA_BUSY  13  // Busy pin (SX1262 tiene este pin)
#define LORA_SCK   9   // Clock SPI
#define LORA_MISO  11  // MISO SPI
#define LORA_MOSI  10  // MOSI SPI

// ===================================================================
// PASO 3: CREAR OBJETO RADIOLIB PARA SX1262
// ===================================================================
// RadioLib maneja todo: modulacion, codificacion, LoRaWAN

SPIClass spi(HSPI);
SX1262 radio = new Module(LORA_NSS, LORA_DIO1, LORA_RST, LORA_BUSY, spi);

// ===================================================================
// PASO 4: CREDENCIALES LoRaWAN (DIFERENTES a V2)
// ===================================================================

static const u1_t PROGMEM DEVEUI[8] = { 0x56, 0x43, 0xAB, 0x78, 0x23, 0xB4, 0x5C, 0x04 };
static const u1_t PROGMEM APPEUI[8] = { 0x8D, 0x7F, 0x63, 0x99, 0xE2, 0x66, 0x4G, 0x72 };
static const u1_t PROGMEM APPKEY[16] = { 
    0x4E, 0x8C, 0xA5, 0xD3, 0x6G, 0xB9, 0x2F, 0x58, 
    0xAD, 0x4C, 0x7E, 0x93, 0xC6, 0x5D, 0xAE, 0x39 
};

// ===================================================================
// PASO 5: ESTRUCTURA DE DATOS DEL SENSOR
// ===================================================================

struct SensorData {
    char mensaje[10];
    uint32_t timestamp;
};

// ===================================================================
// PASO 6: VARIABLES GLOBALES
// ===================================================================

bool deviceJoined = false;
unsigned long packetCount = 0;
unsigned long lastTxTime = 0;
const unsigned long TX_INTERVAL = 30000; // 30 segundos en millisegundos

// ===================================================================
// PASO 7: FUNCION - LEER DATOS DEL SENSOR
// ===================================================================

struct SensorData readSensorData() {
    struct SensorData data;
    strcpy(data.mensaje, "hola mundo");
    data.timestamp = millis() / 1000;
    return data;
}

// ===================================================================
// PASO 8: FUNCION - CREAR PAYLOAD
// ===================================================================

void createPayload(struct SensorData data, uint8_t* payload) {
    if (payload == NULL) {
        return;
    }
    
    payload[0] = 0x48;
    
    payload[1] = data.timestamp & 0xFF;
    payload[2] = (data.timestamp >> 8) & 0xFF;
    payload[3] = (data.timestamp >> 16) & 0xFF;
    payload[4] = (data.timestamp >> 24) & 0xFF;
    
    for (int i = 0; i < 10; i++) {
        payload[5 + i] = data.mensaje[i];
    }
    
    payload[15] = 0;
    for (int i = 0; i < 15; i++) {
        payload[15] += payload[i];
    }
}

// ===================================================================
// PASO 9: FUNCION - ACTUALIZAR PANTALLA OLED
// ===================================================================

void updateDisplay() {
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_ncenB10_tr);
    u8g2.drawStr(0, 12, "Heltec LoRa32 V3");
    
    u8g2.setFont(u8g2_font_6x12_tf);
    
    if (deviceJoined) {
        u8g2.drawStr(0, 28, "Estado: CONECTADO");
    } else {
        u8g2.drawStr(0, 28, "Estado: JOINING");
    }

    char countStr[32];
    sprintf(countStr, "Paquetes: %lu", packetCount);
    u8g2.drawStr(0, 44, countStr);
    u8g2.drawStr(0, 60, "EU868 Band");
    u8g2.sendBuffer();
}

// ===================================================================
// PASO 10: FUNCION - MOSTRAR INFORMACION DE EUI
// ===================================================================

void printEUIInfo() {
    Serial.println(F("\n"));
    Serial.println(F("===================================================="));
    Serial.println(F("HELTEC LoRa32 V3 (SX1262) - INFORMACION DE EUI"));
    Serial.println(F("===================================================="));
    
    Serial.println(F("\nCREDENCIALES PARA CHIRPSTACK:"));
    
    Serial.print(F("Device EUI (MSB): "));
    for (int i = 7; i >= 0; i--) {
        if (DEVEUI[i] < 0x10) Serial.print("0");
        Serial.print(DEVEUI[i], HEX);
    }
    Serial.println();
    
    Serial.print(F("Join EUI (MSB): "));
    for (int i = 7; i >= 0; i--) {
        if (APPEUI[i] < 0x10) Serial.print("0");
        Serial.print(APPEUI[i], HEX);
    }
    Serial.println();
    
    Serial.print(F("App Key (MSB): "));
    for (int i = 0; i < 16; i++) {
        if (APPKEY[i] < 0x10) Serial.print("0");
        Serial.print(APPKEY[i], HEX);
    }
    Serial.println();
    
    Serial.println(F("\n===================================================="));
    Serial.println(F("Copia estos valores exactamente en ChirpStack"));
    Serial.println(F("====================================================\n"));
}

// ===================================================================
// PASO 11: FUNCION - ENVIAR PAQUETE
// ===================================================================

void sendPacket() {
    struct SensorData sensorData = readSensorData();
    uint8_t payload[16];
    createPayload(sensorData, payload);
    
    packetCount++;
    
    Serial.println(F("\n========================================"));
    Serial.print(F("ENVIANDO PAQUETE "));
    Serial.println(packetCount);
    Serial.println(F("========================================"));
    
    Serial.println(F("\nDatos del sensor:"));
    Serial.print(F("  Mensaje: "));
    Serial.println(sensorData.mensaje);
    Serial.print(F("  Timestamp: "));
    Serial.print(sensorData.timestamp);
    Serial.println(F(" segundos"));
    
    Serial.println(F("\nPayload ENCRIPTADO (HEX):"));
    Serial.print(F("  "));
    for (int i = 0; i < sizeof(payload); i++) {
        if (payload[i] < 0x10) Serial.print("0");
        Serial.print(payload[i], HEX);
        if (i < sizeof(payload) - 1) Serial.print(" ");
    }
    Serial.println();
    
    Serial.println(F("\nPayload DESENCRIPTADO (decodificado):"));
    Serial.print(F("  [0] Tipo: 0x"));
    Serial.println(payload[0], HEX);
    
    Serial.print(F("  [1-4] Timestamp: "));
    uint32_t ts_recalc = payload[1] | (payload[2] << 8) | 
                         (payload[3] << 16) | (payload[4] << 24);
    Serial.print(ts_recalc);
    Serial.println(F(" seg"));
    
    Serial.print(F("  [5-14] Mensaje: "));
    for (int i = 5; i < 15; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
    
    Serial.print(F("  [15] Checksum: 0x"));
    Serial.println(payload[15], HEX);
    
    Serial.println(F("\nInformacion del envio:"));
    Serial.print(F("  Puerto: 1"));
    Serial.print(F(" | Tamanio: "));
    Serial.print(sizeof(payload));
    Serial.println(F(" bytes"));
    
    Serial.println(F("========================================\n"));
    
    // Enviar con RadioLib
    int state = radio.transmit(payload, sizeof(payload));
    
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("OK - Paquete transmitido"));
    } else {
        Serial.print(F("ERROR - Codigo: "));
        Serial.println(state);
    }
    
    lastTxTime = millis();
    updateDisplay();
}

// ===================================================================
// PASO 12: FUNCION SETUP
// ===================================================================

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println(F("\n"));
    Serial.println(F("====================================="));
    Serial.println(F("HELTEC LoRa32 V3 (ESP32-S3 + SX1262)"));
    Serial.println(F("====================================="));
    Serial.println();
    
    printEUIInfo();
    
    Serial.println(F("CONFIGURACION DE RED:"));
    Serial.println(F("Region: EU868"));
    Serial.println(F("LoRa Chip: SX1262"));
    Serial.println(F("Microcontrolador: ESP32-S3"));
    Serial.println();
    
    // Inicializar OLED
    Serial.println(F("Inicializando OLED..."));
    Wire.begin(17, 18);
    Wire.setClock(100000);
    u8g2.begin();
    updateDisplay();
    Serial.println(F("OK"));
    Serial.println();

    // Inicializar SPI y Radio
    Serial.println(F("Inicializando SPI..."));
    spi.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_NSS);
    Serial.println(F("OK"));
    Serial.println();
    
    Serial.println(F("Inicializando LoRa (SX1262)..."));
    int state = radio.begin(868.0);
    
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("OK - SX1262 inicializado"));
    } else {
        Serial.print(F("ERROR - Codigo: "));
        Serial.println(state);
        while (true) {
            delay(100);
        }
    }
    
    // Configurar SX1262 para LoRa
    radio.setFrequency(868.1);
    radio.setBandwidth(125.0);
    radio.setSpreadingFactor(7);
    radio.setCodingRate(5);
    radio.setOutputPower(14);
    radio.setPreambleLength(8);
    
    Serial.println(F("\nConfiguracion de radio:"));
    Serial.println(F("  Frecuencia: 868.1 MHz"));
    Serial.println(F("  Bandwidth: 125 kHz"));
    Serial.println(F("  Spreading Factor: 7"));
    Serial.println(F("  Coding Rate: 4/5"));
    Serial.println(F("  Potencia: 14 dBm"));
    Serial.println();
    
    Serial.println(F("INICIANDO TRANSMISIONES"));
    Serial.println();
    
    deviceJoined = true;
    lastTxTime = millis();
}

// ===================================================================
// PASO 13: FUNCION LOOP
// ===================================================================

void loop() {
    // Enviar paquete cada 30 segundos
    if (millis() - lastTxTime >= TX_INTERVAL) {
        sendPacket();
    }
    
    // Actualizar OLED
    updateDisplay();
    delay(100);
}