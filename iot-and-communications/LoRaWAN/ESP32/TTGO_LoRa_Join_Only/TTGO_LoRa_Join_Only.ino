/*
 * =====================================================================
 * TTGO ESP32 LoRa v1 - SOLO JOIN LoRaWAN (OTAA)
 * =====================================================================
 * 
 * VERSIÓN CORREGIDA CON PINMAP EXPLÍCITO
 * Soluciona: "Board not supported -- use an explicit pinmap"
 * 
 * =====================================================================
 */

// =====================================================================
// DEFINIR PINMAP ANTES DE INCLUIR LMIC
// =====================================================================

#define CFG_sx1276_radio 1

// =====================================================================
// LIBRERÍAS
// =====================================================================

#include <Wire.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <lmic.h>
#include <hal/hal.h>

// =====================================================================
// DISPLAY OLED
// =====================================================================

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// =====================================================================
// PINES LoRa - TTGO ESP32 LoRa v1
// =====================================================================

#define LORA_SCK   5    // GPIO 5  - SPI Clock
#define LORA_MISO  19   // GPIO 19 - SPI MISO
#define LORA_MOSI  27   // GPIO 27 - SPI MOSI
#define LORA_SS    18   // GPIO 18 - Chip Select
#define LORA_RST   14   // GPIO 14 - Reset
#define LORA_DIO0  26   // GPIO 26 - DIO0
#define LORA_DIO1  33   // GPIO 33 - DIO1
#define LORA_DIO2  32   // GPIO 32 - DIO2

// =====================================================================
// PINMAP EXPLÍCITO PARA LMIC
// =====================================================================

const lmic_pinmap lmic_pins = {
    .nss = LORA_SS,           // 18
    .rxtx = LMIC_UNUSED_PIN,
    .rst = LORA_RST,          // 14
    .dio = {LORA_DIO0, LORA_DIO1, LORA_DIO2},  // {26, 33, 32}
};

// =====================================================================
// CREDENCIALES LoRaWAN OTAA - DEL DISPOSITIVO REAL
// =====================================================================

// DevEUI:  0238920535e871db (convertido a LSB)
static const u1_t PROGMEM DEVEUI[8] = { 0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x02 };

// JoinEUI/AppEUI: 505246f87143fd8a (convertido a LSB)
static const u1_t PROGMEM APPEUI[8] = { 0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x50 };

// AppKey: (ya en MSB)
static const u1_t PROGMEM APPKEY[16] = { 0x8A, 0xC5, 0x83, 0xDF, 0xEE, 0xC7, 0x6C, 0x81, 0xFF, 0xD1, 0x9C, 0xCF, 0xE7, 0x6B, 0x73, 0xBF };

// Callbacks LMIC
void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

// =====================================================================
// VARIABLES GLOBALES
// =====================================================================

bool deviceJoined = false;
unsigned long joinAttempts = 0;
unsigned long startTime = 0;

// =====================================================================
// ACTUALIZAR DISPLAY OLED
// =====================================================================

void updateDisplay() {
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x12_tf);
    
    // Título
    u8g2.drawStr(0, 10, "TTGO LoRa v1 - Join");
    
    // Estado LoRa
    u8g2.drawStr(0, 22, "Estado LoRaWAN:");
    
    if (deviceJoined) {
        u8g2.drawStr(20, 34, "✅ CONECTADO");
        u8g2.drawStr(0, 46, "Join completado!");
        u8g2.drawStr(0, 58, "Listo para enviar datos");
    } else {
        u8g2.drawStr(20, 34, "⏳ Joining...");
        
        // Tiempo transcurrido
        unsigned long elapsed = (millis() - startTime) / 1000;
        char timeStr[32];
        sprintf(timeStr, "Tiempo: %lu seg", elapsed);
        u8g2.drawStr(0, 46, timeStr);
        
        // Intentos
        char attStr[32];
        sprintf(attStr, "Intentos: %lu", joinAttempts);
        u8g2.drawStr(0, 58, attStr);
    }
    
    u8g2.sendBuffer();
}

// =====================================================================
// MANEJADOR DE EVENTOS LoRaWAN
// =====================================================================

void onEvent (ev_t ev) {
    Serial.print(os_getTime());
    Serial.print(": ");
    
    switch(ev) {
        case EV_JOINING:
            Serial.println(F("📤 EV_JOINING - Enviando Join Request..."));
            joinAttempts++;
            deviceJoined = false;
            updateDisplay();
            break;
        
        case EV_JOINED:
            Serial.println(F(""));
            Serial.println(F("════════════════════════════════════════"));
            Serial.println(F("✅✅✅ ¡JOIN EXITOSO! ✅✅✅"));
            Serial.println(F("════════════════════════════════════════"));
            Serial.println(F("🎉 Dispositivo conectado a la red"));
            Serial.println(F(""));
            
            // Mostrar info de sesión
            Serial.println(F("📊 INFORMACIÓN DE SESIÓN:"));
            Serial.print(F("   DevAddr: 0x"));
            Serial.println(LMIC.devaddr, HEX);
            
            Serial.print(F("   NwkSKey: "));
            for(int i=0; i<16; i++) {
                if (LMIC.nwkKey[i] < 0x10) Serial.print("0");
                Serial.print(LMIC.nwkKey[i], HEX);
                if (i < 15) Serial.print(" ");
            }
            Serial.println();
            
            Serial.print(F("   AppSKey: "));
            for(int i=0; i<16; i++) {
                if (LMIC.artKey[i] < 0x10) Serial.print("0");
                Serial.print(LMIC.artKey[i], HEX);
                if (i < 15) Serial.print(" ");
            }
            Serial.println();
            Serial.println(F("════════════════════════════════════════"));
            Serial.println();
            
            LMIC_setLinkCheckMode(0);
            deviceJoined = true;
            updateDisplay();
            break;
        
        case EV_JOIN_FAILED:
            Serial.println(F("❌ EV_JOIN_FAILED - Reintentando..."));
            deviceJoined = false;
            updateDisplay();
            break;
        
        case EV_REJOIN_FAILED:
            Serial.println(F("❌ EV_REJOIN_FAILED"));
            break;
        
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE"));
            break;
        
        case EV_LOST_TSYNC:
            Serial.println(F("EV_LOST_TSYNC"));
            break;
        
        case EV_RESET:
            Serial.println(F("⚡ EV_RESET"));
            break;
        
        case EV_RXCOMPLETE:
            Serial.println(F("EV_RXCOMPLETE"));
            break;
        
        case EV_LINK_DEAD:
            Serial.println(F("EV_LINK_DEAD"));
            break;
        
        case EV_LINK_ALIVE:
            Serial.println(F("✅ EV_LINK_ALIVE"));
            break;
        
        case EV_SCAN_TIMEOUT:
            Serial.println(F("EV_SCAN_TIMEOUT"));
            break;
        
        default:
            Serial.print(F("⚠️  Evento: "));
            Serial.println((unsigned) ev);
            break;
    }
}

// =====================================================================
// SETUP
// =====================================================================

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println(F("\n"));
    Serial.println(F("════════════════════════════════════════"));
    Serial.println(F("  TTGO ESP32 LoRa v1"));
    Serial.println(F("  PROCEDIMIENTO DE JOIN OTAA"));
    Serial.println(F("════════════════════════════════════════"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // CONFIGURAR GPIOs
    // -----------------------------------------------------------------
    
    pinMode(0, INPUT_PULLUP);   // Boot button
    pinMode(2, OUTPUT);         // LED interno
    digitalWrite(2, LOW);
    
    // -----------------------------------------------------------------
    // DISPLAY OLED
    // -----------------------------------------------------------------
    
    Serial.println(F("📺 Inicializando display OLED..."));
    Wire.begin(21, 22);
    Wire.setClock(100000);
    u8g2.begin();
    updateDisplay();
    Serial.println(F("   ✅ OLED inicializado"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // MÓDULO LoRa
    // -----------------------------------------------------------------
    
    Serial.println(F("📡 Inicializando módulo LoRa (SX1276)..."));
    Serial.println(F("   Configuración SPI:"));
    Serial.print(F("      SCK:   GPIO "));  Serial.println(LORA_SCK);
    Serial.print(F("      MISO:  GPIO "));  Serial.println(LORA_MISO);
    Serial.print(F("      MOSI:  GPIO "));  Serial.println(LORA_MOSI);
    Serial.print(F("      SS:    GPIO "));  Serial.println(LORA_SS);
    Serial.print(F("      RST:   GPIO "));  Serial.println(LORA_RST);
    Serial.print(F("      DIO0:  GPIO "));  Serial.println(LORA_DIO0);
    Serial.print(F("      DIO1:  GPIO "));  Serial.println(LORA_DIO1);
    Serial.print(F("      DIO2:  GPIO "));  Serial.println(LORA_DIO2);
    
    // Inicializar SPI
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    
    // Inicializar LMIC
    os_init();
    LMIC_reset();
    
    Serial.println(F("   ✅ LMIC inicializado"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // CONFIGURAR REGIÓN US915
    // -----------------------------------------------------------------
    
    Serial.println(F("📻 Configurando región US915..."));
    
    /***************
    * AQUI esta el pain
    ****************/
    // Seleccionar sub-banda 1 (canales 8-15) 
    LMIC_selectSubBand(0);
    
    // Compensación del reloj del ESP32
    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
    
    Serial.println(F("   ├─ Región: US915"));
    Serial.println(F("   ├─ Sub-banda: 2 (canales 8-15)"));
    Serial.println(F("   ├─ Rango: 903.9 - 905.3 MHz"));
    Serial.println(F("   └─ Compensación reloj: 1%"));
    Serial.println();
    
    // -----------------------------------------------------------------
    // MOSTRAR CREDENCIALES
    // -----------------------------------------------------------------
    
    Serial.println(F("🔐 CREDENCIALES OTAA:"));
    Serial.print(F("   DevEUI:  "));
    for (int i = 7; i >= 0; i--) {
        if (DEVEUI[i] < 0x10) Serial.print("0");
        Serial.print(DEVEUI[i], HEX);
        if (i > 0) Serial.print(":");
    }
    Serial.println();
    
    Serial.print(F("   AppEUI:  "));
    for (int i = 7; i >= 0; i--) {
        if (APPEUI[i] < 0x10) Serial.print("0");
        Serial.print(APPEUI[i], HEX);
        if (i > 0) Serial.print(":");
    }
    Serial.println();
    Serial.println();
    
    // -----------------------------------------------------------------
    // INICIAR JOIN
    // -----------------------------------------------------------------
    
    startTime = millis();
    
    Serial.println(F("════════════════════════════════════════"));
    Serial.println(F("🚀 INICIANDO PROCEDIMIENTO DE JOIN OTAA"));
    Serial.println(F("════════════════════════════════════════"));
    Serial.println(F(""));
    Serial.println(F("⏳ Esperando respuesta del gateway..."));
    Serial.println(F("⏳ Esto puede tomar 10-60 segundos"));
    Serial.println(F(""));
    Serial.println(F("✅ VERIFICAR ANTES DE CONTINUAR:"));
    Serial.println(F("   1. Gateway encendido y conectado"));
    Serial.println(F("   2. Gateway en US915 Sub-banda 2"));
    Serial.println(F("   3. Dispositivo registrado en ChirpStack"));
    Serial.println(F("   4. Credenciales coinciden exactamente"));
    Serial.println(F(""));
    
    LMIC_startJoining();
}

// =====================================================================
// LOOP
// =====================================================================

void loop() {
    // Ejecutar scheduler LMIC (CRÍTICO)
    os_runloop_once();
    
    // Actualizar display cada segundo
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate >= 1000) {
        updateDisplay();
        lastUpdate = millis();
    }
    
    // Parpadear LED durante join
    static unsigned long lastBlink = 0;
    if (millis() - lastBlink >= 500) {
        if (!deviceJoined) {
            digitalWrite(2, !digitalRead(2));  // Alternar LED
        } else {
            digitalWrite(2, HIGH);  // Mantener encendido si está joined
        }
        lastBlink = millis();
    }
}