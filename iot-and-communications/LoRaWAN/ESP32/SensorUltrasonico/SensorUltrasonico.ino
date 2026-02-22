/*
 * =====================================================================
 * TTGO T3 LoRaWAN + HC-SR04 - CÓDIGO PARA LABORATORIO SEMANA 8
 * =====================================================================
 * 
 * OBJETIVO:
 * Implementar un sistema IoT completo que:
 * 1. Lee distancia de un sensor ultrasónico HC-SR04
 * 2. Transmite los datos vía LoRaWAN a ChirpStack
 * 3. Muestra información en display OLED local
 * 
 * CONCEPTOS CLAVE:
 * - LoRaWAN: Protocolo de comunicación de largo alcance y bajo consumo
 * - OTAA: Over-The-Air Activation (activación segura mediante Join)
 * - Sensores ultrasónicos: Medición de distancia mediante ondas sonoras
 * - IoT: Integración de sensores, conectividad y procesamiento
 * 
 * TOPOLOGÍA DEL SISTEMA:
 * [HC-SR04] --GPIO--> [ESP32] --LoRa--> [Gateway] --Internet--> [ChirpStack]
 * 
 * Curso: Comunicaciones e IoT
 * Semana: 8 - Sensores y LoRaWAN
 * =====================================================================
 */

// =====================================================================
// 1. LIBRERÍAS NECESARIAS
// =====================================================================

#include <Wire.h>        // Comunicación I2C para el display OLED
#include <U8g2lib.h>     // Librería gráfica para pantallas OLED
#include <SPI.h>         // Comunicación SPI para el módulo LoRa
#include <lmic.h>        // IBM LMIC (LoraMAC-in-C) - Stack LoRaWAN
#include <hal/hal.h>     // Hardware Abstraction Layer para LMIC

// =====================================================================
// 2. CONFIGURACIÓN DEL DISPLAY OLED
// =====================================================================

/*
 * Display: SSD1306 de 128x64 píxeles
 * Interfaz: I2C (2 cables: SDA y SCL)
 * Dirección I2C: 0x3C (por defecto)
 * Pines ESP32: SDA=GPIO21, SCL=GPIO22
 */
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// =====================================================================
// 3. CONFIGURACIÓN DEL SENSOR HC-SR04
// =====================================================================

/*
 * SENSOR ULTRASÓNICO HC-SR04
 * ==========================
 * 
 * PRINCIPIO DE FUNCIONAMIENTO:
 * 1. El sensor emite un pulso ultrasónico (40 kHz) por el transmisor
 * 2. El pulso rebota en un objeto y regresa al receptor
 * 3. Se mide el tiempo entre emisión y recepción (tiempo de vuelo)
 * 4. Distancia = (Tiempo × Velocidad_Sonido) / 2
 * 
 * VELOCIDAD DEL SONIDO:
 * - En aire a 20°C: 343 m/s = 0.0343 cm/µs
 * - Dividimos entre 2 porque el sonido va y vuelve
 * 
 * RANGO DE MEDICIÓN:
 * - Mínimo: 2 cm
 * - Máximo: 400 cm (teórico), ~200 cm (práctico)
 * 
 * ALIMENTACIÓN:
 * - VCC: 5V (conectar a pin VIN del TTGO)
 * - GND: Ground
 * 
 * ⚠️  IMPORTANTE: El pin ECHO emite 5V, pero el ESP32 tolera máximo 3.3V
 * Se requiere un DIVISOR DE VOLTAJE (ver guía del laboratorio)
 * 
 * PINES:
 * - TRIG (Trigger): Envía señal para iniciar medición (tolera 3.3V)
 * - ECHO: Devuelve pulso proporcional a la distancia (emite 5V - PELIGRO)
 */

#define TRIG_PIN 25  // GPIO 25 - Pin de salida para trigger
#define ECHO_PIN 34  // GPIO 34 - Pin de entrada (input-only)

// =====================================================================
// 4. CONFIGURACIÓN DE PINES - MÓDULO LoRa SX1276
// =====================================================================

/*
 * El módulo LoRa se comunica mediante SPI (Serial Peripheral Interface)
 * 
 * SPI es un bus síncrono con 4 señales principales:
 * - SCK (Clock):  Señal de reloj generada por el maestro (ESP32)
 * - MISO (Master In, Slave Out): Datos del SX1276 al ESP32
 * - MOSI (Master Out, Slave In): Datos del ESP32 al SX1276
 * - SS (Slave Select): Selecciona el dispositivo SPI activo
 * 
 * Además, el SX1276 tiene pines de interrupción (DIO) para eventos:
 * - DIO0: Transmisión/Recepción completa
 * - DIO1: Timeout de recepción, FHSS change channel
 * - DIO2: FHSS change channel (modo FDD)
 */

#define LORA_SCK   5    // GPIO 5  - SPI Clock
#define LORA_MISO  19   // GPIO 19 - SPI Master In Slave Out
#define LORA_MOSI  27   // GPIO 27 - SPI Master Out Slave In
#define LORA_SS    18   // GPIO 18 - SPI Slave Select (Chip Select)
#define LORA_RST   14   // GPIO 14 - Reset del módulo LoRa
#define LORA_DIO0  26   // GPIO 26 - Interrupción DIO0 (TX/RX Done)
#define LORA_DIO1  33   // GPIO 33 - Interrupción DIO1 (RX Timeout)
#define LORA_DIO2  32   // GPIO 32 - Interrupción DIO2 (FHSS)

// =====================================================================
// 5. CREDENCIALES LoRaWAN - MODO OTAA
// =====================================================================

/*
 * OTAA (Over-The-Air Activation) - Proceso de Join
 * ================================================
 * 
 * OTAA es el método recomendado para activación segura. El proceso:
 * 
 * 1. El dispositivo envía un Join Request con:
 *    - DevEUI: Identificador único del dispositivo (EUI-64)
 *    - JoinEUI/AppEUI: Identificador de la aplicación (EUI-64)
 *    - Nonce: Número aleatorio para evitar replay attacks
 * 
 * 2. El Network Server verifica las credenciales y responde con Join Accept:
 *    - DevAddr: Dirección de red asignada al dispositivo (32 bits)
 *    - Session Keys: Claves de sesión derivadas de AppKey
 *      * NwkSKey: Network Session Key (cifrado MAC)
 *      * AppSKey: Application Session Key (cifrado payload)
 * 
 * 3. El dispositivo ya puede enviar y recibir datos cifrados
 * 
 * ⚠️  IMPORTANTE: Estas credenciales deben coincidir EXACTAMENTE con
 * las configuradas en tu aplicación de ChirpStack.
 */

// DevEUI: Identificador único del dispositivo (LSB format)
/*static const u1_t PROGMEM DEVEUI[8] = { 
    0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x02 
};*/

// JoinEUI/AppEUI: Identificador de la aplicación (LSB format)
/*static const u1_t PROGMEM APPEUI[8] = { 
    0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x50 
};*/

// AppKey: Clave secreta de 128 bits (MSB format)
/*static const u1_t PROGMEM APPKEY[16] = { 
    0x8A, 0xC5, 0x83, 0xDF, 0xEE, 0xC7, 0x6C, 0x81, 
    0xFF, 0xD1, 0x9C, 0xCF, 0xE7, 0x6B, 0x73, 0xBF 
};*/

// DevEUI:  0238920535e871db (convertido a LSB)
static const u1_t PROGMEM DEVEUI[8] = { 0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x02 };

// JoinEUI/AppEUI: 505246f87143fd8a (convertido a LSB)
static const u1_t PROGMEM APPEUI[8] = { 0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x50 };

// AppKey: (ya en MSB)
static const u1_t PROGMEM APPKEY[16] = { 0x8A, 0xC5, 0x83, 0xDF, 0xEE, 0xC7, 0x6C, 0x81, 0xFF, 0xD1, 0x9C, 0xCF, 0xE7, 0x6B, 0x73, 0xBF };


// Funciones callback requeridas por LMIC
void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

// =====================================================================
// 6. VARIABLES GLOBALES DEL SISTEMA
// =====================================================================

/*
 * Job de transmisión
 * ------------------
 * LMIC usa un sistema de jobs (tareas programadas) para manejar eventos.
 * osjob_t es una estructura que representa una tarea en el scheduler.
 */
static osjob_t sendjob;

/*
 * Configuración de temporización
 * ------------------------------
 * LoRaWAN tiene restricciones de duty cycle (tiempo de transmisión permitido)
 * En Europa: 1% duty cycle (36 segundos de TX por hora)
 * En USA: No hay restricción de duty cycle, pero hay fair use policy
 */
const unsigned TX_INTERVAL = 30;      // Intervalo de transmisión en segundos

/*
 * Variables de estado LoRaWAN
 * ---------------------------
 */
bool deviceJoined = false;            // ¿El dispositivo completó el Join?
unsigned long packetCount = 0;        // Contador de paquetes enviados

/*
 * Variables del sensor HC-SR04
 * ----------------------------
 */
float currentDistance = 0.0;          // Última distancia medida en cm
unsigned long measurementCount = 0;   // Contador total de mediciones
long lastDuration = 0;                // Duración del último pulso ECHO en µs
bool echoReceived = false;            // ¿Se recibió respuesta del sensor?

/*
 * Timing de mediciones
 * --------------------
 */
unsigned long lastMeasurement = 0;
const unsigned MEASUREMENT_INTERVAL = 5;  // Medir cada 5 segundos

/*
 * Pin Mapping para LMIC
 * ---------------------
 * Esta estructura le indica a LMIC qué pines usar para comunicarse
 * con el módulo LoRa SX1276/SX1278.
 */
const lmic_pinmap lmic_pins = {
    .nss = LORA_SS,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = LORA_RST,
    .dio = { LORA_DIO0, LORA_DIO1, LORA_DIO2 }
};

// =====================================================================
// 7. FUNCIÓN: LEER SENSOR HC-SR04
// =====================================================================

float readDistance() {
    /*
     * LECTURA DEL SENSOR HC-SR04
     * ==========================
     * 
     * PROTOCOLO DE COMUNICACIÓN:
     * 1. Poner TRIG en LOW por al menos 2 µs (limpiar señal)
     * 2. Poner TRIG en HIGH por 10 µs (iniciar medición)
     * 3. Poner TRIG en LOW
     * 4. Esperar que ECHO pase de LOW a HIGH
     * 5. Medir duración del pulso en ECHO
     * 6. Calcular distancia: distancia = (duración × 0.034) / 2
     * 
     * CÁLCULO:
     * - Velocidad del sonido: 343 m/s = 0.0343 cm/µs
     * - Distancia = Tiempo × Velocidad / 2 (ida y vuelta)
     * - Distancia (cm) = Tiempo (µs) × 0.0343 / 2
     * - Distancia (cm) = Tiempo (µs) × 0.01715
     * 
     * TIMEOUT:
     * - 50ms = 50000 µs
     * - Corresponde a ~850 cm (fuera del rango del sensor)
     * - Evita que el programa se bloquee si no hay respuesta
     */
    
    // Paso 1: Limpiar señal TRIG
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(5);
    
    // Paso 2 y 3: Enviar pulso de trigger
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);  // Pulso de 10 µs según especificación
    digitalWrite(TRIG_PIN, LOW);
    
    // Paso 4 y 5: Medir duración del pulso ECHO
    /*
     * pulseIn(pin, valor, timeout):
     * - Espera a que el pin cambie al valor especificado (HIGH)
     * - Mide cuánto tiempo permanece en ese valor
     * - Retorna 0 si se excede el timeout
     */
    lastDuration = pulseIn(ECHO_PIN, HIGH, 50000);
    
    // Verificar si se recibió respuesta
    if (lastDuration == 0) {
        echoReceived = false;
        return -1.0;  // -1 indica error o sin objeto detectado
    }
    
    echoReceived = true;
    
    // Paso 6: Calcular distancia
    /*
     * FÓRMULA:
     * distancia (cm) = (duración (µs) × velocidad_sonido (cm/µs)) / 2
     * distancia (cm) = (duración × 0.0343) / 2
     * distancia (cm) = duración × 0.01715
     * 
     * Simplificado como: duración × 0.034 / 2
     */
    float distance = (lastDuration * 0.034) / 2;
    
    return distance;
}

// =====================================================================
// 8. FUNCIÓN: ACTUALIZAR DISPLAY OLED
// =====================================================================

void updateDisplay() {
    /*
     * Esta función actualiza el contenido del display OLED.
     * 
     * Flujo de trabajo con U8g2:
     * 1. clearBuffer(): Limpia el buffer de memoria
     * 2. setFont(): Selecciona la fuente tipográfica
     * 3. drawStr(): Dibuja texto en el buffer
     * 4. sendBuffer(): Transfiere el buffer a la pantalla física
     */
    
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x12_tf);
    
    // Línea 1: Estado LoRaWAN
    if (deviceJoined) {
        u8g2.drawStr(0, 10, "LoRa: CONECTADO");
    } else {
        u8g2.drawStr(0, 10, "LoRa: JOINING...");
    }
    
    // Línea 2: Estado del sensor
    if (echoReceived) {
        u8g2.drawStr(0, 22, "Sensor: OK");
    } else {
        u8g2.drawStr(0, 22, "Sensor: SIN RESPUESTA");
    }
    
    // Línea 3: Distancia medida
    if (currentDistance >= 0 && echoReceived) {
        char distStr[32];
        sprintf(distStr, "Dist: %.1f cm", currentDistance);
        u8g2.drawStr(0, 34, distStr);
    } else {
        u8g2.drawStr(0, 34, "Sin lectura valida");
    }
    
    // Línea 4: Contador de paquetes enviados
    char pktStr[32];
    sprintf(pktStr, "Paquetes: %lu", packetCount);
    u8g2.drawStr(0, 46, pktStr);
    
    // Línea 5: Información de red
    u8g2.drawStr(0, 58, "US915 SubBand 2");
    
    u8g2.sendBuffer();
}

// =====================================================================
// 9. DECLARACIÓN ANTICIPADA
// =====================================================================

void do_send(osjob_t* j);

// =====================================================================
// 10. MANEJADOR DE EVENTOS LoRaWAN
// =====================================================================

void onEvent (ev_t ev) {
    /*
     * CALLBACK DE EVENTOS
     * ===================
     * 
     * LMIC llama esta función cuando ocurren eventos importantes en el
     * stack LoRaWAN. Es el corazón de la máquina de estados del protocolo.
     * 
     * EVENTOS PRINCIPALES:
     * - EV_JOINING: Iniciando procedimiento de Join
     * - EV_JOINED: Join exitoso, dispositivo activado
     * - EV_JOIN_FAILED: Join falló, se reintentará
     * - EV_TXCOMPLETE: Transmisión completada (y ventanas RX cerradas)
     */
    
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
            /*
             * El dispositivo está enviando un Join Request.
             * Se construye con DevEUI, JoinEUI y un nonce aleatorio.
             * Se espera un Join Accept del Network Server.
             */
            Serial.println(F("EV_JOINING - Intentando unirse a la red..."));
            Serial.println(F("  → Enviando Join Request"));
            Serial.println(F("  → Esperando Join Accept..."));
            deviceJoined = false;
            updateDisplay();
            break;
        
        case EV_JOINED:
            /*
             * ¡Join exitoso!
             * El Network Server asignó un DevAddr y derivó las claves de sesión.
             * El dispositivo ya puede enviar y recibir datos cifrados.
             */
            Serial.println(F("========================================"));
            Serial.println(F("✅ EV_JOINED - ¡CONECTADO!"));
            Serial.println(F("========================================"));
            Serial.println(F("  → DevAddr asignado"));
            Serial.println(F("  → Claves de sesión establecidas"));
            Serial.println(F("  → Listo para transmitir datos"));
            
            LMIC_setLinkCheckMode(0);
            deviceJoined = true;
            updateDisplay();
            
            // Programar primer envío después de 2 segundos
            Serial.println(F("  → Programando primer envío..."));
            os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(2), do_send);
            break;
        
        case EV_JOIN_FAILED:
            /*
             * El Join Request falló. Posibles causas:
             * - Gateway fuera de alcance
             * - Credenciales incorrectas
             * - Gateway no conectado al servidor
             * LMIC reintentará automáticamente.
             */
            Serial.println(F("❌ EV_JOIN_FAILED"));
            Serial.println(F("  Verifica:"));
            Serial.println(F("  - Gateway encendido y conectado"));
            Serial.println(F("  - Credenciales en ChirpStack"));
            Serial.println(F("  - Dispositivo registrado"));
            Serial.println(F("  → Reintentando..."));
            deviceJoined = false;
            updateDisplay();
            break;
        
        case EV_REJOIN_FAILED:
            Serial.println(F("EV_REJOIN_FAILED"));
            break;
        
        case EV_TXCOMPLETE:
            /*
             * TRANSMISIÓN COMPLETA
             * ====================
             * El uplink fue transmitido y las ventanas RX cerraron.
             * 
             * CLASE A - VENTANAS DE RECEPCIÓN:
             * RX1: 1 segundo después del uplink
             * RX2: 2 segundos después del uplink
             */
            Serial.println(F("========================================"));
            Serial.println(F("📤 EV_TXCOMPLETE"));
            Serial.println(F("========================================"));
            Serial.println(F("  → Uplink enviado"));
            Serial.println(F("  → Ventanas RX1 y RX2 cerradas"));
            
            // Verificar si se recibió ACK
            if (LMIC.txrxFlags & TXRX_ACK)
                Serial.println(F("  ✅ ACK recibido"));
            
            // Verificar si se recibió downlink
            if (LMIC.dataLen) {
                Serial.print(F("  📥 Downlink recibido ("));
                Serial.print(LMIC.dataLen);
                Serial.println(F(" bytes):"));
                Serial.print(F("     Payload: "));
                for (int i = 0; i < LMIC.dataLen; i++) {
                    if (LMIC.frame[LMIC.dataBeg + i] < 0x10) 
                        Serial.print("0");
                    Serial.print(LMIC.frame[LMIC.dataBeg + i], HEX);
                    Serial.print(" ");
                }
                Serial.println();
            }
            
            // Programar siguiente transmisión
            if (deviceJoined) {
                Serial.print(F("  ⏱️  Próximo uplink en "));
                Serial.print(TX_INTERVAL);
                Serial.println(F(" segundos"));
                Serial.println(F("========================================"));
                os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(TX_INTERVAL), do_send);
            }
            updateDisplay();
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
        default:
            Serial.print(F("⚠️  Evento: "));
            Serial.println((unsigned) ev);
            break;
    }
}

// =====================================================================
// 11. FUNCIÓN: ENVIAR DATOS DEL SENSOR
// =====================================================================

void do_send(osjob_t* j) {
    /*
     * CONSTRUCCIÓN Y ENVÍO DEL PAYLOAD
     * =================================
     * 
     * Esta función lee el sensor, construye un payload con los datos
     * y lo envía vía LoRaWAN al servidor ChirpStack.
     * 
     * ESTRUCTURA DEL PAYLOAD (10 bytes):
     * ----------------------------------
     * Byte 0:     Tipo de sensor (0x01 = HC-SR04)
     * Bytes 1-2:  Distancia en décimas de cm (little-endian)
     * Byte 3:     Versión hardware (0x05 = 5V con divisor)
     * Bytes 4-7:  Timestamp en segundos (little-endian)
     * Byte 8:     Estado del sensor (0x01=OK, 0x00=Error)
     * Byte 9:     Contador de paquetes (módulo 256)
     */
    
    // Verificar que no haya otra transmisión en proceso
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("⚠️  TX/RX en progreso, esperando..."));
        return;
    }

    packetCount++;

    // Construir payload
    uint8_t payload[10];
    
    // Byte 0: Tipo de sensor
    payload[0] = 0x01;  // 0x01 = HC-SR04 ultrasónico
    
    // Bytes 1-2: Distancia en décimas de cm
    uint16_t distanceInt;
    if (currentDistance >= 0 && echoReceived) {
        // Multiplicar por 10 para mantener 1 decimal
        // Ejemplo: 123.4 cm → 1234
        distanceInt = (uint16_t)(currentDistance * 10);
    } else {
        // 0xFFFF indica sin lectura
        distanceInt = 0xFFFF;
    }
    payload[1] = distanceInt & 0xFF;         // LSB
    payload[2] = (distanceInt >> 8) & 0xFF;  // MSB
    
    // Byte 3: Versión hardware
    payload[3] = 0x05;  // 0x05 = 5V con divisor de voltaje
    
    // Bytes 4-7: Timestamp en segundos
    uint32_t timestamp = millis() / 1000;
    payload[4] = timestamp & 0xFF;
    payload[5] = (timestamp >> 8) & 0xFF;
    payload[6] = (timestamp >> 16) & 0xFF;
    payload[7] = (timestamp >> 24) & 0xFF;
    
    // Byte 8: Estado del sensor
    payload[8] = echoReceived ? 0x01 : 0x00;
    
    // Byte 9: Contador de paquetes
    payload[9] = packetCount & 0xFF;

    /*
     * LMIC_setTxData2()
     * -----------------
     * Encola el uplink para transmisión.
     * 
     * Parámetros:
     * 1. Puerto (FPort): 1-223 para aplicación
     * 2. Payload: Puntero al array de bytes
     * 3. Longitud: Tamaño del payload
     * 4. Confirmado: 0=Unconfirmed, 1=Confirmed
     */
    LMIC_setTxData2(1, payload, sizeof(payload), 0);
    
    // Log detallado en Serial Monitor
    Serial.println(F("========================================"));
    Serial.print(F("📤 ENVIANDO PAQUETE #"));
    Serial.println(packetCount);
    Serial.println(F("========================================"));
    
    // Información del sensor
    Serial.print(F("  Sensor HC-SR04:       "));
    if (echoReceived) {
        Serial.print(currentDistance, 1);
        Serial.println(F(" cm"));
    } else {
        Serial.println(F("SIN RESPUESTA"));
    }
    
    // Información del uplink
    Serial.print(F("  Puerto (FPort):       "));
    Serial.println(1);
    
    Serial.print(F("  Tamaño payload:       "));
    Serial.print(sizeof(payload));
    Serial.println(F(" bytes"));
    
    Serial.print(F("  Data Rate:            DR"));
    Serial.println(LMIC.datarate);
    
    Serial.print(F("  Potencia TX:          "));
    Serial.print(LMIC.txpow);
    Serial.println(F(" dBm"));
    
    Serial.print(F("  Frecuencia:           "));
    Serial.print(LMIC.freq / 1000000.0, 1);
    Serial.println(F(" MHz"));
    
    // Payload en hexadecimal
    Serial.println(F("  ----------------------------------------"));
    Serial.print(F("  Payload (HEX):        "));
    for (int i = 0; i < sizeof(payload); i++) {
        if (payload[i] < 0x10) Serial.print("0");
        Serial.print(payload[i], HEX);
        if (i < sizeof(payload) - 1) Serial.print(" ");
    }
    Serial.println();
    
    // Decodificación del payload
    Serial.println(F("  ----------------------------------------"));
    Serial.println(F("  Decodificación:"));
    Serial.print(F("    Tipo sensor:        HC-SR04 (0x"));
    Serial.print(payload[0], HEX);
    Serial.println(F(")"));
    
    Serial.print(F("    Distancia:          "));
    if (distanceInt != 0xFFFF) {
        Serial.print(distanceInt / 10.0, 1);
        Serial.println(F(" cm"));
    } else {
        Serial.println(F("Sin lectura"));
    }
    
    Serial.print(F("    Hardware:           5V con divisor"));
    Serial.println();
    
    Serial.print(F("    Timestamp:          "));
    Serial.print(timestamp);
    Serial.println(F(" seg"));
    
    Serial.print(F("    Estado sensor:      "));
    Serial.println(payload[8] ? "OK" : "ERROR");
    
    Serial.println(F("========================================"));
    Serial.println();
}

// =====================================================================
// 12. FUNCIÓN: SETUP (INICIALIZACIÓN)
// =====================================================================

void setup() {
    /*
     * INICIALIZACIÓN DEL SISTEMA
     * ==========================
     * 
     * Esta función se ejecuta UNA VEZ al iniciar el dispositivo.
     * Configura todo el hardware y el software necesario.
     */
    
    Serial.begin(115200);
    delay(2000);
    
    Serial.println(F("\n"));
    Serial.println(F("========================================"));
    Serial.println(F("  LABORATORIO SEMANA 8"));
    Serial.println(F("  TTGO T3 + HC-SR04 + LoRaWAN"));
    Serial.println(F("========================================"));
    Serial.println(F("  Curso: Comunicaciones e IoT"));
    Serial.println(F("  Sistema: Sensor + LPWAN"));
    Serial.println(F("========================================"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // CONFIGURAR SENSOR HC-SR04
    // -----------------------------------------------------------------
    
    Serial.println(F("🔧 CONFIGURANDO SENSOR HC-SR04..."));
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);
    
    Serial.println(F("  ├─ TRIG: GPIO 25 (OUTPUT)"));
    Serial.println(F("  ├─ ECHO: GPIO 34 (INPUT)"));
    Serial.println(F("  ├─ VCC:  5V (VIN del TTGO)"));
    Serial.println(F("  └─ GND:  Ground"));
    Serial.println();
    
    // Test inicial del sensor
    /*delay(500);
    Serial.println(F("🧪 PROBANDO SENSOR..."));
    currentDistance = readDistance();
    
    if (echoReceived) {
        Serial.print(F("  ✅ Sensor funcionando: "));
        Serial.print(currentDistance, 1);
        Serial.println(F(" cm"));
        Serial.print(F("     Duración pulso: "));
        Serial.print(lastDuration);
        Serial.println(F(" µs"));
    } else {
        Serial.println(F("  ⚠️  Sensor sin respuesta"));
        Serial.println(F("     Posibles causas:"));
        Serial.println(F("     - Conexiones incorrectas"));
        Serial.println(F("     - Divisor de voltaje mal armado"));
        Serial.println(F("     - No hay objeto frente al sensor"));
        Serial.println(F("     - Sensor defectuoso"));
    }
    Serial.println();
    */
    // -----------------------------------------------------------------
    // CONFIGURAR GPIOs SEGUROS
    // -----------------------------------------------------------------
    
    /*
     * GPIO 0: Boot button - INPUT con pull-up
     * GPIO 2: LED interno - OUTPUT en LOW
     */
    pinMode(0, INPUT_PULLUP);
    pinMode(2, OUTPUT);
    digitalWrite(2, LOW);

    // -----------------------------------------------------------------
    // INICIALIZAR DISPLAY OLED
    // -----------------------------------------------------------------
    
    Serial.println(F("📺 INICIALIZANDO DISPLAY OLED..."));
    
    /*
     * Configuración I2C:
     * - SDA: GPIO 21
     * - SCL: GPIO 22
     * - Velocidad: 100 kHz (Standard Mode)
     */
    Wire.begin(21, 22);
    Wire.setClock(100000);
    u8g2.begin();
    updateDisplay();
    
    Serial.println(F("  └─ ✅ OLED inicializado"));
    Serial.println();

    // -----------------------------------------------------------------
    // INICIALIZAR MÓDULO LoRa Y STACK LoRaWAN
    // -----------------------------------------------------------------
    
    Serial.println(F("📡 INICIALIZANDO MÓDULO LoRa..."));
    
    /*
     * Inicialización del bus SPI y stack LMIC:
     * 1. SPI.begin() configura los pines SPI
     * 2. os_init() inicializa el scheduler de LMIC
     * 3. LMIC_reset() reinicia el stack LoRaWAN
     */
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    os_init();
    LMIC_reset();
    
    Serial.println(F("  ├─ Bus SPI inicializado"));
    Serial.println(F("  ├─ Stack LMIC inicializado"));
    Serial.println(F("  └─ Módulo SX1276 listo"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // CONFIGURAR PLAN DE CANALES US915
    // -----------------------------------------------------------------
    
    Serial.println(F("📻 CONFIGURANDO PLAN DE CANALES..."));
    
    /*
     * US915 SUB-BANDA 2
     * =================
     * 
     * US915 tiene 72 canales divididos en 8 sub-bandas.
     * Sub-banda 2 usa los canales 8-15:
     * - Canal 8:  903.9 MHz
     * - Canal 9:  904.1 MHz
     * - Canal 10: 904.3 MHz
     * - Canal 11: 904.5 MHz
     * - Canal 12: 904.7 MHz
     * - Canal 13: 904.9 MHz
     * - Canal 14: 905.1 MHz
     * - Canal 15: 905.3 MHz
     * 
     * IMPORTANTE: El gateway debe estar configurado para la misma sub-banda.
     */
    LMIC_selectSubBand(1);  // Índice 1 = Sub-banda 2
    
    Serial.println(F("  ├─ Región:            US915"));
    Serial.println(F("  ├─ Sub-banda activa:  2 (índice 1)"));
    Serial.println(F("  ├─ Canales activos:   8-15"));
    Serial.println(F("  └─ Frecuencias:       903.9 - 905.3 MHz"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // COMPENSACIÓN DE RELOJ
    // -----------------------------------------------------------------
    
    /*
     * Compensa la imprecisión del cristal del ESP32 (±1%)
     * Esto amplía las ventanas RX para mejorar la recepción.
     */
    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
    
    Serial.println(F("⚙️  CONFIGURACIÓN ADICIONAL:"));
    Serial.println(F("  ├─ Compensación reloj: 1%"));
    Serial.println(F("  ├─ ADR:                Habilitado"));
    Serial.println(F("  ├─ Link Check:         Deshabilitado"));
    Serial.println(F("  └─ Intervalo TX:       30 segundos"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // INICIAR PROCEDIMIENTO DE JOIN
    // -----------------------------------------------------------------
    
    Serial.println(F("========================================"));
    Serial.println(F("🚀 INICIANDO PROCEDIMIENTO DE JOIN"));
    Serial.println(F("========================================"));
    Serial.println();
    Serial.println(F("  📋 CREDENCIALES:"));
    Serial.print(F("     DevEUI:  "));
    for (int i = 7; i >= 0; i--) {
        if (DEVEUI[i] < 0x10) Serial.print("0");
        Serial.print(DEVEUI[i], HEX);
        if (i > 0) Serial.print(":");
    }
    Serial.println();
    
    Serial.print(F("     AppEUI:  "));
    for (int i = 7; i >= 0; i--) {
        if (APPEUI[i] < 0x10) Serial.print("0");
        Serial.print(APPEUI[i], HEX);
        if (i > 0) Serial.print(":");
    }
    Serial.println();
    Serial.println();
    
    Serial.println(F("  ⏳ Enviando Join Request..."));
    Serial.println(F("  ⏳ Esperando Join Accept..."));
    Serial.println(F("  ⏳ Este proceso puede tomar 10-60 segundos"));
    Serial.println();
    Serial.println(F("  💡 VERIFICAR EN CHIRPSTACK:"));
    Serial.println(F("     1. Gateway conectado y activo"));
    Serial.println(F("     2. Dispositivo registrado con estas credenciales"));
    Serial.println(F("     3. Sub-banda correcta en gateway (Sub-banda 2)"));
    Serial.println();
    
    /*
     * LMIC_startJoining()
     * -------------------
     * Inicia el procedimiento OTAA de activación.
     * Enviará Join Requests hasta recibir un Join Accept.
     */
    LMIC_startJoining();
    
    lastMeasurement = millis();
}

// =====================================================================
// 13. FUNCIÓN: LOOP (BUCLE PRINCIPAL)
// =====================================================================

void loop() {
    /*
     * BUCLE PRINCIPAL
     * ===============
     * 
     * Este bucle se ejecuta continuamente y realiza tres tareas:
     * 1. Ejecutar el scheduler de LMIC (manejo de LoRaWAN)
     * 2. Leer el sensor HC-SR04 periódicamente
     * 3. Actualizar el display OLED
     * 
     * IMPORTANTE: No usar delay() largo aquí, ya que bloquearía
     * el scheduler de LMIC y causaría mal funcionamiento.
     */
    
    // -----------------------------------------------------------------
    // TAREA 1: SCHEDULER DE LMIC
    // -----------------------------------------------------------------
    
    /*
     * os_runloop_once()
     * -----------------
     * Ejecuta UNA iteración del scheduler de LMIC.
     * 
     * Esta función:
     * - Procesa interrupciones del módulo LoRa
     * - Ejecuta tareas programadas (jobs)
     * - Maneja timeouts y timers
     * - Avanza la máquina de estados de LoRaWAN
     * 
     * Debe llamarse frecuentemente (cada pocos ms) para que
     * LMIC funcione correctamente.
     */
    os_runloop_once();

    // -----------------------------------------------------------------
    // TAREA 2: LEER SENSOR PERIÓDICAMENTE
    // -----------------------------------------------------------------
    
    /*
     * Medición cada 5 segundos
     * ------------------------
     * Lee el sensor HC-SR04 y muestra el resultado en Serial Monitor.
     * La última lectura se envía a ChirpStack cada 30 segundos.
     */
    /*if (millis() - lastMeasurement >= (MEASUREMENT_INTERVAL * 1000)) {
        currentDistance = readDistance();
        measurementCount++;
        
        // Log en Serial Monitor
        Serial.print(F("[MED #"));
        Serial.print(measurementCount);
        Serial.print(F("] "));
        
        if (echoReceived) {
            Serial.print(F("✅ "));
            Serial.print(currentDistance, 1);
            Serial.print(F(" cm | Pulso: "));
            Serial.print(lastDuration);
            Serial.println(F(" µs"));
        } else {
            Serial.println(F("❌ Sensor sin respuesta"));
        }
        
        lastMeasurement = millis();
    }
    */
    // -----------------------------------------------------------------
    // TAREA 3: ACTUALIZAR DISPLAY
    // -----------------------------------------------------------------
    
    /*
     * Actualización cada 1 segundo
     * ----------------------------
     * Refresca la información en el display OLED.
     * Usamos una variable estática para recordar el último update.
     */
    static unsigned long lastDisplayUpdate = 0;
    if (millis() - lastDisplayUpdate >= 1000) {
        updateDisplay();
        lastDisplayUpdate = millis();
    }
    
    /*
     * OPTIMIZACIÓN PARA BAJO CONSUMO (OPCIONAL):
     * ===========================================
     * 
     * Para aplicaciones con batería, considera:
     * 
     * 1. Deep Sleep entre transmisiones:
     *    esp_sleep_enable_timer_wakeup(TX_INTERVAL * 1000000);
     *    esp_deep_sleep_start();
     * 
     * 2. Desactivar display OLED cuando no se necesita
     * 
     * 3. Reducir frecuencia de mediciones del sensor
     * 
     * 4. Usar Spreading Factor más bajo (DR más alto) si es posible
     * 
     * CONSUMO TÍPICO:
     * - TX @ 20 dBm: ~120 mA durante 1-2 segundos
     * - RX: ~12 mA durante ventanas RX
     * - Idle: ~80 mA (con display y sensor activos)
     * - Deep Sleep: ~10 µA
     */
}

// =====================================================================
// FIN DEL CÓDIGO
// =====================================================================

/*
 * =====================================================================
 * DECODIFICADOR PARA CHIRPSTACK
 * =====================================================================
 * 
 * Copia este código en ChirpStack para decodificar los datos:
 * Application → Codec → Custom JavaScript codec
 * 
 * function decodeUplink(input) {
 *   var bytes = input.bytes;
 *   
 *   // Byte 0: Tipo de sensor
 *   var sensorType = bytes[0];
 *   
 *   // Bytes 1-2: Distancia (little-endian)
 *   var distanceRaw = bytes[1] | (bytes[2] << 8);
 *   var distance = distanceRaw === 0xFFFF ? null : distanceRaw / 10.0;
 *   
 *   // Byte 3: Versión hardware
 *   var voltage = bytes[3] === 0x05 ? "5V con divisor" : "3.3V";
 *   
 *   // Bytes 4-7: Timestamp (little-endian)
 *   var timestamp = bytes[4] | (bytes[5] << 8) | (bytes[6] << 16) | (bytes[7] << 24);
 *   
 *   // Byte 8: Estado del sensor
 *   var sensorStatus = bytes[8] === 0x01 ? "OK" : "ERROR";
 *   
 *   // Byte 9: Contador de paquetes
 *   var packetNumber = bytes[9];
 *   
 *   return {
 *     data: {
 *       sensor_type: "HC-SR04",
 *       distance_cm: distance,
 *       hardware_version: voltage,
 *       timestamp_seconds: timestamp,
 *       sensor_status: sensorStatus,
 *       packet_number: packetNumber
 *     }
 *   };
 * }
 * 
 * =====================================================================
 * PREGUNTAS DE EVALUACIÓN
 * =====================================================================
 * 
 * 1. ¿Por qué es necesario el divisor de voltaje en el pin ECHO?
 * 
 * 2. ¿Qué diferencia hay entre OTAA y ABP? ¿Cuál es más seguro y por qué?
 * 
 * 3. ¿Qué son las ventanas RX1 y RX2? ¿Cuándo se abren?
 * 
 * 4. ¿Por qué se usa little-endian para los bytes de distancia y timestamp?
 * 
 * 5. ¿Qué es el Frame Counter y para qué sirve en LoRaWAN?
 * 
 * 6. ¿Cómo afecta el Spreading Factor (SF) al alcance y al consumo?
 * 
 * 7. ¿Por qué LMIC usa un scheduler en lugar de delay()?
 * 
 * 8. ¿Qué significa duty cycle y por qué es importante en LoRaWAN?
 * 
 * =====================================================================
 * EJERCICIOS PROPUESTOS
 * =====================================================================
 * 
 * BÁSICO:
 * 1. Modificar el intervalo de transmisión a 60 segundos
 * 2. Añadir un LED que parpadee al enviar datos
 * 3. Crear alarma visual si distancia < 10 cm
 * 
 * INTERMEDIO:
 * 4. Implementar promedio móvil de 5 lecturas del sensor
 * 5. Calcular y enviar velocidad de cambio de distancia
 * 6. Añadir temperatura del sensor (si tu HC-SR04 lo tiene)
 * 
 * AVANZADO:
 * 7. Implementar downlink para cambiar intervalo de TX
 * 8. Añadir deep sleep para optimizar batería
 * 9. Crear gráficas en tiempo real en ChirpStack
 * 10. Implementar detección de movimiento con el sensor
 * 
 * =====================================================================
 */