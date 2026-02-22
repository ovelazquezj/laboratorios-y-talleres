# Laboratorio Semana 6 – Comunicaciones e IoT

**Introducción a LoRaWAN: Conexión de dispositivo TTGO a ChirpStack**

## Organización del laboratorio

| Día       | Actividad principal                                                 |
|-----------|---------------------------------------------------------------------|
| Miércoles | Configurar región US915 en ChirpStack y verificar gateway          |
| Viernes   | Configurar dispositivo TTGO, conectarlo al LNS y verificar uplinks |

---

## Requisitos previos

Antes de iniciar el laboratorio, asegúrate de tener lo siguiente:

1. **ChirpStack** funcionando desde el laboratorio anterior (Semana 5).
2. **Gateway LoRaWAN** configurado para la banda US915.
3. **Arduino IDE** instalado con soporte para ESP32.
4. **Bibliotecas instaladas** en Arduino IDE:
   - MCCI LoRaWAN LMIC library (`MCCI LoRaWAN LMIC library` en el Library Manager)
   - U8g2 (para OLED)
   - Wire (incluida por defecto)
5. **Hardware del laboratorio**:
   - TTGO T3 LoRa32 v1.6.1
   - Cable micro USB

---

## Contexto: ¿Qué es LoRaWAN?

LoRaWAN (Long Range Wide Area Network) es un protocolo de comunicación diseñado para dispositivos IoT de bajo consumo que necesitan transmitir pequeñas cantidades de datos a largas distancias. A diferencia de WiFi o Bluetooth, LoRaWAN puede alcanzar varios kilómetros en espacios abiertos.

**Arquitectura básica:**
- **Nodo (End Device):** Dispositivo que envía datos (TTGO en nuestro caso)
- **Gateway:** Recibe datos de los nodos y los reenvía al servidor
- **LNS (LoRa Network Server):** ChirpStack en nuestro caso, gestiona la red
- **Application Server:** Procesa y visualiza los datos

**Métodos de activación:**
- **OTAA (Over-The-Air Activation):** El dispositivo se une dinámicamente usando credenciales (más seguro)
- **ABP (Activation By Personalization):** Las claves se programan directamente en el dispositivo

En este laboratorio usaremos **OTAA**.

---

# Día 1 – Miércoles: Configurar ChirpStack para US915

## Paso 1: Detener ChirpStack

Si ChirpStack está corriendo desde el laboratorio anterior, primero detenlo:

```bash
cd chirpstack-docker
docker-compose down
```

---

## Paso 2: Modificar configuración de región

La instalación por defecto de ChirpStack viene configurada para la región EU868. Necesitamos cambiarla a US915_0 para que coincida con nuestro gateway.

### Editar archivo de configuración:

```bash
nano configuration/chirpstack/region_us915_0.toml
```

Verifica o modifica las siguientes secciones:

```toml
[regions.us915_0]
# Configuración para US915, SubBand 1 (canales 0-7)

  # Configuración de red
  [regions.us915_0.network]
  installation_margin = 10
  rx_window = 3
  rx1_delay = 1
  rx1_dr_offset = 0
  rx2_dr = 8
  rx2_frequency = 923300000
  
  # Canales habilitados (SubBand 1: 0-7 + 64)
  [regions.us915_0.channels]
  enabled_channels = [0, 1, 2, 3, 4, 5, 6, 7, 64]
```

Guarda y cierra el archivo (Ctrl+O, Enter, Ctrl+X).

---

## Paso 3: Modificar docker-compose.yml

Edita el archivo `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Busca la sección del servicio `chirpstack` y modifica la variable de entorno:

**ANTES:**
```yaml
chirpstack:
  image: chirpstack/chirpstack:4
  command: -c /etc/chirpstack
  restart: unless-stopped
  volumes:
    - ./configuration/chirpstack:/etc/chirpstack
    - ./lorawan-devices:/opt/lorawan-devices
  depends_on:
    - postgres
    - mosquitto
    - redis
  environment:
    - MQTT_BROKER_HOST=mosquitto
    - REDIS_HOST=redis
    - POSTGRESQL_HOST=postgres
  ports:
    - 8080:8080
```

**DESPUÉS (agrega la línea de REGION):**
```yaml
chirpstack:
  image: chirpstack/chirpstack:4
  command: -c /etc/chirpstack
  restart: unless-stopped
  volumes:
    - ./configuration/chirpstack:/etc/chirpstack
    - ./lorawan-devices:/opt/lorawan-devices
  depends_on:
    - postgres
    - mosquitto
    - redis
  environment:
    - MQTT_BROKER_HOST=mosquitto
    - REDIS_HOST=redis
    - POSTGRESQL_HOST=postgres
    - REGION=us915_0
  ports:
    - 8080:8080
```

Guarda y cierra el archivo.

---

## Paso 4: Levantar ChirpStack con la nueva configuración

```bash
docker-compose up -d
```

Espera unos 30 segundos para que todos los servicios inicien correctamente.

---

## Paso 5: Verificar configuración en ChirpStack

1. Accede a ChirpStack: `http://localhost:8080`
2. Credenciales por defecto:
   - Usuario: `admin`
   - Contraseña: `admin`
3. Ve a **Regions** en el menú lateral
4. Deberías ver **us915_0** como región activa

---

## Paso 6: Verificar que el gateway esté conectado

1. Ve a **Gateways** en el menú lateral
2. Tu gateway debe aparecer con estado **Online** o **Last seen: just now**
3. Si aparece offline:
   - Verifica que el packet forwarder del gateway apunte a la IP del servidor en puerto **1700**
   - Revisa logs del gateway bridge:
     ```bash
     docker logs -f chirpstack-docker-chirpstack-gateway-bridge-1
     ```

---

## ✓ Checkpoint Día 1

Antes de continuar al Viernes, asegúrate de:
- [ ] ChirpStack corriendo con región US915_0
- [ ] Gateway visible y online en ChirpStack
- [ ] Puedes acceder a la interfaz web sin problemas

---

# Día 2 – Viernes: Configurar y conectar dispositivo TTGO

## Paso 1: Identificar el TTGO T3 v1.6.1

El TTGO T3 LoRa32 v1.6.1 incluye:
- **ESP32:** Microcontrolador principal con WiFi y Bluetooth
- **Módulo LoRa SX1276/SX1278:** Para comunicación LoRaWAN en 915MHz
- **Pantalla OLED 128x64:** Para visualización local de información
- **Antena externa:** Conector SMA para antena LoRa

**IMPORTANTE:** Siempre conecta la antena antes de encender el dispositivo para evitar dañar el módulo LoRa.

### Pines LoRa del TTGO T3 v1.6.1:
```
SCK:  GPIO5
MISO: GPIO19
MOSI: GPIO27
NSS:  GPIO18
RST:  GPIO14
DIO0: GPIO26
DIO1: GPIO33
DIO2: GPIO32
```

Estos pines ya están cableados internamente en la placa.

---

## Paso 2: Crear aplicación en ChirpStack

1. En ChirpStack, ve a **Applications** en el menú lateral
2. Haz clic en **Add application**
3. Llena los campos:
   - **Name:** `Lab-LoRaWAN-Estudiantes` (o el nombre que prefieras)
   - **Description:** `Aplicación del laboratorio de IoT`
4. Haz clic en **Submit**

---

## Paso 3: Crear Device Profile

Antes de agregar dispositivos, necesitamos crear un perfil con la configuración correcta.

1. Ve a **Device Profiles** en el menú lateral
2. Haz clic en **Add device profile**
3. Pestaña **General**:
   - **Name:** `TTGO-OTAA-US915`
   - **Region:** Selecciona **US915 (channels 0-7 + 64)**
   - **MAC version:** `1.0.3`
   - **Regional parameters revision:** `A`
   - **ADR enabled:** ✓ (marcado)
   - **Class:** `Class-A`
4. Pestaña **Join (OTAA/ABP)**:
   - **Device supports OTAA:** ✓ (marcado)
5. Haz clic en **Submit**

---

## Paso 4: Crear dispositivo en ChirpStack

1. Ve a **Applications** → Selecciona tu aplicación → **Devices**
2. Haz clic en **Add device**
3. Llena los campos:
   - **Device name:** `TTGO-[TuNombre]` (ejemplo: `TTGO-Juan`)
   - **Device EUI:** Puedes generar uno aleatorio haciendo clic en el icono de dado 🎲
   - **Device profile:** Selecciona `TTGO-OTAA-US915`
4. Haz clic en **Submit**
5. Automáticamente te llevará a la vista del dispositivo

---

## Paso 5: Obtener credenciales OTAA

1. Dentro del dispositivo recién creado, ve a la pestaña **Keys (OTAA)**
2. Si no existe una Application key, haz clic en **Generate** para crear una
3. Anota las siguientes credenciales (las necesitarás para el código):
   - **DevEUI** (8 bytes en formato hexadecimal)
   - **JoinEUI/AppEUI** (por defecto `0000000000000000`)
   - **Application key** (16 bytes en formato hexadecimal)

**Ejemplo:**
```
DevEUI:  70B3D57ED005A8C3
JoinEUI: 0000000000000000
AppKey:  A1B2C3D4E5F6789012345678ABCDEF01
```

---

## Paso 6: Instalar biblioteca LMIC en Arduino IDE

1. Abre Arduino IDE
2. Ve a **Sketch** → **Include Library** → **Manage Libraries**
3. En el buscador, escribe: `MCCI LoRaWAN LMIC`
4. Instala la biblioteca **MCCI LoRaWAN LMIC library** by IBM, Matthijs Kooijman, Terry Moore, ChaeHee Won, Frank Rose
5. Cierra el Library Manager

---

## Paso 7: Configurar biblioteca LMIC para US915

Después de instalar LMIC, necesitamos configurarla para US915:

1. Navega a la carpeta de la biblioteca LMIC:
   - **Windows:** `Documents\Arduino\libraries\MCCI_LoRaWAN_LMIC_library\project_config`
   - **Linux/Mac:** `~/Arduino/libraries/MCCI_LoRaWAN_LMIC_library/project_config`

2. Abre el archivo `lmic_project_config.h` con un editor de texto

3. Comenta (agrega `//` al inicio) la línea de EU868 y descomenta US915:

**ANTES:**
```cpp
// #define CFG_us915 1
#define CFG_eu868 1
```

**DESPUÉS:**
```cpp
#define CFG_us915 1
// #define CFG_eu868 1
```

4. Guarda el archivo

---

## Paso 8: Convertir credenciales al formato LMIC

LMIC requiere las credenciales en un formato específico:

- **DevEUI:** LSB (invertir orden de bytes)
- **JoinEUI/AppEUI:** LSB (invertir orden de bytes)
- **AppKey:** MSB (mantener orden original)

### Herramienta de conversión:

Usa esta tabla para convertir tus credenciales:

**Ejemplo de conversión:**

Si ChirpStack te dio:
```
DevEUI:  70B3D57ED005A8C3
JoinEUI: 0000000000000000
AppKey:  A1B2C3D4E5F6789012345678ABCDEF01
```

En el código Arduino será:
```cpp
// DevEUI (LSB - invertido)
static const u1_t PROGMEM DEVEUI[8] = { 
    0xC3, 0xA8, 0x05, 0xD0, 0x7E, 0xD5, 0xB3, 0x70 
};

// JoinEUI/AppEUI (LSB - invertido)
static const u1_t PROGMEM APPEUI[8] = { 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
};

// AppKey (MSB - sin invertir)
static const u1_t PROGMEM APPKEY[16] = { 
    0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6, 0x78, 0x90,
    0x12, 0x34, 0x56, 0x78, 0xAB, 0xCD, 0xEF, 0x01
};
```

---

## Paso 9: Sketch básico de prueba OTAA

Copia el siguiente código en Arduino IDE:

```cpp
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// -------- REEMPLAZA CON TUS CREDENCIALES --------
// DevEUI (LSB - bytes invertidos)
static const u1_t PROGMEM DEVEUI[8] = { 
    0xC3, 0xA8, 0x05, 0xD0, 0x7E, 0xD5, 0xB3, 0x70 
};

// AppEUI/JoinEUI (LSB - bytes invertidos)
static const u1_t PROGMEM APPEUI[8] = { 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
};

// AppKey (MSB - orden normal)
static const u1_t PROGMEM APPKEY[16] = { 
    0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6, 0x78, 0x90,
    0x12, 0x34, 0x56, 0x78, 0xAB, 0xCD, 0xEF, 0x01
};
// -------------------------------------------------

void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8);}
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8);}
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16);}

static uint8_t mydata[] = "Hola ChirpStack!";
static osjob_t sendjob;

// Configuración de pines para TTGO T3 v1.6.1
const lmic_pinmap lmic_pins = {
    .nss = 18,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 14,
    .dio = {26, 33, 32},
};

void printHex2(unsigned v) {
    v &= 0xff;
    if (v < 16)
        Serial.print('0');
    Serial.print(v, HEX);
}

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
            Serial.println(F("EV_JOINING"));
            break;
        case EV_JOINED:
            Serial.println(F("EV_JOINED"));
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
                printHex2(artKey[i]);
              }
              Serial.println("");
              Serial.print("NwkSKey: ");
              for (size_t i=0; i<sizeof(nwkKey); ++i) {
                      if (i != 0)
                              Serial.print("-");
                      printHex2(nwkKey[i]);
              }
              Serial.println();
            }
            LMIC_setLinkCheckMode(0);
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("EV_JOIN_FAILED"));
            break;
        case EV_REJOIN_FAILED:
            Serial.println(F("EV_REJOIN_FAILED"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE (incluye espera de RX windows)"));
            if (LMIC.txrxFlags & TXRX_ACK)
              Serial.println(F("ACK recibido"));
            if (LMIC.dataLen) {
              Serial.print(F("Datos recibidos: "));
              Serial.write(LMIC.frame+LMIC.dataBeg, LMIC.dataLen);
              Serial.println();
            }
            // Programar siguiente transmisión en 60 segundos
            os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(60), do_send);
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
            Serial.println(F("EV_TXSTART"));
            break;
        case EV_TXCANCELED:
            Serial.println(F("EV_TXCANCELED"));
            break;
        case EV_RXSTART:
            break;
        case EV_JOIN_TXCOMPLETE:
            Serial.println(F("EV_JOIN_TXCOMPLETE: sin respuesta"));
            break;
        default:
            Serial.print(F("Evento desconocido: "));
            Serial.println((unsigned) ev);
            break;
    }
}

void do_send(osjob_t* j){
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, no enviando"));
    } else {
        LMIC_setTxData2(1, mydata, sizeof(mydata)-1, 0);
        Serial.println(F("Paquete en cola"));
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println(F("Iniciando..."));

    #ifdef VCC_ENABLE
    pinMode(VCC_ENABLE, OUTPUT);
    digitalWrite(VCC_ENABLE, HIGH);
    delay(1000);
    #endif

    os_init();
    LMIC_reset();

    #ifdef CFG_us915
    // SubBand 1 (canales 0-7)
    LMIC_selectSubBand(0);
    #endif

    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
    
    // Iniciar proceso de JOIN
    LMIC_startJoining();
}

void loop() {
    os_runloop_once();
}
```

**IMPORTANTE:** Reemplaza las credenciales en las líneas 7-19 con las tuyas convertidas al formato correcto.

---

## Paso 10: Subir el código al TTGO

1. Conecta el TTGO con el cable USB
2. En Arduino IDE, selecciona:
   - **Board:** ESP32 Dev Module
   - **Upload Speed:** 921600
   - **Flash Frequency:** 80MHz
   - **Flash Mode:** QIO
   - **Flash Size:** 4MB
   - **Port:** El puerto COM correspondiente
3. Haz clic en **Upload** (flecha →)
4. Espera a que termine la compilación y carga

---

## Paso 11: Verificar conexión

1. Abre Serial Monitor (Ctrl+Shift+M o icono de lupa)
2. Configura baudios a **115200**
3. Deberías ver:
   ```
   Iniciando...
   EV_JOINING
   ```
4. Después de unos segundos:
   ```
   EV_JOINED
   netid: 1
   devaddr: 01234567
   AppSKey: XX-XX-XX...
   NwkSKey: XX-XX-XX...
   ```

---

## Paso 12: Verificar uplinks en ChirpStack

1. Ve a tu dispositivo en ChirpStack
2. Pestaña **LoRaWAN frames**
3. Deberías ver:
   - **JOIN REQUEST** (del dispositivo al servidor)
   - **JOIN ACCEPT** (del servidor al dispositivo)
   - **Uplinks** con el mensaje "Hola ChirpStack!" cada 60 segundos

---

## Troubleshooting

### El dispositivo no hace JOIN:

**1. Verifica logs de ChirpStack:**
```bash
docker logs -f chirpstack-docker-chirpstack-1
```

**Errores comunes:**
- `region config ID does not match`: El Device Profile usa una región diferente a la configurada en el código
- `invalid mic`: Las credenciales están incorrectas o mal convertidas
- `device not found`: El DevEUI no existe en ChirpStack

**2. Verifica que el gateway reciba los JOIN REQUEST:**
```bash
docker logs -f chirpstack-docker-chirpstack-gateway-bridge-1
```

Deberías ver mensajes indicando que recibe uplinks del dispositivo.

**3. Verifica configuración de SubBand:**

En el código debe ser:
```cpp
LMIC_selectSubBand(0); // Para canales 0-7
```

En el Device Profile debe ser:
```
US915 (channels 0-7 + 64)
```

**4. Verifica conversión de credenciales:**

- DevEUI y JoinEUI deben estar en formato LSB (invertidos)
- AppKey debe estar en formato MSB (sin invertir)

### El Serial Monitor no muestra nada:

- Verifica que seleccionaste el puerto correcto
- Confirma baudios en 115200
- Presiona el botón RST del TTGO para reiniciarlo

### El gateway aparece offline:

- Verifica que el packet forwarder apunte al puerto 1700
- Confirma que la IP del servidor sea correcta
- Revisa logs del gateway físico

---

## Preguntas que debes poder responder

1. **Conceptos LoRaWAN:**
   - ¿Cuál es la diferencia entre LoRa y LoRaWAN?
   - ¿Qué es OTAA y en qué se diferencia de ABP?
   - ¿Por qué US915 se divide en SubBands?
   - ¿Qué función cumple el DevEUI?

2. **Arquitectura:**
   - ¿Qué componentes participan en una red LoRaWAN?
   - ¿Cuál es la diferencia entre el LNS y el Application Server?
   - ¿Por qué el gateway no procesa los datos?

3. **Seguridad:**
   - ¿Qué keys se generan después del JOIN?
   - ¿Por qué OTAA es más seguro que ABP?
   - ¿Dónde se almacenan las session keys?

4. **Técnico:**
   - ¿Por qué invertimos el orden de bytes en DevEUI pero no en AppKey?
   - ¿Qué pasa si el dispositivo pierde la sesión?
   - ¿Cuánto tiempo tarda típicamente un JOIN REQUEST?

---

## Entregables del laboratorio

1. **Capturas de pantalla:**
   - Serial Monitor mostrando JOIN exitoso con las session keys
   - ChirpStack mostrando el dispositivo en estado "Active"
   - LoRaWAN frames mostrando JOIN REQUEST, JOIN ACCEPT y al menos 2 uplinks

2. **Logs de ChirpStack:**
   - Exporta los logs del momento del JOIN mostrando que no hubo errores

3. **Documento con respuestas** a las preguntas de la sección anterior

4. **Análisis de tu configuración:**
   - ¿Qué SubBand usaste y por qué?
   - ¿Cuál es el DevAddr asignado a tu dispositivo?
   - ¿Qué payload enviaste y en qué puerto (f_port)?

---

## Recursos adicionales

- [Documentación oficial LMIC](https://github.com/mcci-catena/arduino-lmic)
- [ChirpStack documentation](https://www.chirpstack.io/docs/)
- [LoRaWAN specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-0-3/)
- [TTGO LoRa32 GitHub](https://github.com/LilyGO/TTGO-LORA32)
- [US915 Channel Plan](https://lora-developers.semtech.com/documentation/tech-papers-and-guides/physical-layer-proposal-2.4ghz/)

---

## Notas finales

Este laboratorio te introduce a los conceptos fundamentales de LoRaWAN:
- Activación segura mediante OTAA
- Configuración de regiones y SubBands
- Arquitectura de red LoRaWAN
- Integración con un LNS real (ChirpStack)

En el siguiente laboratorio (Semana 7) agregaremos sensores al TTGO para crear un nodo IoT completo que envíe datos reales a través de LoRaWAN.

¡Éxito en tu laboratorio!

---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)