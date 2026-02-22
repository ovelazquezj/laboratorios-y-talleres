#include "LoRaWan_APP.h"
#include "Arduino.h"
#include <DHT.h>

/* ============================================================
 * CubeCell (HTCC-AB01) - LoRaWAN OTAA CON SENSORES
 * SEMANA 7 - ARQUITECTURA MODULAR EDUCATIVA
 * ============================================================
 * 
 * OBJETIVO EDUCATIVO:
 * Demostrar arquitectura profesional para IoT con LoRaWAN:
 * - Lectura de sensores reales (HC-SR04, DHT11)
 * - Separación de responsabilidades (modular)
 * - Lectura de timestamp del sistema
 * - Creación estructurada de payloads
 * - Encriptación y desencriptación de datos
 * - OTAA Join real
 * - Comunicación con ChirpStack
 * 
 * SENSORES:
 * - HC-SR04:  Sensor ultrasónico de distancia
 * - DHT11:    Sensor de temperatura y humedad
 * 
 * FLUJO DE DATOS:
 * [HC-SR04] → [readDistance()]
 * [DHT11]   → [readTemperatureHumidity()]
 * [Sensors] → [prepareTxFrame()] → [Payload] → 
 * [LoRaWAN] → [ChirpStack]
 * 
 * ============================================================ */

/* ============================================================
 * SECCIÓN 0: CONFIGURACIÓN DE PINES (SENSORES)
 * ============================================================ */

// HC-SR04 Ultrasonic Sensor Pins
#define HC_TRIG_PIN GPIO3      // Pin 6  - Trigger (3.3V)
#define HC_ECHO_PIN GPIO2      // Pin 7  - Echo (3.3V con divisor de voltaje)

// DHT11 Temperature & Humidity Sensor
#define DHT_PIN GPIO4          // Pin 14 - Data pin (3.3V con pull-up 4.7k)
#define DHTTYPE DHT11          // Sensor type
DHT dht(DHT_PIN, DHTTYPE);

// Variables para almacenar lecturas
float sensorDistance = 0.0;    // Distancia en cm
float sensorTemperature = 0.0; // Temperatura en °C
float sensorHumidity = 0.0;    // Humedad en %

// Contador de lecturas
static unsigned long sensorReadCount = 0;

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
 * SECCIÓN 4: FUNCIÓN - LEER DISTANCIA (HC-SR04)
 * ============================================================
 * 
 * FUNCIONAMIENTO:
 * 1. Enviar pulso de 10µs al pin TRIG
 * 2. Medir duración del pulso ALTO en pin ECHO
 * 3. Calcular distancia: (duración_µs × 0.034) / 2 cm
 * 
 * DIVISOR DE VOLTAJE (ECHO):
 *   HC-SR04 ECHO (5V) → R1(2.7k) → GPIO2 → R2(4.7k) → GND
 *   Salida: ≈ 3.3V (seguro para HTCC-AB01)
 * 
 * ============================================================ */

float readDistance() {
    // Enviar pulso de disparo (10µs)
    digitalWrite(HC_TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(HC_TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(HC_TRIG_PIN, LOW);
    
    // Medir duración del pulso ECHO
    unsigned long duration = pulseIn(HC_ECHO_PIN, HIGH, 30000);  // timeout 30ms
    
    // Calcular distancia en cm
    // Velocidad del sonido ≈ 340 m/s = 0.034 cm/µs
    // Distancia = (duración × velocidad) / 2 (viaje de ida y vuelta)
    float distance = (duration * 0.034) / 2;
    
    // Validar rango sensato (5cm a 400cm para HC-SR04)
    if (distance < 2 || distance > 400) {
        distance = 0;  // Valor inválido
    }
    
    return distance;
}

/* ============================================================
 * SECCIÓN 5: FUNCIÓN - LEER TEMPERATURA Y HUMEDAD (DHT11)
 * ============================================================
 * 
 * FUNCIONAMIENTO:
 * 1. Iniciar lectura del DHT11
 * 2. Esperar respuesta (protocolo 1-wire)
 * 3. Retornar temperatura y humedad
 * 
 * PULL-UP RESISTOR (DATA):
 *   DHT11 DATA → R(4.7k) → VDD(3.3V)
 *   Requerido para protocolo 1-wire
 * 
 * NOTA: Máximo 1 lectura por segundo (limitación del sensor)
 * 
 * ============================================================ */

bool readTemperatureHumidity() {
    // Leer valores del DHT11
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    // Validar lecturas
    if (isnan(temp) || isnan(hum)) {
        Serial.println(F("⚠️  Error al leer DHT11 (checksum falló)"));
        return false;
    }
    
    // Almacenar valores globales
    sensorTemperature = temp;
    sensorHumidity = hum;
    
    return true;
}

/* ============================================================
 * SECCIÓN 6: FUNCIÓN - PREPARAR PAQUETE DE DATOS
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
 * BYTES 4-5: Distancia HC-SR04 (2 bytes, uint16, Big-Endian)
 *   Byte 4: (distance >> 8) & 0xFF        (byte alto)
 *   Byte 5: distance & 0xFF                (byte bajo)
 *   Rango: 0-65535 cm (resolución: 0.01 cm)
 * 
 * BYTE 6: Temperatura DHT11 (1 byte, uint8)
 *   Rango: 0-50°C (resolución: 1°C, redondeado)
 * 
 * BYTE 7: Humedad DHT11 (1 byte, uint8)
 *   Rango: 20-80% (resolución: 1%, redondeado)
 * 
 * BYTES 8-13: Reservado para expansión futura (6 bytes)
 *   Se envían como ceros
 * 
 * BYTE 14: Checksum (suma de verificación)
 *   Suma de bytes 0-13, modulo 256
 *   Detecta corrupción de datos
 * 
 * TOTAL: 15 bytes
 * 
 * ============================================================ */

static void prepareTxFrame(uint8_t port) {
    // PASO 1: Leer sensores
    sensorReadCount++;
    
    Serial.println(F("\n>>> LECTURA DE SENSORES <<<"));
    
    // Leer HC-SR04
    sensorDistance = readDistance();
    Serial.print(F("  HC-SR04 Distancia: "));
    Serial.print(sensorDistance);
    Serial.println(F(" cm"));
    
    // Leer DHT11 (máximo 1 vez por segundo)
    delay(1000);  // Esperar 1 segundo antes de leer DHT11
    if (!readTemperatureHumidity()) {
        sensorTemperature = 0;
        sensorHumidity = 0;
    }
    Serial.print(F("  DHT11 Temperatura: "));
    Serial.print(sensorTemperature);
    Serial.println(F(" °C"));
    Serial.print(F("  DHT11 Humedad: "));
    Serial.print(sensorHumidity);
    Serial.println(F(" %"));
    
    // PASO 2: Obtener timestamp del sistema (en segundos)
    uint32_t timestamp = millis() / 1000;
    
    // PASO 3: Construir payload de 15 bytes
    
    // BYTES 0-3: Timestamp en Little-Endian
    appData[0] = timestamp & 0xFF;
    appData[1] = (timestamp >> 8) & 0xFF;
    appData[2] = (timestamp >> 16) & 0xFF;
    appData[3] = (timestamp >> 24) & 0xFF;
    
    // BYTES 4-5: Distancia en Big-Endian (uint16)
    uint16_t distanceInt = (uint16_t)(sensorDistance * 100);  // Convertir a centímetros enteros
    appData[4] = (distanceInt >> 8) & 0xFF;      // Byte alto
    appData[5] = distanceInt & 0xFF;             // Byte bajo
    
    // BYTE 6: Temperatura (uint8, redondeado)
    appData[6] = (uint8_t)(sensorTemperature);
    
    // BYTE 7: Humedad (uint8, redondeado)
    appData[7] = (uint8_t)(sensorHumidity);
    
    // BYTES 8-13: Reservado (llenar con ceros)
    for (int i = 8; i < 14; i++) {
        appData[i] = 0x00;
    }
    
    // BYTE 14: Checksum (suma de bytes 0-13)
    appData[14] = 0;
    for (int i = 0; i < 14; i++) {
        appData[14] += appData[i];
    }
    
    appDataSize = 15;  // Total: 15 bytes
    
    // PASO 4: Mostrar información en Serial Monitor (educativo)
    
    packetCount++;
    
    Serial.println(F("\n========================================"));
    Serial.print(F("ENVIANDO PAQUETE #"));
    Serial.println(packetCount);
    Serial.println(F("========================================"));
    
    // Mostrar datos del sensor (sin encriptar)
    Serial.println(F("\nDatos de sensores (SIN encriptar):"));
    Serial.print(F("  Timestamp: "));
    Serial.print(timestamp);
    Serial.println(F(" segundos"));
    Serial.print(F("  Distancia (HC-SR04): "));
    Serial.print(sensorDistance);
    Serial.println(F(" cm"));
    Serial.print(F("  Temperatura (DHT11): "));
    Serial.print(sensorTemperature);
    Serial.println(F(" °C"));
    Serial.print(F("  Humedad (DHT11): "));
    Serial.print(sensorHumidity);
    Serial.println(F(" %"));
    
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
    
    Serial.print(F("  [4-5] Distancia (Big-Endian): "));
    uint16_t dist_recalc = (appData[4] << 8) | appData[5];
    Serial.print((float)dist_recalc / 100.0);
    Serial.println(F(" cm"));
    
    Serial.print(F("  [6] Temperatura (uint8): "));
    Serial.print(appData[6]);
    Serial.println(F(" °C"));
    
    Serial.print(F("  [7] Humedad (uint8): "));
    Serial.print(appData[7]);
    Serial.println(F(" %"));
    
    Serial.print(F("  [8-13] Reservado: "));
    for (int i = 8; i < 14; i++) {
        Serial.print("0x");
        if (appData[i] < 0x10) Serial.print("0");
        Serial.print(appData[i], HEX);
        if (i < 13) Serial.print(" ");
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
 * SECCIÓN 7: FUNCIÓN - SETUP (INICIALIZACIÓN)
 * ============================================================ */

void setup() {
    Serial.begin(115200);
    delay(1500);
    
    Serial.println(F("\n"));
    Serial.println(F("====================================="));
    Serial.println(F("  CubeCell (HTCC-AB01)"));
    Serial.println(F("  LoRaWAN OTAA con Sensores"));
    Serial.println(F("  Semana 7"));
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
    
    Serial.println(F("SENSORES CONECTADOS:"));
    Serial.println(F("- HC-SR04 (Ultrasónico de distancia)"));
    Serial.println(F("  TRIG: GPIO3 (Pin 6)"));
    Serial.println(F("  ECHO: GPIO2 (Pin 7) con divisor voltaje"));
    Serial.println(F("- DHT11 (Temp/Humedad)"));
    Serial.println(F("  DATA: GPIO4 (Pin 14) con pull-up 4.7k"));
    Serial.println();
    
    Serial.println(F("ESTRUCTURA DEL PAYLOAD (15 bytes):"));
    Serial.println(F("Bytes 0-3:   Timestamp (4 bytes)"));
    Serial.println(F("Bytes 4-5:   Distancia HC-SR04 (2 bytes, Big-Endian)"));
    Serial.println(F("Byte 6:      Temperatura DHT11 (1 byte)"));
    Serial.println(F("Byte 7:      Humedad DHT11 (1 byte)"));
    Serial.println(F("Bytes 8-13:  Reservado (6 bytes)"));
    Serial.println(F("Byte 14:     Checksum (1 byte)"));
    Serial.println();

    // Inicializar pines de HC-SR04
    pinMode(HC_TRIG_PIN, OUTPUT);
    pinMode(HC_ECHO_PIN, INPUT);
    digitalWrite(HC_TRIG_PIN, LOW);
    
    // Inicializar DHT11
    dht.begin();
    
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
 * SECCIÓN 8: FUNCIÓN - LOOP (MÁQUINA DE ESTADOS)
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
 * Copiar y pegar esta función en el "Payload Codec" de ChirpStack
 * (Configuración de la Aplicación → Payload Codec Type: Custom JavaScript)
 * 
 * function Decode(fPort, bytes) {
 *   // Bytes 0-3: Timestamp (Little-Endian)
 *   var timestamp = bytes[0] | (bytes[1] << 8) | 
 *                   (bytes[2] << 16) | (bytes[3] << 24);
 *   
 *   // Bytes 4-5: Distancia (Big-Endian, uint16) en centímetros × 100
 *   var distanceRaw = (bytes[4] << 8) | bytes[5];
 *   var distance = distanceRaw / 100.0;  // Convertir a cm
 *   
 *   // Byte 6: Temperatura (uint8) en °C
 *   var temperature = bytes[6];
 *   
 *   // Byte 7: Humedad (uint8) en %
 *   var humidity = bytes[7];
 *   
 *   // Bytes 8-13: Reservado (no procesados)
 *   
 *   // Byte 14: Checksum
 *   var checksum = bytes[14];
 *   
 *   return {
 *     timestamp_s: timestamp,
 *     distance_cm: distance,
 *     temperature_c: temperature,
 *     humidity_percent: humidity,
 *     checksum: '0x' + checksum.toString(16).padStart(2, '0')
 *   };
 * }
 * 
 * =====================================================================
 */
