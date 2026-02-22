# GUÍA DE LABORATORIO - SEMANA 7
## Registro y Conexión de TTGO LoRa32 a ChirpStack (OTAA)

**Curso:** Comunicaciones e IoT  
**Día:** Jueves y Viernes
**Duración:** 2 horas  
**Modalidad:** Presencial

---

## OBJETIVOS DEL LABORATORIO

### Objetivo General:
Implementar la conexión de un dispositivo TTGO LoRa32 a la plataforma ChirpStack utilizando el mecanismo de activación OTAA (Over-The-Air Activation) con LoRaWAN 1.1.

### Objetivos Específicos:
1. Crear y configurar un entorno completo en ChirpStack v4
2. Registrar un dispositivo End Node con sus credenciales OTAA
3. Configurar Arduino IDE para programar TTGO LoRa32
4. Completar el firmware con las credenciales desde ChirpStack
5. Verificar la conexión exitosa mediante Join Request/Accept
6. Comprender el proceso de activación OTAA

---

## REQUISITOS PREVIOS

### Hardware:
- Placa TTGO LoRa32 (ESP32 + SX1276)
- Cable USB (Micro-USB o USB-C según modelo)
- Antena LoRa conectada
- Computadora con puerto USB disponible

### Software:
- Arduino IDE 1.8.19 o superior instalado
- Soporte ESP32 en Arduino IDE
- Librería MCCI LoRaWAN LMIC instalada
- Driver USB (CH340 o CP2102) instalado

### Acceso a Servicios:
- Gateway LoRaWAN operativo (banda US915)
- ChirpStack v4 accesible
- Credenciales de acceso a ChirpStack

### Ubicación del Código:
```
\\Drive compartido\IoT-2025\Desarrollo\Laboratorios\LoRaWAN\ESP32\TTGO_LoRaWAN_v3
```

---

## PREPARACIÓN DEL ENTORNO

### Paso 0.1: Instalar Arduino IDE (si no lo tienes)

1. **Descargar Arduino IDE:**
   ```
   URL: https://www.arduino.cc/en/software
   Versión recomendada: 1.8.19 o superior
   ```

2. **Instalar en tu sistema operativo**

3. **Abrir Arduino IDE y verificar que funciona**

---

### Paso 0.2: Configurar Soporte para ESP32

1. **Abrir Preferencias:**
   ```
   File → Preferences (o Ctrl+,)
   ```

2. **Agregar URL del Board Manager:**
   ```
   En "Additional Board Manager URLs" pegar:
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```

3. **Instalar plataforma ESP32:**
   ```
   Tools → Board → Board Manager
   Buscar: "esp32"
   Instalar: "esp32 by Espressif Systems" (versión 2.0.11 o superior)
   Esperar a que termine la instalación (puede tardar varios minutos)
   ```

4. **Verificar instalación:**
   ```
   Tools → Board → ESP32 Arduino
   Debe aparecer "TTGO LoRa32-OLED" en la lista de placas
   ```

---

### Paso 0.3: Instalar Librería LMIC

1. **Abrir Library Manager:**
   ```
   Sketch → Include Library → Manage Libraries
   o
   Ctrl+Shift+I
   ```

2. **Buscar e instalar LMIC:**
   ```
   En el buscador escribir: "MCCI LoRaWAN LMIC"
   Seleccionar: "MCCI LoRaWAN LMIC library" por Terry Moore
   Click en "Install"
   Versión recomendada: 4.1.1 o superior
   ```

3. **Verificar instalación:**
   ```
   File → Examples → MCCI LoRaWAN LMIC library
   Deben aparecer ejemplos
   ```

---

### Paso 0.4: Conectar y Verificar TTGO

1. **Conectar la antena:**
   ```
   ⚠️ MUY IMPORTANTE: NUNCA transmitir sin antena conectada
   
   - Conectar antena al conector SMA
   - Asegurar que esté bien apretada
   - Colocar en posición vertical
   ```

2. **Conectar USB:**
   ```
   - Conectar cable USB al TTGO
   - Conectar otro extremo a la computadora
   - Observar que el LED de power enciende
   ```

3. **Seleccionar placa en Arduino IDE:**
   ```
   Tools → Board → ESP32 Arduino → TTGO LoRa32-OLED
   
   Esta es la opción correcta para las placas TTGO con LoRa y OLED.
   Configura automáticamente todos los parámetros necesarios.
   ```

4. **Seleccionar puerto COM:**
   ```
   Tools → Port → COMx (Windows) o /dev/ttyUSBx (Linux/Mac)
   
   Si no aparece puerto:
   - Desconectar y reconectar USB
   - Instalar driver CH340 o CP2102
   - Probar otro cable USB
   - Probar otro puerto USB de la computadora
   ```

5. **Configurar parámetros de carga:**
   ```
   Tools → Upload Speed: 921600
   Tools → CPU Frequency: 240MHz
   Tools → Flash Frequency: 80MHz
   Tools → Flash Mode: QIO
   Tools → Flash Size: 4MB (32Mb)
   Tools → Partition Scheme: Default 4MB with spiffs
   ```

6. **Probar con código de prueba:**
   ```cpp
   void setup() {
     Serial.begin(115200);
     pinMode(2, OUTPUT);
   }
   
   void loop() {
     Serial.println("TTGO OK");
     digitalWrite(2, !digitalRead(2));
     delay(1000);
   }
   ```

7. **Cargar código de prueba:**
   ```
   Click en Upload (→)
   Esperar: "Hard resetting via RTS pin..."
   ```

8. **Abrir Serial Monitor:**
   ```
   Tools → Serial Monitor
   Baudrate: 115200
   Debe aparecer: "TTGO OK" cada segundo
   ```

✅ Si todo lo anterior funciona, estás listo para continuar.

---

##  PARTE 1: CREACIÓN DEL ENTORNO EN CHIRPSTACK

### Paso 1.1: Acceder a ChirpStack

1. **Abrir navegador web**

2. **Ir a la URL proporcionada por el profesor:**
   ```
   Ejemplo: http://192.168.1.100:8080
   o
   https://chirpstack.universidad.edu
   ```

3. **Iniciar sesión:**
   ```
   Usuario: [proporcionado por profesor]
   Contraseña: [proporcionada por profesor]
   ```

4. **Verificar que aparece el dashboard principal**

---

### Paso 1.2: Crear un Tenant (Inquilino)

**¿Qué es un Tenant?**
Un Tenant es un espacio aislado dentro de ChirpStack donde puedes organizar aplicaciones y dispositivos. Es como tu "espacio de trabajo" personal.

**Pasos:**

1. **Navegar a Tenants:**
   ```
   En el menú lateral izquierdo → Tenants
   ```

2. **Crear nuevo Tenant:**
   ```
   Click en botón: "+ Add tenant"
   ```

3. **Llenar formulario:**
   ```
   Tenant name: iot-lab-equipo[X]
   
   Donde [X] es tu número de equipo
   Ejemplos: iot-lab-equipo1, iot-lab-equipo2
   
   Description: Laboratorio Semana 7 - Equipo [X]
   
   Can have gateways: ☑️ (marcar checkbox)
   Max device count: 10
   Max gateway count: 1
   ```

4. **Guardar:**
   ```
   Click en "Submit" o "Add tenant"
   ```

5. **Verificar:**
   ```
   Debe aparecer tu tenant en la lista
   Click en el nombre para entrar
   ```

---

### Paso 1.3: Crear una Aplicación

**¿Qué es una Aplicación?**
Una Aplicación en ChirpStack agrupa dispositivos relacionados. Todos los dispositivos de tu proyecto estarán dentro de esta aplicación.

**Pasos:**

1. **Dentro de tu Tenant:**
   ```
   Click en pestaña "Applications"
   ```

2. **Crear nueva aplicación:**
   ```
   Click en botón: "+ Add application"
   ```

3. **Llenar formulario:**
   ```
   Application name: modulacion-digital
   
   Description: Proyecto de modulación digital - Semana 7
   ```

4. **Guardar:**
   ```
   Click en "Submit"
   ```

5. **Entrar a la aplicación:**
   ```
   Click en "modulacion-digital" para abrirla
   ```

---

### Paso 1.4: Crear un Device Profile (Perfil de Dispositivo)

**¿Qué es un Device Profile?**
Define las características técnicas del dispositivo: región, clase LoRaWAN, versión MAC, etc. Es como una "plantilla" de configuración.

**Pasos:**

1. **Navegar a Device Profiles:**
   ```
   Desde tu Tenant → Device profiles
   ```

2. **Crear nuevo perfil:**
   ```
   Click en "+ Add device profile"
   ```

3. **Pestaña "General":**
   ```
   Name: TTGO-LoRa32-OTAA
   
   Description: TTGO LoRa32 con OTAA para laboratorio
   
   Region: US915
   
   MAC version: LoRaWAN 1.1.0
   
   Regional parameters revision: RP002-1.0.3
   
   Expected uplink interval: 60 (segundos)
   ```

4. **Pestaña "Join (OTAA/ABP)":**
   ```
   Device supports OTAA: ☑️ (MARCAR)
   
   Device supports Class B: ☐ (NO marcar)
   
   Device supports Class C: ☐ (NO marcar)
   ```

5. **Pestaña "Class-A":**
   ```
   RX1 delay: 1 (segundo)
   
   RX1 data rate offset: 0
   
   RX2 data rate: 8
   
   RX2 frequency: 923300000 (Hz)
   ```

6. **Pestaña "Codec" (opcional por ahora):**
   ```
   Codec: None
   (Lo configuraremos en semana 8)
   ```

7. **Guardar:**
   ```
   Click en "Submit"
   ```

---

### Paso 1.5: Crear el Dispositivo (Device)

**Este es el paso más importante - aquí registramos tu TTGO específico.**

**Pasos:**

1. **Ir a tu aplicación:**
   ```
   Applications → modulacion-digital
   ```

2. **Ir a Devices:**
   ```
   Click en pestaña "Devices"
   ```

3. **Agregar dispositivo:**
   ```
   Click en "+ Add device"
   ```

4. **Llenar información básica:**
   ```
   Device name: TTGO-[TuNombre]
   Ejemplo: TTGO-Juan
   
   Description: Dispositivo TTGO LoRa32 de [Tu Nombre]
   
   Device EUI (EUI-64):
   ┌─────────────────────────────────────┐
   │ Click en botón 🔄 "Generate"        │
   │ Se generará automáticamente         │
   │ Ejemplo: 70b3d5e75e0012a4           │
   └─────────────────────────────────────┘
   
   ⚠️ COPIAR ESTE VALOR - Lo necesitarás después
   ```

5. **Seleccionar perfil:**
   ```
   Device-profile: TTGO-LoRa32-OTAA
   (El que creamos en paso anterior)
   ```

6. **Guardar:**
   ```
   Click en "Submit"
   ```

---

### Paso 1.6: Obtener Claves OTAA

**Estas son las credenciales que pegará en el código Arduino.**

**Pasos:**

1. **Entrar al dispositivo:**
   ```
   Devices → TTGO-[TuNombre]
   ```

2. **Ir a pestaña "Keys (OTAA)":**
   ```
   Click en pestaña "Keys (OTAA)"
   ```

3. **Copiar DevEUI:**
- MSB (Most Significant Bit) 
- LSB (Least Significant Bit)
  
   ```
   Formato en ChirpStack (MSB): 70b3d5e75e0012a4
    
   Para LMIC necesitas LSB (invertido):
   a4 12 00 5e e7 d5 b3 70
   
   COPIAR EN ESTA TABLA:
   ┌──────────────────────────────────────┐
   │ DevEUI (MSB): ______________________ │
   │ DevEUI (LSB): ______________________ │
   └──────────────────────────────────────┘
   ```

4. **Copiar JoinEUI/AppEUI:**
   ```
   Si está vacío, usar valor común:
   0000000000000000
   
   O generar uno nuevo con botón Generate
   
   📋 COPIAR:
   ┌──────────────────────────────────────┐
   │ JoinEUI (MSB): _____________________ │
   │ JoinEUI (LSB): _____________________ │
   └──────────────────────────────────────┘
   ```

5. **Generar y copiar AppKey:**
   ```
   Click en botón 🔄 "(Re)generate application key"
   
   Se generará clave de 32 caracteres hex (16 bytes)
   Ejemplo: a1b2c3d4e5f6071829384756a1b2c3d4
   
   ⚠️ AppKey se usa en MSB (tal cual)
   
   📋 COPIAR:
   ┌──────────────────────────────────────┐
   │ AppKey (MSB): ______________________ │
   └──────────────────────────────────────┘
   ```

6. **Guardar claves:**
   ```
   Click en "Submit" para guardar
   ```

---

### Paso 1.7: Herramienta para Convertir Formato (LSB)

**Para convertir DevEUI y JoinEUI de MSB a LSB:**

```
Formato MSB (ChirpStack): 70 b3 d5 e7 5e 00 12 a4
Formato LSB (LMIC):       a4 12 00 5e e7 d5 b3 70
                          ↑                       ↑
                          Se invierte byte por byte
```

**Ejemplo práctico:**

```
ChirpStack muestra: 70b3d5e75e0012a4

Separar en bytes: 70 b3 d5 e7 5e 00 12 a4

Invertir orden: a4 12 00 5e e7 d5 b3 70

Para Arduino: 0xA4, 0x12, 0x00, 0x5E, 0xE7, 0xD5, 0xB3, 0x70
```

**Herramienta online (opcional):**
```
https://www.scadacore.com/tools/programming-calculators/online-hex-converter/
```

---

## 💻 PARTE 2: CONFIGURACIÓN DEL SKETCH ARDUINO

### Paso 2.1: Descargar el Código

1. **Acceder al Drive compartido:**
   ```
   Ruta: \IoT-2025\Desarrollo\Laboratorios\LoRaWAN\ESP32\TTGO_LoRaWAN_v3
   ```

2. **Descargar el archivo:**
   ```
   Archivo: TTGO_LoRaWAN_v3.ino
   ```

3. **Guardar en tu computadora:**
   ```
   Crear carpeta: Documents\Arduino\TTGO_LoRaWAN_v3\
   Guardar archivo dentro de esta carpeta
   ```

4. **Abrir en Arduino IDE:**
   ```
   File → Open → Seleccionar TTGO_LoRaWAN_v3.ino
   ```

---

### Paso 2.2: Entender la Estructura del Código

**El código tiene estas secciones principales:**

```cpp
// 1. LIBRERÍAS
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// 2. CREDENCIALES OTAA (AQUÍ PEGARÁS TUS DATOS)
static const u1_t PROGMEM APPEUI[8] = { ... };
static const u1_t PROGMEM DEVEUI[8] = { ... };
static const u1_t PROGMEM APPKEY[16] = { ... };

// 3. CONFIGURACIÓN DE PINES TTGO
const lmic_pinmap lmic_pins = {
  .nss = 18,      // Slave Select
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 14,      // Reset
  .dio = {26, 33, 32},  // DIO0, DIO1, DIO2
};

// 4. FUNCIONES CALLBACK (NO TOCAR)
void os_getArtEui (u1_t* buf) { ... }
void os_getDevEui (u1_t* buf) { ... }
void os_getDevKey (u1_t* buf) { ... }

// 5. SETUP (INICIALIZACIÓN)
void setup() {
  Serial.begin(115200);
  os_init();
  LMIC_reset();
  LMIC_startJoining();
}

// 6. LOOP (BUCLE PRINCIPAL)
void loop() {
  os_runloop_once();
}
```

---

### Paso 2.3: Completar las Credenciales OTAA

**⚠️ ESTA ES LA PARTE MÁS IMPORTANTE**

**Buscar en el código estas líneas:**

```cpp
//  LLAVES OTAA 
// Estos valores deben copiarse desde la plataforma ChirpStack
static const u1_t PROGMEM APPEUI[8] = { 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ }; // JoinEUI
static const u1_t PROGMEM DEVEUI[8] = { 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ }; // DevEUI
static const u1_t PROGMEM APPKEY[16] = { 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ , 0x__ }; // AppKey
```

---

#### Ejemplo Completo de Llenado:

**Datos de ejemplo de ChirpStack:**
```
DevEUI (MSB):  70b3d5e75e0012a4
JoinEUI (MSB): 0000000000000000
AppKey (MSB):  a1b2c3d4e5f6071829384756a1b2c3d4
```

**Paso 1: Convertir DevEUI a LSB**
```
MSB: 70 b3 d5 e7 5e 00 12 a4
LSB: a4 12 00 5e e7 d5 b3 70
```

**Paso 2: Convertir JoinEUI a LSB**
```
MSB: 00 00 00 00 00 00 00 00
LSB: 00 00 00 00 00 00 00 00
```

**Paso 3: AppKey queda en MSB**
```
MSB: a1 b2 c3 d4 e5 f6 07 18 29 38 47 56 a1 b2 c3 d4
(No se invierte)
```

**Paso 4: Pegar en el código:**

```cpp
// JoinEUI / AppEUI (LSB - invertido)
static const u1_t PROGMEM APPEUI[8] = { 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
};

// DevEUI (LSB - invertido)
static const u1_t PROGMEM DEVEUI[8] = { 
    0xA4, 0x12, 0x00, 0x5E, 0xE7, 0xD5, 0xB3, 0x70 
};

// AppKey (MSB - tal cual)
static const u1_t PROGMEM APPKEY[16] = { 
    0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6, 0x07, 0x18,
    0x29, 0x38, 0x47, 0x56, 0xA1, 0xB2, 0xC3, 0xD4 
};
```

---

### Paso 2.4: Verificar y Compilar

1. **Guardar el archivo:**
   ```
   File → Save (Ctrl+S)
   ```

2. **Verificar/Compilar:**
   ```
   Click en botón ✓ (Verify)
   o
   Sketch → Verify/Compile
   ```

3. **Esperar compilación:**
   ```
   Debe decir en consola:
   "Sketch uses XXXXX bytes..."
   "Done compiling"
   ```

4. **Si hay errores:**
   ```
   Error común: Falta coma entre bytes
   Solución: Verificar todas las comas
   
   Error común: Falta 0x antes del número
   Solución: Todos deben tener 0x
   
   Error común: Número de bytes incorrecto
   Solución: APPEUI y DEVEUI = 8 bytes
              APPKEY = 16 bytes
   ```

---

### Paso 2.5: Cargar al TTGO

1. **Verificar configuración:**
   ```
   Tools → Board: TTGO LoRa32-OLED ✅
   Tools → Port: COMx ✅
   Tools → Upload Speed: 921600 ✅
   ```

2. **Iniciar carga:**
   ```
   Click en botón → (Upload)
   ```

3. **Esperar:**
   ```
   "Connecting........_____...."
   "Writing at 0x00010000... (100%)"
   "Hard resetting via RTS pin..."
   ```

4. **Si no conecta:**
   ```
   Mantén presionado botón BOOT del TTGO
   Click Upload
   Cuando empiece a cargar, suelta BOOT
   ```

---

## ✅ PARTE 3: VERIFICACIÓN Y PRUEBAS

### Paso 3.1: Abrir Serial Monitor

1. **Abrir monitor:**
   ```
   Tools → Serial Monitor
   o
   Ctrl+Shift+M
   ```

2. **Configurar:**
   ```
   Baudrate: 115200
   ```

3. **Reiniciar TTGO:**
   ```
   Presionar botón RESET
   ```

---

### Paso 3.2: Observar Join Request

**Salida esperada en Serial Monitor:**

```
Iniciando OTAA...
Packet queued
212850: EV_JOINING
295122: EV_TXSTART
```

**¿Qué significa cada línea?**
```
"Iniciando OTAA..."  → Setup completo
"Packet queued"      → Join Request preparado
"EV_JOINING"         → Intentando Join
"EV_TXSTART"         → Transmitiendo Join Request
```

---

### Paso 3.3: Verificar en ChirpStack

1. **Ir a tu dispositivo en ChirpStack:**
   ```
   Applications → modulacion-digital → Devices → TTGO-[TuNombre]
   ```

2. **Ir a pestaña "LoRaWAN frames":**
   ```
   Click en "LoRaWAN frames"
   ```

3. **Buscar JoinRequest:**
   ```
   Debe aparecer un evento tipo "JoinRequest" (uplink)
   
   Información visible:
   - Timestamp
   - Frequency (MHz)
   - Data rate
   - RSSI y SNR
   ```

4. **Si NO aparece JoinRequest:**
   ```
   Problemas posibles:
   - Gateway apagado o sin internet
   - TTGO muy lejos del gateway
   - Antena no conectada
   - Credenciales incorrectas
   - Región incorrecta (debe ser US915)
   ```

---

### Paso 3.4: Join Accept Exitoso

**Si todo está correcto, verás en Serial Monitor:**

```
295122: EV_TXSTART
467890: EV_JOINED
DevAddr: 26011234
```

**¿Qué significa?**
```
"EV_JOINED"    → ¡Join exitoso!
"DevAddr: ..." → Dirección asignada por el servidor
```

**En ChirpStack verás:**
```
LoRaWAN frames:
1. JoinRequest (uplink del dispositivo)
2. JoinAccept (downlink del servidor) ✅
```

**En la pestaña "Device data":**
```
Debe cambiar:
- Last seen: hace pocos segundos
- Status: Activo
```

---

### Paso 3.5: Enviar Primer Uplink (Opcional)

Si el Join fue exitoso, el dispositivo puede enviar datos.

**Modificar código para enviar mensaje:**

Agregar esta función después de `setup()`:

```cpp
static osjob_t sendjob;

void do_send(osjob_t* j) {
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, no enviando"));
    } else {
        uint8_t mydata[] = "Hello";
        LMIC_setTxData2(1, mydata, sizeof(mydata)-1, 0);
        Serial.println(F("Packet queued"));
    }
}

void onEvent (ev_t ev) {
    switch(ev) {
        case EV_JOINED:
            Serial.println(F("EV_JOINED"));
            LMIC_setLinkCheckMode(0);
            // Enviar primer paquete
            do_send(&sendjob);
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE"));
            break;
    }
}
```

---

## ACTIVIDADES PARA ENTREGAR

### Entregable 1: Configuración ChirpStack
```
Captura de pantalla que incluya:
- Nombre del Tenant visible
- Lista de aplicaciones con "modulacion-digital"
- Device Profile "TTGO-LoRa32-OTAA" visible
```

### Entregable 2: Dispositivo Registrado
```
Captura de pantalla mostrando:
- Nombre del dispositivo: TTGO-[TuNombre]
- Pestaña "Keys (OTAA)" con las tres claves visibles
- DevEUI, JoinEUI/AppEUI, AppKey
(Puedes difuminar parte de las claves por seguridad)
```

### Entregable 3: Código Arduino
```
Archivo .ino con:
- Credenciales completadas correctamente
- Nombre del archivo: TTGO_[TuNombre]_v3.ino

⚠️ NO subir a repositorio público (contiene claves)
Entregar por plataforma del curso
```

### Entregable 4: Join Request
```
Captura del Serial Monitor mostrando:
- "Iniciando OTAA..."
- "EV_JOINING"
- "EV_TXSTART"

Y/O

Captura de ChirpStack mostrando:
- LoRaWAN frames con JoinRequest visible
- Timestamp, frequency, data rate
```

### Entregable 5: Join Accept (si fue exitoso)
```
Captura del Serial Monitor mostrando:
- "EV_JOINED"
- "DevAddr: ..."

Y

Captura de ChirpStack mostrando:
- JoinRequest + JoinAccept en LoRaWAN frames
- Device data con "Last seen" reciente
```

### Entregable 6: Primer Uplink (BONUS +10 pts)
```
Captura de ChirpStack mostrando:
- Uplink de datos (no Join) en LoRaWAN frames
- Payload visible (aunque sea en HEX)
```

---

## TROUBLESHOOTING

### Problema 1: No compila - Error de librería

**Error:**
```
lmic.h: No such file or directory
```

**Solución:**
```
1. Sketch → Include Library → Manage Libraries
2. Buscar "MCCI LoRaWAN LMIC"
3. Instalar versión 4.1.1 o superior
4. Reiniciar Arduino IDE
```

---

### Problema 2: No aparece puerto COM

**Síntomas:**
```
Tools → Port → (grayed out)
```

**Soluciones:**
```
1. Verificar cable USB funciona (probar con otro dispositivo)
2. Desconectar y reconectar USB
3. Probar otro puerto USB de la computadora
4. Instalar driver:
   - Para CH340: https://sparks.gogo.co.nz/ch340.html
   - Para CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
5. Reiniciar computadora
6. En Windows: Device Manager → verificar que aparece COM port
```

---

### Problema 3: Error al cargar - ESP32-S3

**Error:**
```
A fatal error occurred: This chip is ESP32-S3, not ESP32
```

**Solución:**
```
Tu TTGO tiene chip diferente.

Cambiar en Arduino IDE:
Tools → Board → ESP32 Arduino → ESP32S3 Dev Module

O si tienes TTGO específico:
Tools → Board → ESP32 Arduino → TTGO T-Beam
```

---

### Problema 4: No encuentra placa TTGO LoRa32-OLED

**Síntomas:**
```
En Tools → Board no aparece "TTGO LoRa32-OLED"
```

**Solución:**
```
1. Verificar que instalaste ESP32:
   Tools → Board → Board Manager → esp32

2. Si no aparece, actualizar a versión más reciente:
   Board Manager → esp32 → Update

3. Reiniciar Arduino IDE

4. Si aún no aparece, usar:
   Tools → Board → ESP32 Dev Module
   Pero configurar manualmente todos los parámetros
```

---

### Problema 5: Join Request no llega a ChirpStack

**Síntomas:**
```
Serial Monitor:
✅ "EV_JOINING"
✅ "EV_TXSTART"

ChirpStack:
❌ No aparece JoinRequest
```

**Diagnóstico paso a paso:**

**1. Verificar Gateway activo:**
```
ChirpStack → Gateways → [Tu gateway]
Last seen: debe ser < 1 minuto

Si no está activo:
→ Contactar al profesor/administrador
```

**2. Verificar distancia al gateway:**
```
LoRaWAN alcance típico:
- Interiores: 100-500 metros
- Exteriores: 2-5 km

Solución:
- Acercarse al gateway
- Ir a zona con línea de vista
- Evitar sótanos o lugares blindados
```

**3. Verificar antena:**
```
⚠️ CRÍTICO: Antena debe estar conectada

Verificar:
✅ Antena conectada al conector SMA
✅ Antena apretada (no floja)
✅ Antena en posición vertical

Si transmitiste sin antena:
→ Módulo LoRa puede haberse dañado
```

**4. Verificar región/sub-banda:**
```
En el código, agregar después de LMIC_reset():

LMIC_selectSubBand(1); // Para Sub-banda 2 (canales 8-15)

Gateway debe estar en la misma sub-banda
```

**5. Verificar credenciales:**
```
Común error: Orden de bytes incorrecto

APPEUI y DEVEUI: DEBEN estar en LSB (invertidos)
APPKEY: DEBE estar en MSB (tal cual)

Verificar byte por byte con ChirpStack
```

---

### Problema 6: Join fallido repetidamente

**Síntomas:**
```
Serial Monitor:
EV_JOINING
EV_TXSTART
EV_JOIN_FAILED
EV_JOINING (se repite)
```

**Soluciones:**

**1. Credenciales incorrectas:**
```
Verificar EXACTAMENTE cada byte:

En ChirpStack Device → Keys (OTAA)
vs
Tu código

Un solo byte diferente = Join fallará
```

**2. Dispositivo no registrado:**
```
Verificar en ChirpStack:
Applications → modulacion-digital → Devices

Tu dispositivo debe estar en la lista
Estado: puede estar "Never seen" (normal antes de Join)
```

**3. Device Profile incorrecto:**
```
Verificar:
- MAC version: LoRaWAN 1.1.0 ✅
- Region: US915 ✅
- Supports OTAA: Yes ✅

Si está mal: Editar o recrear Device Profile
```

**4. Limpiar sesión anterior:**
```
En el código, en setup() después de LMIC_reset():

LMIC.dn2Dr = DR_SF9;  // Forzar data rate
LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
```

---

### Problema 7: Compilación exitosa pero no funciona

**Síntomas:**
```
- Código carga sin errores
- Serial Monitor no muestra nada
o muestra caracteres raros
```

**Soluciones:**

**1. Baudrate incorrecto:**
```
Serial Monitor → 115200 baud (esquina inferior derecha)

Debe coincidir con Serial.begin(115200) en código
```

**2. Reset después de cargar:**
```
Después de "Hard resetting via RTS pin..."
Presionar botón RESET físico del TTGO
```

**3. Puerto COM incorrecto:**
```
Cerrar Serial Monitor
Tools → Port → Verificar puerto
Abrir Serial Monitor nuevamente
```

**4. Cable USB de mala calidad:**
```
Algunos cables son solo para carga, no datos
Probar con cable USB que sepas que funciona
```

---

### Problema 8: Error de memoria

**Error:**
```
Sketch uses XXXXXX bytes (XX%) of program storage space
region `drom0_0_seg' overflowed
```

**Solución:**
```
1. Tools → Partition Scheme: "Huge APP (3MB No OTA/1MB SPIFFS)"

2. Eliminar código innecesario o comentarios muy largos

3. Usar F() macro para strings:
   Serial.println(F("Texto"));
   En lugar de:
   Serial.println("Texto");
```

---

### Problema 9: Lecturas inestables de RSSI/SNR

**Síntomas:**
```
En ChirpStack:
RSSI varía mucho: -120 dBm, -80 dBm, -110 dBm...
```

**Soluciones:**
```
1. Mejorar ubicación del TTGO:
   - Evitar cerca de metales
   - Evitar dentro de cajas metálicas
   - Colocar cerca de ventana

2. Verificar antena:
   - Debe estar vertical
   - No debe estar doblada
   - No debe tocar objetos metálicos

3. Alejarse de fuentes de interferencia:
   - WiFi routers
   - Microondas
   - Motores eléctricos
```

---

## CONCEPTOS CLAVE EXPLICADOS

### ¿Qué es OTAA?

**Over-The-Air Activation (OTAA)** es el método más seguro de activación en LoRaWAN.

```
Proceso OTAA:

1. DISPOSITIVO tiene guardado:
   - DevEUI (ID único)
   - JoinEUI/AppEUI (ID de aplicación)
   - AppKey (clave secreta)

2. DISPOSITIVO envía Join Request:
   Join Request = [DevEUI + JoinEUI + Nonce + MIC]
   MIC = firma calculada con AppKey

3. SERVIDOR verifica:
   - ¿DevEUI registrado? ✓
   - ¿MIC correcto? ✓
   - Si todo OK → genera claves de sesión

4. SERVIDOR envía Join Accept:
   Join Accept = [DevAddr + NwkSKey + AppSKey] (cifrado)

5. DISPOSITIVO ya puede comunicarse:
   - Todos los datos cifrados con NwkSKey y AppSKey
   - Claves válidas solo para esta sesión
   - Si se reinicia, vuelve a hacer Join
```

**Ventajas de OTAA:**
- ✅ Claves de sesión únicas por Join
- ✅ Mayor seguridad que ABP
- ✅ Permite re-Join automático
- ✅ Soportado por todos los servidores LoRaWAN

---

### ¿Qué es LSB vs MSB?

**MSB (Most Significant Byte first)** = Byte más significativo primero
**LSB (Least Significant Byte first)** = Byte menos significativo primero

```
Ejemplo con número: 0x12345678

MSB: 12 34 56 78 (se lee normal)
LSB: 78 56 34 12 (se lee al revés)

Por qué importa:
- ChirpStack muestra claves en MSB
- Librería LMIC espera DevEUI y JoinEUI en LSB
- Librería LMIC espera AppKey en MSB

Por eso debemos invertir DevEUI y JoinEUI,
pero NO invertir AppKey
```

---

### ¿Qué es un Device Profile?

Es una "plantilla" de configuración que define:

```
Configuración de Red:
- Región: US915, EU868, AS923, etc.
- Clase: A (más común), B, C
- MAC version: LoRaWAN 1.0.x o 1.1.x

Configuración de Radio:
- Data rates permitidos
- Frecuencias RX
- Potencia de transmisión

Configuración de Aplicación:
- Codec para decodificar payloads
- Intervalo esperado de uplinks
```

Un Device Profile se puede reutilizar para múltiples dispositivos similares.

---

### ¿Qué significan los eventos LMIC?

```
EV_JOINING
→ Dispositivo está intentando hacer Join
→ Construyendo y enviando Join Request

EV_TXSTART  
→ Inicio de transmisión RF
→ Modulando y enviando por antena

EV_JOINED
→ Join exitoso
→ Recibido Join Accept del servidor
→ Claves de sesión establecidas

EV_TXCOMPLETE
→ Transmisión completada
→ Ventanas RX cerradas
→ Listo para siguiente transmisión

EV_JOIN_FAILED
→ Join falló
→ No se recibió Join Accept
→ LMIC reintentará automáticamente
```

---

##  PREGUNTAS PARA EL REPORTE DE LABORATORIO

### Preguntas Teóricas (responder en el reporte):

1. **(5 pts)** ¿Cuál es la diferencia entre OTAA y ABP? ¿Cuál es más seguro y por qué?

2. **(5 pts)** Explica qué son DevEUI, JoinEUI y AppKey. ¿Para qué se usa cada uno?

3. **(5 pts)** ¿Por qué DevEUI y JoinEUI deben invertirse (LSB) pero AppKey no?

4. **(5 pts)** ¿Qué es un Device Profile y para qué sirve?

5. **(5 pts)** Explica el flujo completo del proceso OTAA desde que el dispositivo enciende hasta que puede enviar datos.

### Preguntas Prácticas (responder con capturas):

6. **(10 pts)** ¿Qué región y sub-banda usaste? ¿Por qué es importante que Gateway y dispositivo estén en la misma?

7. **(10 pts)** Muestra con captura el RSSI y SNR de tu Join Request. ¿Es buena la señal? Justifica.

8. **(10 pts)** Si cambiaras la AppKey en ChirpStack pero no en el código, ¿qué pasaría? ¿Por qué?

---


## RÚBRICA DE EVALUACIÓN

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| **Configuración ChirpStack** | 30 | |
| - Tenant y Application | 10 | Creados correctamente |
| - Device Profile | 10 | Configurado para OTAA, US915 |
| - Device registrado | 10 | Con credenciales válidas |
| **Código Arduino** | 30 | |
| - Credenciales correctas | 15 | LSB/MSB apropiados |
| - Código compila | 10 | Sin errores |
| - Código cargado | 5 | Funciona en TTGO |
| **Pruebas** | 20 | |
| - Join Request enviado | 10 | Visible en ChirpStack |
| - Join Accept recibido | 10 | BONUS si exitoso |
| **Reporte** | 20 | |
| - Capturas incluidas | 10 | Claras y relevantes |
| - Preguntas respondidas | 10 | Completas y correctas |
| **TOTAL** | **100** | |

---


### Recursos Adicionales:

**Documentación:**
- ChirpStack v4: https://www.chirpstack.io/docs/
- LMIC Arduino: https://github.com/mcci-catena/arduino-lmic
- LoRaWAN Spec: https://lora-alliance.org/resource_hub/lorawan-specification-v1-1/

**Videos de referencia:**
- [Si tienes videos disponibles, añadir links]

---

## REFERENCIAS

1. ChirpStack Documentation. (2024). *ChirpStack v4 User Guide*. https://www.chirpstack.io/docs/

2. LoRa Alliance. (2021). *LoRaWAN® Specification v1.1*. https://lora-alliance.org/

3. MCCI Corporation. (2024). *Arduino-LMIC library for LoRaWAN®*. GitHub repository.

4. Semtech Corporation. (2019). *SX1276/77/78/79 Datasheet*.

5. Espressif Systems. (2023). *ESP32 Series Datasheet*.

---

## PRÓXIMOS PASOS

**Después de completar este laboratorio:**

1. **Semana 8:** Agregar sensor HC-SR04 y enviar datos reales
2. **Semana 9:** Implementar decodificador de payloads en ChirpStack
3. **Semana 10:** Crear dashboard de visualización de datos
4. **Proyecto Final:** Sistema IoT con sensores y NSS y Application Server

---

## CONSEJOS FINALES

```
- Toma tu tiempo para entender cada paso
- Anota las credenciales en un lugar seguro
- Haz capturas de pantalla en cada etapa
- Si algo falla, revisa esta guía paso a paso
- No dudes en preguntar al profesor
- Trabaja en equipo pero entrega individual
- Guarda tu código en múltiples lugares
```

⚠️ NO compartas tus credenciales OTAA públicamente

---


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)