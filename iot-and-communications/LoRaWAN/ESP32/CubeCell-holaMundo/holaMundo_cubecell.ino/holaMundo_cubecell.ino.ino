#include "LoRaWan_APP.h"
#include "Arduino.h"

/* ============================================================
 * CubeCell (HTCC-AB01) - LoRaWAN OTAA
 * SEMANA 7 - ARQUITECTURA MODULAR EDUCATIVA
 * ============================================================
 * 
 * OBJETIVO EDUCATIVO:
 * Demostrar arquitectura profesional para IoT con LoRaWAN:
 * - Separación de responsabilidades (modular)
 * - Lectura de timestamp del sistema
 * - Creación estructurada de payloads
 * - Encriptación y desencriptación de datos
 * - OTAA Join real
 * - Comunicación con ChirpStack
 * 
 * FLUJO DE DATOS:
 * [Sistema] → [readTimestamp()] → [createPayload()] → 
 * [radio.transmit()] → [LoRaWAN] → [ChirpStack]
 * 
 * ============================================================ */

/* ============================================================
 * SECCIÓN 1: CREDENCIALES OTAA - ChirpStack iot-lab-itpa
 * ============================================================
 * 
 * CONCEPTOS:
 * - DevEUI: Identificador único del dispositivo (8 bytes)
 * - AppEUI/JoinEUI: Identificador de la aplicación (8 bytes)
 * - AppKey: Clave de encriptación (16 bytes)
 * 
 * FORMATO: MSB (tal como aparece en ChirpStack)
 * Nota: La librería LoRaWan_APP.h maneja internamente la conversión
 * 
 * ============================================================ */

uint8_t devEui[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77 };
uint8_t appEui[] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88 };
uint8_t appKey[] = {
  0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
  0xAB, 0xF7, 0x97, 0x68, 0x4C, 0x2B, 0x7E, 0x16
};

/* ============================================================
 * SECCIÓN 2: CONFIGURACIÓN LoRaWAN
 * ============================================================
 * 
 * overTheAirActivation = true
 *   → Activación OTAA (el dispositivo solicita Join)
 * 
 * loraWanAdr = true
 *   → Adaptive Data Rate (servidor ajusta automáticamente SF)
 * 
 * appTxDutyCycle = 30000 ms
 *   → Intervalo entre transmisiones (30 segundos)
 * 
 * userChannelsMask: Sub-banda 1 (Canales 8-15 + 65)
 *   → 0xFF00 = activa canales 8-15
 *   → 0x0002 en posición 4 = activa canal 65
 * 
 * ============================================================ */

bool     overTheAirActivation = true;      // Activación OTAA
bool     loraWanAdr           = true;       // Adaptive Data Rate
bool     keepNet              = false;      // Mantener conexión
bool     isTxConfirmed        = false;      // Sin confirmación de TX
uint8_t  confirmedNbTrials    = 4;
uint32_t appTxDutyCycle       = 30000;     // 30 segundos

/* 
 * SUB-BANDA 1: Canales 8-15 + 65
 * Máscara de canales: 0xFF00 = 11111111 00000000 (canales 8-15)
 */
uint16_t userChannelsMask[6]  = { 0xFF00, 0x0000, 0x0000, 0x0000, 0x0002, 0x0000 };

/* ============================================================
 * ABP Placeholders (no usados en OTAA, pero requeridos por linker)
 * ============================================================ */
uint32_t devAddr = 0x00000000;
uint8_t  nwkSKey[16] = { 0 };
uint8_t  appSKey[16] = { 0 };

/* ============================================================
 * REGIÓN Y CLASE LoRaWAN
 * ============================================================ */
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;     // Desde Tools
DeviceClass_t   loraWanClass  = LORAWAN_CLASS;     // Desde Tools

/* ============================================================
 * EXTERNS DE LA LIBRERÍA
 * ============================================================ */
extern enum eDeviceState_LoraWan deviceState;
extern uint8_t  appData[];
extern uint8_t  appDataSize;
extern uint32_t txDutyCycleTime;
uint8_t appPort = 2;                               // Puerto aplicación

/* ============================================================
 * SECCIÓN 3: VARIABLES GLOBALES Y CONTADORES
 * ============================================================ */

static unsigned long packetCount = 0;
bool deviceJoined = false;

/* ============================================================
 * SECCIÓN 4: FUNCIÓN - PREPARAR PAQUETE DE DATOS
 * ============================================================
 * 
 * ESTRUCTURA DEL PAYLOAD (15 bytes total):
 * ─────────────────────────────────────────
 * 
 * BYTES 0-3: Timestamp (4 bytes, Little-Endian)
 *   Byte 0: timestamp & 0xFF              (bits 0-7, LSB)
 *   Byte 1: (timestamp >> 8) & 0xFF       (bits 8-15)
 *   Byte 2: (timestamp >> 16) & 0xFF      (bits 16-23)
 *   Byte 3: (timestamp >> 24) & 0xFF      (bits 24-31, MSB)
 * 
 * BYTES 4-13: Mensaje "hola mundo" (10 caracteres ASCII)
 *   h=0x68  o=0x6F  l=0x6C  a=0x61  (esp)=0x20
 *   m=0x6D  u=0x75  n=0x6E  d=0x64  o=0x6F
 * 
 * BYTE 14: Checksum (suma de verificación)
 *   Suma de bytes 0-13, modulo 256
 *   Detecta corrupción de datos
 * 
 * TOTAL: 15 bytes
 * 
 * ============================================================ */

static void prepareTxFrame(uint8_t port) {
    // PASO 1: Obtener timestamp del sistema (en segundos)
    uint32_t timestamp = millis() / 1000;
    
    // PASO 2: Construir payload de 15 bytes
    
    // BYTES 0-3: Timestamp en Little-Endian
    appData[0] = timestamp & 0xFF;
    appData[1] = (timestamp >> 8) & 0xFF;
    appData[2] = (timestamp >> 16) & 0xFF;
    appData[3] = (timestamp >> 24) & 0xFF;
    
    // BYTES 4-13: Mensaje "hola mundo"
    const char mensaje[] = "hola mundo";
    for (int i = 0; i < 10; i++) {
        appData[4 + i] = mensaje[i];
    }
    
    // BYTE 14: Checksum (suma de bytes 0-13)
    appData[14] = 0;
    for (int i = 0; i < 14; i++) {
        appData[14] += appData[i];
    }
    
    appDataSize = 15;  // Total: 15 bytes
    
    // PASO 3: Mostrar información en Serial Monitor (educativo)
    
    packetCount++;
    
    Serial.println(F("\n========================================"));
    Serial.print(F("ENVIANDO PAQUETE #"));
    Serial.println(packetCount);
    Serial.println(F("========================================"));
    
    // Mostrar datos del sensor (sin encriptar)
    Serial.println(F("\nDatos del sistema (SIN encriptar):"));
    Serial.print(F("  Timestamp: "));
    Serial.print(timestamp);
    Serial.println(F(" segundos"));
    Serial.println(F("  Mensaje: hola mundo"));
    
    // Mostrar payload en HEX (como se transmite)
    Serial.println(F("\nPayload ENCRIPTADO (HEX - tal como se transmite):"));
    Serial.print(F("  "));
    for (int i = 0; i < 15; i++) {
        if (appData[i] < 0x10) Serial.print("0");
        Serial.print(appData[i], HEX);
        if (i < 14) Serial.print(" ");
    }
    Serial.println();
    
    // Mostrar payload desencriptado (interpretación byte por byte)
    Serial.println(F("\nPayload DESENCRIPTADO (interpretado byte por byte):"));
    
    Serial.print(F("  [0-3] Timestamp (Little-Endian): "));
    uint32_t ts_recalc = appData[0] | (appData[1] << 8) | 
                         (appData[2] << 16) | (appData[3] << 24);
    Serial.print(ts_recalc);
    Serial.println(F(" segundos"));
    
    Serial.print(F("  [4-13] Mensaje (ASCII): "));
    for (int i = 4; i < 14; i++) {
        Serial.print((char)appData[i]);
    }
    Serial.println();
    
    Serial.print(F("  [14] Checksum (suma de bytes 0-13): 0x"));
    if (appData[14] < 0x10) Serial.print("0");
    Serial.println(appData[14], HEX);
    
    Serial.println(F("\nInformacion tecnica del envio:"));
    Serial.print(F("  Puerto LoRaWAN: "));
    Serial.print(port);
    Serial.print(F(" | Tamanio del payload: "));
    Serial.print(appDataSize);
    Serial.println(F(" bytes"));
    
    Serial.println(F("========================================"));
}

/* ============================================================
 * SECCIÓN 5: FUNCIÓN - SETUP (INICIALIZACIÓN)
 * ============================================================ */

void setup() {
    Serial.begin(115200);
    delay(1500);
    
    Serial.println(F("\n"));
    Serial.println(F("====================================="));
    Serial.println(F("  CubeCell (HTCC-AB01)"));
    Serial.println(F("  LoRaWAN OTAA - Semana 7"));
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
    
    Serial.println(F("ESTRUCTURA DEL PAYLOAD (15 bytes):"));
    Serial.println(F("Bytes 0-3:   Timestamp (4 bytes)"));
    Serial.println(F("Bytes 4-13:  'hola mundo' (10 bytes)"));
    Serial.println(F("Byte 14:     Checksum (1 byte)"));
    Serial.println();

    // Alimentar RGB LED si está habilitado
    pinMode(Vext, OUTPUT);
    digitalWrite(Vext, LOW);
    delay(10);

    // Iniciar máquina de estados
    deviceState = DEVICE_STATE_INIT;
    LoRaWAN.ifskipjoin();

    Serial.println(F("INICIANDO PROCEDIMIENTO OTAA JOIN"));
    Serial.println(F("Esperando conexion a gateway...\n"));
}

/* ============================================================
 * SECCIÓN 6: FUNCIÓN - LOOP (MÁQUINA DE ESTADOS)
 * ============================================================
 * 
 * La máquina de estados es manejada automáticamente por la librería.
 * El dispositivo transita entre estados:
 * INIT → JOIN → SEND → CYCLE → SLEEP → (esperar) → SEND → ...
 * 
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
 *   // Bytes 0-3: Timestamp (Little-Endian)
 *   var timestamp = bytes[0] | (bytes[1] << 8) | 
 *                   (bytes[2] << 16) | (bytes[3] << 24);
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
 *     timestamp: timestamp,
 *     mensaje: mensaje,
 *     checksum: '0x' + checksum.toString(16)
 *   };
 * }
 * 
 * =====================================================================
 */