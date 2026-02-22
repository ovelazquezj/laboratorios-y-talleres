#include "LoRaWan_APP.h"
#include "Arduino.h"
#include "DHT.h"

/* ============================================================
 * SECCIÓN 0: CONFIGURACIÓN DHT11
 * ============================================================
 * 
 * SENSOR: DHT11 - Temperatura y Humedad
 * 
 * PINOUT DHT11 (3 pines):
 * ───────────────────────
 * Pin 1 (VCC):  Conectar a 5V del CubeCell
 * Pin 2 (DATA): Conectar a GPIO 11 del CubeCell
 *               ⚠️ IMPORTANTE: Agregar resistor pull-up 10K
 *               entre DATA pin y VCC
 * Pin 3 (GND):  Conectar a GND del CubeCell
 * 
 * DIAGRAMA DE CONEXIÓN:
 * ────────────────────
 * 
 *     DHT11          CubeCell
 *     ─────          ────────
 *      VCC  ────────→  5V
 *      DATA ──[10K]──→  GPIO 11
 *      GND  ────────→  GND
 * 
 * NOTA: El resistor de 10K es OBLIGATORIO para el DHT11
 *       Conectar entre el pin DATA y VCC
 * 
 * LIBRERÍA REQUERIDA:
 * - "DHT sensor library by Adafruit" (Library Manager)
 * - "Adafruit Unified Sensor" (Library Manager)
 * 
 * LIMITACIÓN IMPORTANTE:
 * - Tiempo mínimo entre lecturas: 1 segundo
 * - No leer más rápido que 1 Hz
 * 
 * ============================================================ */

#define DHTPIN 11       // GPIO 11 del CubeCell
#define DHTTYPE DHT11   // Tipo de sensor

// Inicializar sensor DHT
DHT dht(DHTPIN, DHTTYPE);

/* ============================================================
 * SECCIÓN 1: CREDENCIALES OTAA - ChirpStack iot-lab-itpa
 * ============================================================ */
uint8_t devEui[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77 };
uint8_t appEui[] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88 };
uint8_t appKey[] = {
  0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
  0xAB, 0xF7, 0x97, 0x68, 0x4C, 0x2B, 0x7E, 0x16
};

/* ============================================================
 * SECCIÓN 2: CONFIGURACIÓN LoRaWAN
 * ============================================================ */
bool     overTheAirActivation = true;
bool     loraWanAdr           = true;
bool     keepNet              = false;
bool     isTxConfirmed        = false;
uint8_t  confirmedNbTrials    = 4;
uint32_t appTxDutyCycle       = 30000;     // 30 segundos

/* SUB-BANDA 1: Canales 8-15 + 65 */
uint16_t userChannelsMask[6]  = { 0xFF00, 0x0000, 0x0000, 0x0000, 0x0002, 0x0000 };

// ABP Placeholders
uint32_t devAddr = 0x00000000;
uint8_t  nwkSKey[16] = { 0 };
uint8_t  appSKey[16] = { 0 };

// Región y Clase
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;
DeviceClass_t   loraWanClass  = LORAWAN_CLASS;

// Externs
extern enum eDeviceState_LoraWan deviceState;
extern uint8_t  appData[];
extern uint8_t  appDataSize;
extern uint32_t txDutyCycleTime;
uint8_t appPort = 2;

/* ============================================================
 * SECCIÓN 3: VARIABLES GLOBALES
 * ============================================================ */
static unsigned long packetCount = 0;
bool deviceJoined = false;
static unsigned long lastDHTRead = 0;

/* ============================================================
 * SECCIÓN 4: ESTRUCTURA DE DATOS DEL SENSOR
 * ============================================================
 * 
 * ARQUITECTURA MODULAR:
 * Separamos datos lógicos (struct) de datos físicos (bytes)
 * 
 */

struct SensorData {
    int temperatura;     // 0-50°C
    int humedad;         // 0-100%
    char mensaje[10];    // "hola mundo"
};

/* ============================================================
 * SECCIÓN 5: FUNCIÓN - LEER DATOS DEL SENSOR DHT11
 * ============================================================
 * 
 * RESPONSABILIDAD: Leer temperatura y humedad del DHT11
 * 
 * ⚠️ IMPORTANTE: 
 * - El DHT11 requiere mínimo 1 segundo entre lecturas
 * - Esta función valida el tiempo mínimo antes de leer
 * - Si falla, retorna -1 (valor inválido)
 * 
 */

struct SensorData readSensorData() {
    struct SensorData data;
    
    // VALIDACIÓN: Tiempo mínimo 1 segundo entre lecturas
    if (millis() - lastDHTRead < 1000) {
        // No suficiente tiempo, usar valores anteriores
        data.temperatura = 0;
        data.humedad = 0;
        strcpy(data.mensaje, "hola mundo");
        return data;
    }
    
    // LECTURA: Obtener temperatura y humedad del DHT11
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    // VALIDACIÓN: Verificar que las lecturas sean válidas
    if (isnan(temp) || isnan(hum)) {
        Serial.println(F("ERROR: No se pudo leer del DHT11"));
        data.temperatura = 0;
        data.humedad = 0;
    } else {
        data.temperatura = (int)temp;      // Convertir a entero
        data.humedad = (int)hum;           // Convertir a entero
    }
    
    strcpy(data.mensaje, "hola mundo");
    lastDHTRead = millis();
    
    return data;
}

/* ============================================================
 * SECCIÓN 6: FUNCIÓN - CREAR PAYLOAD
 * ============================================================
 * 
 * ESTRUCTURA DEL PAYLOAD (15 bytes total):
 * ─────────────────────────────────────────
 * 
 * BYTES 0-1: Temperatura (2 bytes, entero 0-50)
 *   Byte 0: temp & 0xFF           (byte bajo)
 *   Byte 1: (temp >> 8) & 0xFF    (byte alto)
 * 
 * BYTES 2-3: Humedad (2 bytes, entero 0-100)
 *   Byte 2: humedad & 0xFF        (byte bajo)
 *   Byte 3: (humedad >> 8) & 0xFF (byte alto)
 * 
 * BYTES 4-13: Mensaje "hola mundo" (10 caracteres ASCII)
 *   h=0x68  o=0x6F  l=0x6C  a=0x61  (esp)=0x20
 *   m=0x6D  u=0x75  n=0x6E  d=0x64  o=0x6F
 * 
 * BYTE 14: Checksum (suma de bytes 0-13)
 * 
 * TOTAL: 15 bytes
 * 
 */

void createPayload(struct SensorData data, uint8_t* payload) {
    if (payload == NULL) {
        Serial.println(F("ERROR: payload es NULL"));
        return;
    }
    
    // BYTES 0-1: Temperatura (Little-Endian)
    payload[0] = data.temperatura & 0xFF;
    payload[1] = (data.temperatura >> 8) & 0xFF;
    
    // BYTES 2-3: Humedad (Little-Endian)
    payload[2] = data.humedad & 0xFF;
    payload[3] = (data.humedad >> 8) & 0xFF;
    
    // BYTES 4-13: Mensaje "hola mundo"
    for (int i = 0; i < 10; i++) {
        payload[4 + i] = data.mensaje[i];
    }
    
    // BYTE 14: Checksum
    payload[14] = 0;
    for (int i = 0; i < 14; i++) {
        payload[14] += payload[i];
    }
}

/* ============================================================
 * SECCIÓN 7: FUNCIÓN - PREPARAR PAQUETE DE DATOS
 * ============================================================ */

static void prepareTxFrame(uint8_t port) {
    // PASO 1: Leer datos del sensor DHT11
    struct SensorData sensorData = readSensorData();
    
    // PASO 2: Empaquetar datos en payload de 15 bytes
    uint8_t payload[15];
    createPayload(sensorData, payload);
    
    appDataSize = 15;
    memcpy(appData, payload, appDataSize);
    
    // PASO 3: Mostrar información en Serial Monitor (educativo)
    packetCount++;
    
    Serial.println(F("\n========================================"));
    Serial.print(F("ENVIANDO PAQUETE #"));
    Serial.println(packetCount);
    Serial.println(F("========================================"));
    
    // Mostrar datos del sensor (sin encriptar)
    Serial.println(F("\nDatos del sensor DHT11 (SIN encriptar):"));
    Serial.print(F("  Temperatura: "));
    Serial.print(sensorData.temperatura);
    Serial.println(F("°C"));
    Serial.print(F("  Humedad: "));
    Serial.print(sensorData.humedad);
    Serial.println(F("%"));
    Serial.println(F("  Mensaje: hola mundo"));
    
    // Mostrar payload en HEX (como se transmite)
    Serial.println(F("\nPayload ENCRIPTADO (HEX - tal como se transmite):"));
    Serial.print(F("  "));
    for (int i = 0; i < 15; i++) {
        if (payload[i] < 0x10) Serial.print("0");
        Serial.print(payload[i], HEX);
        if (i < 14) Serial.print(" ");
    }
    Serial.println();
    
    // Mostrar payload desencriptado (interpretación byte por byte)
    Serial.println(F("\nPayload DESENCRIPTADO (interpretado byte por byte):"));
    
    Serial.print(F("  [0-1] Temperatura (Little-Endian): "));
    int temp_recalc = payload[0] | (payload[1] << 8);
    Serial.print(temp_recalc);
    Serial.println(F("°C"));
    
    Serial.print(F("  [2-3] Humedad (Little-Endian): "));
    int hum_recalc = payload[2] | (payload[3] << 8);
    Serial.print(hum_recalc);
    Serial.println(F("%"));
    
    Serial.print(F("  [4-13] Mensaje (ASCII): "));
    for (int i = 4; i < 14; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
    
    Serial.print(F("  [14] Checksum (suma de bytes 0-13): 0x"));
    if (payload[14] < 0x10) Serial.print("0");
    Serial.println(payload[14], HEX);
    
    Serial.println(F("\nInformacion tecnica del envio:"));
    Serial.print(F("  Puerto LoRaWAN: "));
    Serial.print(port);
    Serial.print(F(" | Tamanio del payload: "));
    Serial.print(appDataSize);
    Serial.println(F(" bytes"));
    
    Serial.println(F("========================================"));
}

/* ============================================================
 * SECCIÓN 8: FUNCIÓN SETUP
 * ============================================================ */

void setup() {
    Serial.begin(115200);
    delay(1500);
    
    Serial.println(F("\n"));
    Serial.println(F("====================================="));
    Serial.println(F("  CubeCell (HTCC-AB01)"));
    Serial.println(F("  LoRaWAN OTAA - Semana 7"));
    Serial.println(F("  CON SENSOR DHT11"));
    Serial.println(F("====================================="));
    Serial.println();
    
    Serial.println(F("CREDENCIALES PARA CHIRPSTACK (MSB):"));
    Serial.println(F("Device EUI: 00-11-22-33-44-55-66-77"));
    Serial.println(F("Join EUI:   11-22-33-44-55-66-77-88"));
    Serial.println(F("App Key:    2B-7E-15-16-28-AE-D2-A6-AB-F7-97-68-4C-2B-7E-16"));
    Serial.println();
    
    Serial.println(F("CONFIGURACION DE RED:"));
    Serial.println(F("Region: US915"));
    Serial.println(F("Sub-banda: 1 (Canales 8-15 + 65)"));
    Serial.println(F("Clase: A"));
    Serial.println(F("Modo: OTAA"));
    Serial.println(F("Intervalo: 30 segundos"));
    Serial.println();
    
    Serial.println(F("SENSOR DHT11:"));
    Serial.println(F("Pin DATA: GPIO 11"));
    Serial.println(F("Resistor pull-up: 10K ohms (obligatorio)"));
    Serial.println();
    
    Serial.println(F("ESTRUCTURA DEL PAYLOAD (15 bytes):"));
    Serial.println(F("Bytes 0-1:   Temperatura (2 bytes)"));
    Serial.println(F("Bytes 2-3:   Humedad (2 bytes)"));
    Serial.println(F("Bytes 4-13:  'hola mundo' (10 bytes)"));
    Serial.println(F("Byte 14:     Checksum (1 byte)"));
    Serial.println();

    // Alimentar RGB LED si está habilitado
    pinMode(Vext, OUTPUT);
    digitalWrite(Vext, LOW);
    delay(10);

    // Inicializar sensor DHT11
    Serial.println(F("Inicializando DHT11..."));
    dht.begin();
    Serial.println(F("DHT11 OK\n"));

    // Iniciar máquina de estados
    deviceState = DEVICE_STATE_INIT;
    LoRaWAN.ifskipjoin();

    Serial.println(F("INICIANDO PROCEDIMIENTO OTAA JOIN"));
    Serial.println(F("Esperando conexion a gateway...\n"));
}

/* ============================================================
 * SECCIÓN 9: FUNCIÓN LOOP
 * ============================================================ */

void loop() {
    switch (deviceState) {
        
        case DEVICE_STATE_INIT: {
#if (LORAWAN_DEVEUI_AUTO)
            LoRaWAN.generateDeveuiByChipID();
#endif
            Serial.println(F("[STATE] INIT"));
            printDevParam();
            LoRaWAN.init(loraWanClass, loraWanRegion);
            deviceState = DEVICE_STATE_JOIN;
            break;
        }

        case DEVICE_STATE_JOIN: {
            Serial.println(F("[STATE] JOIN - Enviando JoinRequest (OTAA)"));
            Serial.println(F("  ⏳ Esperando JoinAccept del servidor..."));
            LoRaWAN.join();
            break;
        }

        case DEVICE_STATE_SEND: {
            Serial.println(F("[STATE] SEND - Transmitiendo datos"));
            
            prepareTxFrame(appPort);
            
            LoRaWAN.send();
            deviceState = DEVICE_STATE_CYCLE;
            break;
        }

        case DEVICE_STATE_CYCLE: {
            Serial.println(F("[STATE] CYCLE - Programando proximo envio"));
            
            txDutyCycleTime = appTxDutyCycle + randr(0, APP_TX_DUTYCYCLE_RND);
            Serial.print(F("  ⏱️  Proximo TX en: "));
            Serial.print(txDutyCycleTime / 1000);
            Serial.println(F(" segundos\n"));
            
            LoRaWAN.cycle(txDutyCycleTime);
            deviceState = DEVICE_STATE_SLEEP;
            break;
        }

        case DEVICE_STATE_SLEEP: {
            LoRaWAN.sleep();
            break;
        }

        default: {
            Serial.println(F("[STATE] DEFAULT - Reiniciando a INIT"));
            deviceState = DEVICE_STATE_INIT;
            break;
        }
    }
}

/*
 * =====================================================================
 * DECODIFICADOR JAVASCRIPT PARA CHIRPSTACK
 * =====================================================================
 * 
 * function Decode(fPort, bytes) {
 *   // Bytes 0-1: Temperatura (Little-Endian)
 *   var temperatura = bytes[0] | (bytes[1] << 8);
 *   
 *   // Bytes 2-3: Humedad (Little-Endian)
 *   var humedad = bytes[2] | (bytes[3] << 8);
 *   
 *   // Bytes 4-13: Mensaje ASCII
 *   var mensaje = '';
 *   for (var i = 4; i < 14; i++) {
 *     mensaje += String.fromCharCode(bytes[i]);
 *   }
 *   
 *   // Byte 14: Checksum
 *   var checksum = bytes[14];
 *   
 *   return {
 *     temperatura: temperatura + '°C',
 *     humedad: humedad + '%',
 *     mensaje: mensaje,
 *     checksum: '0x' + checksum.toString(16)
 *   };
 * }
 * 
 * =====================================================================
 */