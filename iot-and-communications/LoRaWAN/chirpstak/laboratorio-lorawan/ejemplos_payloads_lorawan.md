# Ejemplos de Payloads LoRaWAN para Pruebas

Este archivo contiene payloads de ejemplo para probar decodificadores.

## Formato del Payload de 6 bytes

```
[Temp_H] [Temp_L] [Hum] [Pres_H] [Pres_L] [Bat]
```

### Campos:
- **Temperatura** (2 bytes): int16, rango -40 a 85°C, x100
- **Humedad** (1 byte): uint8, 0-100%
- **Presión** (2 bytes): uint16, 300-1100 hPa
- **Batería** (1 byte): uint8, voltaje (x100 - 200), 2.5-4.2V

---

## Casos de Prueba Exitosos

### Ejemplo 1: Condiciones Normales
```json
{
  "payload_hex": "0A1F3C03D60A7",
  "interpretacion": {
    "temperatura": 25.91,
    "humedad": 60,
    "presion": 982,
    "voltaje": 3.67
  },
  "descripcion": "Temperatura ambiente, 60% humedad, presión normal"
}
```

**Desglose:**
- `0A1F` = 2591 → 25.91°C
- `3C` = 60 → 60%
- `03D6` = 982 → 982 hPa
- `A7` = 167 → (167+200)/100 = 3.67V

---

### Ejemplo 2: Temperatura Alta
```json
{
  "payload_hex": "0FA03203E80B4",
  "interpretacion": {
    "temperatura": 40.00,
    "humedad": 50,
    "presion": 1000,
    "voltaje": 3.80
  },
  "descripcion": "Día caluroso, presión estable"
}
```

**Desglose:**
- `0FA0` = 4000 → 40.00°C
- `32` = 50 → 50%
- `03E8` = 1000 → 1000 hPa
- `B4` = 180 → 3.80V

---

### Ejemplo 3: Temperatura Baja
```json
{
  "payload_hex": "F8304503840064",
  "interpretacion": {
    "temperatura": -19.60,
    "humedad": 69,
    "presion": 900,
    "voltaje": 3.00
  },
  "descripcion": "Condiciones frías, baja presión"
}
```

**Desglose:**
- `F830` = -1960 (complemento a 2) → -19.60°C
- `45` = 69 → 69%
- `0384` = 900 → 900 hPa
- `64` = 100 → 3.00V

---

### Ejemplo 4: Batería Baja
```json
{
  "payload_hex": "09C43203E8032",
  "interpretacion": {
    "temperatura": 25.00,
    "humedad": 50,
    "presion": 1000,
    "voltaje": 2.50
  },
  "descripcion": "Condiciones normales, batería crítica"
}
```

**Desglose:**
- `09C4` = 2500 → 25.00°C
- `32` = 50 → 50%
- `03E8` = 1000 → 1000 hPa
- `32` = 50 → (50+200)/100 = 2.50V (¡ALERTA BATERÍA!)

---

### Ejemplo 5: Temperatura Negativa Extrema
```json
{
  "payload_hex": "F06014046400FA",
  "interpretacion": {
    "temperatura": -40.00,
    "humedad": 20,
    "presion": 1124,
    "voltaje": 4.50
  },
  "descripcion": "Temperatura mínima del sensor"
}
```

**Desglose:**
- `F060` = -4000 (complemento a 2) → -40.00°C
- `14` = 20 → 20%
- `0464` = 1124 → 1124 hPa
- `FA` = 250 → 4.50V (FUERA DE RANGO - debe detectarse error)

---

## Casos de Prueba con Errores

### Error 1: Temperatura Imposible (muy alta)
```json
{
  "payload_hex": "7FFF6403E80B4",
  "interpretacion": {
    "temperatura": 327.67,
    "humedad": 100,
    "presion": 1000,
    "voltaje": 3.80
  },
  "estatus": "error",
  "error_esperado": "Temperatura fuera de rango: 327.67°C"
}
```

---

### Error 2: Humedad Mayor a 100%
```json
{
  "payload_hex": "09C4FF03E80B4",
  "interpretacion": {
    "temperatura": 25.00,
    "humedad": 255,
    "presion": 1000,
    "voltaje": 3.80
  },
  "estatus": "error",
  "error_esperado": "Humedad fuera de rango: 255%"
}
```

---

### Error 3: Presión Baja Imposible
```json
{
  "payload_hex": "09C43200500B4",
  "interpretacion": {
    "temperatura": 25.00,
    "humedad": 50,
    "presion": 80,
    "voltaje": 3.80
  },
  "estatus": "error",
  "error_esperado": "Presión fuera de rango: 80 hPa"
}
```

---

### Error 4: Longitud Incorrecta (muy corto)
```json
{
  "payload_hex": "0A1F",
  "interpretacion": null,
  "estatus": "error",
  "error_esperado": "Longitud incorrecta: esperados 6 bytes, recibidos 2"
}
```

---

### Error 5: Longitud Incorrecta (muy largo)
```json
{
  "payload_hex": "0A1F3C03D60A7FF",
  "interpretacion": null,
  "estatus": "error",
  "error_esperado": "Longitud incorrecta: esperados 6 bytes, recibidos 7"
}
```

---

### Error 6: Caracteres No Hexadecimales
```json
{
  "payload_hex": "0A1FZZ03D60A7",
  "interpretacion": null,
  "estatus": "error",
  "error_esperado": "Formato hexadecimal inválido"
}
```

---

## Payloads para Pruebas Rápidas (copiar/pegar)

### Comando mosquitto_pub para testing

```bash
# Payload válido 1
mosquitto_pub -h localhost -t "lorawan/uplink/raw" -m '{
  "devEUI": "70B3D57ED005ABCD",
  "fPort": 1,
  "fCnt": 1,
  "mensaje": "0A1F3C03D60A7",
  "timestamp": 1699725600
}'

# Payload válido 2 (temperatura alta)
mosquitto_pub -h localhost -t "lorawan/uplink/raw" -m '{
  "devEUI": "70B3D57ED005ABCD",
  "fPort": 1,
  "fCnt": 2,
  "mensaje": "0FA03203E80B4",
  "timestamp": 1699725660
}'

# Payload con error (humedad > 100)
mosquitto_pub -h localhost -t "lorawan/uplink/raw" -m '{
  "devEUI": "70B3D57ED005ABCD",
  "fPort": 1,
  "fCnt": 3,
  "mensaje": "09C4FF03E80B4",
  "timestamp": 1699725720
}'
```

---

## Tabla de Referencia Rápida

| Hex | Dec | Temp (°C) | Hum (%) | Presión (hPa) | Voltaje (V) |
|-----|-----|-----------|---------|---------------|-------------|
| 0000 | 0 | 0.00 | - | - | - |
| 03E8 | 1000 | 10.00 | - | 1000 | - |
| 09C4 | 2500 | 25.00 | - | - | - |
| 0FA0 | 4000 | 40.00 | - | - | - |
| F060 | -4000* | -40.00 | - | - | - |
| 32 | 50 | - | 50 | - | - |
| 64 | 100 | - | 100 | - | - |
| A7 | 167 | - | - | - | 3.67 |

*Complemento a 2 para números negativos

---

## Cálculos Manuales para Validación

### Convertir Temperatura a Hex
```python
# Ejemplo: 25.91°C
temp_celsius = 25.91
temp_int = int(temp_celsius * 100)  # 2591
temp_hex = hex(temp_int)  # '0xa1f'
# Separar en bytes:
high_byte = (temp_int >> 8) & 0xFF  # 0x0A
low_byte = temp_int & 0xFF           # 0x1F
```

### Convertir Temperatura Negativa
```python
# Ejemplo: -19.60°C
temp_celsius = -19.60
temp_int = int(temp_celsius * 100)  # -1960
# Complemento a 2 (16 bits)
if temp_int < 0:
    temp_int = temp_int + 65536  # 63576
temp_hex = hex(temp_int)  # '0xf830'
```

### Decodificar desde Hex
```javascript
// En Node-RED Function:
const bytes = [0x0A, 0x1F, 0x3C, 0x03, 0xD6, 0xA7];

// Temperatura
let temp = (bytes[0] << 8) | bytes[1];  // 2591
if (temp > 32767) temp -= 65536;  // Manejar negativos
const temperatura = temp / 100.0;  // 25.91°C

// Humedad
const humedad = bytes[2];  // 60%

// Presión
const presion = (bytes[3] << 8) | bytes[4];  // 982 hPa

// Voltaje
const voltaje = (bytes[5] + 200) / 100.0;  // 3.67V
```

---

## Generador de Payloads (Script Python)

```python
#!/usr/bin/env python3
"""
Generador de payloads LoRaWAN para pruebas
"""

import struct
import random

def generar_payload(temp, hum, pres, volt):
    """
    Genera payload hexadecimal
    
    Args:
        temp: Temperatura en °C (-40 a 85)
        hum: Humedad en % (0-100)
        pres: Presión en hPa (300-1100)
        volt: Voltaje en V (2.5-4.2)
    
    Returns:
        String hexadecimal
    """
    # Temperatura (int16, x100)
    temp_int = int(temp * 100)
    if temp_int < 0:
        temp_int = temp_int + 65536  # Complemento a 2
    
    # Presión (uint16)
    pres_int = int(pres)
    
    # Voltaje (uint8, x100 - 200)
    volt_int = int((volt * 100) - 200)
    
    # Construir payload
    payload = struct.pack('>HBHBhB', 
                          temp_int,
                          int(hum),
                          pres_int,
                          volt_int)
    
    return payload.hex().upper()

# Ejemplos de uso
if __name__ == "__main__":
    print("Payload 1 (normal):", generar_payload(25.91, 60, 982, 3.67))
    print("Payload 2 (calor):", generar_payload(40.0, 50, 1000, 3.80))
    print("Payload 3 (frío):", generar_payload(-19.6, 69, 900, 3.00))
    
    # Generar 5 payloads aleatorios
    print("\nPayloads aleatorios:")
    for i in range(5):
        t = random.uniform(-10, 45)
        h = random.randint(20, 90)
        p = random.randint(950, 1050)
        v = random.uniform(3.0, 4.2)
        print(f"  {generar_payload(t, h, p, v)} -> T={t:.2f}°C")
```

---

## Notas para Estudiantes

1. **Siempre valida los rangos físicamente posibles**
   - No puede haber 150% de humedad
   - La temperatura tiene límites del sensor

2. **Maneja correctamente números negativos**
   - Usa complemento a 2 para int16
   - Verifica si el bit más significativo está en 1

3. **Prueba casos extremos**
   - Temperatura = -40°C (límite inferior)
   - Temperatura = 85°C (límite superior)
   - Batería = 2.5V (crítica)

4. **Documenta tu formato**
   - Orden de bytes (big-endian/little-endian)
   - Factores de escala
   - Offsets aplicados

---

**Última actualización:** 11 de noviembre de 2025
