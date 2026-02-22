#  GUÍA DE LABORATORIO - SEMANA 8
## Sistema IoT: Sensor Ultrasónico HC-SR04 + LoRaWAN con ChirpStack

**Curso:** Comunicaciones e IoT  
**Duración:** 2-3 horas  
**Dificultad:** Intermedia  
**Modalidad:** Presencial con hardware

---

##  TABLA DE CONTENIDOS

1. [Objetivos de Aprendizaje](#objetivos)
2. [Materiales Necesarios](#materiales)
3. [Fundamentos Teóricos](#fundamentos)
4. [Preparación Previa](#preparacion)
5. [Parte 1: Construcción del Divisor de Voltaje](#parte1)
6. [Parte 2: Montaje del Hardware Completo](#parte2)
7. [Parte 3: Configuración de ChirpStack](#parte3)
8. [Parte 4: Programación del TTGO](#parte4)
9. [Parte 5: Pruebas y Validación](#parte5)
10. [Parte 6: Análisis de Resultados](#parte6)
11. [Alternativa: Sin Sensor Físico](#alternativa)
12. [Troubleshooting](#troubleshooting)
13. [Evaluación y Entrega](#evaluacion)

---

##  OBJETIVOS DE APRENDIZAJE {#objetivos}

Al finalizar esta práctica, el estudiante será capaz de:

### Objetivos Generales:
-  Implementar un sistema IoT completo desde el sensor hasta la nube
-  Comprender y aplicar el protocolo LoRaWAN en aplicaciones reales
-  Integrar sensores con microcontroladores de forma segura

### Objetivos Específicos:
1. **Hardware:** Construir un divisor de voltaje resistivo para proteger el ESP32
2. **Sensores:** Configurar y leer datos del sensor ultrasónico HC-SR04
3. **LoRaWAN:** Implementar activación OTAA y transmisión de datos
4. **ChirpStack:** Registrar dispositivos y decodificar payloads
5. **Análisis:** Evaluar precisión y rendimiento del sistema

---

##  MATERIALES NECESARIOS {#materiales}

### Hardware Principal:

| Cantidad | Componente | Especificación | Notas |
|----------|------------|----------------|-------|
| 1 | TTGO T3 LoRa | v1, v2 o v1.6.1 | Con antena incluida |
| 1 | Sensor HC-SR04 | Ultrasónico 5V | Verificar que funcione |
| 1 | Resistencia 1kΩ | ±5% (marrón-negro-rojo-dorado) | Para divisor |
| 1 | Resistencia 1.2kΩ | ±5% (marrón-rojo-rojo-dorado) | Para divisor |
| 1 | Protoboard | 400 o 830 puntos | Cualquier tamaño |
| 8-10 | Cables dupont | Macho-macho y macho-hembra | Varios colores |
| 1 | Cable USB | Micro-USB o USB-C | Para programar |

### Herramientas Opcionales:
- Multímetro digital (para verificación)
- Regla o cinta métrica (para calibración)
- Objeto para pruebas (caja, libro, etc.)

### Software Requerido:

| Software | Versión | Link de descarga |
|----------|---------|------------------|
| Arduino IDE | 1.8.19 o superior | https://www.arduino.cc/en/software |
| Driver ESP32 | Última | Incluido en Arduino IDE |
| Librería LMIC | MCCI v4.1+ | Library Manager |
| Librería U8g2 | Última | Library Manager |

### Acceso a Servicios:
-  Gateway LoRaWAN operativo y conectado
-  Cuenta en servidor ChirpStack
-  Permisos para crear aplicaciones y dispositivos

---

## FUNDAMENTOS TEÓRICOS {#fundamentos}

### 1. El Sensor Ultrasónico HC-SR04

#### Principio de Funcionamiento:

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  [EMISOR]  ──→  Onda ultrasónica (40 kHz)  ──→       │
│     ↓                                          ↓       │
│  Genera pulso                            Rebota en    │
│  de 8 ciclos                             objeto       │
│     ↓                                          ↓       │
│  [RECEPTOR]  ←──  Onda reflejada regresa  ←──        │
│     ↓                                                  │
│  Mide tiempo de vuelo (Time of Flight)                │
│     ↓                                                  │
│  Distancia = (Tiempo × Velocidad_sonido) / 2          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

#### Especificaciones Técnicas:

| Parámetro | Valor | Notas |
|-----------|-------|-------|
| Voltaje de operación | 5V DC | ±0.5V |
| Corriente de operación | 15 mA | Típico |
| Frecuencia ultrasónica | 40 kHz | Inaudible para humanos |
| Rango de medición | 2 cm - 400 cm | Práctico: hasta 200 cm |
| Precisión | ±3 mm | En condiciones ideales |
| Ángulo de medición | 15° | Cono efectivo |
| Duración del trigger | 10 µs | Mínimo |
| Ancho del pulso ECHO | 150 µs - 25 ms | Proporcional a distancia |

#### Cálculo de Distancia:

```
Velocidad del sonido en aire (20°C) = 343 m/s = 0.0343 cm/µs

Distancia (cm) = (Tiempo_ida_y_vuelta (µs) × 0.0343) / 2
Distancia (cm) = Tiempo (µs) × 0.01715
Simplificado: Distancia (cm) = Tiempo (µs) × 0.034 / 2
```

**Ejemplo:**
- Tiempo medido: 1000 µs
- Distancia = 1000 × 0.034 / 2 = 17 cm

---

### 2. LoRaWAN y el Protocolo OTAA

#### Arquitectura LoRaWAN:

```
┌──────────────┐         ┌──────────┐         ┌────────────────┐
│   End Device │         │ Gateway  │         │ Network Server │
│   (TTGO T3)  │◄───────►│(LoRa GW) │◄───────►│  (ChirpStack)  │
└──────────────┘   RF    └──────────┘ Internet └────────────────┘
     Sensor          LoRa 868/915 MHz        LoRaWAN Protocol
     HC-SR04         Alcance: 2-15 km        TCP/IP
```

#### Proceso OTAA (Over-The-Air Activation):

```
PASO 1: CONFIGURACIÓN INICIAL
─────────────────────────────
Dispositivo tiene:                 ChirpStack tiene:
• DevEUI (único)                   • DevEUI registrado
• AppEUI/JoinEUI                   • AppEUI/JoinEUI
• AppKey (secreta)                 • AppKey (secreta)

PASO 2: JOIN REQUEST
────────────────────
[Dispositivo] ──────→ Join Request ──────→ [Network Server]
              DevEUI, AppEUI, Nonce
              MIC calculado con AppKey

PASO 3: VERIFICACIÓN
────────────────────
                    Network Server:
                    1. Verifica DevEUI existe
                    2. Verifica MIC con AppKey
                    3. Si OK, continúa

PASO 4: JOIN ACCEPT
───────────────────
[Network Server] ──→ Join Accept ──→ [Dispositivo]
                 DevAddr, NwkSKey, AppSKey
                 (Cifrado con AppKey)

PASO 5: SESIÓN ESTABLECIDA
──────────────────────────
Dispositivo ahora puede:
• Enviar uplinks (cifrados con AppSKey)
• Recibir downlinks del servidor
• Frame Counter inicializado en 0
```

#### Clases de Dispositivos:

| Clase | Descripción | Uso en este lab |
|-------|-------------|-----------------|
| **Clase A** | Uplink cuando necesite, RX después de TX | ✅ Usamos esta |
| Clase B | + ventanas RX programadas con beacon | No |
| Clase C | RX continuo (mayor consumo) | No |

---

### 3. ¿Por qué Necesitamos el Divisor de Voltaje?

#### El Problema:

```
HC-SR04 (5V)                 ESP32 (3.3V)
┌─────────┐                  ┌─────────┐
│  ECHO   │──── 5V ────X────→│ GPIO34  │  💥 PELIGRO!
└─────────┘                  └─────────┘
                             Máximo: 3.3V
                             Input: 5V = DAÑO PERMANENTE
```

**Consecuencias de conectar directo:**
- ⚠️ Sobrevoltaje en GPIO34
- ⚠️ Daño en el pin (puede quedar inutilizable)
- ⚠️ En casos extremos: daño al ESP32 completo

#### La Solución: Divisor de Voltaje Resistivo

```
         Entrada 5V
              │
              R1 (1kΩ)
              │
              ├────────→ Salida 2.73V (a GPIO34)
              │
              R2 (1.2kΩ)
              │
             GND
```

#### Fórmula del Divisor:

```
V_out = V_in × (R2 / (R1 + R2))

Con nuestros valores:
V_out = 5V × (1.2kΩ / (1kΩ + 1.2kΩ))
V_out = 5V × (1.2 / 2.2)
V_out = 5V × 0.545
V_out = 2.727V ≈ 2.73V

 2.73V < 3.3V → SEGURO para ESP32
```

#### ¿Por qué estos valores de resistencia?

1. **Total razonable (2.2kΩ):**
   - No consume mucha corriente
   - No interfiere con la señal del sensor

2. **Proporción 1:1.2:**
   - Da factor de 0.545
   - Convierte 5V en 2.73V perfectamente

3. **Valores estándar:**
   - Fáciles de conseguir
   - Serie E12 (las más comunes)

---

##  PREPARACIÓN PREVIA {#preparacion}

### Antes de Iniciar el Laboratorio:

#### 1. Verificar Materiales
- [ ] Todos los componentes de la lista
- [ ] Cables en buen estado (sin roturas)
- [ ] TTGO con antena conectada
- [ ] Sensor HC-SR04 sin daños visibles

#### 2. Instalar Software

**Arduino IDE:**
1. Descargar de https://www.arduino.cc/en/software
2. Instalar para tu sistema operativo
3. Abrir Arduino IDE

**Configurar ESP32:**
```
1. File → Preferences → Additional Board Manager URLs:
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

2. Tools → Board → Board Manager
   Buscar "ESP32" e instalar

3. Tools → Board → ESP32 Arduino → TTGO LoRa32-OLED 
```

**Instalar Librerías:**
```
Sketch → Include Library → Manage Libraries

Buscar e instalar:
1. "MCCI LoRaWAN LMIC library" por Terry Moore (v4.1.1 o superior)
2. "U8g2" por oliver (cualquier versión reciente)
```

#### 3. Probar Conexión TTGO
```cpp
// Código de prueba simple
void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
}

void loop() {
  Serial.println("TTGO funcionando");
  digitalWrite(2, !digitalRead(2));
  delay(1000);
}
```
- Cargar este código
- Abrir Serial Monitor (115200 baud)
- Debe aparecer "TTGO funcionando" cada segundo
- El LED debe parpadear

---

##  PARTE 1: CONSTRUCCIÓN DEL DIVISOR DE VOLTAJE {#parte1}

### Paso 1.1: Identificar las Resistencias

#### Código de Colores:

**Resistencia 1kΩ (1000Ω):**
```
┌────────────────────────────┐
│ ████ ████ ████ ████        │
│ Marrón Negro Rojo Dorado   │
│   1     0    ×100  ±5%     │
└────────────────────────────┘
Valor: 1 × 10 × 100 = 1000Ω = 1kΩ
```

**Resistencia 1.2kΩ (1200Ω):**
```
┌────────────────────────────┐
│ ████ ████ ████ ████        │
│ Marrón Rojo Rojo Dorado    │
│   1     2    ×100  ±5%     │
└────────────────────────────┘
Valor: 1 × 2 × 100 = 1200Ω = 1.2kΩ
```

**Importante:** Si no estás seguro, usa un multímetro para medir.

---

### Paso 1.2: Calcular Ubicación en Protoboard

#### Esquema de Conexión Completo:

```
HC-SR04                    PROTOBOARD                      TTGO T3
────────                   ──────────                      ───────

  VCC  ───────────────────────────────────────────────────→ VIN (5V)

  TRIG ───────────────────────────────────────────────────→ GPIO25

           ┌──────────────────────────────────────┐
  ECHO ────┤                                      │
           │  [Fila A]                            │
           │     │                                │
           │     │                                │
           │  R1 (1kΩ)                            │
           │     │                                │
           │     │                                │
           │  [Fila B] ──────────────────────────┼───────→ GPIO34
           │     │                                │
           │     │                                │
           │  R2 (1.2kΩ)                          │
           │     │                                │
           │     │                                │
           │    GND ─────────────────────────────┼───────→ GND
           │                                      │
           └──────────────────────────────────────┘

  GND  ───────────────────────────────────────────────────→ GND
```

---

### Paso 1.3: Montaje en Protoboard (Paso a Paso)

#### Vista Superior del Protoboard:

```
     a  b  c  d  e     f  g  h  i  j
   ┌──────────────┬───┬──────────────┐
 1 │  │  │  │  │  │ - │  │  │  │  │  │
 2 │  │  │  │  │  │ + │  │  │  │  │  │  ← Rieles de alimentación
 3 │══════════════│ ═ │══════════════│
 4 │  │  │  │  │  │   │  │  │  │  │  │
 5 │  ●──●  │  │  │   │  │  │  │  │  │  ← Fila A (ECHO entra aquí)
 6 │  │  │  │  │  │   │  │  │  │  │  │
 7 │  ●  ●  │  │  │   │  │  │  │  │  │  ← Fila B (Punto medio del divisor)
 8 │  │  │  │  │  │   │  │  │  │  │  │
 9 │  │  │  │  │  │   │  │  │  │  │  │
   └──────────────┴───┴──────────────┘

● = Puntos de conexión importantes
```

#### Instrucciones Detalladas:

**1. Insertar R1 (1kΩ):**
```
Paso a paso:
1. Toma la resistencia de 1kΩ (marrón-negro-rojo)
2. Dobla las patitas en forma de "U"
3. Inserta un extremo en fila A, columna 'a' (ejemplo: A5)
4. Inserta otro extremo en fila B, columna 'a' (ejemplo: B7)
5. Presiona suavemente hasta que quede firme

Verificación: R1 conecta fila A con fila B
```

**2. Insertar R2 (1.2kΩ):**
```
Paso a paso:
1. Toma la resistencia de 1.2kΩ (marrón-rojo-rojo)
2. Dobla las patitas en forma de "U"
3. Inserta un extremo en fila B, columna 'b' (mismo nivel que R1)
4. Inserta otro extremo en riel negativo (-) o fila de GND
5. Presiona suavemente hasta que quede firme

Verificación: R2 conecta fila B con GND
```

**3. Verificar Continuidad:**
```
Con multímetro en modo resistencia (Ω):

Medición 1: Entre extremos de R1
Resultado esperado: ~1000Ω (980Ω - 1020Ω)

Medición 2: Entre extremos de R2
Resultado esperado: ~1200Ω (1140Ω - 1260Ω)

Medición 3: Entre fila A y GND (todo el divisor)
Resultado esperado: ~2200Ω (R1 + R2 en serie)
```

---

### Paso 1.4: Conectar Cables

**Orden de Conexión (MUY IMPORTANTE para evitar cortos):**

```
1º) GND primero (siempre):
    HC-SR04 GND → Protoboard GND → TTGO GND

2º) Divisor de voltaje:
    HC-SR04 ECHO → Protoboard Fila A
    Protoboard Fila B → TTGO GPIO34

3º) Señal TRIG:
    HC-SR04 TRIG → TTGO GPIO25

4º) Alimentación al final:
    HC-SR04 VCC → TTGO VIN (5V)
```

**Codificación por colores (sugerida):**
```
- Cable NEGRO:  GND
- Cable ROJO:   VCC (5V)
- Cable AMARILLO: TRIG
- Cable AZUL:   ECHO / Divisor
```

---

### Paso 1.5: Verificación del Divisor (CRÍTICO)

**Con Multímetro (RECOMENDADO):**

```
1. NO conectar USB todavía
2. Configurar multímetro en modo voltaje DC (20V)
3. Conectar USB al TTGO
4. Poner sonda negra en GND
5. Poner sonda roja en pin ECHO del HC-SR04
   → Debe medir cerca de 0V (sin pulso activo)
6. Activar sensor (poner mano frente a él)
7. Medir voltaje en GPIO34 del ESP32
   → Debe medir entre 2.5V - 3.0V cuando ECHO está HIGH
   → Debe medir cerca de 0V cuando ECHO está LOW

✅ Si mides >3.3V en GPIO34: DETENER, revisar divisor
❌ Si mides 5V en GPIO34: NO CONTINUAR, revisar conexiones
```

**Sin Multímetro:**
```
Verificación visual:
✅ R1 conecta ECHO con punto medio
✅ R2 conecta punto medio con GND  
✅ GPIO34 conecta al punto medio
✅ No hay cables sueltos
✅ No hay cortocircuitos visibles
```

---

##  PARTE 2: MONTAJE DEL HARDWARE COMPLETO {#parte2}

### Paso 2.1: Diagrama de Conexiones Final

```
Vista Completa del Sistema:
═══════════════════════════

HC-SR04                PROTOBOARD            TTGO T3 LoRa v1.6.1
┌─────────┐            ┌────────┐            ┌──────────┐
│         │            │        │            │          │
│  VCC ●──┼────────────┼────────┼────────────┼──● VIN   │ 5V
│         │            │        │            │          │
│  TRIG●──┼────────────┼────────┼────────────┼──● G25   │ Trigger
│         │            │        │            │          │
│       │  R1          │        │            │          │
│  ECHO●──┼────● 1kΩ──●┼────────┼────────────┼──● G34   │ Echo (protegido)
│         │       │    │        │            │          │
│         │       └R2  │        │            │          │
│         │      1.2kΩ │        │            │          │
│         │         │  │        │            │          │
│  GND ●──┼─────────┴──┼────────┼────────────┼──● GND   │ Ground
│         │            │        │            │          │
└─────────┘            └────────┘            │  ┌────┐  │
                                             │  │OLED│  │ Display I2C
                                             │  └────┘  │
                                             │  ┌────┐  │
                                             │  │LoRa│  │ Módulo SX1276
                                             │  └────┘  │
                                             └──────────┘
```

---

### Paso 2.2: Lista de Verificación Física

Marca cada ítem después de verificarlo:

**Alimentación:**
- [ ] VCC del HC-SR04 conectado a VIN del TTGO (5V)
- [ ] GND del HC-SR04 conectado a GND del TTGO
- [ ] No hay cortocircuito entre VCC y GND

**Señales:**
- [ ] TRIG del HC-SR04 conectado a GPIO25
- [ ] ECHO del HC-SR04 conectado a Fila A del protoboard
- [ ] R1 (1kΩ) conecta Fila A con Fila B
- [ ] R2 (1.2kΩ) conecta Fila B con GND
- [ ] GPIO34 del TTGO conectado a Fila B

**TTGO:**
- [ ] Antena LoRa conectada (IMPORTANTE)
- [ ] Display OLED funcionando (se verá al encender)
- [ ] No hay pines doblados o rotos

**Protoboard:**
- [ ] Todas las conexiones firmes
- [ ] No hay cables cruzados que no deben tocarse
- [ ] Divisor de voltaje correctamente armado

---

### Paso 2.3: Primera Prueba de Energización

**ANTES DE CONECTAR USB:**

1. **Inspección visual final:**
   - Revisar todas las conexiones
   - Buscar cables sueltos
   - Verificar polaridad de alimentación

2. **Conectar USB:**
   ```
   1. Conecta cable USB al TTGO
   2. Conecta otro extremo a la computadora
   3. Observa:
      - LED de power del TTGO debe encender
      - Display OLED debe mostrar algo (aunque sea basura inicial)
      - HC-SR04 no debe humear ni oler raro
   ```

3. **Si algo sale mal:**
   ```
   DESCONECTAR INMEDIATAMENTE si:
   - Huele a quemado
   - Algún componente se calienta mucho
   - Hay chispas
   - La computadora muestra error de sobrecorriente
   ```

---

## PARTE 3: CONFIGURACIÓN DE CHIRPSTACK {#parte3}

### Paso 3.1: Acceder a ChirpStack

1. **Abrir navegador**
2. **Ir a la URL del servidor:**
   ```
   http://[IP_del_servidor]:8080
   
   Ejemplo: http://192.168.1.100:8080
   o
   https://chirpstack.tu-universidad.edu
   ```

3. **Iniciar sesión:**
   ```
   Usuario: [proporcionado por el profesor]
   Contraseña: [proporcionada por el profesor]
   ```

---

### Paso 3.2: Verificar Gateway Activo

**Antes de registrar tu dispositivo, asegúrate de que el gateway funcione:**

1. En el menú lateral, haz clic en **"Gateways"**

2. Deberías ver al menos un gateway listado

3. Haz clic en el gateway para ver sus detalles

4. **Verificar:**
   ```
   ✅ Estado: "Seen: a few seconds ago" o similar
   ✅ Packets received: número incrementando
   ✅ Gateway ID: anota este valor
   ```

5. **Si el gateway NO está activo:**
   ```
   ❌ Consulta con el profesor
   ❌ No continúes hasta que esté operativo
   ```

---

### Paso 3.3: Crear Aplicación

1. **Navegar a Applications:**
   ```
   Menú lateral → Applications
   ```

2. **Crear nueva aplicación:**
   ```
   Botón: "+ Create"
   ```

3. **Llenar formulario:**
   ```
   Application name: Lab8_[TuApellido]_[TuNombre]
   Ejemplo: Lab8_Garcia_Juan
   
   Description: Laboratorio Semana 8 - Sensor HC-SR04
   
   Service profile: Seleccionar el disponible (usualmente hay uno solo)
   ```

4. **Guardar:**
   ```
   Botón: "Submit" o "Create application"
   ```

---

### Paso 3.4: Registrar Dispositivo (Parte 1 - Información Básica)

1. **Dentro de tu aplicación:**
   ```
   Pestaña: "Devices"
   Botón: "+ Create"
   ```

2. **Llenar información del dispositivo:**

   ```
   Device name: TTGO_HC-SR04_[TuNombre]
   Ejemplo: TTGO_HC-SR04_Juan
   
   Description: Sensor ultrasónico con LoRaWAN
   
   Device EUI (EUI-64):
   02389205358E71DB
   
   ⚠️ IMPORTANTE: Copiar EXACTAMENTE como aparece en el código
   ```

3. **Device profile:**
   ```
   Seleccionar: "Class A, OTAA"
   
   Si no existe, crear uno nuevo con:
   - LoRaWAN MAC version: 1.0.3
   - LoRaWAN Regional Parameters: RP002-1.0.3
   - Class: A
   - Supports OTAA: Yes
   ```

4. **Guardar device básico:**
   ```
   Botón: "Submit" o "Create device"
   ```

---

### Paso 3.5: Configurar Credenciales OTAA (Parte 2)

1. **Entrar al dispositivo recién creado**

2. **Ir a pestaña "Keys (OTAA)"**

3. **Configurar las claves:**

   ```
   Application key:
   8AC583DFEEC76C81FFD19CCFE76B73BF
   
   ⚠️ Copiar EXACTAMENTE, sin espacios
   ```

4. **Configurar JoinEUI/AppEUI:**
   ```
   En "Variables" o "Configuration":
   
   JoinEUI / AppEUI:
   505246F87143FD8A
   ```

5. **Guardar:**
   ```
   Botón: "Submit" o "Set device-keys"
   ```

---

### Paso 3.6: Configurar Codec (Decodificador)

El codec permite ver los datos en formato legible en lugar de hexadecimal.

1. **Ir a nivel de Application:**
   ```
   Navegar: Applications → [Tu aplicación]
   ```

2. **Pestaña "Codec":**
   ```
   Click en pestaña "Codec" o "Payload codec"
   ```

3. **Seleccionar tipo:**
   ```
   Codec: Custom JavaScript codec
   ```

4. **Pegar el siguiente código en el editor:**

```javascript
// Decodificador para HC-SR04 + LoRaWAN
// Payload: 10 bytes
function decodeUplink(input) {
  var bytes = input.bytes;
  
  // Validar longitud del payload
  if (bytes.length !== 10) {
    return {
      errors: ["Payload debe ser de 10 bytes, recibido: " + bytes.length]
    };
  }
  
  // Byte 0: Tipo de sensor
  var sensorType = bytes[0];
  var sensorName;
  switch(sensorType) {
    case 0x01:
      sensorName = "HC-SR04 Ultrasónico";
      break;
    case 0x99:
      sensorName = "Sensor de Prueba";
      break;
    default:
      sensorName = "Desconocido (0x" + sensorType.toString(16) + ")";
  }
  
  // Bytes 1-2: Distancia en décimas de cm (little-endian)
  var distanceRaw = bytes[1] | (bytes[2] << 8);
  var distance = null;
  var distanceStatus = "Sin lectura";
  
  if (distanceRaw === 0xFFFF) {
    distance = null;
    distanceStatus = "Sensor sin respuesta";
  } else {
    distance = distanceRaw / 10.0;
    distanceStatus = "OK";
  }
  
  // Byte 3: Versión de hardware
  var hwVersion = bytes[3];
  var voltage;
  switch(hwVersion) {
    case 0x05:
      voltage = "5V con divisor de voltaje";
      break;
    case 0x33:
      voltage = "3.3V directo";
      break;
    default:
      voltage = "Desconocido (0x" + hwVersion.toString(16) + ")";
  }
  
  // Bytes 4-7: Timestamp en segundos (little-endian)
  var timestamp = bytes[4] | (bytes[5] << 8) | (bytes[6] << 16) | (bytes[7] << 24);
  
  // Byte 8: Estado del sensor
  var sensorStatus = bytes[8] === 0x01 ? "OK" : "ERROR";
  
  // Byte 9: Contador de paquetes
  var packetNumber = bytes[9];
  
  // Retornar datos decodificados
  return {
    data: {
      sensor_type: sensorName,
      distance_cm: distance,
      distance_status: distanceStatus,
      hardware_version: voltage,
      timestamp_seconds: timestamp,
      sensor_status: sensorStatus,
      packet_number: packetNumber
    }
  };
}
```

5. **Guardar el codec:**
   ```
   Botón: "Submit" o "Update codec"
   ```

6. **Probar el codec (opcional):**
   ```
   Payload de ejemplo: 01 FD 00 05 10 00 00 00 01 01
   
   Resultado esperado:
   {
     "sensor_type": "HC-SR04 Ultrasónico",
     "distance_cm": 25.3,
     "distance_status": "OK",
     "hardware_version": "5V con divisor de voltaje",
     "timestamp_seconds": 16,
     "sensor_status": "OK",
     "packet_number": 1
   }
   ```

---

### Paso 3.7: Resumen de Configuración ChirpStack

**Verificación final antes de programar:**

```
✅ Application creada: Lab8_[TuNombre]
✅ Device registrado con:
   - DevEUI: 02389205358E71DB
   - AppKey: 8AC583DFEEC76C81FFD19CCFE76B73BF
   - AppEUI: 505246F87143FD8A
✅ Device profile: Class A, OTAA
✅ Codec configurado y probado
✅ Gateway activo y visible
```

**Anotar para referencia:**
```
URL ChirpStack: ____________________
Usuario: ____________________
Application ID: ____________________
Device EUI: 02389205358E71DB
```

---

## 💻 PARTE 4: PROGRAMACIÓN DEL TTGO {#parte4}

### Paso 4.1: Descargar el Código

1. **Obtener el sketch:**
   ```
   Archivo: TTGO_LoRaWAN_HC_SR04_Lab8.ino
   (Proporcionado por el profesor o disponible en plataforma)
   ```

2. **Abrir en Arduino IDE:**
   ```
   Archivo → Abrir → Seleccionar el .ino
   ```

---

### Paso 4.2: Verificar Credenciales en el Código

**Buscar esta sección en el código:**

```cpp
// =====================================================================
// 5. CREDENCIALES LoRaWAN - MODO OTAA
// =====================================================================

// DevEUI: Identificador único del dispositivo (LSB format)
static const u1_t PROGMEM DEVEUI[8] = { 
    0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x02 
};

// JoinEUI/AppEUI: Identificador de la aplicación (LSB format)
static const u1_t PROGMEM APPEUI[8] = { 
    0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x50 
};

// AppKey: Clave secreta de 128 bits (MSB format)
static const u1_t PROGMEM APPKEY[16] = { 
    0x8A, 0xC5, 0x83, 0xDF, 0xEE, 0xC7, 0x6C, 0x81, 
    0xFF, 0xD1, 0x9C, 0xCF, 0xE7, 0x6B, 0x73, 0xBF 
};
```

**Verificar que coincidan EXACTAMENTE con ChirpStack.**

---

### Paso 4.3: Configurar Arduino IDE

1. **Seleccionar placa:**
   ```
   Tools → Board → ESP32 Arduino → TTGO LoRa32-OLED 
   ```

2. **Configurar parámetros de compilación:**
   ```
   Upload Speed: 921600
   CPU Frequency: 240MHz (WiFi/BT)
   Flash Frequency: 80MHz
   Flash Mode: QIO
   Flash Size: 4MB (32Mb)
   Partition Scheme: Default 4MB with spiffs
   Core Debug Level: None
   PSRAM: Disabled
   ```

3. **Seleccionar puerto COM:**
   ```
   Tools → Port → COMx (Windows) o /dev/ttyUSBx (Linux)
   
   Si no aparece:
   - Desconectar y reconectar USB
   - Instalar driver CH340 o CP2102
   - Probar otro cable USB
   ```

---

### Paso 4.4: Compilar el Código

1. **Verificar/Compilar:**
   ```
   Click en el botón ✓ (Verify)
   o
   Sketch → Verify/Compile
   ```

2. **Esperar compilación:**
   ```
   Debe decir en consola:
   "Sketch uses XXXXX bytes (XX%) of program storage space..."
   "Done compiling"
   ```

3. **Si hay errores:**
   ```
   Error común 1: "lmic.h: No such file or directory"
   Solución: Instalar librería MCCI LoRaWAN LMIC
   
   Error común 2: "U8g2lib.h: No such file or directory"
   Solución: Instalar librería U8g2
   
   Error común 3: Errores de sintaxis
   Solución: Verificar que el código esté completo
   ```

---

### Paso 4.5: Cargar el Código al TTGO

1. **Preparar TTGO:**
   ```
   - Conectado por USB
   - Puerto COM correcto seleccionado
   - No hay Serial Monitor abierto
   ```

2. **Iniciar carga:**
   ```
   Click en botón → (Upload)
   o
   Sketch → Upload
   ```

3. **Durante la carga:**
   ```
   Verás en consola:
   "Connecting........_____...."
   
   Si se queda en "Connecting....":
   1. Mantén presionado botón BOOT del TTGO
   2. Presiona botón RESET
   3. Suelta RESET, luego suelta BOOT
   4. La carga debe iniciar
   ```

4. **Carga exitosa:**
   ```
   Consola debe mostrar:
   "Hard resetting via RTS pin..."
   ```

---

### Paso 4.6: Abrir Serial Monitor

1. **Abrir monitor:**
   ```
   Tools → Serial Monitor
   o
   Ctrl+Shift+M
   ```

2. **Configurar baudrate:**
   ```
   En la esquina inferior derecha:
   Seleccionar: 115200 baud
   ```

3. **Reiniciar TTGO:**
   ```
   Presiona botón RESET del TTGO
   ```

4. **Salida esperada:**
   ```
   ========================================
     LABORATORIO SEMANA 8
     TTGO T3 + HC-SR04 + LoRaWAN
   ========================================
     Curso: Comunicaciones e IoT
     Sistema: Sensor + LPWAN
   ========================================
   
   🔧 CONFIGURANDO SENSOR HC-SR04...
     ├─ TRIG: GPIO 25 (OUTPUT)
     ├─ ECHO: GPIO 34 (INPUT)
     ├─ VCC:  5V (VIN del TTGO)
     └─ GND:  Ground
   
   🧪 PROBANDO SENSOR...
     ✅ Sensor funcionando: 25.3 cm
        Duración pulso: 1480 µs
   
   📺 INICIALIZANDO DISPLAY OLED...
     └─ ✅ OLED inicializado
   
   📡 INICIALIZANDO MÓDULO LoRa...
     ├─ Bus SPI inicializado
     ├─ Stack LMIC inicializado
     └─ Módulo SX1276 listo
   
   📻 CONFIGURANDO PLAN DE CANALES...
     ├─ Región:            US915
     ├─ Sub-banda activa:  2 (índice 1)
     ├─ Canales activos:   8-15
     └─ Frecuencias:       903.9 - 905.3 MHz
   
   🚀 INICIANDO PROCEDIMIENTO DE JOIN
   ⏳ Enviando Join Request...
   ⏳ Esperando Join Accept...
   ```

---

## ✅ PARTE 5: PRUEBAS Y VALIDACIÓN {#parte5}

### Paso 5.1: Verificar Join Exitoso

**En Serial Monitor:**

```
Debes ver después de 10-60 segundos:

EV_JOINING - Intentando unirse a la red...
...
========================================
✅ EV_JOINED - ¡CONECTADO!
========================================
  → DevAddr asignado
  → Claves de sesión establecidas
  → Listo para transmitir datos
  → Programando primer envío...
```

**En Display OLED:**
```
┌─────────────────┐
│ LoRa: CONECTADO │
│ Sensor: OK      │
│ Dist: 25.3 cm   │
│ Paquetes: 0     │
│ US915 SubBand 2 │
└─────────────────┘
```

**En ChirpStack:**
```
1. Ve a tu dispositivo
2. Pestaña: "LoRaWAN frames"
3. Debes ver:
   - JoinRequest (uplink del dispositivo)
   - JoinAccept (downlink del servidor)
```

---

### Paso 5.2: Verificar Primera Transmisión

**Después del Join (esperar ~2-5 segundos):**

**En Serial Monitor:**
```
========================================
📤 ENVIANDO PAQUETE #1
========================================
  Sensor HC-SR04:       25.3 cm
  Puerto (FPort):       1
  Tamaño payload:       10 bytes
  Data Rate:            DR0
  Potencia TX:          20 dBm
  Frecuencia:           904.1 MHz
  ----------------------------------------
  Payload (HEX):        01 FD 00 05 10 00 00 00 01 01
  ----------------------------------------
  Decodificación:
    Tipo sensor:        HC-SR04 (0x01)
    Distancia:          25.3 cm
    Hardware:           5V con divisor
    Timestamp:          16 seg
    Estado sensor:      OK
========================================

📤 EV_TXCOMPLETE
========================================
  → Uplink enviado
  → Ventanas RX1 y RX2 cerradas
  ⏱️  Próximo uplink en 30 segundos
========================================
```

**En ChirpStack (Device → Events):**
```
Debes ver un nuevo evento tipo "uplink" con:
- Payload decodificado visible
- Campos: sensor_type, distance_cm, etc.
- Timestamp del evento
```

---

### Paso 5.3: Prueba de Distancias Múltiples

**Objetivo:** Validar precisión del sensor en diferentes distancias.

**Materiales:**
- Regla o cinta métrica
- Objeto plano (libro, caja, tablero)

**Procedimiento:**

1. **Preparar tabla de mediciones:**

| # | Distancia Real | Lectura Sensor | Error (cm) | Error (%) |
|---|----------------|----------------|------------|-----------|
| 1 | 10 cm          |                |            |           |
| 2 | 20 cm          |                |            |           |
| 3 | 30 cm          |                |            |           |
| 4 | 50 cm          |                |            |           |
| 5 | 75 cm          |                |            |           |
| 6 | 100 cm         |                |            |           |
| 7 | 150 cm         |                |            |           |
| 8 | 200 cm         |                |            |           |

2. **Para cada distancia:**
   ```
   a) Colocar objeto a distancia conocida
   b) Esperar que aparezca medición en Serial Monitor
      [MED #X] ✅ 25.3 cm | Pulso: 1480 µs
   c) Anotar lectura en tabla
   d) Calcular error: |Real - Medido|
   e) Calcular error %: (Error / Real) × 100
   ```

3. **Repetir 3 veces cada distancia y promediar**

---

### Paso 5.4: Verificar Transmisiones Continuas

**Monitorear durante 5 minutos:**

1. **En Serial Monitor:**
   ```
   Cada 5 segundos: Nueva medición del sensor
   Cada 30 segundos: Nuevo paquete LoRaWAN enviado
   ```

2. **En ChirpStack (Device → Events):**
   ```
   Debe haber al menos 10 uplinks en 5 minutos
   (5 min ÷ 30 seg = 10 paquetes)
   ```

3. **Verificar consistencia:**
   ```
   ✅ Todos los paquetes decodificados correctamente
   ✅ Contador de paquetes incrementa: 1, 2, 3, 4...
   ✅ Timestamp incrementa lógicamente
   ✅ No hay paquetes perdidos (contador consecutivo)
   ```

---

### Paso 5.5: Prueba de Movimiento

**Objetivo:** Ver respuesta del sistema ante cambios de distancia.

**Procedimiento:**

1. **Configurar visualización:**
   ```
   - Serial Monitor abierto
   - ChirpStack Events abierto
   - Objeto en mano frente al sensor
   ```

2. **Secuencia de movimientos:**
   ```
   a) Objeto a 10 cm → esperar 10 seg → observar
   b) Mover a 50 cm → esperar 10 seg → observar
   c) Mover a 100 cm → esperar 10 seg → observar
   d) Alejar completamente → esperar 10 seg → observar
   ```

3. **Observaciones esperadas:**
   ```
   - Serial Monitor muestra cambios inmediatos
   - ChirpStack muestra cambios con delay (30 seg máx)
   - Display OLED actualiza en tiempo real
   ```

---

### Paso 5.6: Prueba de Límites

**Distancia mínima:**
```
Acercar objeto gradualmente hasta que sensor deje de responder
Esperado: < 2 cm → "Sensor sin respuesta"
```

**Distancia máxima:**
```
Alejar objeto gradualmente hasta que sensor deje de responder
Esperado: > 200 cm → "Sensor sin respuesta"
```

**Objetos problemáticos:**
```
Probar con:
- Superficie absorbente (tela, espuma)
- Superficie irregular (mano abierta)
- Superficie en ángulo

Anotar comportamiento para cada caso
```

---

## 📊 PARTE 6: ANÁLISIS DE RESULTADOS {#parte6}

### Paso 6.1: Calcular Métricas del Sensor

**1. Error Promedio:**
```
Error_promedio = Σ|Distancia_real - Lectura_sensor| / n

Ejemplo con tus datos:
Error_promedio = (|10-9.8| + |20-20.3| + ... + |200-198.5|) / 8
Error_promedio = (0.2 + 0.3 + ... + 1.5) / 8
Error_promedio = 0.85 cm
```

**2. Error Máximo:**
```
Error_máximo = max(|Distancia_real - Lectura_sensor|)

Buscar el mayor error absoluto en tu tabla
```

**3. Precisión del Sistema:**
```
Precisión (%) = (1 - Error_promedio / Distancia_promedio) × 100

Ejemplo:
Distancia_promedio = (10+20+30+50+75+100+150+200) / 8 = 79.4 cm
Precisión = (1 - 0.85/79.4) × 100 = 98.9%
```

**4. Desviación Estándar:**
```
σ = √(Σ(error_i - error_promedio)² / n)

Indica qué tan consistentes son los errores
```

---

### Paso 6.2: Análisis de Conectividad LoRaWAN

**Métricas a registrar:**

```
Total de paquetes enviados: _______
Total de paquetes recibidos: _______
Tasa de éxito (PDR): _______ %

PDR = (Recibidos / Enviados) × 100

Objetivo: PDR > 95% indica buena conectividad
```

**Estadísticas en ChirpStack:**
```
1. Ve a Device → Metrics
2. Anotar:
   - RSSI promedio: _______ dBm
   - SNR promedio: _______ dB
   - Spreading Factor usado: DR_______
```

**Interpretar RSSI:**
```
> -70 dBm: Excelente
-70 a -85 dBm: Buena
-85 a -100 dBm: Regular
< -100 dBm: Pobre
```

---

### Paso 6.3: Crear Gráfica en ChirpStack

1. **Acceder a Dashboards:**
   ```
   (Si está disponible en tu versión de ChirpStack)
   ```

2. **Crear nueva gráfica:**
   ```
   - Tipo: Line Chart
   - Eje Y: distance_cm
   - Eje X: time
   - Período: Últimos 30 minutos
   ```

3. **Exportar datos:**
   ```
   - Copiar eventos de ChirpStack
   - Pegar en Excel/Google Sheets
   - Crear gráfica distance vs timestamp
   ```

---

### Paso 6.4: Preguntas de Análisis

**Responder en tu reporte:**

1. **¿El error aumenta con la distancia?**
   ```
   Analizar si hay correlación entre distancia y error
   Graficar: Distancia vs Error
   ```

2. **¿Hay objetos que el sensor no detecta bien?**
   ```
   Listar materiales problemáticos
   Explicar por qué (absorción, reflexión, ángulo)
   ```

3. **¿La conectividad LoRaWAN es estable?**
   ```
   Analizar PDR, RSSI, SNR
   ¿Hubo paquetes perdidos? ¿Por qué?
   ```

4. **¿El divisor de voltaje funciona correctamente?**
   ```
   Si mediste con multímetro: ¿Voltaje correcto?
   ¿El sensor responde correctamente?
   ```

---

## 🔄 ALTERNATIVA: EMULACIÓN DEL SENSOR (SIN HARDWARE FÍSICO) {#alternativa}

**⚠️ NOTA:** Esta sección es SOLO para estudiantes que **NO tienen el sensor HC-SR04** disponible.

Si tienes el sensor, **OMITE esta sección** y continúa con la práctica normal.

---

### ¿Qué aprenderás con la emulación?

| Concepto | Con Emulación | Con Sensor Real |
|----------|---------------|-----------------|
| Protocolo LoRaWAN OTAA | ✅ | ✅ |
| Configuración ChirpStack | ✅ | ✅ |
| Construcción de payloads | ✅ | ✅ |
| Decodificación de datos | ✅ | ✅ |
| Divisor de voltaje | ❌ Solo teoría | ✅ Práctica |
| Comportamiento real del sensor | ❌ | ✅ |
| Calibración y precisión | ❌ | ✅ |

---

### Código para Emular el Sensor

**Reemplazar la función `readDistance()` en el código:**

```cpp
// =====================================================================
// FUNCIÓN: EMULAR SENSOR HC-SR04
// =====================================================================
// ⚠️ USAR SOLO SI NO TIENES EL SENSOR FÍSICO

float readDistance() {
    /*
     * EMULACIÓN DEL SENSOR HC-SR04
     * =============================
     * 
     * Esta función genera datos simulados realistas del sensor
     * para estudiantes que no tienen el hardware disponible.
     * 
     * COMPORTAMIENTO:
     * - Genera distancias entre 10 y 200 cm
     * - Simula patrón de movimiento senoidal
     * - Añade ruido aleatorio (±2 cm)
     * - Simula fallas ocasionales (5%)
     */
    
    // Simular falla del sensor (5% de probabilidad)
    if (random(100) < 5) {
        echoReceived = false;
        lastDuration = 0;
        Serial.println("  [EMULACIÓN] Simulando falla del sensor");
        return -1.0;
    }
    
    echoReceived = true;
    
    // Generar patrón de movimiento senoidal
    // Simula objeto moviéndose entre 20 cm y 100 cm
    unsigned long timeSeconds = millis() / 1000;
    float baseDistance = 60.0 + 40.0 * sin(timeSeconds * 0.1);
    
    // Añadir ruido aleatorio (±2 cm) para realismo
    float noise = (random(-20, 21)) / 10.0;  // -2.0 a +2.0 cm
    float distance = baseDistance + noise;
    
    // Limitar al rango válido del sensor
    distance = constrain(distance, 10.0, 200.0);
    
    // Calcular duración simulada del pulso ECHO
    // Fórmula inversa: duración (µs) = distancia (cm) × 2 / 0.034
    lastDuration = (long)(distance * 2 / 0.034);
    
    Serial.print("  [EMULACIÓN] Distancia generada: ");
    Serial.print(distance, 1);
    Serial.println(" cm");
    
    return distance;
}
```

---

### Cambios en el Setup (Modo Emulación)

**Reemplazar la sección de configuración del sensor:**

```cpp
// -----------------------------------------------------------------
// CONFIGURAR SENSOR HC-SR04 (MODO EMULACIÓN)
// -----------------------------------------------------------------

Serial.println(F("🔧 MODO EMULACIÓN ACTIVADO"));
Serial.println(F("  ⚠️  NOTA: Sensor HC-SR04 simulado por software"));
Serial.println(F("  ⚠️  Los datos son generados algorítmicamente"));
Serial.println(F("  ⚠️  NO se requiere hardware del sensor"));
Serial.println();

// NO configurar pines GPIO (no se usan)
// pinMode(TRIG_PIN, OUTPUT);  // COMENTAR
// pinMode(ECHO_PIN, INPUT);   // COMENTAR

// Inicializar generador de números aleatorios
randomSeed(analogRead(0));

Serial.println(F("  ✅ Generador de datos simulados inicializado"));
Serial.println();

// Test de emulación
delay(500);
Serial.println(F("🧪 PROBANDO EMULACIÓN..."));
currentDistance = readDistance();
Serial.print(F("  ✅ Emulación funcionando: "));
Serial.print(currentDistance, 1);
Serial.println(F(" cm (dato simulado)"));
Serial.println();
```

---

### Limitaciones de la Emulación

```
❌ NO podrás:
  - Armar el divisor de voltaje (solo lo estudiarás teóricamente)
  - Ver comportamiento real del sensor ultrasónico
  - Medir distancias reales
  - Calibrar el sensor
  - Experimentar con diferentes objetos y superficies
  - Entender problemas prácticos del HC-SR04

✅ SÍ podrás:
  - Aprender todo el protocolo LoRaWAN OTAA
  - Configurar ChirpStack completamente
  - Ver cómo se transmiten y decodifican datos
  - Entender la arquitectura de un sistema IoT
  - Practicar programación de ESP32
  - Trabajar con display OLED
```

---

### Ejercicios Adapatados para Emulación

**En lugar de medir distancias reales:**

1. **Modificar patrón de emulación:**
   ```cpp
   // Cambiar a patrón lineal creciente
   float baseDistance = 10.0 + (timeSeconds % 190);
   ```

2. **Simular diferentes escenarios:**
   ```cpp
   // Objeto estático
   float distance = 50.0 + noise;
   
   // Objeto alejándose
   float distance = 20.0 + (timeSeconds * 2) + noise;
   
   // Movimiento aleatorio
   float distance = random(10, 200) + noise;
   ```

3. **Aumentar tasa de fallas:**
   ```cpp
   // Simular sensor defectuoso (20% fallas)
   if (random(100) < 20) {
       return -1.0;
   }
   ```

---

## 🔧 TROUBLESHOOTING (RESOLUCIÓN DE PROBLEMAS) {#troubleshooting}

### Problema 1: Sensor No Responde

**Síntomas:**
```
Serial Monitor:
❌ Sensor sin respuesta

Display OLED:
Sensor: SIN RESPUESTA
Sin lectura valida
```

**Diagnóstico paso a paso:**

1. **Verificar alimentación:**
   ```
   Con multímetro:
   - Medir entre VCC y GND del HC-SR04
   - Debe ser ~5V
   - Si es 0V: verificar conexión VCC
   ```

2. **Verificar divisor de voltaje:**
   ```
   Con multímetro en modo resistencia:
   - Medir R1: debe ser ~1kΩ (980-1020Ω)
   - Medir R2: debe ser ~1.2kΩ (1140-1260Ω)
   - Medir total (Fila A a GND): ~2.2kΩ
   ```

3. **Verificar señal TRIG:**
   ```
   Con multímetro en modo voltaje DC:
   - Medir GPIO25 cuando sensor activo
   - Debe tener pulsos periódicos (difícil de ver)
   - Alternativamente: conectar LED entre GPIO25 y GND
     (con resistencia 220Ω) - debe parpadear cada 5 seg
   ```

4. **Verificar divisor funciona:**
   ```
   Con multímetro en voltaje DC:
   - Poner sonda negra en GND
   - Poner sonda roja en ECHO del HC-SR04
   - Poner mano frente al sensor
   - Debe alternar entre 0V y ~5V
   
   Ahora medir en GPIO34:
   - Debe alternar entre 0V y ~2.7V
   - Si mide 5V aquí: ¡PELIGRO! Divisor mal armado
   ```

5. **Verificar objeto frente al sensor:**
   ```
   - Colocar libro u objeto plano a 20-50 cm
   - Asegurarse que esté perpendicular al sensor
   - Evitar ángulos > 30°
   ```

6. **Probar con otro sensor:**
   ```
   Si todo lo anterior está correcto:
   - El HC-SR04 puede estar dañado
   - Probar con otro sensor si está disponible
   ```

---

### Problema 2: Join Fallido (No se Conecta a ChirpStack)

**Síntomas:**
```
Serial Monitor:
EV_JOINING - Intentando unirse a la red...
(Se repite cada 10-30 segundos sin éxito)

ChirpStack:
No aparece ningún JoinRequest
```

**Soluciones por orden de probabilidad:**

1. **Gateway no está activo:**
   ```
   En ChirpStack → Gateways:
   ✅ Verificar "Last seen" sea reciente (< 1 minuto)
   ❌ Si dice "Never seen" o tiempo antiguo:
      - Gateway apagado
      - Gateway sin conexión a internet
      - Gateway mal configurado
   → Contactar al profesor/administrador
   ```

2. **Dispositivo muy lejos del gateway:**
   ```
   LoRaWAN alcance típico:
   - Interiores: 100-500 metros
   - Exteriores: 2-5 km
   
   Solución:
   - Acercarse al gateway
   - Ir a lugar con línea de vista al gateway
   - Verificar con profesor ubicación del gateway
   ```

3. **Antena LoRa no conectada:**
   ```
   ⚠️ CRÍTICO: Nunca transmitir sin antena
   
   Verificar:
   ✅ Antena conectada al conector SMA
   ✅ Antena apretada (no floja)
   ✅ Antena en posición vertical
   
   Si transmitiste sin antena:
   - El módulo LoRa puede haberse dañado
   - Probar con otra placa
   ```

4. **Credenciales incorrectas:**
   ```
   Verificar EXACTAMENTE:
   
   En código:
   DEVEUI[8] = { 0xDB, 0x71, 0x8E, 0x35, 0x05, 0x92, 0x38, 0x02 }
   APPEUI[8] = { 0x8A, 0xFD, 0x43, 0x71, 0xF8, 0x46, 0x52, 0x50 }
   APPKEY[16] = { 0x8A, 0xC5, 0x83, 0xDF, ... }
   
   En ChirpStack:
   DevEUI: 02389205358E71DB
   AppEUI: 505246F87143FD8A
   AppKey: 8AC583DFEEC76C81FFD19CCFE76B73BF
   
   ⚠️ Un solo carácter diferente = Join fallará
   ```

5. **Sub-banda incorrecta:**
   ```
   En código (línea ~450):
   LMIC_selectSubBand(1);  // Sub-banda 2
   
   Gateway debe estar en Sub-banda 2 también
   
   Si gateway usa otra sub-banda:
   - Cambiar código a: LMIC_selectSubBand(0) para SB1
   - O ajustar gateway a Sub-banda 2
   ```

6. **Dispositivo no registrado en ChirpStack:**
   ```
   Verificar en ChirpStack:
   Applications → [Tu app] → Devices
   
   Debe aparecer tu dispositivo con:
   ✅ DevEUI correcto
   ✅ Estado: Nunca visto (normal antes de Join)
   ✅ Device profile: Class A, OTAA
   ```

---

### Problema 3: Join Exitoso pero No Llegan Datos

**Síntomas:**
```
Serial Monitor:
✅ EV_JOINED - ¡CONECTADO!
📤 ENVIANDO PAQUETE #1
📤 EV_TXCOMPLETE

ChirpStack:
✅ JoinAccept visible
❌ No aparecen uplinks de datos
```

**Soluciones:**

1. **Verificar ventana de eventos:**
   ```
   En ChirpStack:
   Device → Events (no LoRaWAN frames)
   
   Buscar eventos tipo "uplink"
   Verificar timestamp sea reciente
   ```

2. **Verificar FPort:**
   ```
   En Serial Monitor:
   Puerto (FPort): 1
   
   En ChirpStack events:
   fPort debe ser 1
   
   Si es diferente: problema en el código
   ```

3. **Payload corrupto:**
   ```
   En ChirpStack, ver payload en HEX:
   Debe ser: 01 XX XX 05 ... (10 bytes)
   
   Si es diferente o truncado:
   - Revisar función do_send() en código
   - Verificar sizeof(payload) = 10
   ```

4. **Problema de timing:**
   ```
   Esperar al menos 60 segundos después de Join
   
   Primera TX: 2 segundos después de Join
   Siguientes: cada 30 segundos
   
   Ser paciente, no reiniciar constantemente
   ```

---

### Problema 4: Datos No se Decodifican

**Síntomas:**
```
ChirpStack Events muestra:
✅ Uplink recibido
✅ Payload en HEX: 01 FD 00 05 10 00 00 00 01 01
❌ No aparecen campos decodificados
```

**Soluciones:**

1. **Verificar codec configurado:**
   ```
   Application → Codec
   
   Debe decir:
   ✅ Codec: Custom JavaScript codec
   ✅ Código del decoder presente
   
   Si no:
   - Copiar codec de la sección 3.6
   - Pegar completo
   - Guardar
   ```

2. **Probar codec manualmente:**
   ```
   En algunos ChirpStack hay opción "Test"
   
   Payload de prueba:
   01 FD 00 05 10 00 00 00 01 01
   
   Debe retornar objeto JSON con campos
   ```

3. **Revisar errores de JavaScript:**
   ```
   Abrir consola del navegador (F12)
   Buscar errores en rojo
   
   Error común:
   "Unexpected token" = falta coma o llave
   ```

4. **Refrescar sesión:**
   ```
   - Cerrar sesión en ChirpStack
   - Limpiar caché del navegador
   - Iniciar sesión nuevamente
   - Verificar codec aún está guardado
   ```

---

### Problema 5: Lecturas Inestables o Erráticas

**Síntomas:**
```
Serial Monitor:
[MED #1] ✅ 25.3 cm
[MED #2] ✅ 125.8 cm
[MED #3] ✅ 15.2 cm
[MED #4] ✅ 205.4 cm
(Variaciones extremas sin mover nada)
```

**Causas y Soluciones:**

1. **Objeto no reflectante:**
   ```
   Materiales problemáticos:
   ❌ Telas (absorben sonido)
   ❌ Espuma
   ❌ Pelo/cabello
   ❌ Superficies muy irregulares
   
   Usar en su lugar:
   ✅ Cartón
   ✅ Madera
   ✅ Plástico plano
   ✅ Libro con tapa dura
   ```

2. **Ángulo incorrecto:**
   ```
   El sensor tiene cono de 15°
   
   Correcto:        Incorrecto:
      ║              ╱
      ║             ╱
    ┌─╨─┐         ┌─┐
    │Sen│         │Sen│
   
   Mantener objeto perpendicular ±15°
   ```

3. **Interferencias ultrasónicas:**
   ```
   Alejar de:
   - Otros sensores HC-SR04
   - Motores eléctricos
   - Ventiladores
   - Altavoces
   ```

4. **Alimentación inestable:**
   ```
   - Usar cable USB de buena calidad
   - Conectar a puerto USB de computadora (no hub)
   - Verificar que VCC sea estable 5V
   - Añadir capacitor 100µF entre VCC y GND (opcional)
   ```

5. **Implementar filtro en software:**
   ```cpp
   // Promedio móvil simple (añadir al código)
   #define SAMPLES 5
   float distanceBuffer[SAMPLES];
   int bufferIndex = 0;
   
   float getFilteredDistance() {
       distanceBuffer[bufferIndex] = readDistance();
       bufferIndex = (bufferIndex + 1) % SAMPLES;
       
       float sum = 0;
       int validSamples = 0;
       for(int i = 0; i < SAMPLES; i++) {
           if(distanceBuffer[i] > 0) {
               sum += distanceBuffer[i];
               validSamples++;
           }
       }
       return validSamples > 0 ? sum / validSamples : -1;
   }
   ```

---

### Problema 6: Display OLED No Funciona

**Síntomas:**
```
- Pantalla negra / blanca
- No muestra nada
- Código compila bien
```

**Soluciones:**

1. **Verificar conexión I2C:**
   ```
   Pines del TTGO:
   SDA: GPIO 21
   SCL: GPIO 22
   
   Verificar con código de prueba:
   ```
   ```cpp
   #include <Wire.h>
   
   void setup() {
     Serial.begin(115200);
     Wire.begin(21, 22);
     
     Serial.println("Escaneando I2C...");
     for(byte i = 1; i < 127; i++) {
       Wire.beginTransmission(i);
       if(Wire.endTransmission() == 0) {
         Serial.print("Dispositivo en 0x");
         Serial.println(i, HEX);
       }
     }
   }
   void loop() {}
   ```
   Debe encontrar dispositivo en 0x3C

2. **OLED dañado:**
   ```
   Si scan I2C no encuentra 0x3C:
   - OLED puede estar dañado
   - Contactar al profesor para reemplazo
   - El sistema funciona sin OLED (datos en Serial)
   ```

---

### Problema 7: No Compila el Código

**Errores comunes:**

```
Error: 'LMIC' was not declared
Solución: Instalar "MCCI LoRaWAN LMIC library"

Error: 'U8G2' does not name a type
Solución: Instalar "U8g2"

Error: 'LMIC_setSession' was not declared
Solución: Estás usando librería LMIC incorrecta
         Desinstalar todas las LMIC
         Instalar solo MCCI LoRaWAN LMIC

Error: Board 'ESP32' not found
Solución: Añadir URL de ESP32 en Preferences
         Instalar ESP32 en Board Manager
```

---

## 📝 EVALUACIÓN Y ENTREGA {#evaluacion}

### Criterios de Evaluación

| Criterio | Puntos | Descripción |
|----------|--------|-------------|
| **1. Montaje de Hardware** | 25 | |
| - Divisor de voltaje correcto | 10 | Resistencias correctas, bien conectadas |
| - Conexiones HC-SR04 | 8 | VCC, GND, TRIG, ECHO correctos |
| - Conexión LoRa y OLED | 7 | Antena conectada, todo funcional |
| **2. Configuración ChirpStack** | 20 | |
| - Aplicación creada | 5 | Nombre correcto, configurada |
| - Dispositivo registrado | 10 | Credenciales correctas, OTAA |
| - Codec funcionando | 5 | Decodifica correctamente |
| **3. Funcionamiento del Sistema** | 25 | |
| - Join exitoso | 10 | Conecta a ChirpStack en <60 seg |
| - Transmisiones continuas | 10 | Al menos 10 paquetes recibidos |
| - Sensor funcional | 5 | Lee distancias correctamente |
| **4. Pruebas y Mediciones** | 15 | |
| - Tabla de datos completa | 8 | Mínimo 8 distancias probadas |
| - Cálculos correctos | 7 | Error promedio, desviación, etc. |
| **5. Reporte** | 15 | |
| - Formato profesional | 5 | Portada, índice, referencias |
| - Análisis de resultados | 5 | Gráficas, interpretación |
| - Respuestas a preguntas | 5 | Completas y fundamentadas |
| **TOTAL** | **100** | |

---

### Formato del Reporte

**El reporte debe incluir:**

#### 1. Portada (1 página)
```
Universidad: [Nombre]
Curso: Comunicaciones e IoT
Laboratorio: Semana 8 - Sensor HC-SR04 + LoRaWAN

Estudiante: [Nombre completo]
Matrícula: [Tu matrícula]
Profesor: [Nombre del profesor]
Fecha: [DD/MM/AAAA]
```

#### 2. Índice (1 página)
```
1. Introducción .................... 3
2. Objetivos ....................... 4
3. Marco Teórico ................... 5
4. Desarrollo ...................... 8
   4.1 Montaje del Hardware ........ 8
   4.2 Configuración Software ...... 10
   4.3 Pruebas ..................... 12
5. Resultados ...................... 15
6. Análisis ........................ 18
7. Conclusiones .................... 20
8. Referencias ..................... 21
9. Anexos .......................... 22
```

#### 3. Introducción (1 página)
```
- Contexto del laboratorio
- Importancia de IoT y LPWAN
- Aplicaciones de sensores ultrasónicos
- Estructura del documento
```

#### 4. Objetivos (1 página)
```
Objetivo General:
[Copiar del inicio de la guía]

Objetivos Específicos:
1. [...]
2. [...]
3. [...]
```

#### 5. Marco Teórico (2-3 páginas)
```
Incluir:
- Fundamentos de LoRaWAN
- Protocolo OTAA
- Sensor HC-SR04
- Divisor de voltaje resistivo
- Todas las fórmulas usadas
```

#### 6. Desarrollo (3-4 páginas)
```
Con FOTOGRAFÍAS de:
- Protoboard con divisor armado
- Conexiones completas del sistema
- TTGO conectado al sensor
- Display OLED mostrando datos

Capturas de pantalla de:
- Serial Monitor con Join exitoso
- ChirpStack con dispositivo registrado
- ChirpStack con eventos/uplinks
- Codec configurado
```

#### 7. Resultados (2-3 páginas)

**Tabla de mediciones:**
```
| # | Dist. Real | Lectura | Error | Error % |
|---|------------|---------|-------|---------|
| 1 | 10 cm      | 9.8 cm  | 0.2   | 2.0%    |
| 2 | 20 cm      | 20.3 cm | 0.3   | 1.5%    |
...
```

**Estadísticas:**
```
Error promedio: _______ cm
Error máximo: _______ cm
Precisión del sistema: _______ %
Desviación estándar: _______ cm
```

**Métricas LoRaWAN:**
```
Paquetes enviados: _______
Paquetes recibidos: _______
PDR (Packet Delivery Ratio): _______ %
RSSI promedio: _______ dBm
SNR promedio: _______ dB
```

**Gráficas (mínimo 2):**
```
1. Distancia medida vs Distancia real
2. Distancia vs Tiempo (últimos 30 min)
3. (Opcional) Error vs Distancia
```

#### 8. Análisis (2 páginas)
```
Responder:
1. ¿El sensor es preciso? Justificar con datos
2. ¿Hay correlación entre distancia y error?
3. ¿Qué factores afectan la precisión?
4. ¿La conectividad LoRaWAN fue estable?
5. ¿El divisor de voltaje funcionó correctamente?
6. Comparar resultados con especificaciones del HC-SR04
```

#### 9. Respuestas a Preguntas de Evaluación (2-3 páginas)

Responder las 10 preguntas de la sección correspondiente.

#### 10. Conclusiones (1 página)
```
- Objetivos cumplidos (sí/no y por qué)
- Principales aprendizajes
- Dificultades encontradas y cómo se resolvieron
- Aplicaciones prácticas del sistema
- Mejoras propuestas
```

#### 11. Referencias (1 página)
```
Formato APA o IEEE:

[1] LoRa Alliance. (2021). LoRaWAN® Specification v1.0.3.
    https://lora-alliance.org/resource_hub/...

[2] Semtech. (2019). SX1276/77/78/79 Datasheet.

[3] ChirpStack Documentation. (2024).
    https://www.chirpstack.io/docs/

[Añadir más referencias usadas]
```

#### 12. Anexos
```
Anexo A: Código completo del sketch
Anexo B: Configuración completa de ChirpStack
Anexo C: Cálculos detallados
Anexo D: Fotografías adicionales
```

---

### Especificaciones de Entrega

**Formato:**
```
Tipo de archivo: PDF
Nombre: Lab8_[Apellido]_[Nombre].pdf
Ejemplo: Lab8_Garcia_Juan.pdf

Tamaño máximo: 15 MB
Páginas: 20-25 páginas
```

**Fecha de entrega:**
```
[Según calendario del curso]
Plataforma: [Especificada por el profesor]
```

**Penalizaciones:**
```
Entrega tardía:
- 1 día tarde: -10 puntos
- 2 días tarde: -20 puntos
- >3 días: no se acepta

Formato incorrecto: -5 puntos
Sin fotografías: -10 puntos
Sin código en anexo: -5 puntos
```

---

## 🎓 CONCLUSIÓN

¡Felicitaciones por completar el laboratorio de la Semana 8!

### Lo que has logrado:

✅ Construir un divisor de voltaje para proteger microcontroladores  
✅ Integrar un sensor ultrasónico con ESP32  
✅ Implementar el protocolo LoRaWAN OTAA  
✅ Configurar un servidor IoT (ChirpStack)  
✅ Transmitir datos de sensores a la nube  
✅ Decodificar y analizar datos en tiempo real  
✅ Evaluar precisión y rendimiento de un sistema IoT  

### Aplicaciones en el mundo real:

Este tipo de sistema se usa en:

 **Industria:** Monitoreo de nivel de tanques y silos  
 **Transporte:** Sensores de estacionamiento  
 **Retail:** Contador de personas en tiendas  
 **Ciudades inteligentes:** Medición de nivel de basureros  
 **Agricultura:** Monitoreo de nivel de agua en reservorios  

### Próximos pasos:

1. Experimentar con otros sensores (temperatura, humedad, etc.)
2. Implementar Deep Sleep para optimizar batería
3. Crear dashboards personalizados en ChirpStack
4. Desarrollar aplicaciones que consuman datos del sensor
5. Escalar a múltiples dispositivos en una red

---


**Documentación:**
- Guía TTGO T3: https://www.thethingsindustries.com/docs/hardware/devices/models/lilygo-lora32/
- Manual HC-SR04: PDF en el drive con datasheet HC-SR04.pdf
- ChirpStack docs: https://www.chirpstack.io/docs/


---

## REFERENCIAS

1. LoRa Alliance. (2021). *LoRaWAN® Specification v1.0.3*. Retrieved from https://lora-alliance.org/

2. Semtech Corporation. (2019). *SX1276/77/78/79 - 137 MHz to 1020 MHz Low Power Long Range Transceiver*. Datasheet.

3. Elecfreaks. (2018). *HC-SR04 Ultrasonic Sensor User Guide*.

4. ChirpStack. (2024). *ChirpStack open-source LoRaWAN® Network Server documentation*. https://www.chirpstack.io/docs/

5. Espressif Systems. (2023). *ESP32 Series Datasheet*. Version 3.9.

6. MCCI Corporation. (2024). *Arduino-LMIC library for LoRaWAN®*. GitHub repository.

7. Olikraus. (2024). *U8g2: Library for monochrome displays*. GitHub repository.

---



---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)