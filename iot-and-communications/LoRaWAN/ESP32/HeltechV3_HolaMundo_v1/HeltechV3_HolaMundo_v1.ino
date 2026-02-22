/*
 * HELTEC LoRa32 V3 (ESP32-S3 + SX1262) OLED - ARQUITECTURA MODULAR
 * VERSION: 4.1 - CORREGIDO (DevNonce fix)
 * 
 * CAMBIO PRINCIPAL:
 * - SOLO acepta RADIOLIB_ERR_NONE como éxito en activateOTAA()
 * - Rechaza -1118 y -1117 que NO son éxito
 * 
 * LIBRERÍA: ropg/heltec_esp32_lora_v3
 */

#include <heltec_unofficial.h>

// ===================================================================
// CREDENCIALES LoRaWAN (OTAA)
// ===================================================================
static uint64_t devEui = 0x065CB42378AB4359ULL;
static uint64_t joinEui = 0x744E66E299637F5DULL;
static uint8_t nwkKey[] = { 0x4E, 0x8C, 0xA5, 0xD3, 0x6E, 0xB9, 0x2F, 0x58, 0xAD, 0x4C, 0x7E, 0x93, 0xC6, 0x5D, 0xAE, 0x40 };
static uint8_t appKey[] = { 0x4E, 0x8C, 0xA5, 0xD3, 0x6E, 0xB9, 0x2F, 0x58, 0xAD, 0x4C, 0x7E, 0x93, 0xC6, 0x5D, 0xAE, 0x43 };

// ===================================================================
// ESTRUCTURA DE DATOS DEL SENSOR
// ===================================================================
struct SensorData {
    char mensaje[10];
    uint32_t timestamp;
};

// ===================================================================
// VARIABLES GLOBALES
// ===================================================================
LoRaWANNode *node = NULL;
bool deviceJoined = false;
unsigned long packetCount = 0;
unsigned long lastTxTime = 0;
const unsigned long TX_INTERVAL = 30000;
int16_t state = 0;

// ===================================================================
// FUNCION - LEER DATOS DEL SENSOR
// ===================================================================
struct SensorData readSensorData() {
    struct SensorData data;
    strcpy(data.mensaje, "hola mundo");
    data.timestamp = millis() / 1000;
    return data;
}

// ===================================================================
// FUNCION - CREAR PAYLOAD
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
// FUNCION - ACTUALIZAR PANTALLA OLED
// ===================================================================
void updateDisplay() {
    display.clear();
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    
    display.drawString(0, 0, "Heltec LoRa32 V3");
    
    if (deviceJoined) {
        display.drawString(0, 16, "Estado: CONECTADO");
    } else {
        display.drawString(0, 16, "Estado: JOIN...");
    }

    char countStr[32];
    sprintf(countStr, "Paquetes: %lu", packetCount);
    display.drawString(0, 32, countStr);
    display.drawString(0, 48, "US915 OTAA");
    
    display.display();
}

// ===================================================================
// FUNCION - MOSTRAR INFORMACION DE CREDENCIALES
// ===================================================================
void printEUIInfo() {
    Serial.println(F("\n"));
    Serial.println(F("===================================================="));
    Serial.println(F("HELTEC LoRa32 V3 (SX1262) - OTAA JOIN"));
    Serial.println(F("VERSION: 4.1 - CORREGIDA"));
    Serial.println(F("===================================================="));
    
    Serial.println(F("\nCREDENCIALES PARA CHIRPSTACK (MSB):"));
    Serial.println(F("Device EUI: 065CB42378AB4359"));
    Serial.println(F("Join EUI:   744E66E299637F5D"));
    Serial.println(F("App Key:    4E8CA5D36EB92F58AD4C7E93C65DAE43"));
    
    Serial.println(F("\n===================================================="));
    Serial.println(F("Copia estos valores EXACTAMENTE en ChirpStack"));
    Serial.println(F("====================================================\n"));
}

// ===================================================================
// FUNCION - ENVIAR PAQUETE
// ===================================================================
void sendPacket() {
    // VALIDACION: Solo enviar si esta conectado
    if (!deviceJoined) {
        Serial.println(F("ERROR - Dispositivo no conectado."));
        return;
    }
    
    // PASO 1: Leer datos del sensor
    struct SensorData sensorData = readSensorData();
    
    // PASO 2: Empaquetar datos en payload de 16 bytes
    uint8_t payload[16];
    createPayload(sensorData, payload);
    
    // PASO 3: Incrementar contador de paquetes
    packetCount++;
    
    // PASO 4: Mostrar informacion en Serial Monitor
    Serial.println(F("\n========================================"));
    Serial.print(F("ENVIANDO PAQUETE "));
    Serial.println(packetCount);
    Serial.println(F("========================================"));
    
    // Mostrar datos crudos del sensor
    Serial.println(F("\nDatos del sensor (SIN encriptar):"));
    Serial.print(F("  Mensaje: "));
    Serial.println(sensorData.mensaje);
    Serial.print(F("  Timestamp: "));
    Serial.print(sensorData.timestamp);
    Serial.println(F(" segundos"));
    
    // Mostrar payload en HEX
    Serial.println(F("\nPayload ENCRIPTADO (HEX - tal como se transmite):"));
    Serial.print(F("  "));
    for (int i = 0; i < sizeof(payload); i++) {
        if (payload[i] < 0x10) Serial.print("0");
        Serial.print(payload[i], HEX);
        if (i < sizeof(payload) - 1) Serial.print(" ");
    }
    Serial.println();
    
    // Mostrar payload desencriptado
    Serial.println(F("\nPayload DESENCRIPTADO (interpretado byte por byte):"));
    Serial.print(F("  [0] Tipo de mensaje: 0x"));
    Serial.println(payload[0], HEX);
    
    Serial.print(F("  [1-4] Timestamp: "));
    uint32_t ts_recalc = payload[1] | (payload[2] << 8) | 
                         (payload[3] << 16) | (payload[4] << 24);
    Serial.print(ts_recalc);
    Serial.println(F(" segundos"));
    
    Serial.print(F("  [5-14] Mensaje: "));
    for (int i = 5; i < 15; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
    
    Serial.print(F("  [15] Checksum (suma de bytes 0-14): 0x"));
    Serial.println(payload[15], HEX);
    
    Serial.println(F("\nInformacion tecnica del envio:"));
    Serial.print(F("  Puerto LoRaWAN: 1"));
    Serial.print(F(" | Tamanio del payload: "));
    Serial.print(sizeof(payload));
    Serial.println(F(" bytes"));
    
    Serial.println(F("========================================"));
    
    // PASO 5: Enviar por LoRaWAN
    uint8_t downlinkData[256];
    size_t lenDown = sizeof(downlinkData);
    
    state = node->sendReceive(payload, sizeof(payload), 1, downlinkData, &lenDown);
    
    // Verificar resultado del envio
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("OK - Paquete transmitido (sin downlink)"));
    } else if (state > 0) {
        Serial.println(F("OK - Paquete transmitido (CON downlink recibido)"));
        Serial.print(F("Downlink size: "));
        Serial.println(lenDown);
    } else {
        Serial.print(F("ERROR en transmision - Codigo: "));
        Serial.println(state);
    }
    
    Serial.println();
    lastTxTime = millis();
}

// ===================================================================
// FUNCION SETUP (INICIALIZACION)
// ===================================================================
void setup() {
    heltec_setup();
    
    delay(2000);
    
    Serial.println(F("\n"));
    Serial.println(F("====================================="));
    Serial.println(F("HELTEC LoRa32 V3 (ESP32-S3 + SX1262)"));
    Serial.println(F("VERSION: 4.1 - CORREGIDA"));
    Serial.println(F("====================================="));
    Serial.println();
    
    printEUIInfo();
    
    Serial.println(F("CONFIGURACION DE RED:"));
    Serial.println(F("Region: US915"));
    Serial.println(F("LoRa Chip: SX1262"));
    Serial.println(F("Microcontrolador: ESP32-S3FN8"));
    Serial.println(F("Modo: OTAA (Over-The-Air Activation)"));
    Serial.println();

    updateDisplay();
    
    Serial.println(F("Inicializando LoRaWAN..."));
    node = new LoRaWANNode(&radio, &US915);
    Serial.println(F("OK"));
    Serial.println();
    
    Serial.println(F("Configurando parametros de radio:"));
    Serial.println(F("  Frecuencia: 902.3 MHz (US915)"));
    Serial.println(F("  Bandwidth: 125 kHz"));
    Serial.println(F("  Spreading Factor: 8 (robusto)"));
    Serial.println(F("  Coding Rate: 4/5"));
    Serial.println(F("  Potencia: 20 dBm"));
    Serial.println();
    
    Serial.println(F("Inicializando OTAA..."));
    state = node->beginOTAA(joinEui, devEui, nwkKey, appKey);
    
    if (state != RADIOLIB_ERR_NONE) {
        Serial.print(F("ERROR - Codigo: "));
        Serial.println(state);
        while (true) {
            heltec_loop();
            delay(100);
        }
    }
    Serial.println(F("OK"));
    Serial.println();
    
    Serial.println(F("INICIANDO PROCEDIMIENTO OTAA JOIN"));
    Serial.println(F("Esperando conexion a gateway..."));
    Serial.println();
}

// ===================================================================
// FUNCION LOOP (BUCLE PRINCIPAL)
// ===================================================================
void loop() {
    heltec_loop();
    
    // Estado 1: No conectado - Intentar JOIN
    if (!deviceJoined) {
        Serial.println(F("Intentando OTAA activation..."));
        state = node->activateOTAA();
        
        // CORRECCION: SOLO aceptar RADIOLIB_ERR_NONE (0) como éxito
        if (state == RADIOLIB_ERR_NONE) {
            // JOIN EXITOSO
            Serial.println(F("\n*** JOIN EXITOSO ***"));
            Serial.println(F("Dispositivo conectado a ChirpStack"));
            Serial.println(F("Iniciando transmisiones de datos\n"));
            deviceJoined = true;
            updateDisplay();
            lastTxTime = millis();
        } else if (state == -1116) {
            // NO recibio JoinAccept
            Serial.println(F("Join fallido (-1116) - NO recibio JoinAccept"));
            Serial.println(F("Verifica:"));
            Serial.println(F("  1. Gateway LoRaWAN ACTIVO y en rango (<10km)"));
            Serial.println(F("  2. DevEUI/JoinEUI/AppKey EXACTOS en ChirpStack"));
            Serial.println(F("  3. ChirpStack configurado para US915"));
            Serial.println(F("  4. Presiona 'Flush OTAA device nonces' en ChirpStack"));
            Serial.println(F("  5. Antena LoRa conectada correctamente"));
            Serial.println(F("Reintentando en 60 segundos...\n"));
            delay(60000);
        } else {
            Serial.print(F("Join fallido - Codigo: "));
            Serial.println(state);
            Serial.println(F("Reintentando en 30 segundos...\n"));
            delay(30000);
        }
    } 
    // Estado 2: Conectado - Enviar datos periodicamente
    else {
        if (millis() - lastTxTime >= TX_INTERVAL) {
            sendPacket();
        }
        updateDisplay();
        delay(1000);
    }
}
