# LABORATORIO: API REST ChirpStack v4
## Consumo de Datos con CURL y jq

Instituto Tecnológico Nacional
Campus Pabellón de Arteaga
9º Semestre - Mecatrónica y TICs

---

## TABLA DE CONTENIDOS

1. [Objetivos de Aprendizaje](#objetivos-de-aprendizaje)
2. [Información del Laboratorio](#información-del-laboratorio)
3. [PARTE 1: Generar tu API Token](#parte-1-generar-tu-api-token)
4. [PARTE 2: Estructura Jerárquica de ChirpStack](#parte-2-estructura-jerárquica-de-chirpstack)
5. [PARTE 3: Exploración Detallada de Datos](#parte-3-exploración-detallada-de-datos)
6. [PARTE 4: Script Integrado](#parte-4-script-integrado)
7. [Evaluación: Laboratorio Práctico](#evaluación-laboratorio-práctico)
8. [Entrega del Laboratorio](#entrega-del-laboratorio)

---

## OBJETIVOS DE APRENDIZAJE

Al finalizar este laboratorio, serás capaz de:

1. Generar y utilizar API tokens para autenticarse en ChirpStack
2. Consumir endpoints REST usando CURL desde terminal
3. Procesar datos JSON con jq para extraer información específica
4. Consultar información de gateways, aplicaciones y dispositivos LoRaWAN
5. Obtener datos de sensores desde dispositivos específicos
6. Comprender la estructura jerárquica de ChirpStack
7. Aplicar estos conceptos a tu aplicación "monitoreo"

---

## INFORMACIÓN DEL LABORATORIO

### Servidor ChirpStack

| Parámetro | Valor |
|-----------|-------|
| Dirección IP | 192.168.18.62 |
| Puerto UI | 8080 |
| Puerto API REST | 8090 |
| URL UI | http://192.168.18.62:8080 |
| URL API REST | http://192.168.18.62:8090 |
| Swagger UI | http://192.168.18.62:8090/api/ |
| Credenciales | admin / admin |

### Herramientas Necesarias

- Terminal Linux o WSL en Windows
- CURL (generalmente preinstalado)
- jq (herramienta para procesar JSON)
- Navegador web

### Requisitos Previos

- Usuario registrado en ChirpStack
- Aplicación LoRaWAN creada (nombre: 'monitoreo')
- Al menos un dispositivo registrado en esa aplicación
- Conocimiento básico de terminal bash

---

## PARTE 1: GENERAR TU API TOKEN

### Paso 1: Acceder a la UI de ChirpStack

1. Abre tu navegador en: http://192.168.18.62:8080
2. Inicia sesión con usuario: admin, contraseña: admin

### Paso 2: Navegar a API Keys

1. En la esquina superior derecha, haz clic en el icono de usuario
2. Selecciona "API Keys"

### Paso 3: Crear Nueva Clave API

1. Haz clic en "Create"
2. Nombre: "Lab-CURL-Token"
3. Haz clic en "Create"

### Paso 4: Copiar tu Token

El token se mostrará una sola vez. Cópialo inmediatamente y guárdalo en variables de terminal:

```bash
export CHIRPSTACK_TOKEN="tu_token_aqui"
export CHIRPSTACK_URL="http://192.168.18.62:8090"
```

### Paso 5: Verificar que funciona

```bash
curl -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  $CHIRPSTACK_URL/api/devices?limit=1
```

Lo que deberías ver: Respuesta JSON con datos de dispositivos

---

## PARTE 2: ESTRUCTURA JERÁRQUICA DE CHIRPSTACK

ChirpStack organiza los datos así:

```
TENANT (Tu organización)
  |
  +-- GATEWAY (Antena LoRaWAN)
  |      └─ Recibe uplinks de múltiples dispositivos
  |
  +-- APPLICATION: "monitoreo" (Tu aplicación)
  |      └─ DEVICE: "TTGO-01" (Nodo LoRaWAN)
  |      |    └─ Envía uplinks con payload
  |      |
  |      └─ DEVICE: "TTGO-02"
  |           └─ Envía uplinks con payload
  |
  +-- APPLICATION: "Otra App"
         └─ DEVICE
```

### Qué es cada nivel

TENANT: Tu organización/proyecto general

GATEWAY: Dispositivos físicos (antenas) que reciben datos LoRaWAN

APPLICATION: Agrupa dispositivos relacionados con un proyecto específico

DEVICE: Nodos LoRaWAN (TTGO, Heltec, etc.) que envían datos

---

## PARTE 3: EXPLORACIÓN DETALLADA DE DATOS

### Introducción a jq

jq procesa JSON desde terminal.

Instalar si no lo tienes:

```bash
sudo apt install jq
```

### 3.1: LISTAR TODOS LOS GATEWAYS

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/gateways?limit=100"
```

Información que obtienes:

| Campo | Descripción |
|-------|-------------|
| gateway_id | ID único |
| name | Nombre |
| location.latitude | Latitud |
| location.longitude | Longitud |
| location.altitude | Altitud |
| last_seen_at | Última conexión |

Con jq - Datos limpios:

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/gateways?limit=100" | \
  jq '.gateways[] | {
    id: .gateway_id,
    nombre: .name,
    ubicacion: "\(.location.latitude), \(.location.longitude)",
    ultima_conexion: .last_seen_at
  }'
```

Lo que deberías ver:
- Gateways registrados con su información
- Ubicación geográfica
- Último registro de actividad

### 3.2: LISTAR TODAS LAS APLICACIONES

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/applications?limit=100"
```

Información que obtienes:

| Campo | Descripción |
|-------|-------------|
| id | ID único |
| name | Nombre |
| description | Descripción |

Con jq:

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/applications?limit=100" | \
  jq '.applications[] | {
    id: .id,
    nombre: .name,
    descripcion: .description
  }'
```

Lo que deberías ver:
- Tu aplicación "monitoreo" listada
- Otras aplicaciones del sistema

### 3.3: LISTAR TODOS LOS DISPOSITIVOS

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices?limit=100"
```

Información que obtienes:

| Campo | Descripción |
|-------|-------------|
| dev_eui | EUI único |
| name | Nombre |
| application_id | Aplicación a la que pertenece |
| device_status.battery | Batería % |
| device_status.margin | Margen SNR |
| last_seen_at | Última conexión |

Con jq:

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices?limit=100" | \
  jq '.devices[] | {
    nombre: .name,
    eui: .dev_eui,
    app_id: .application_id,
    bateria: .device_status.battery,
    snr_margen: .device_status.margin
  }'
```

Lo que deberías ver:
- Todos tus dispositivos
- A qué aplicación pertenecen
- Estado de batería y señal

### 3.4: CONSULTAR UN DISPOSITIVO ESPECÍFICO

Paso 1: Identificar el EUI de tu dispositivo

De la lista anterior, selecciona uno de tu aplicación "monitoreo" y copia su dev_eui:

```bash
export DEVICE_EUI="70b3d5a69aaa0000"
```

Paso 2: Obtener detalles del dispositivo

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI" | jq '.device'
```

Paso 3: Obtener eventos (uplinks) del dispositivo

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI/events?limit=10&type=up"
```

Información que obtienes:

| Campo | Descripción |
|-------|-------------|
| received_at | Timestamp |
| f_port | Puerto LoRa |
| f_cnt | Contador de frames |
| data | Payload Base64 |
| rx_info[0].rssi | Intensidad señal |
| rx_info[0].lora_snr | Relación Señal/Ruido |
| tx_info.frequency | Frecuencia Hz |
| tx_info.lora_modulation_info.spreading_factor | Spreading Factor |

Con jq:

```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI/events?limit=10&type=up" | \
  jq '.events[] | {
    timestamp: .received_at,
    payload: .data,
    puerto: .f_port,
    contador: .f_cnt,
    rssi: .rx_info[0].rssi,
    snr: .rx_info[0].lora_snr,
    spreading_factor: .tx_info.lora_modulation_info.spreading_factor
  }'
```

Lo que deberías ver:
- Múltiples eventos (uplinks)
- Payload en Base64
- Métricas de calidad (RSSI, SNR)
- Parámetros LoRa (SF, frecuencia)

---

## PARTE 4: SCRIPT INTEGRADO

Guárdalo como 'chirpstack-explorer.sh':

```bash
#!/bin/bash

CHIRPSTACK_TOKEN="$1"
CHIRPSTACK_URL="http://192.168.18.62:8090"

if [ -z "$CHIRPSTACK_TOKEN" ]; then
  echo "Uso: ./chirpstack-explorer.sh <tu_api_token>"
  exit 1
fi

HEADER="Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN"

echo "=========================================="
echo "    EXPLORADOR DE CHIRPSTACK - API REST"
echo "=========================================="

echo ""
echo "========== GATEWAYS DISPONIBLES =========="
curl -s -H "$HEADER" "$CHIRPSTACK_URL/api/gateways?limit=100" | \
  jq '.gateways[] | "\(.gateway_id) | \(.name) | \(.last_seen_at)"' -r

echo ""
echo "========== APLICACIONES =========="
curl -s -H "$HEADER" "$CHIRPSTACK_URL/api/applications?limit=100" | \
  jq '.applications[] | "ID: \(.id) | Nombre: \(.name)"' -r

echo ""
echo "========== DISPOSITIVOS =========="
curl -s -H "$HEADER" "$CHIRPSTACK_URL/api/devices?limit=100" | \
  jq '.devices[] | "\(.name) | EUI: \(.dev_eui) | App: \(.application_id) | Bat: \(.device_status.battery // "N/A")%"' -r

echo ""
echo "Done!"
```

Usar:

```bash
chmod +x chirpstack-explorer.sh
./chirpstack-explorer.sh $CHIRPSTACK_TOKEN
```

---

## EVALUACIÓN: LABORATORIO PRÁCTICO

Debes ejecutar todos los comandos con TU aplicación 'monitoreo' y capturar evidencia.

### Actividad 1: Probar tu API Token

Ejecuta:
```bash
curl -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  $CHIRPSTACK_URL/api/devices?limit=1
```

Captura: Screenshot del resultado JSON

Preguntas:
- ¿Qué información recibiste?
- ¿Cuántos dispositivos se mostraron?

### Actividad 2: Listar Estructura Completa

Ejecuta y captura resultados de:

1. Gateways:
```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/gateways?limit=100" | jq '.gateways[] | {id: .gateway_id, nombre: .name}'
```

2. Aplicaciones:
```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/applications?limit=100" | jq '.applications[] | {id: .id, nombre: .name}'
```

3. Dispositivos:
```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices?limit=100" | jq '.devices[] | {nombre: .name, eui: .dev_eui}'
```

Preguntas:
- ¿Cuántos gateways hay?
- ¿Cuántas aplicaciones?
- ¿Cuántos dispositivos totales?

### Actividad 3: Consultar tu Aplicación "monitoreo"

Encuentra el ID de tu aplicación:
```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/applications?limit=100" | \
  jq '.applications[] | select(.name=="monitoreo")'
```

Copia el "id" y ejecuta:
```bash
export APP_ID="[copia_aqui_el_id]"
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/applications/$APP_ID/devices?limit=100" | jq '.'
```

Captura: Screenshot de dispositivos en "monitoreo"

Preguntas:
- ¿Cuántos dispositivos tiene tu aplicación?
- ¿Cuáles son sus nombres?

### Actividad 4: Dispositivo Específico y Eventos

Selecciona uno de tus dispositivos de "monitoreo" y copia su dev_eui

Obtener información:
```bash
export DEVICE_EUI="[copia_aqui_el_eui]"
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI" | \
  jq '.device | {nombre: .name, bateria: .device_status.battery}'
```

Obtener eventos:
```bash
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI/events?limit=5&type=up" | \
  jq '.events[] | {timestamp: .received_at, rssi: .rx_info[0].rssi, snr: .rx_info[0].lora_snr}'
```

Captura: Screenshots de ambos resultados

Preguntas:
- ¿Cuál es el RSSI del último evento?
- ¿Cuál es el SNR?
- ¿Cuántos uplinks registrados?

### Actividad 5: Análisis Crítico

Responde en documento:

1. ¿Qué información es más importante para monitorear un dispositivo? RSSI, SNR, Batería, o algo más? Justifica.

2. ¿Cómo usarías esta API para crear un sistema de alertas automático?

3. ¿Qué limitaciones encontraste usando CURL comparado con la UI gráfica?

4. ¿Cómo integrarías un script Python para consultar automáticamente cada X minutos?

5. ¿Para qué aplicaciones reales podrías usar esta API?

---

## ENTREGA DEL LABORATORIO

Entrega un PDF con:

1. Portada:
   - Tu nombre
   - Número de estudiante
   - Fecha
   - Título: Laboratorio API REST ChirpStack

2. Screenshots de Actividades 1-4

3. Respuestas a preguntas de Actividad 5

4. El script bash completo (chirpstack-explorer.sh)

5. Conclusiones personales

Formato:
- PDF o Word
- Nombre archivo: Lab_ChirpStack_[Apellido]_[Nombre].pdf
- Máximo 5 páginas

---

## GUÍA RÁPIDA

Recordar: Siempre puerto 8090 y header "Grpc-Metadata-Authorization"

```bash
# Generar variables
export CHIRPSTACK_TOKEN="tu_token"
export CHIRPSTACK_URL="http://192.168.18.62:8090"

# Probar conexión
curl -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  $CHIRPSTACK_URL/api/devices?limit=1

# Listar gateways
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/gateways?limit=100" | jq '.gateways[]'

# Listar aplicaciones
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/applications?limit=100" | jq '.applications[]'

# Listar dispositivos
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices?limit=100" | jq '.devices[]'

# Dispositivo específico
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI" | jq '.device'

# Eventos de dispositivo
curl -s -H "Grpc-Metadata-Authorization: $CHIRPSTACK_TOKEN" \
  "$CHIRPSTACK_URL/api/devices/$DEVICE_EUI/events?limit=10&type=up" | jq '.events[]'
```

---

Fin del Laboratorio

Instituto Tecnológico Nacional
Campus Pabellón de Arteaga


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)