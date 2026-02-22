# 🚀 GUÍA DE LABORATORIO: DECODIFICADORES EN CHIRPSTACK
## "Hola Mundo" con TTGO, Heltec y CubeCell

**Duración Total: 60 minutos**
**Objetivo:** Entender cómo codifica cada dispositivo y crear decodificadores en ChirpStack para interpretarlos

---



---

# 📌 SECCIÓN 1: INTRODUCCIÓN Y CONTEXTO
**⏱️ 5 minutos**

## ¿Qué es un Codec?

Un **codec** es un programa que traduce datos:
- **Encode:** Convierte datos legibles → datos encriptados/comprimidos
- **Decode:** Convierte datos encriptados → datos legibles nuevamente

**En nuestro caso:**
```
Device (TTGO/Heltec/CubeCell)
    ↓ [Crea payload en bytes]
    ↓ [Lo encripta con AES-128]
    ↓ [Lo envía por LoRaWAN]
LoRaWAN Gateway
    ↓ [Recibe bytes encriptados]
ChirpStack
    ↓ [Los desencripta automáticamente]
    ↓ [AQUÍ entra tu DECODER]
    ↓ [Interpreta: byte[0]=tipo, bytes[1-4]=timestamp, etc.]
Dashboard
    ↓ [Muestra datos legibles para humanos]
```

---

## 🔍 Los 3 Dispositivos Envían Datos Diferentes

Aunque todos envían **"hola mundo" + timestamp**, lo hacen de formas distintas:

### TTGO T3 (16 bytes)
```
┌─────┬──────────────────┬─────────────────────┬─────────┐
│[0]  │  [1-4]           │     [5-14]          │  [15]   │
├─────┼──────────────────┼─────────────────────┼─────────┤
│0x48 │ Timestamp (LE)   │ "hola mundo" (ASCII)│Checksum │
│Tipo │ 4 bytes          │ 10 bytes            │ 1 byte  │
└─────┴──────────────────┴─────────────────────┴─────────┘
Total: 16 bytes
```

**¿Por qué?** El TTGO usa LMIC library, que agrega un byte de tipo al inicio para identificar qué sensor transmite.

### Heltec LoRa32 V3 (16 bytes)
```
┌─────┬──────────────────┬─────────────────────┬─────────┐
│[0]  │  [1-4]           │     [5-14]          │  [15]   │
├─────┼──────────────────┼─────────────────────┼─────────┤
│0x48 │ Timestamp (LE)   │ "hola mundo" (ASCII)│Checksum │
│Tipo │ 4 bytes          │ 10 bytes            │ 1 byte  │
└─────┴──────────────────┴─────────────────────┴─────────┘
Total: 16 bytes
```

**¿Por qué?** Heltec usa RadioLib library con la MISMA arquitectura que TTGO (mismo patrón educativo).

### CubeCell HTCC-AB01 (15 bytes)
```
┌──────────────────┬─────────────────────┬─────────┐
│  [0-3]           │     [4-13]          │  [14]   │
├──────────────────┼─────────────────────┼─────────┤
│ Timestamp (LE)   │ "hola mundo" (ASCII)│Checksum │
│ 4 bytes          │ 10 bytes            │ 1 byte  │
└──────────────────┴─────────────────────┴─────────┘
Total: 15 bytes
```

**¿Por qué?** CubeCell usa LoRaWan_APP library (propietaria de Seeed), que es más compacta y sin byte de tipo.

---

## 💡 Punto Clave para Alumnos

**Todos codifican igual:**
- Little-Endian para timestamp
- ASCII para mensaje
- Suma simple para checksum

**Pero en DIFERENTES posiciones:**
- TTGO/Heltec: Timestamp en [1-4]
- CubeCell: Timestamp en [0-3]

Esto es importante porque el **decoder debe saber dónde buscar cada dato**.

---

# 📌 SECCIÓN 2: ENTENDER LA ARQUITECTURA DE CODIFICACIÓN
**⏱️ 10 minutos**

## Flujo: Cómo El Device Codifica

### Paso 1: El Device Lee Datos
```cpp
// readSensorData() en TTGO
struct SensorData data;
strcpy(data.mensaje, "hola mundo");      // 10 caracteres
data.timestamp = millis() / 1000;         // Segundos desde inicio
```

### Paso 2: El Device Crea El Payload

**TTGO/Heltec:**
```cpp
void createPayload(struct SensorData data, uint8_t* payload) {
    payload[0] = 0x48;                           // Byte 0: Tipo "Hola"
    
    // Bytes 1-4: Desmenuzar timestamp en Little-Endian
    payload[1] = data.timestamp & 0xFF;           // Bits 0-7 (LSB)
    payload[2] = (data.timestamp >> 8) & 0xFF;    // Bits 8-15
    payload[3] = (data.timestamp >> 16) & 0xFF;   // Bits 16-23
    payload[4] = (data.timestamp >> 24) & 0xFF;   // Bits 24-31 (MSB)
    
    // Bytes 5-14: Copiar mensaje ASCII
    for (int i = 0; i < 10; i++) {
        payload[5 + i] = data.mensaje[i];
    }
    
    // Byte 15: Checksum
    payload[15] = 0;
    for (int i = 0; i < 15; i++) {
        payload[15] += payload[i];
    }
}
```

**CubeCell:**
```cpp
void prepareTxFrame(uint8_t port) {
    uint32_t timestamp = millis() / 1000;
    
    // Bytes 0-3: Desmenuzar timestamp en Little-Endian (DIRECTO, sin tipo)
    appData[0] = timestamp & 0xFF;
    appData[1] = (timestamp >> 8) & 0xFF;
    appData[2] = (timestamp >> 16) & 0xFF;
    appData[3] = (timestamp >> 24) & 0xFF;
    
    // Bytes 4-13: Copiar mensaje ASCII
    const char mensaje[] = "hola mundo";
    for (int i = 0; i < 10; i++) {
        appData[4 + i] = mensaje[i];
    }
    
    // Byte 14: Checksum
    appData[14] = 0;
    for (int i = 0; i < 14; i++) {
        appData[14] += appData[i];
    }
    
    appDataSize = 15;
}
```

---

## 🧮 Ejemplo Real: Timestamp = 102 segundos

### TTGO/Heltec
```
timestamp = 102 decimal = 0x66 hex

Little-Endian (LSB primero):
┌──────┬──────┬──────┬──────┐
│ 0x66 │ 0x00 │ 0x00 │ 0x00 │
└──────┴──────┴──────┴──────┘
payload[1-4]

Resultado en payload:
[0]  = 0x48                          (Tipo)
[1]  = 0x66                          (Byte 0 del timestamp)
[2]  = 0x00                          (Byte 1 del timestamp)
[3]  = 0x00                          (Byte 2 del timestamp)
[4]  = 0x00                          (Byte 3 del timestamp)
[5-14] = 68 6F 6C 61 20 6D 75 6E 64 6F  ("hola mundo" en ASCII)
[15] = Checksum = 0x48 + 0x66 + ... = resultado
```

### CubeCell
```
timestamp = 102 decimal = 0x66 hex

Little-Endian (LSB primero):
┌──────┬──────┬──────┬──────┐
│ 0x66 │ 0x00 │ 0x00 │ 0x00 │
└──────┴──────┴──────┴──────┘
appData[0-3]

Resultado en appData:
[0]  = 0x66                          (Byte 0 del timestamp)
[1]  = 0x00                          (Byte 1 del timestamp)
[2]  = 0x00                          (Byte 2 del timestamp)
[3]  = 0x00                          (Byte 3 del timestamp)
[4-13] = 68 6F 6C 61 20 6D 75 6E 64 6F  ("hola mundo" en ASCII)
[14] = Checksum = 0x66 + 0x00 + ... = resultado
```

---

## 📊 Tabla Comparativa Rápida

| Concepto | TTGO | Heltec | CubeCell |
|----------|------|--------|----------|
| Byte 0 | Tipo (0x48) | Tipo (0x48) | Timestamp LSB |
| Bytes para Timestamp | [1-4] | [1-4] | [0-3] |
| Bytes para Mensaje | [5-14] | [5-14] | [4-13] |
| Checksum | [15] | [15] | [14] |
| Total | 16 | 16 | 15 |

---

# 📌 SECCIÓN 3: CONFIGURACIÓN DE CHIRPSTACK
**⏱️ 10 minutos**

## Paso 1: Acceder a ChirpStack

1. Abre navegador → `http://localhost:8080` (o IP del servidor)
2. Login con credenciales de administrador
3. Vas a **Applications** (lado izquierdo)

---

## Paso 2: Crear Aplicación (Si no existe)

1. Click en **"+ Create"** (botón verde)
2. Nombre: `IoT-Lab-LoRaWAN` (o similar)
3. Description: `Laboratorio de LoRaWAN - Decodificadores`
4. Click **"Create Application"**

---

## Paso 3: Crear Dispositivo (Si no existe)

1. En la aplicación, click en **"Devices"**
2. Click **"+ Create"**
3. Información básica:
   - **Device name:** `TTGO-HolaMundo` (o `Heltec-HolaMundo` o `CubeCell-HolaMundo`)
   - **Device EUI:** Copia del sketch (línea ~60 del código)
   - **Device Type:** Selecciona el perfil correcto (US915 para TTGO/Heltec, EU868 para CubeCell)

4. Click **"Create Device"**

---

## Paso 4: Ingresar Credenciales OTAA

En el dispositivo, click en **"OTAA"** (Over The Air Activation):

```
Para TTGO:
  AppEUI:  8A FD 43 71 F8 46 52 51  (copia de línea 65 del sketch)
  AppKey:  8A C5 83 DF EE C7 6C 81 FF D1 9C CF E7 6B 73 BF
           (copia de línea 69-71 del sketch)

Para Heltec:
  AppEUI:  8D 7F 63 99 E2 66 4G 72  (copia del sketch)
  AppKey:  4E 8C A5 D3 6G B9 2F 58 AD 4C 7E 93 C6 5D AE 39
           (copia del sketch)

Para CubeCell:
  AppEUI:  11 22 33 44 55 66 77 88  (copia del sketch)
  AppKey:  2B 7E 15 16 28 AE D2 A6 AB F7 97 68 4C 2B 7E 16
           (copia del sketch)
```

---

# 📌 SECCIÓN 4: AGREGAR Y VALIDAR DECODIFICADORES
**⏱️ 15 minutos**

## Paso 1: Acceder a Codecs

En el dispositivo, busca la sección **"Codec configuration"** o similar.

En ChirpStack moderno, puede estar en:
- **Device Profile** → **Codec** (si usas profile general)
- **Device** → **Codec** (si está directamente en el dispositivo)

---

## Paso 2: Elegir tu Dispositivo y Copiar el Codec

### Para TTGO (16 bytes):

```javascript
// COPIAR DESDE AQUÍ ↓
function Decode(fPort, bytes) {
  var tipo = bytes[0];
  var timestamp = bytes[1] | (bytes[2] << 8) | 
                  (bytes[3] << 16) | (bytes[4] << 24);
  var mensaje = '';
  for (var i = 5; i < 15; i++) {
    mensaje += String.fromCharCode(bytes[i]);
  }
  var checksum = bytes[15];
  
  var checksum_calculado = 0;
  for (var i = 0; i < 15; i++) {
    checksum_calculado += bytes[i];
  }
  checksum_calculado = checksum_calculado & 0xFF;
  
  return {
    tipo: '0x' + tipo.toString(16).toUpperCase(),
    timestamp: timestamp,
    mensaje: mensaje,
    checksum: '0x' + checksum.toString(16).toUpperCase(),
    checksum_ok: (checksum === checksum_calculado)
  };
}
// HASTA AQUÍ ↑
```

### Para Heltec (16 bytes - IDÉNTICO a TTGO):

Copia el mismo código que TTGO.

### Para CubeCell (15 bytes):

```javascript
// COPIAR DESDE AQUÍ ↓
function Decode(fPort, bytes) {
  var timestamp = bytes[0] | (bytes[1] << 8) | 
                  (bytes[2] << 16) | (bytes[3] << 24);
  var mensaje = '';
  for (var i = 4; i < 14; i++) {
    mensaje += String.fromCharCode(bytes[i]);
  }
  var checksum = bytes[14];
  
  var checksum_calculado = 0;
  for (var i = 0; i < 14; i++) {
    checksum_calculado += bytes[i];
  }
  checksum_calculado = checksum_calculado & 0xFF;
  
  return {
    timestamp: timestamp,
    mensaje: mensaje,
    checksum: '0x' + checksum.toString(16).toUpperCase(),
    checksum_ok: (checksum === checksum_calculado)
  };
}
// HASTA AQUÍ ↑
```

---

## Paso 3: Validar el Codec (Prueba Manual)

ChirpStack permite probar el codec sin dispositivo.

### Ejemplo de payload para TTGO (HEX):
```
48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7
```

En ChirpStack, busca un campo que diga **"Test Codec"** o similar:

1. Pega el HEX: `48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7`
2. Presiona **"Decode"** o similar
3. Deberías ver en JSON:
```json
{
  "tipo": "0x48",
  "timestamp": 102,
  "mensaje": "hola mundo",
  "checksum": "0xC7",
  "checksum_ok": true
}
```

---

## Paso 4: Guardar el Codec

Click en **"Save"** o **"Update Codec"**

✅ **Validación de éxito:** ChirpStack confirma "Codec saved successfully"

---

# 📌 SECCIÓN 5: PRUEBA EN VIVO CON DISPOSITIVO
**⏱️ 15 minutos**

## Paso 1: Cargar el Sketch en el Dispositivo

### Para TTGO:
1. Arduino IDE → File → Open → `TTGO_HolaMundo_v1.ino`
2. Tools → Board → `TTGO T3`
3. Tools → Port → Selecciona COM/ttyUSB
4. Carga el sketch (Ctrl+U o Upload)
5. Abre Serial Monitor (115200 baud)

### Para Heltec:
1. Arduino IDE → File → Open → `Heltech_HolaMundo_v1.ino`
2. Tools → Board → `Heltec WiFi LoRa 32 V3`
3. Tools → Port → Selecciona COM/ttyUSB
4. Carga el sketch
5. Abre Serial Monitor (115200 baud)

### Para CubeCell:
1. CubeCellDevKit o Arduino IDE → Abre `holaMundo_cubecell_ino.ino`
2. Tools → Board → `CubeCell-Board`
3. Tools → Port → Selecciona COM/ttyUSB
4. Carga el sketch
5. Abre Serial Monitor (115200 baud)

---

## Paso 2: Observar Serial Monitor

Deberías ver (después de ~20-30 segundos):

```
========================================
ENVIANDO PAQUETE #1
========================================

Datos del sensor:
  Mensaje: hola mundo
  Timestamp: 102 segundos

Payload ENCRIPTADO (HEX):
  48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7

Payload DESENCRIPTADO (decodificado):
  [0] Tipo: 0x48
  [1-4] Timestamp: 102 seg
  [5-14] Mensaje: hola mundo
  [15] Checksum: 0xC7

Informacion del envio:
  Puerto: 1 | Tamanio: 16 bytes

========================================
```

✅ **Validación:** ¿Ves el payload en HEX? ✓ Sí → El dispositivo está codificando correctamente

---

## Paso 3: Buscar el Paquete en ChirpStack

1. Abre ChirpStack en navegador
2. Ve a **Applications** → Tu aplicación → **Devices** → Tu dispositivo
3. Click en **"Live Device Data"**
4. Espera a que llegue un paquete (máximo 30 segundos)

Deberías ver:

```
RX Payload:
├─ Frame Counter: 1
├─ Port: 1
├─ Data (hex): 48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7
└─ Decoded (JSON):
   {
     "tipo": "0x48",
     "timestamp": 102,
     "mensaje": "hola mundo",
     "checksum": "0xC7",
     "checksum_ok": true
   }
```

✅ **Validación:** ¿Ves el JSON con "mensaje": "hola mundo"? ✓ Sí → El decoder funcionó correctamente

---

## Paso 4: Analizar Byte por Byte

**En el Serial Monitor del dispositivo, copias el HEX:**
```
48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7
```

**Conviertes a tabla:**

| Posición | Valor HEX | Significado | Decodificación |
|----------|-----------|-------------|-----------------|
| [0] | 0x48 | Tipo | ASCII 'H' |
| [1] | 0x66 | TS byte 0 | 102 en decimal |
| [2] | 0x00 | TS byte 1 | (102 >> 8) = 0 |
| [3] | 0x00 | TS byte 2 | (102 >> 16) = 0 |
| [4] | 0x00 | TS byte 3 | (102 >> 24) = 0 |
| [5] | 0x68 | Msg char 0 | ASCII 'h' |
| [6] | 0x6F | Msg char 1 | ASCII 'o' |
| [7] | 0x6C | Msg char 2 | ASCII 'l' |
| [8] | 0x61 | Msg char 3 | ASCII 'a' |
| [9] | 0x20 | Msg char 4 | ASCII ' ' (espacio) |
| [10] | 0x6D | Msg char 5 | ASCII 'm' |
| [11] | 0x75 | Msg char 6 | ASCII 'u' |
| [12] | 0x6E | Msg char 7 | ASCII 'n' |
| [13] | 0x64 | Msg char 8 | ASCII 'd' |
| [14] | 0x6F | Msg char 9 | ASCII 'o' |
| [15] | 0xC7 | Checksum | Suma mod 256 |

---

# 📌 SECCIÓN 6: ANÁLISIS Y CONCLUSIONES
**⏱️ 5 minutos**

## Checklist Final

- [ ] ¿El dispositivo envió "hola mundo"?
- [ ] ¿Lo viste en Serial Monitor (HEX)?
- [ ] ¿Lo decodificó ChirpStack correctamente?
- [ ] ¿El JSON muestra "mensaje": "hola mundo"?
- [ ] ¿El checksum_ok es true?

---

## Preguntas de Reflexión para Alumnos

1. **¿Por qué el timestamp está en Little-Endian?**
   - Respuesta: Porque el ESP32/ARM usan Little-Endian nativamente. Es más eficiente enviarlo así que invertirlo.

2. **¿Por qué el TTGO tiene byte de tipo y CubeCell no?**
   - Respuesta: Diferentes librerías. TTGO (LMIC) incluye tipo para múltiples sensores. CubeCell (LoRaWan_APP) es más compacto.

3. **¿Qué pasaría si no tuvieras el decoder?**
   - Respuesta: ChirpStack mostraría solo los bytes en HEX. No podría interpretar qué significa cada byte.

4. **¿Por qué el checksum está al final?**
   - Respuesta: Permite detectar corrupción de datos durante la transmisión.

---

## Lecciones Clave

✅ **Cada dispositivo puede codificar diferente** → Necesitas decoders específicos

✅ **El decoder es el "diccionario" de ChirpStack** → Sin él, solo ves números

✅ **Little-Endian es estándar en microcontroladores** → Importante para IoT

✅ **Checksums detectan errores** → Validación de integridad de datos

---

## 🎯 Siguientes Pasos Opcionales (Si hay tiempo)

1. **Agregar más campos:** Modificar sketch para enviar temperatura + humedad
2. **Crear decodificador más complejo:** Manejar múltiples tipos de mensajes
3. **Implementar encriptación adicional:** (Bonus para alumnos avanzados)
4. **Dashboard:** Visualizar datos en tiempo real con gráficas

---

## 📚 Referencias

- [Documentación ChirpStack](https://www.chirpstack.io/)
- [LMIC Library Documentation](https://github.com/mcci-catena/arduino-lmic)
- [RadioLib Documentation](https://jgromes.github.io/RadioLib/)
- [LoRaWAN Specification](https://lora-alliance.org/)

---

**¡Felicitaciones! Completaste el laboratorio.** 🎉


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)