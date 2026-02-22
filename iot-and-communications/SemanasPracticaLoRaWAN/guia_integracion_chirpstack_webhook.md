# Guía para Integración de LNS (ChirpStack) con App Server por Medio de Integración HTTP y Webhook

## Introducción y Requisitos

### Objetivo de este laboratorio

En este laboratorio aprenderás a integrar ChirpStack v4 (tu Network Server LoRaWAN local) con un **Application Server personalizado** que recibe datos en tiempo real mediante **webhooks HTTP**. Los datos que envía tu dispositivo TTGO ( el ESP32 con LoRa WAN) fluirán así:

```
Dispositivo TTGO ( el ESP32 con LoRa WAN) → Gateway LoRaWAN → ChirpStack → HTTP Webhook → Application Server (Flask)
```

### Requisitos previos

Antes de comenzar, asegúrate de tener:

-   **ChirpStack v4** instalado y corriendo en `http://192.168.18.62:8080`
-   **Gateway LoRaWAN** conectado y registrado en ChirpStack
-   **Aplicación "picaro_1"** (o tu nombre de aplicación) creada en ChirpStack
-   **Sketch TTGO ( el ESP32 con LoRa WAN) ( el ESP32 con LoRa WAN) V3** con generador de datos dummy **ya flasheado** en la placa ESP32
-   **Python 3.7+** instalado en tu máquina
-   Acceso a la red local (misma WiFi que ChirpStack)

### Componentes que crearemos

1. **Device Profile** con Codec JavaScript para decodificar payloads
2. **Dispositivo** registrado en ChirpStack
3. **HTTP Integration** (webhook) en ChirpStack
4. **Application Server** en Python/Flask que recibe eventos en tiempo real

---

## Sección 1: Crear Device Profile con Codec

El Device Profile define cómo decodificar los datos que envía tu dispositivo TTGO ( el ESP32 con LoRa WAN). Incluye un Codec JavaScript que convierte bytes en datos legibles.

### Pasos en ChirpStack UI

1. Abre ChirpStack: `http://192.168.18.62:8080`
2. Ve a: **Device Profiles** → **Create**
3. Completa los campos básicos:
   - **Name:** `TTGO ( el ESP32 con LoRa WAN)_LoRa_Profile`
   - **Region:** `US915` (o la tuya)
   - **MAC version:** `1.0.3`
   - **Supports OTAA:**   Activado

4. En la pestaña **Codec**, selecciona: **Codec type: Custom JavaScript**

5. **En la sección "Decode function"**, copia y pega el siguiente código:

```javascript
/**
 * ChirpStack v4 Codec para TTGO ( el ESP32 con LoRa WAN) LoRa GPS+BMP280
 * Payload: 12 bytes Big-Endian
 * lat_e7:int32 | lon_e7:int32 | alt_m:int16 | temp_centi:int16
 */

function decodeUplink(input) {
  var bytes = input.bytes;
  var fPort = input.fPort;

  if (fPort !== 1) {
    return { data: { error: "Invalid fPort" } };
  }

  if (bytes.length !== 12) {
    return { data: { error: "Invalid payload length" } };
  }

  // Decodificar Big-Endian int32 para lat_e7
  var lat_e7 = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
  if (lat_e7 & 0x80000000) lat_e7 = lat_e7 - 0x100000000;
  var latitude = lat_e7 / 1e7;

  // Decodificar Big-Endian int32 para lon_e7
  var lon_e7 = (bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7];
  if (lon_e7 & 0x80000000) lon_e7 = lon_e7 - 0x100000000;
  var longitude = lon_e7 / 1e7;

  // Decodificar Big-Endian int16 para alt_m
  var alt_m = (bytes[8] << 8) | bytes[9];
  if (alt_m & 0x8000) alt_m = alt_m - 0x10000;
  var altitude = alt_m;

  // Decodificar Big-Endian int16 para temp_centi
  var temp_centi = (bytes[10] << 8) | bytes[11];
  if (temp_centi & 0x8000) temp_centi = temp_centi - 0x10000;
  var temperature = temp_centi === 0x7FFF ? null : temp_centi / 100.0;

  return {
    data: {
      latitude: parseFloat(latitude.toFixed(7)),
      longitude: parseFloat(longitude.toFixed(7)),
      altitude: altitude,
      temperature: temperature,
      gps_valid: !(latitude === 0 && longitude === 0),
      payload_hex: bytes.map(function(x) { return (x < 16 ? '0' : '') + x.toString(16); }).join('')
    }
  };
}

function encodeDownlink(input) {
  return { bytes: [] };
}
```

6. Haz clic en **Create** o **Submit**

El Device Profile está listo. Este codec decodificará los 12 bytes que envía tu TTGO ( el ESP32 con LoRa WAN) en datos estructurados: latitud, longitud, altitud y temperatura.

---

## Sección 2: Registrar el Dispositivo

Ahora registrarás tu dispositivo TTGO ( el ESP32 con LoRa WAN) en ChirpStack para que pueda hacer join a la red.

### Pasos en ChirpStack UI

1. Ve a: **Applications** → **picaro_1** (tu aplicación) → **Create device**

2. Completa los campos:
   - **Device name:** `TTGO ( el ESP32 con LoRa WAN)-dummy-001` (o un nombre único)
   - **Device EUI:** Genera uno o deja que ChirpStack lo cree
   - **Device class:** `Class A`
   - **Activation method:** `OTAA`
   - **Device profile:** Selecciona `TTGO ( el ESP32 con LoRa WAN)_LoRa_Profile`

3. En la pestaña **OTAA keys**, configura:
   - **Join EUI:** (valor del sketch TTGO ( el ESP32 con LoRa WAN))
   - **Application Key:** (valor del sketch TTGO ( el ESP32 con LoRa WAN))

4. Haz clic en **Create**

El dispositivo está registrado y listo para hacer join a la red.

---

## Sección 3: Flashear el Sketch TTGO ( el ESP32 con LoRa WAN)

### Prerequisito

Tu placa **TTGO V3( el ESP32 con LoRa WAN)** debe tener **previamente flasheado** el sketch con generador de datos dummy que simula:
- Coordenadas GPS alrededor de CDMX
- Temperatura variable entre 20-27.9°C
- Envío cada 30 segundos

Si aún no lo has flasheado, hazlo ahora antes de continuar con los siguientes pasos.

---

## Sección 4: Verificar JOIN en ChirpStack

Una vez flasheado el sketch en la placa TTGO ( el ESP32 con LoRa WAN), el dispositivo intentará hacer join a la red LoRaWAN.

### Qué hacer

1. Enciende la placa TTGO ( el ESP32 con LoRa WAN)
2. Espera entre 30-60 segundos
3. Ve a ChirpStack: **Applications** → **picaro_1** → **Devices** → tu dispositivo
4. Revisa que el dispositivo esté **haciendo JOIN** (busca eventos de join en el panel de eventos)

### Qué esperar

- El dispositivo debe cambiar de estado: "Never seen" → "Active" o "Last seen: hace unos segundos"
- En la sección de **Events**, deberías ver eventos como `JoinRequest` o `JoinAccept`

---

## Sección 5: Verificar Uplinks en ChirpStack

Una vez que el dispositivo ha hecho join, comenzará a enviar datos (uplinks).

### Qué hacer

1. Ve a tu dispositivo en ChirpStack: **Applications** → **picaro_1** → **Devices** → tu dispositivo
2. Abre la pestaña **Events** o **LoRaWAN frames**
3. Espera a que lleguen nuevos eventos

### Qué esperar

Deberías ver eventos de tipo `up` (uplink) con:
- **Payload (Base64):** Datos del TTGO ( el ESP32 con LoRa WAN) codificados
- **objectJson:** Los datos **decodificados** por tu Codec:
  ```json
  {
    "latitude": 25.540701,
    "longitude": -103.557434,
    "altitude": 1500,
    "temperature": 20.7,
    "gps_valid": true,
    "payload_hex": "0F5DE1A1F79AB1A105DC0952"
  }
  ```

Si ves esta información, tu Device Profile y Codec están trabajando correctamente.  

---

## Sección 6: Configurar HTTP Integration (Webhook)

Ahora configurarás un **webhook** en ChirpStack para que envíe todos los eventos a tu Application Server.

### Pasos en ChirpStack UI

1. Ve a: **Applications** → **picaro_1** → **Integrations**

2. Haz clic en **+ HTTP**

3. Rellena los campos:
   - **Event endpoint URL(s):** `http://192.168.18.62:8000/webhook`
   - **Payload marshaler:** `JSON`
   - **Headers:** Deja en blanco por ahora

4. Haz clic en **Create** o **Submit**

El webhook está configurado. ChirpStack ahora enviará todos los eventos (uplinks, joins, errors) a tu Application Server en el puerto 8000.

---

## Sección 7: Crear Application Server

Ahora crearás el **Application Server** en Python que recibe y procesa los webhooks de ChirpStack.

### Prerequisito: Instalar Flask

Abre una terminal y ejecuta:

```bash
pip install flask
```

### Crear el archivo app_server.py

En tu computadora, crea un archivo llamado `app_server.py` con el siguiente contenido:

```python
#!/usr/bin/env python3
"""
Application Server para ChirpStack v4
Recibe eventos HTTP desde ChirpStack mediante webhook
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

def format_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_separator():
    print("─" * 80)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint que recibe eventos de ChirpStack"""
    
    # Obtener parámetro 'event' de la URL
    event_type = request.args.get('event', 'unknown')
    
    # Obtener el JSON del body
    data = request.get_json()
    
    print_separator()
    print(f"[{format_timestamp()}] 📡 EVENTO RECIBIDO: {event_type.upper()}")
    print_separator()
    
    # Mostrar toda la información según el tipo de evento
    if event_type == "up":
        display_uplink(data)
    elif event_type == "join":
        display_join(data)
    elif event_type == "ack":
        display_ack(data)
    elif event_type == "txack":
        display_txack(data)
    elif event_type == "error":
        display_error(data)
    else:
        print(json.dumps(data, indent=2))
    
    print()
    
    # Responder OK a ChirpStack
    return jsonify({"status": "ok"}), 200


def display_uplink(data):
    """Muestra evento de uplink (datos recibidos del dispositivo)"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Application:    {device_info.get('applicationName', 'N/A')}")
    print(f"Tenant:         {device_info.get('tenantName', 'N/A')}")
    
    print(f"\nFPort:          {data.get('fPort', 'N/A')}")
    print(f"Frame Counter:  {data.get('fCnt', 'N/A')}")
    print(f"Data Rate:      {data.get('dr', 'N/A')}")
    print(f"Device Address: {data.get('devAddr', 'N/A')}")
    
    # Payload en HEX
    if data.get('data'):
        print(f"\nPayload (Base64): {data.get('data')}")
        try:
            import base64
            decoded = base64.b64decode(data.get('data'))
            print(f"Payload (HEX):    {decoded.hex().upper()}")
        except:
            pass
    
    # Datos decodificados por el Codec
    if 'objectJson' in data and data['objectJson']:
        print(f"\n✓ Datos Decodificados:")
        try:
            decoded_data = json.loads(data['objectJson'])
            print(json.dumps(decoded_data, indent=2))
        except:
            print(data.get('objectJson'))
    
    # RX Info (información de recepción del gateway)
    if data.get('rxInfo'):
        print(f"\nGateway RX Info:")
        for i, rx in enumerate(data.get('rxInfo', []), 1):
            print(f"  Gateway {i}:")
            print(f"    - RSSI:       {rx.get('rssi', 'N/A')} dBm")
            print(f"    - SNR:        {rx.get('snr', 'N/A')}")
            if rx.get('location'):
                print(f"    - Latitude:   {rx['location'].get('latitude', 'N/A')}")
                print(f"    - Longitude:  {rx['location'].get('longitude', 'N/A')}")
    
    # TX Info (información de transmisión)
    if data.get('txInfo'):
        tx = data.get('txInfo', {})
        print(f"\nTX Info:")
        freq_mhz = float(tx.get('frequency', 0)) / 1e6
        print(f"  Frequency:      {freq_mhz:.1f} MHz")
        if tx.get('lora'):
            lora = tx['lora']
            print(f"  SF:             SF{lora.get('spreadingFactor', 'N/A')}")
            bw = float(lora.get('bandwidth', 0)) / 1000
            print(f"  Bandwidth:      {bw:.0f} kHz")
            print(f"  Code Rate:      {lora.get('codeRate', 'N/A')}")


def display_join(data):
    """Muestra evento de join (dispositivo se une a la red)"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Application:    {device_info.get('applicationName', 'N/A')}")
    print(f"DevAddr:        {data.get('devAddr', 'N/A')}")


def display_ack(data):
    """Muestra evento de ACK (confirmación)"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Frame Counter:  {data.get('fCnt', 'N/A')}")


def display_txack(data):
    """Muestra evento de TXACK (confirmación de transmisión)"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Frame Counter:  {data.get('fCnt', 'N/A')}")


def display_error(data):
    """Muestra evento de error"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Error:          {data.get('error', 'N/A')}")


if __name__ == "__main__":
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ChirpStack HTTP Integration Server" + " " * 24 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print("[INFO] Iniciando servidor en http://0.0.0.0:8000")
    print("[INFO] Webhook endpoint: http://0.0.0.0:8000/webhook")
    print("[INFO] Esperando eventos de ChirpStack...")
    print("[INFO] Presiona Ctrl+C para detener\n")
    
    # Ejecutar en puerto 8000, accesible desde la red local
    app.run(host='0.0.0.0', port=8000, debug=False)
```

Guarda este archivo en una carpeta accesible (ej: `~/IoT_Lab/app_server.py`).

---

## Sección 8: Ejecutar y Verificar

### Paso 1: Inicia el Application Server

Abre una terminal en el directorio donde guardaste `app_server.py` y ejecuta:

```bash
python app_server.py
```

Deberías ver:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                 ChirpStack HTTP Integration Server                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

[INFO] Iniciando servidor en http://0.0.0.0:8000
[INFO] Webhook endpoint: http://0.0.0.0:8000/webhook
[INFO] Esperando eventos de ChirpStack...
[INFO] Presiona Ctrl+C para detener
```

El servidor está corriendo y esperando eventos.

### Paso 2: Verifica que los datos llegan

Cuando tu dispositivo TTGO ( el ESP32 con LoRa WAN) envíe datos (cada 30 segundos), deberías ver en la consola algo como:

```
────────────────────────────────────────────────────────────────────────────────
[2025-11-17 23:45:30] 📡 EVENTO RECIBIDO: UP
────────────────────────────────────────────────────────────────────────────────
Device Name:    TTGO ( el ESP32 con LoRa WAN)-dummy-001
DevEUI:         3098f6bdb525853e
Application:    picaro_1
Tenant:         picaro-desk-lab

FPort:          1
Frame Counter:  15
Data Rate:      3
Device Address: 017f8eff

Payload (Base64): DzkzocJGY7wF3AgW

✓ Datos Decodificados:
{
  "latitude": 25.540701,
  "longitude": -103.557434,
  "altitude": 1500,
  "temperature": 20.7,
  "gps_valid": true,
  "payload_hex": "0F5DE1A1F79AB1A105DC0952"
}

Gateway RX Info:
  Gateway 1:
    - RSSI:       -18 dBm
    - SNR:        13.25
    - Latitude:   25.54
    - Longitude:  -103.54

TX Info:
  Frequency:      902.3 MHz
  SF:             SF7
  Bandwidth:      125 kHz
  Code Rate:      4/5
```

**¡Si ves esto, todo está funcionando correctamente!**  

---

## Conclusión y Troubleshooting

### ¿Qué lograste?

Has integrado exitosamente:
-   ChirpStack como tu **Network Server LoRaWAN**
-   Un **Device Profile con Codec** que decodifica payloads
-   Un **dispositivo TTGO ( el ESP32 con LoRa WAN)** registrado y enviando datos
-   Un **webhook HTTP** que transmite eventos en tiempo real
-   Un **Application Server personalizado** que recibe y procesa eventos

Esta arquitectura es la base para:
- Almacenar datos en bases de datos
- Crear dashboards de visualización
- Implementar alertas y automatizaciones
- Integrar con sistemas externos

### Troubleshooting: Problemas Comunes

#### Problema 1: El dispositivo no hace JOIN

**Síntomas:** El dispositivo no aparece como "Active" en ChirpStack después de flashear

**Soluciones:**
- Verifica que las credenciales (DevEUI, AppKey) en el sketch coincidan exactamente con ChirpStack
- Asegúrate que el Device Profile tiene **OTAA habilitado**
- Verifica que el gateway esté online y correctamente configurado
- Revisa los logs de ChirpStack buscando errores de autenticación

#### Problema 2: El webhook no recibe eventos

**Síntomas:** El Application Server está corriendo pero no ve eventos de ChirpStack

**Soluciones:**
- Verifica que la URL del webhook en ChirpStack sea exacta: `http://192.168.18.62:8000/webhook`
- Asegúrate que no hay firewall bloqueando el puerto 8000
- Revisa que ChirpStack pueda alcanzar tu máquina (prueba desde otra máquina: `curl http://192.168.18.62:8000/webhook`)
- En los logs de ChirpStack (Events), deberías ver intentos fallidos si hay un problema de conectividad

#### Problema 3: Los datos no se decodifican

**Síntomas:** Ves el evento UP pero el campo `objectJson` está vacío

**Soluciones:**
- Verifica que el Codec JavaScript esté correctamente guardado en el Device Profile
- Asegúrate que el `fPort` en el sketch sea 1 (línea `fPort: 1`)
- Verifica que el payload tenga exactamente 12 bytes
- Prueba el Codec directamente en la UI de ChirpStack (hay una sección de test)

#### Problema 4: Connection refused al conectar a ChirpStack

**Síntomas:** No puedes acceder a `http://192.168.18.62:8080`

**Soluciones:**
- Verifica que estés conectado a la misma red WiFi que ChirpStack
- Comprueba que ChirpStack esté corriendo (docker ps si usas Docker)
- Intenta con la dirección IP local en lugar del hostname

---

### Próximos Pasos

Ahora que tu Application Server recibe eventos en tiempo real, puedes:

1. **Almacenar en base de datos:** Agregar MongoDB o PostgreSQL
2. **Crear un Dashboard:** Visualizar datos con Grafana o React
3. **Implementar alertas:** Enviar notificaciones cuando ciertos umbrales se alcancen
4. **Procesar datos:** Aplicar filtros, agregaciones o machine learning
5. **Integrar con otras plataformas:** IFTTT, Telegram, email, etc.

---

**¿Necesitas ayuda con alguno de estos pasos?** Contacta a tu instructor. 🚀


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)