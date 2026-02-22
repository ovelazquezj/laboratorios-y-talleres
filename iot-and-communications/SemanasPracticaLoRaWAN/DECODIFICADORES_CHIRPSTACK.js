// ╔════════════════════════════════════════════════════════════════════════╗
// ║                                                                        ║
// ║     DECODIFICADORES CHIRPSTACK - "HOLA MUNDO" IoT LABORATORY          ║
// ║                                                                        ║
// ║  Tres decodificadores para TTGO, Heltec y CubeCell                    ║
// ║  Cada uno explica CÓMO y POR QUÉ el device codifica así               ║
// ║                                                                        ║
// ╚════════════════════════════════════════════════════════════════════════╝

// ════════════════════════════════════════════════════════════════════════════
// DECODIFICADOR 1: TTGO T3 LoRaWAN (16 bytes)
// ════════════════════════════════════════════════════════════════════════════

/*
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║                     TTGO T3 DECODIFICADOR                             ║
 * ║                      16 Bytes Total                                   ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 * 
 * ESTRUCTURA DEL PAYLOAD QUE ENVÍA EL TTGO:
 * ──────────────────────────────────────────
 * 
 * [Byte 0]     → 0x48 (Tipo de mensaje: 'H' de "Hola")
 * [Bytes 1-4]  → Timestamp en Little-Endian (4 bytes)
 * [Bytes 5-14] → "hola mundo" en ASCII (10 caracteres)
 * [Byte 15]    → Checksum (suma de verificación)
 * 
 * TOTAL: 16 BYTES
 * 
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║ ¿POR QUÉ TTGO CODIFICA ASÍ?                                          ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 * 
 * 1. BYTE 0 (Tipo):
 *    - El TTGO usa LMIC library (IBM LoRaWAN stack)
 *    - LMIC fue diseñada para manejar múltiples sensores
 *    - Agrega un "byte de tipo" al inicio para identificar cuál sensor transmite
 *    - Esto permite que en la MISMA aplicación, diferentes sensores 
 *      codifiquen diferente
 *    - Ejemplo: Tipo 0x48=Hola, Tipo 0x54=Temperatura, Tipo 0x48=Humedad
 * 
 * 2. BYTES 1-4 (Timestamp en Little-Endian):
 *    - El timestamp es un uint32_t de 32 bits (4 bytes)
 *    - ESP32 (que usa TTGO) es Little-Endian nativo
 *    - El TTGO cómo enía este uint32_t en 4 bytes:
 *      
 *      Código TTGO (línea ~175 del sketch):
 *      ─────────────────────────────────────
 *      payload[1] = data.timestamp & 0xFF;           // Byte 0 (bits 0-7)
 *      payload[2] = (data.timestamp >> 8) & 0xFF;    // Byte 1 (bits 8-15)
 *      payload[3] = (data.timestamp >> 16) & 0xFF;   // Byte 2 (bits 16-23)
 *      payload[4] = (data.timestamp >> 24) & 0xFF;   // Byte 3 (bits 24-31)
 *      
 *      Operaciones bit a bit explicadas:
 *      ──────────────────────────────────
 *      & 0xFF        → Máscara: toma solo los 8 bits menos significativos
 *      >> 8          → Desplaza a la derecha 8 bits (divide entre 256)
 *      >> 16         → Desplaza 16 bits (divide entre 65536)
 *      >> 24         → Desplaza 24 bits (divide entre 16777216)
 *    
 *    - Ejemplo real: timestamp = 102 segundos
 *      ─────────────────────────────────────────
 *      102 en hexadecimal = 0x66
 *      En binario (32 bits): 00000000 00000000 00000000 01100110
 *      
 *      payload[1] = 102 & 0xFF = 0x66 (byte LSB)
 *      payload[2] = (102 >> 8) & 0xFF = 0x00
 *      payload[3] = (102 >> 16) & 0xFF = 0x00
 *      payload[4] = (102 >> 24) & 0xFF = 0x00
 * 
 * 3. BYTES 5-14 ("hola mundo"):
 *    - "hola mundo" tiene 10 caracteres exactos
 *    - Cada carácter se convierte a su código ASCII:
 *      h = 0x68 = 104
 *      o = 0x6F = 111
 *      l = 0x6C = 108
 *      a = 0x61 = 97
 *      (espacio) = 0x20 = 32
 *      m = 0x6D = 109
 *      u = 0x75 = 117
 *      n = 0x6E = 110
 *      d = 0x64 = 100
 *      o = 0x6F = 111
 *    - El TTGO copia byte a byte (línea ~182-184):
 *      for (int i = 0; i < 10; i++) {
 *          payload[5 + i] = data.mensaje[i];
 *      }
 * 
 * 4. BYTE 15 (Checksum):
 *    - Detecta corrupción de datos en transmisión
 *    - Se calcula como suma de TODOS los bytes anteriores (0 al 14)
 *    - Fórmula: checksum = (sum of bytes 0-14) mod 256
 *    - Por qué mod 256? Porque el resultado debe caber en 1 byte (0-255)
 *    - Ejemplo: 0x48 + 0x66 + ... = suma, y tomar solo los 8 bits bajos
 * 
 * ════════════════════════════════════════════════════════════════════════
 * EJEMPLO VISUAL: TTGO ENVIANDO TIMESTAMP=102
 * ════════════════════════════════════════════════════════════════════════
 * 
 * En Serial Monitor del TTGO ves:
 * ───────────────────────────────
 * Payload empaquetado (HEX):
 *   48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7
 * 
 * Decodificación manual:
 * ─────────────────────
 * [0]     Tipo:       0x48 ('H')
 * [1-4]   TS:         102 seg  (en Little-Endian: 66 00 00 00)
 * [5-14]  Msg:        hola mundo (68 6F 6C 61 20 6D 75 6E 64 6F)
 * [15]    Checksum:   0xC7
 * 
 * Este es exactamente el HEX que llega a ChirpStack.
 * TU DECODER debe interpretarlo correctamente.
 */

function Decode(fPort, bytes) {
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 1: EXTRAER BYTE DE TIPO (Posición [0])
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * El TTGO pone un byte identificador en la posición [0]
   * En nuestro caso es 0x48 (ASCII 'H' de "Hola Mundo")
   * 
   * Este byte permite que el mismo decoder entienda múltiples tipos:
   * - 0x48 = "Hola Mundo" (nuestro caso)
   * - 0x54 = "Temperatura" (podría ser futuro)
   * - 0x48 = "Humedad" (podría ser futuro)
   * 
   * Línea correspondiente en TTGO (sketch línea 165):
   * payload[0] = 0x48;
   */
  
  var tipo = bytes[0];
  
  // Conversión a formato legible:
  // HEX → String con formato "0x48"
  var tipo_hex = '0x' + tipo.toString(16).toUpperCase().padStart(2, '0');
  
  // ASCII → Si es imprimible, mostrar carácter
  var tipo_ascii = (tipo >= 32 && tipo <= 126) ? 
                   String.fromCharCode(tipo) : '?';
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 2: RECOMBINAR TIMESTAMP DESDE BYTES [1-4] (Little-Endian)
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * El TTGO dividió un uint32_t en 4 bytes (Little-Endian)
   * Nosotros hacemos el INVERSO: recombinamos los 4 bytes en uint32_t
   * 
   * Fórmula Little-Endian (LSB primero):
   * 
   *   timestamp = byte[1] | (byte[2] << 8) | (byte[3] << 16) | (byte[4] << 24)
   * 
   * Explicación bit a bit:
   * ──────────────────────
   * 
   * byte[1] | (byte[2] << 8) | (byte[3] << 16) | (byte[4] << 24)
   * 
   * Parte 1: byte[1]
   *   → Uso directo (bits 0-7)
   *   → Ejemplo: 0x66 = 01100110 (bits 0-7)
   * 
   * Parte 2: (byte[2] << 8)
   *   → Desplaza 8 bits a la izquierda
   *   → 0x00 << 8 = 00000000 (bits 8-15)
   * 
   * Parte 3: (byte[3] << 16)
   *   → Desplaza 16 bits a la izquierda
   *   → 0x00 << 16 = 00000000 (bits 16-23)
   * 
   * Parte 4: (byte[4] << 24)
   *   → Desplaza 24 bits a la izquierda
   *   → 0x00 << 24 = 00000000 (bits 24-31)
   * 
   * Operador |
   *   → OR bitwise: combina todos los bits en un solo número
   * 
   * Línea correspondiente en TTGO (sketch línea 472):
   * uint32_t ts_recalc = payload[1] | (payload[2] << 8) | 
   *                      (payload[3] << 16) | (payload[4] << 24);
   * 
   * EJEMPLO REAL: bytes = [48, 66, 00, 00, 00, ...]
   * ─────────────────────────────────────────────────
   * 
   * timestamp = 0x66 | (0x00 << 8) | (0x00 << 16) | (0x00 << 24)
   * timestamp = 0x66 | 0x0000 | 0x000000 | 0x00000000
   * timestamp = 0x66
   * timestamp = 102 en decimal
   * 
   * Este es el timestamp que el TTGO capturó con millis()/1000
   */
  
  var timestamp = bytes[1] |           // Byte 1 (bits 0-7, LSB)
                  (bytes[2] << 8) |    // Byte 2 (bits 8-15)
                  (bytes[3] << 16) |   // Byte 3 (bits 16-23)
                  (bytes[4] << 24);    // Byte 4 (bits 24-31, MSB)
  
  // Convertir timestamp a tiempo legible
  var minutos = Math.floor(timestamp / 60);
  var segundos = timestamp % 60;
  var tiempo_legible = minutos + 'm ' + segundos + 's desde inicio del TTGO';
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 3: EXTRAER MENSAJE DESDE BYTES [5-14] (ASCII)
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * El TTGO copió "hola mundo" en bytes [5] a [14]
   * Cada byte es un carácter ASCII (10 caracteres = 10 bytes)
   * 
   * Conversión ASCII:
   * h = 0x68 → String.fromCharCode(0x68) = "h"
   * o = 0x6F → String.fromCharCode(0x6F) = "o"
   * ... etc
   * 
   * Línea correspondiente en TTGO (sketch línea 182-184):
   * for (int i = 0; i < 10; i++) {
   *     payload[5 + i] = data.mensaje[i];
   * }
   * 
   * Línea correspondiente en TTGO lectura (sketch línea 478-480):
   * for (int i = 5; i < 15; i++) {
   *     Serial.print((char)payload[i]);
   * }
   * 
   * EJEMPLO: bytes[5-14] = [68, 6F, 6C, 61, 20, 6D, 75, 6E, 64, 6F]
   * ──────────────────────────────────────────────────────────────────
   * Conversión:
   * 0x68 → 'h'
   * 0x6F → 'o'
   * 0x6C → 'l'
   * 0x61 → 'a'
   * 0x20 → ' ' (espacio)
   * 0x6D → 'm'
   * 0x75 → 'u'
   * 0x6E → 'n'
   * 0x64 → 'd'
   * 0x6F → 'o'
   * 
   * Resultado final: "hola mundo"
   */
  
  var mensaje = '';
  for (var i = 5; i < 15; i++) {
    // String.fromCharCode() convierte código ASCII → carácter
    mensaje += String.fromCharCode(bytes[i]);
  }
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 4: EXTRAER Y VALIDAR CHECKSUM (Byte [15])
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * El TTGO calcula checksum como suma simple de bytes [0-14] mod 256
   * 
   * Código TTGO (línea 189-191):
   * payload[15] = 0;
   * for (int i = 0; i < 15; i++) {
   *     payload[15] += payload[i];
   * }
   * 
   * Por qué mod 256? Porque el checksum debe caber en 1 byte (máx 255)
   * 
   * Validación: Recalculamos el checksum localmente y lo comparamos
   * Si coinciden → Payload no fue corrompido en transmisión
   * Si no coinciden → Algo salió mal
   * 
   * EJEMPLO: Si suma = 256, checksum = 256 & 0xFF = 0
   * EJEMPLO: Si suma = 300, checksum = 300 & 0xFF = 44
   * 
   * FÓRMULA: checksum = (sum of bytes 0-14) & 0xFF
   * 
   * La operación & 0xFF es equivalente a mod 256:
   * Toma solo los 8 bits menos significativos
   */
  
  var checksum_recibido = bytes[15];
  
  // Recalcular checksum
  var checksum_calculado = 0;
  for (var i = 0; i < 15; i++) {
    checksum_calculado += bytes[i];
  }
  
  // Aplicar máscara de 8 bits (equivalente a mod 256)
  checksum_calculado = checksum_calculado & 0xFF;
  
  // Validar
  var checksum_ok = (checksum_recibido === checksum_calculado);
  var checksum_status = checksum_ok ? 
                        '✅ VÁLIDO - Payload intacto' : 
                        '❌ CORRUPTO - Error en transmisión';
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 5: RETORNAR OBJETO JSON CON DATOS DECODIFICADOS
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * ChirpStack toma el objeto JavaScript que retornamos
   * y lo convierte a JSON para mostrar en el dashboard
   * 
   * Este JSON es lo que ven los alumnos como "Decoded Payload"
   * en la interfaz de ChirpStack
   */
  
  return {
    // Información del tipo de mensaje
    tipo_hex: tipo_hex,
    tipo_ascii: tipo_ascii,
    tipo_descripcion: 'Hola Mundo - Laboratorio IoT',
    
    // Información del timestamp
    timestamp_segundos: timestamp,
    timestamp_legible: tiempo_legible,
    
    // Información del mensaje
    mensaje: mensaje,
    mensaje_longitud: mensaje.length + ' caracteres',
    
    // Información del checksum
    checksum_hex: '0x' + checksum_recibido.toString(16).toUpperCase().padStart(2, '0'),
    checksum_ok: checksum_ok,
    checksum_status: checksum_status,
    
    // Información estructural
    tamanio_payload: bytes.length + ' bytes',
    puerto_lora: fPort,
    
    // Resumen educativo
    resumen: {
      "Bytes totales": 16,
      "Bytes tipo": 1,
      "Bytes timestamp": 4,
      "Bytes mensaje": 10,
      "Bytes checksum": 1,
      "Formato timestamp": "Little-Endian (LSB first)",
      "Codificación mensaje": "ASCII"
    }
  };
}


// ════════════════════════════════════════════════════════════════════════════
// DECODIFICADOR 2: HELTEC LoRa32 V3 (16 bytes - IDÉNTICO a TTGO)
// ════════════════════════════════════════════════════════════════════════════

/*
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║                   HELTEC LORА32 V3 DECODIFICADOR                      ║
 * ║                      16 Bytes Total                                   ║
 * ║              ⚠️ ESTRUCTURA IDÉNTICA A TTGO                            ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 * 
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║ ¿POR QUÉ HELTEC ES IDÉNTICO A TTGO?                                  ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 * 
 * Aunque Heltec V3 es diferente en hardware al TTGO:
 * - TTGO: ESP32 + SX1276
 * - Heltec: ESP32-S3 + SX1262
 * 
 * El CÓDIGO DE PAYLOAD es IDÉNTICO porque:
 * 
 * 1. AMBOS USAN ARQUITECTURA MODULAR SIMILAR
 *    - Byte 0 = Tipo
 *    - Bytes 1-4 = Timestamp LE
 *    - Bytes 5-14 = Mensaje
 *    - Byte 15 = Checksum
 * 
 * 2. LA CODIFICACIÓN DE DATOS RESPETA ESTÁNDARES
 *    - Little-Endian para enteros (ambos son arquitecturas ARM/Xtensa)
 *    - ASCII para texto
 *    - Suma simple para checksum
 * 
 * 3. MISMO PATRÓN EDUCATIVO EN LABORATORIO
 *    El mismo sketch sirve para explicar cómo codifican ambos
 * 
 * DIFERENCIAS EN HARDWARE (no afectan el payload):
 * ───────────────────────────────────────────────
 * - Microcontrolador: ESP32-S3 (en lugar de ESP32)
 *   → Ambos Little-Endian, sin cambio en encoding
 * 
 * - LoRa Chip: SX1262 (en lugar de SX1276)
 *   → Usa RadioLib (en lugar de LMIC)
 *   → Pero RadioLib usa el mismo patrón de payload
 * 
 * - Resolución: 128x64 OLED (igual al TTGO)
 * 
 * - Región: EU868 (en lugar de US915)
 *   → Es solo configuración de frecuencia, no afecta payload
 * 
 * ════════════════════════════════════════════════════════════════════════
 * CONCLUSIÓN: USA EL MISMO DECODER QUE TTGO
 * ════════════════════════════════════════════════════════════════════════
 * 
 * Este decoder funciona para AMBOS porque:
 * ✓ Estructura interna idéntica
 * ✓ Codificación de datos idéntica
 * ✓ Posiciones de bytes idénticas
 * 
 * Los alumnos aprenden que:
 * "Diferentes hardware + diferentes librerías pueden
 *  producir el MISMO payload si siguen estándares comunes"
 */

// NOTA: El decoder es exactamente el mismo que TTGO
// No necesita código separado
// Este comentario es solo para documentación educativa

// Si necesitas usar en ChirpStack con device name "Heltec":
// Copia el código del TTGO arriba (líneas ~80 en adelante)


// ════════════════════════════════════════════════════════════════════════════
// DECODIFICADOR 3: CUBECELL HTCC-AB01 (15 bytes - DIFERENTE)
// ════════════════════════════════════════════════════════════════════════════

/*
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║                    CUBECELL HTCC-AB01 DECODIFICADOR                   ║
 * ║                      15 Bytes Total (MÁS COMPACTO)                    ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 * 
 * ESTRUCTURA DEL PAYLOAD QUE ENVÍA CUBECELL:
 * ───────────────────────────────────────────
 * 
 * [Bytes 0-3]   → Timestamp en Little-Endian (4 bytes)
 * [Bytes 4-13]  → "hola mundo" en ASCII (10 caracteres)
 * [Byte 14]     → Checksum (suma de verificación)
 * 
 * TOTAL: 15 BYTES (1 byte menos que TTGO)
 * 
 * ╔═══════════════════════════════════════════════════════════════════════╗
 * ║ ¿POR QUÉ CUBECELL CODIFICA DIFERENTE?                                ║
 * ╚═══════════════════════════════════════════════════════════════════════╝
 * 
 * CubeCell (Seeed Studio) usa una librería DIFERENTE: LoRaWan_APP.h
 * 
 * Características de LoRaWan_APP:
 * ───────────────────────────────
 * 
 * 1. SIN BYTE DE TIPO
 *    - LoRaWan_APP fue diseñada para aplicaciones simples
 *    - Asume que hay UN SOLO tipo de mensaje
 *    - Por eso no incluye byte identificador
 *    - ¡Ahorra 1 byte de payload!
 * 
 *    Comparación:
 *    TTGO:     [TIPO] [TIMESTAMP] [MENSAJE] [CHECKSUM] = 16 bytes
 *    CubeCell: [TIMESTAMP] [MENSAJE] [CHECKSUM] = 15 bytes
 * 
 * 2. TIMESTAMP COMIENZA EN BYTE 0
 *    Código CubeCell (línea 138-141 del sketch):
 *    ────────────────────────────────────────
 *    appData[0] = timestamp & 0xFF;
 *    appData[1] = (timestamp >> 8) & 0xFF;
 *    appData[2] = (timestamp >> 16) & 0xFF;
 *    appData[3] = (timestamp >> 24) & 0xFF;
 *    
 *    Nota el índice: [0-3] no [1-4]
 *    Porque no hay byte de tipo antes
 * 
 * 3. MENSAJE COMIENZA EN BYTE 4
 *    Código CubeCell (línea 145-147):
 *    ──────────────────────────────
 *    for (int i = 0; i < 10; i++) {
 *        appData[4 + i] = mensaje[i];
 *    }
 *    
 *    Nota: [4 + i] en lugar de [5 + i]
 * 
 * 4. CHECKSUM EN BYTE 14
 *    Código CubeCell (línea 150-153):
 *    ──────────────────────────────
 *    appData[14] = 0;
 *    for (int i = 0; i < 14; i++) {
 *        appData[14] += appData[i];
 *    }
 *    
 *    Nota: Suma desde [0] a [13], no [0] a [14]
 * 
 * ════════════════════════════════════════════════════════════════════════
 * EJEMPLO VISUAL: CUBECELL ENVIANDO TIMESTAMP=102
 * ════════════════════════════════════════════════════════════════════════
 * 
 * En Serial Monitor del CubeCell ves:
 * ──────────────────────────────────
 * Payload empaquetado (HEX):
 *   66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F XX
 * 
 * Decodificación manual:
 * ─────────────────────
 * [0-3]   TS:         102 seg (en LE: 66 00 00 00)
 * [4-13]  Msg:        hola mundo (68 6F 6C 61 20 6D 75 6E 64 6F)
 * [14]    Checksum:   XX (suma mod 256)
 * 
 * COMPARACIÓN CON TTGO:
 * ────────────────────
 * TTGO:     48 66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F C7
 *           ││ └──────┬──────┘ └──────┬────────────────┘ ││
 *           Tipo   Timestamp         Mensaje         Checksum
 *           (16 bytes)
 * 
 * CubeCell:    66 00 00 00 68 6F 6C 61 20 6D 75 6E 64 6F XX
 *              └──────┬──────┘ └──────┬────────────────┘ │
 *              Timestamp           Mensaje          Checksum
 *              (15 bytes)
 *              
 *              ↑ FALTA EL 0x48 AL INICIO
 * 
 * ════════════════════════════════════════════════════════════════════════
 * IMPLICACIÓN EDUCATIVA
 * ════════════════════════════════════════════════════════════════════════
 * 
 * Para los alumnos es CRÍTICO entender que:
 * 
 * "Aunque manden el MISMO contenido (timestamp + 'hola mundo'),
 *  el FORMATO DEL PAYLOAD es diferente.
 *  
 *  Por eso necesitas DECODERS DIFERENTES:
 *  - Decoder TTGO busca tipo en [0], timestamp en [1-4]
 *  - Decoder CubeCell busca timestamp directo en [0-3]
 *  
 *  Si confundes los decoders:
 *  - TTGO en decoder CubeCell: Lee el 0x48 como parte del timestamp
 *    Resultado: timestamp = 0x48 + 0x66 = ¡INCORRECTO!
 *  - CubeCell en decoder TTGO: Falla porque espera 16 bytes, solo recibe 15
 *    Resultado: Error 'bytes[15] is undefined'"
 */

function Decode(fPort, bytes) {
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 1: RECOMBINAR TIMESTAMP DESDE BYTES [0-3] (Little-Endian)
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * ⚠️ DIFERENCIA CRÍTICA: CubeCell comienza en [0], NO en [1]
   * 
   * TTGO/Heltec:  timestamp en bytes [1-4]
   * CubeCell:     timestamp en bytes [0-3]
   * 
   * La razón: CubeCell no tiene byte de tipo, comienza directo con datos
   * 
   * Fórmula Little-Endian (igual que TTGO, solo diferente índice):
   * 
   *   timestamp = byte[0] | (byte[1] << 8) | (byte[2] << 16) | (byte[3] << 24)
   * 
   * Código CubeCell en sketch (línea 187-189):
   * ───────────────────────────────────────────
   * uint32_t ts_recalc = appData[0] | (appData[1] << 8) | 
   *                      (appData[2] << 16) | (appData[3] << 24);
   * 
   * EJEMPLO: bytes = [66, 00, 00, 00, 68, 6F, 6C, 61, 20, ...]
   * ─────────────────────────────────────────────────────────
   * 
   * timestamp = 0x66 | (0x00 << 8) | (0x00 << 16) | (0x00 << 24)
   * timestamp = 0x66 | 0x0000 | 0x000000 | 0x00000000
   * timestamp = 0x66 = 102 decimal
   */
  
  var timestamp = bytes[0] |           // Byte 0 (bits 0-7, LSB) ← DIRECTO
                  (bytes[1] << 8) |    // Byte 1 (bits 8-15)
                  (bytes[2] << 16) |   // Byte 2 (bits 16-23)
                  (bytes[3] << 24);    // Byte 3 (bits 24-31, MSB)
  
  // Convertir a formato legible
  var minutos = Math.floor(timestamp / 60);
  var segundos = timestamp % 60;
  var tiempo_legible = minutos + 'm ' + segundos + 's desde inicio del CubeCell';
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 2: EXTRAER MENSAJE DESDE BYTES [4-13] (ASCII)
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * ⚠️ DIFERENCIA CRÍTICA: CubeCell comienza en [4], NO en [5]
   * 
   * TTGO/Heltec:  mensaje en bytes [5-14]
   * CubeCell:     mensaje en bytes [4-13]
   * 
   * La razón: Sin byte de tipo, los índices se desplazan -1
   * 
   * Código CubeCell en sketch (línea 194-196):
   * ──────────────────────────────────────────
   * for (int i = 4; i < 14; i++) {
   *     Serial.print((char)appData[i]);
   * }
   * 
   * EJEMPLO: bytes[4-13] = [68, 6F, 6C, 61, 20, 6D, 75, 6E, 64, 6F]
   * ───────────────────────────────────────────────────────────────
   * Conversión ASCII:
   * 0x68 → 'h'
   * 0x6F → 'o'
   * 0x6C → 'l'
   * 0x61 → 'a'
   * 0x20 → ' '
   * 0x6D → 'm'
   * 0x75 → 'u'
   * 0x6E → 'n'
   * 0x64 → 'd'
   * 0x6F → 'o'
   * 
   * Resultado: "hola mundo"
   */
  
  var mensaje = '';
  for (var i = 4; i < 14; i++) {  // ← NOTA: comienza en [4], NO [5]
    mensaje += String.fromCharCode(bytes[i]);
  }
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 3: EXTRAER Y VALIDAR CHECKSUM (Byte [14])
  // ──────────────────────────────────────────────────────────────────────
  
  /*
   * ⚠️ DIFERENCIA CRÍTICA: CubeCell checksum en [14], NO en [15]
   * 
   * TTGO/Heltec:  checksum en byte [15]
   * CubeCell:     checksum en byte [14]
   * 
   * La razón: 15 bytes totales, no 16
   * 
   * Código CubeCell en sketch (línea 150-153):
   * ──────────────────────────────────────────
   * appData[14] = 0;
   * for (int i = 0; i < 14; i++) {
   *     appData[14] += appData[i];
   * }
   * 
   * Suma desde [0] a [13], NO [0] a [14]
   * 
   * FÓRMULA: checksum = (sum of bytes 0-13) & 0xFF
   * 
   * EJEMPLO: sum = 500, checksum = 500 & 0xFF = 244
   */
  
  var checksum_recibido = bytes[14];  // ← NOTA: posición [14], NO [15]
  
  // Recalcular checksum
  var checksum_calculado = 0;
  for (var i = 0; i < 14; i++) {  // ← Suma [0] a [13], NO [0] a [14]
    checksum_calculado += bytes[i];
  }
  
  // Aplicar máscara de 8 bits
  checksum_calculado = checksum_calculado & 0xFF;
  
  // Validar
  var checksum_ok = (checksum_recibido === checksum_calculado);
  var checksum_status = checksum_ok ? 
                        '✅ VÁLIDO - Payload intacto' : 
                        '❌ CORRUPTO - Error en transmisión';
  
  // ──────────────────────────────────────────────────────────────────────
  // PASO 4: RETORNAR OBJETO JSON CON DATOS DECODIFICADOS
  // ──────────────────────────────────────────────────────────────────────
  
  return {
    // Información del dispositivo
    dispositivo: 'CubeCell HTCC-AB01',
    dispositivo_caracteristica: 'Formato compacto (sin byte de tipo)',
    
    // Información del timestamp
    timestamp_segundos: timestamp,
    timestamp_legible: tiempo_legible,
    
    // Información del mensaje
    mensaje: mensaje,
    mensaje_longitud: mensaje.length + ' caracteres',
    
    // Información del checksum
    checksum_hex: '0x' + checksum_recibido.toString(16).toUpperCase().padStart(2, '0'),
    checksum_ok: checksum_ok,
    checksum_status: checksum_status,
    
    // Información estructural
    tamanio_payload: bytes.length + ' bytes',
    puerto_lora: fPort,
    
    // Resumen educativo
    resumen: {
      "Bytes totales": 15,
      "Bytes timestamp": 4,
      "Bytes mensaje": 10,
      "Bytes checksum": 1,
      "Bytes tipo": "NINGUNO (más compacto que TTGO/Heltec)",
      "Formato timestamp": "Little-Endian (LSB first)",
      "Codificación mensaje": "ASCII",
      "Diferencia con TTGO": "CubeCell es 1 byte más pequeño (sin tipo)"
    },
    
    // Advertencia educativa
    nota_importante: "Este decoder NO funciona con TTGO/Heltec. Necesitas decoders diferentes porque los índices de bytes son distintos."
  };
}


// ════════════════════════════════════════════════════════════════════════════
// TABLA COMPARATIVA FINAL PARA ALUMNOS
// ════════════════════════════════════════════════════════════════════════════

/*
 * ╔════════════════════════════════════════════════════════════════════════╗
 * ║                     TABLA DE DIFERENCIAS                              ║
 * ╠════════════════════════════════════════════════════════════════════════╣
 * ║ PARÁMETRO            │  TTGO/Heltec      │  CubeCell               ║
 * ╠════════════════════════════════════════════════════════════════════════╣
 * ║ Total bytes          │  16               │  15                     ║
 * ║ Byte de Tipo         │  [0] = 0x48       │  NO EXISTE              ║
 * ║ Timestamp            │  [1-4] LE         │  [0-3] LE               ║
 * ║ Mensaje ("hola...")  │  [5-14] ASCII     │  [4-13] ASCII           ║
 * ║ Checksum             │  [15]             │  [14]                   ║
 * ║ Librería             │  LMIC (TTGO)      │  LoRaWan_APP            ║
 * ║                      │  RadioLib (Heltec)│  (Seeed)                ║
 * ║ Decodificación       │  Bytes [1-4]      │  Bytes [0-3]            ║
 * ║ Validación           │  Checksum [0-14]  │  Checksum [0-13]        ║
 * ╚════════════════════════════════════════════════════════════════════════╝
 * 
 * ¿QUÉ APRENDEN LOS ALUMNOS?
 * ──────────────────────────
 * 
 * 1. Diferentes librerías → Diferentes payloads
 * 2. El DECODER es el "diccionario" que interpreta cada formato
 * 3. Pequeñas diferencias en índices rompen todo
 * 4. Importancia de documentación clara (comentarios en código)
 * 5. Little-Endian es estándar en microcontroladores ARM
 * 6. Checksums detectan corrupción
 */
