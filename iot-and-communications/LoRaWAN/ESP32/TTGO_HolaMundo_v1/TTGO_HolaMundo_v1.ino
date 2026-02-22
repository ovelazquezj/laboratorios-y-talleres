/*
 * TTGO T3 LoRaWAN - ARQUITECTURA MODULAR PARA SENSORES
 * VERSION: 2.0 - Modular con Lectura de Sensores
 * 
 * OBJETIVO EDUCATIVO:
 * Demostrar arquitectura profesional para IoT con LoRaWAN:
 * - Separacion de responsabilidades (modular)
 * - Lectura de sensores (hoy simulados, manana reales)
 * - Creacion estructurada de payloads
 * - Encriptacion y desencriptacion de datos
 * - Comunicacion con ChirpStack
 * 
 * FLUJO DE DATOS:
 * [Sensor] -> [readSensorData()] -> [createPayload()] -> 
 * [LMIC_setTxData2()] -> [LoRaWAN] -> [ChirpStack]
 */

// ===================================================================
// PASO 1: INCLUIR LIBRERIAS NECESARIAS
// ===================================================================
// Estas librerias nos permiten usar protocolos de comunicacion
// y componentes del TTGO

#include <Wire.h>      // Protocolo I2C (para OLED y sensores)
#include <U8g2lib.h>   // Libreria para pantalla OLED
#include <SPI.h>       // Protocolo SPI (para modulo LoRa)
#include <lmic.h>      // Stack LoRaWAN (IBM LMIC library)
#include <hal/hal.h>   // Funciones del hardware

// ===================================================================
// PASO 2: CONFIGURAR PANTALLA OLED
// ===================================================================
// El TTGO tiene una pantalla OLED pequeña para mostrar estado
// Parametros: (Rotacion, PIN_RESET)

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// ===================================================================
// PASO 3: DEFINIR PINES DEL MODULO LoRa (SX1276)
// ===================================================================
// El modulo LoRa se comunica por SPI con el ESP32
// Necesitamos asignar los pines GPIO del ESP32 al modulo

#define LORA_SCK   5   // Reloj SPI
#define LORA_MISO  19  // Master In Slave Out (datos que recibe)
#define LORA_MOSI  27  // Master Out Slave In (datos que envia)
#define LORA_SS    18  // Chip Select (habilitar/deshabilitar modulo)
#define LORA_RST   14  // Reset del modulo
#define LORA_DIO0  26  // Interrupt 0
#define LORA_DIO1  33  // Interrupt 1
#define LORA_DIO2  32  // Interrupt 2

// ===================================================================
// PASO 4: CREDENCIALES LoRaWAN (OTAA - Over The Air Activation)
// ===================================================================
// Estas credenciales identifica tu dispositivo en la red LoRaWAN
// Se obtienen de la plataforma ChirpStack

// DevEUI: Identificador unico del dispositivo (64 bits = 8 bytes)
// IMPORTANTE: En codigo Arduino va en LSB (Little-Endian/invertido)
static const u1_t PROGMEM DEVEUI[8] = { 0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x03 };

// AppEUI/JoinEUI: Identificador de la aplicacion (64 bits = 8 bytes)
// IMPORTANTE: En codigo Arduino va en LSB (Little-Endian/invertido)
static const u1_t PROGMEM APPEUI[8] = { 0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x51 };

// AppKey: Clave de la aplicacion (128 bits = 16 bytes)
// IMPORTANTE: SIEMPRE va en MSB (Big-Endian/derecho), NUNCA se invierte
static const u1_t PROGMEM APPKEY[16] = { 
    0x8A, 0xC5, 0x83, 0xDF, 0xEE, 0xC7, 0x6C, 0x81, 
    0xFF, 0xD1, 0x9C, 0xCF, 0xE7, 0x6B, 0x73, 0xBF 
};

// ===================================================================
// PASO 5: FUNCIONES CALLBACK REQUERIDAS POR LMIC
// ===================================================================
// Estas funciones son OBLIGATORIAS. LMIC las llama internamente
// para obtener las credenciales. No las modifiques.

void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

// ===================================================================
// PASO 6: DEFINIR ESTRUCTURA DE DATOS DEL SENSOR
// ===================================================================
// Una estructura es una forma de agrupar multiples datos relacionados
// Hoy tiene: mensaje (texto) y timestamp (tiempo)
// Manana podra tener: temperatura, humedad, presion, etc.

struct SensorData {
    char mensaje[10];      // Arreglo de 10 caracteres para texto
    uint32_t timestamp;    // Numero de 32 bits (0 a 4 billones)
};

// ===================================================================
// PASO 7: VARIABLES GLOBALES
// ===================================================================
// Estas variables persisten durante toda la ejecucion del programa

static osjob_t sendjob;                // Tarea que envia datos periodicamente
const unsigned TX_INTERVAL = 30;       // Enviar cada 30 segundos
bool deviceJoined = false;             // Bandera: esta conectado?
unsigned long packetCount = 0;         // Contador de paquetes enviados

// ===================================================================
// PASO 8: CONFIGURACION DEL HARDWARE (PINMAP)
// ===================================================================
// Le decimos a LMIC cuales pines usar para comunicarse con el modulo

const lmic_pinmap lmic_pins = {
    .nss = LORA_SS,        // Pin de seleccion
    .rxtx = LMIC_UNUSED_PIN,
    .rst = LORA_RST,       // Pin de reset
    .dio = {
        LORA_DIO0,         // Interrupt 0
        LORA_DIO1,         // Interrupt 1
        LORA_DIO2          // Interrupt 2
    }
};

// ===================================================================
// PASO 9: FUNCION - LEER DATOS DEL SENSOR
// ===================================================================
// Esta funcion simula la lectura de un sensor real
// Retorna una estructura con los datos leidos
// 
// ARQUITECTURA MODULAR:
// Si manana quieres cambiar de sensor, solo cambias esta funcion
// El resto del codigo no cambia

struct SensorData readSensorData() {
    struct SensorData data;
    
    // Simulacion: Mensaje de texto fijo
    // En realidad esto vendria de un sensor DHT22, BMP280, etc.
    strcpy(data.mensaje, "hola mundo");
    
    // Timestamp: Segundos desde que arranco el ESP32
    // millis() devuelve millisegundos, dividimos por 1000 para segundos
    data.timestamp = millis() / 1000;
    
    return data;
}

// ===================================================================
// PASO 10: FUNCION - CREAR PAYLOAD (PAQUETE DE DATOS)
// ===================================================================
// Convierte la estructura SensorData en un arreglo de 16 bytes
// Este formato es el que se envia por LoRaWAN
// 
// ESTRUCTURA DEL PAYLOAD (16 bytes):
// Byte 0:      Tipo de mensaje (0x48 = "Hola")
// Bytes 1-4:   Timestamp (32 bits, formato Little-Endian)
// Bytes 5-14:  Mensaje de texto (10 caracteres ASCII)
// Byte 15:     Checksum (suma de bytes 0-14 para validacion)

void createPayload(struct SensorData data, uint8_t* payload) {
    if (payload == NULL) {
        return;
    }
    
    // BYTE 0: Tipo de mensaje
    // 0x48 = ASCII "H" de "Hola Mundo"
    payload[0] = 0x48;
    
    // BYTES 1-4: Timestamp en formato Little-Endian
    // Esto divide un numero de 32 bits en 4 bytes
    // Ejemplo: timestamp = 1234 (0x000004D2)
    //   payload[1] = 0xD2 (bits 0-7, LSB)
    //   payload[2] = 0x04 (bits 8-15)
    //   payload[3] = 0x00 (bits 16-23)
    //   payload[4] = 0x00 (bits 24-31, MSB)
    
    payload[1] = data.timestamp & 0xFF;           // Byte 0 (LSB)
    payload[2] = (data.timestamp >> 8) & 0xFF;    // Byte 1 (desplazar 8 bits)
    payload[3] = (data.timestamp >> 16) & 0xFF;   // Byte 2 (desplazar 16 bits)
    payload[4] = (data.timestamp >> 24) & 0xFF;   // Byte 3 (MSB)
    
    // BYTES 5-14: Mensaje de texto (10 caracteres)
    // Copiamos cada caracter del mensaje al payload
    for (int i = 0; i < 10; i++) {
        payload[5 + i] = data.mensaje[i];
    }
    
    // BYTE 15: Checksum (suma de todos los bytes anteriores)
    // Se usa para detectar errores en la transmision
    // El servidor calcula el checksum y lo compara
    payload[15] = 0;
    for (int i = 0; i < 15; i++) {
        payload[15] += payload[i];
    }
}

// ===================================================================
// PASO 11: FUNCION - ACTUALIZAR PANTALLA OLED
// ===================================================================
// Muestra en tiempo real el estado de la conexion y cantidad de paquetes

void updateDisplay() {
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_ncenB10_tr);
    u8g2.drawStr(0, 12, "TTGO LoRaWAN v2.0");
    
    u8g2.setFont(u8g2_font_6x12_tf);
    
    if (deviceJoined) {
        u8g2.drawStr(0, 28, "Estado: CONECTADO");
    } else {
        u8g2.drawStr(0, 28, "Estado: JOINING");
    }

    char countStr[32];
    sprintf(countStr, "Paquetes: %lu", packetCount);
    u8g2.drawStr(0, 44, countStr);
    u8g2.drawStr(0, 60, "US915 SubBand 2");
    u8g2.sendBuffer();
}

// ===================================================================
// PASO 12: DECLARACION ANTICIPADA
// ===================================================================
// Declara que existe la funcion do_send
// Se necesita porque se usa antes de definirse

void do_send(osjob_t* j);

// ===================================================================
// PASO 13: FUNCION - MOSTRAR INFORMACION DE EUI
// ===================================================================
// Muestra en Serial Monitor las credenciales en ambos formatos
// Educativo: explica LSB vs MSB

void printEUIInfo() {
    Serial.println(F("\n"));
    Serial.println(F("===================================================="));
    Serial.println(F("INFORMACION CRITICA SOBRE EUI - LSB vs MSB"));
    Serial.println(F("===================================================="));
    
    Serial.println(F("\nPROBLEMA:"));
    Serial.println(F("Arduino LMIC usa LSB (Little-Endian)"));
    Serial.println(F("ChirpStack UI usa MSB (Big-Endian)"));
    Serial.println(F("Si no los inviertes, el dispositivo NO hace Join"));
    
    Serial.println(F("\nDEVEUI (IDENTIFICADOR DEL DISPOSITIVO):"));
    
    Serial.print(F("EN CODIGO (LSB/Invertido): "));
    for (int i = 0; i < 8; i++) {
        if (DEVEUI[i] < 0x10) Serial.print("0");
        Serial.print(DEVEUI[i], HEX);
        if (i < 7) Serial.print(" ");
    }
    Serial.println();
    
    Serial.print(F("EN CHIRPSTACK (MSB/Derecho): "));
    for (int i = 7; i >= 0; i--) {
        if (DEVEUI[i] < 0x10) Serial.print("0");
        Serial.print(DEVEUI[i], HEX);
    }
    Serial.println();
    
    Serial.println(F("\nJOINEUI / APPEUI (IDENTIFICADOR APP):"));
    
    Serial.print(F("EN CODIGO (LSB/Invertido): "));
    for (int i = 0; i < 8; i++) {
        if (APPEUI[i] < 0x10) Serial.print("0");
        Serial.print(APPEUI[i], HEX);
        if (i < 7) Serial.print(" ");
    }
    Serial.println();
    
    Serial.print(F("EN CHIRPSTACK (MSB/Derecho): "));
    for (int i = 7; i >= 0; i--) {
        if (APPEUI[i] < 0x10) Serial.print("0");
        Serial.print(APPEUI[i], HEX);
    }
    Serial.println();
    
    Serial.println(F("\nAPPKEY (CLAVE DE APLICACION):"));
    Serial.print(F("SIEMPRE EN MSB (NUNCA se invierte): "));
    for (int i = 0; i < 16; i++) {
        if (APPKEY[i] < 0x10) Serial.print("0");
        Serial.print(APPKEY[i], HEX);
    }
    Serial.println();
    
    Serial.println(F("\nCHECKLIST PARA CHIRPSTACK:"));
    Serial.println(F("Copia EXACTAMENTE estos valores:"));
    Serial.println();
    Serial.print(F("Device EUI: "));
    for (int i = 7; i >= 0; i--) {
        if (DEVEUI[i] < 0x10) Serial.print("0");
        Serial.print(DEVEUI[i], HEX);
    }
    Serial.println();
    
    Serial.print(F("Join EUI: "));
    for (int i = 7; i >= 0; i--) {
        if (APPEUI[i] < 0x10) Serial.print("0");
        Serial.print(APPEUI[i], HEX);
    }
    Serial.println();
    
    Serial.print(F("Application Key: "));
    for (int i = 0; i < 16; i++) {
        if (APPKEY[i] < 0x10) Serial.print("0");
        Serial.print(APPKEY[i], HEX);
    }
    Serial.println();
    
    Serial.println(F("\n===================================================="));
    Serial.println(F("Si no coinciden, el Join FALLARA"));
    Serial.println(F("====================================================\n"));
}

// ===================================================================
// PASO 14: MANEJADOR DE EVENTOS LoRaWAN
// ===================================================================
// Esta funcion se llama automaticamente cuando ocurren eventos
// en la comunicacion LoRaWAN (Join, TX completo, etc.)

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
        
        // EVENTO: Intentando hacer Join a la red
        case EV_JOINING:
            Serial.println(F("EV_JOINING - Intentando unirse..."));
            deviceJoined = false;
            updateDisplay();
            break;
        
        // EVENTO: Join exitoso, dispositivo conectado
        case EV_JOINED:
            Serial.println(F("OK EV_JOINED - CONECTADO A CHIRPSTACK"));
            LMIC_setLinkCheckMode(0);
            deviceJoined = true;
            updateDisplay();
            // Programar primer envio en 2 segundos
            os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(2), do_send);
            break;
        
        // EVENTO: Join fallo, revisar credenciales
        case EV_JOIN_FAILED:
            Serial.println(F("ERROR EV_JOIN_FAILED"));
            deviceJoined = false;
            updateDisplay();
            break;
        
        case EV_REJOIN_FAILED:
            Serial.println(F("EV_REJOIN_FAILED"));
            break;
        
        // EVENTO: Transmision completada exitosamente
        case EV_TXCOMPLETE:
            Serial.println(F("OK EV_TXCOMPLETE - Transmision completa"));
            
            if (LMIC.txrxFlags & TXRX_ACK) {
                Serial.println(F("ACK recibido"));
            }
            
            if (LMIC.dataLen) {
                Serial.print(F("Downlink: "));
                Serial.print(LMIC.dataLen);
                Serial.println(F(" bytes"));
            }
            
            if (deviceJoined) {
                Serial.print(F("Proximo uplink en "));
                Serial.print(TX_INTERVAL);
                Serial.println(F(" segundos"));
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
            Serial.print(F("Evento: "));
            Serial.println((unsigned) ev);
            break;
    }
}

// ===================================================================
// PASO 15: FUNCION PRINCIPAL - ENVIAR PAQUETE
// ===================================================================
// Este es el flujo modular completo:
// 1. Leer datos del sensor
// 2. Empaquetar en payload
// 3. Mostrar en Serial (HEX encriptado y decodificado)
// 4. Enviar por LoRaWAN

void do_send(osjob_t* j) {
    
    // Verificar si hay operacion pendiente
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("TX/RX en progreso..."));
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
    Serial.println(F("\nDatos del sensor:"));
    Serial.print(F("  Mensaje: "));
    Serial.println(sensorData.mensaje);
    Serial.print(F("  Timestamp: "));
    Serial.print(sensorData.timestamp);
    Serial.println(F(" segundos"));
    
    // Mostrar payload en HEX (como se envia encriptado)
    Serial.println(F("\nPayload ENCRIPTADO (HEX):"));
    Serial.print(F("  "));
    for (int i = 0; i < sizeof(payload); i++) {
        if (payload[i] < 0x10) Serial.print("0");
        Serial.print(payload[i], HEX);
        if (i < sizeof(payload) - 1) Serial.print(" ");
    }
    Serial.println();
    
    // Mostrar payload desencriptado (decodificado)
    Serial.println(F("\nPayload DESENCRIPTADO (decodificado):"));
    Serial.print(F("  [0] Tipo: 0x"));
    Serial.println(payload[0], HEX);
    
    // Recalcular timestamp para verificar
    Serial.print(F("  [1-4] Timestamp: "));
    uint32_t ts_recalc = payload[1] | (payload[2] << 8) | 
                         (payload[3] << 16) | (payload[4] << 24);
    Serial.print(ts_recalc);
    Serial.println(F(" seg"));
    
    // Mostrar mensaje decodificado
    Serial.print(F("  [5-14] Mensaje: "));
    for (int i = 5; i < 15; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
    
    // Mostrar checksum
    Serial.print(F("  [15] Checksum: 0x"));
    Serial.println(payload[15], HEX);
    
    // Mostrar informacion tecnica del envio
    Serial.println(F("\nInformacion del envio:"));
    Serial.print(F("  Puerto: 1"));
    Serial.print(F(" | Tamanio: "));
    Serial.print(sizeof(payload));
    Serial.print(F(" bytes | Data Rate: DR"));
    Serial.println(LMIC.datarate);
    
    Serial.println(F("========================================\n"));
    
    // PASO 5: Enviar por LoRaWAN
    // Parametros: (puerto=1, datos, tamanio, confirmacion=0)
    LMIC_setTxData2(1, payload, sizeof(payload), 0);
}

// ===================================================================
// PASO 16: FUNCION SETUP (INICIALIZACION)
// ===================================================================
// Se ejecuta UNA SOLA VEZ al iniciar el ESP32
// Inicializa todos los perifericos

void setup() {
    // Inicializar comunicacion Serial a 115200 baud
    Serial.begin(115200);
    delay(2000);
    
    // Mostrar mensaje de bienvenida
    Serial.println(F("\n"));
    Serial.println(F("====================================="));
    Serial.println(F("TTGO T3 LoRaWAN v2.0 - MODULAR"));
    Serial.println(F("====================================="));
    Serial.println();
    
    // Mostrar informacion de credenciales
    printEUIInfo();
    
    // Mostrar configuracion de red
    Serial.println(F("CONFIGURACION DE RED:"));
    Serial.println(F("Region: US915"));
    Serial.println(F("Sub-banda: 2"));
    Serial.println(F("Modo: OTAA"));
    Serial.println();
    
    // Configurar pines de entrada/salida
    pinMode(0, INPUT_PULLUP);
    pinMode(2, OUTPUT);
    digitalWrite(2, LOW);

    // Inicializar pantalla OLED
    Serial.println(F("Inicializando OLED..."));
    Wire.begin(21, 22);
    Wire.setClock(100000);
    u8g2.begin();
    updateDisplay();
    Serial.println(F("OK"));
    Serial.println();

    // Inicializar modulo LoRa
    Serial.println(F("Inicializando LoRa..."));
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    os_init();                    // Inicializar LMIC
    LMIC_reset();                 // Reset de LMIC
    Serial.println(F("OK"));
    Serial.println();
    
    // Configurar canales
    Serial.println(F("Configurando Canales..."));
    LMIC_selectSubBand(1);        // Sub-banda 2 (indices 8-15)
    Serial.println(F("Region: US915"));
    Serial.println(F("Sub-banda: 2"));
    Serial.println();
    
    // Configurar tolerancia de reloj
    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
    
    // Iniciar procedimiento de Join
    Serial.println(F("INICIANDO JOIN"));
    Serial.println();
    
    LMIC_startJoining();
}

// ===================================================================
// PASO 17: FUNCION LOOP (BUCLE PRINCIPAL)
// ===================================================================
// Se ejecuta repetidamente mientras el ESP32 este encendido
// Es donde ocurre la "magia" de LoRaWAN

void loop() {
    // Procesar eventos LMIC
    // Esta funcion es CRITICAL: maneja todo el protocolo LoRaWAN
    os_runloop_once();

    // Actualizar pantalla OLED cada 1 segundo
    static unsigned long lastDisplayUpdate = 0;
    if (millis() - lastDisplayUpdate >= 1000) {
        updateDisplay();
        lastDisplayUpdate = millis();
    }
}
