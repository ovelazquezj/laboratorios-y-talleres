# Laboratorio 2 – Integración Node-RED ↔ ChirpStack v4

**Curso:** Internet de las Cosas
**Duración:** 2 sesiones (4 h)
**Objetivo:** Simular uplinks LoRaWAN crudos desde Node-RED hacia ChirpStack v4 y ver su decodificación con un codec JavaScript.

---

## Parte 1 – Arquitectura y objetivos

### Diagrama de flujo

```
[Node-RED (Emisor uplink crudo)] → [MQTT Broker Mosquitto] → [ChirpStack Gateway Bridge v4] → [Network Server + AS] → [Codec JS → MQTT → Node-RED (Receptor)]
```

**Objetivos:**

1. Enviar uplinks crudos Base64 al topic de gateway.
2. ChirpStack los procesará y ejecutará el codec JS.
3. Recibir el evento decodificado en Node-RED.

---

## Parte 2 – Preparar el entorno

Ya tienes los contenedores de **Mosquitto**, **Node-RED** y **ChirpStack v4** en la misma red Docker (`bridge`).
Verifica que el broker MQTT es accesible como `mosquitto:1883` desde los otros contenedores.

```bash
docker ps | grep mosquitto
docker ps | grep chirpstack
```

---

## Parte 3 – Configurar ChirpStack (v4)

1. Accede a la UI → [http://localhost:8080](http://localhost:8080)
2. Crea un **Application** (`Laboratorio-IoT`).
3. Crea un **Device Profile** → Región: US915 → **Custom Codec JS**.
4. Pega el siguiente codec en la sección **Codec Functions** → **Decode uplink**.

```javascript
// ChirpStack v4 Codec – 6 bytes [Temp_H, Temp_L, Hum, Pres_H, Pres_L, Bat]
function decodeUplink(input) {
  const bytes = input.bytes || [];
  if (bytes.length < 6) {
    return { errors: ["Payload demasiado corto"], data: {} };
  }
  let temp_raw = (bytes[0] << 8) | bytes[1];
  if (temp_raw > 32767) temp_raw -= 65536;
  const temperatura = temp_raw / 100.0;
  const humedad = bytes[2];
  const presion = (bytes[3] << 8) | bytes[4];
  const voltaje = (bytes[5] + 200) / 100.0;
  let alerta = voltaje < 3.0 ? "CRÍTICO" : "OK";
  return {
    data: { temperatura, humedad, presion, voltaje, alerta }
  };
}
```

5. Crea un **Device** con DevEUI ficticio `70B3D57ED005ABCD` y asigna el perfil anterior.

---

## Parte 4 – Importar el Flow Node-RED

1. Abre Node-RED → [http://localhost:1880](http://localhost:1880)
2. Menú ☰ → **Import** → pega el JSON proporcionado (`lab2_flow_uplinks.json`).
3. Clic en **Import** → **Deploy**.

El flow crea:

* **Pestaña Emisor:** simula uplinks crudos.
* **Pestaña Receptor:** escucha uplinks decodificados del Application Server.

### Flow Node-RED JSON

Guarda como `lab2_flow_uplinks.json`.

```json
[
  {
    "id": "lab2-flow",
    "type": "tab",
    "label": "Lab2_Uplinks_ChirpStack",
    "disabled": false,
    "info": ""
  },
  {
    "id": "inject-uplink",
    "type": "inject",
    "z": "lab2-flow",
    "name": "🚀 Enviar Uplink crudo",
    "props": [],
    "repeat": "",
    "once": false,
    "topic": "",
    "x": 150,
    "y": 100,
    "wires": [["fn-build-payload"]]
  },
  {
    "id": "fn-build-payload",
    "type": "function",
    "z": "lab2-flow",
    "name": "Construir payload gateway",
    "func": "// 6 bytes ejemplo: 0A1F3C03D60A7\nlet hexPayload = \"0A1F3C03D60A7\";\nlet base64Payload = Buffer.from(hexPayload, \"hex\").toString(\"base64\");\nmsg.payload = {\n  gatewayId: \"0016c001f153a14c\",\n  rxInfo: [{ rssi: -57, snr: 5.5 }],\n  phyPayload: base64Payload\n};\nreturn msg;",
    "outputs": 1,
    "noerr": 0,
    "x": 410,
    "y": 100,
    "wires": [["mqtt-out-chirpstack", "debug-out"]]
  },
  {
    "id": "mqtt-out-chirpstack",
    "type": "mqtt out",
    "z": "lab2-flow",
    "name": "MQTT → ChirpStack gateway",
    "topic": "us915/gateway/0016c001f153a14c/event/up",
    "qos": "0",
    "retain": "false",
    "respTopic": "",
    "contentType": "",
    "userProps": "",
    "correl": "",
    "expiry": "",
    "broker": "mqtt-local",
    "x": 730,
    "y": 100,
    "wires": []
  },
  {
    "id": "mqtt-in-decoded",
    "type": "mqtt in",
    "z": "lab2-flow",
    "name": "MQTT ← ChirpStack decoded",
    "topic": "application/1/device/70B3D57ED005ABCD/event/up",
    "qos": "0",
    "datatype": "auto",
    "broker": "mqtt-local",
    "x": 250,
    "y": 220,
    "wires": [["debug-in-decoded"]]
  },
  {
    "id": "debug-in-decoded",
    "type": "debug",
    "z": "lab2-flow",
    "name": "Debug uplink decodificado",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": false,
    "complete": "payload",
    "targetType": "msg",
    "x": 600,
    "y": 220,
    "wires": []
  },
  {
    "id": "debug-out",
    "type": "debug",
    "z": "lab2-flow",
    "name": "Debug uplink crudo",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": false,
    "complete": "payload",
    "targetType": "msg",
    "x": 730,
    "y": 160,
    "wires": []
  },
  {
    "id": "mqtt-local",
    "type": "mqtt-broker",
    "name": "Mosquitto Local",
    "broker": "mosquitto",
    "port": "1883",
    "clientid": "",
    "usetls": false,
    "protocolVersion": "4",
    "keepalive": "60",
    "cleansession": true,
    "birthTopic": "",
    "birthQos": "0",
    "birthRetain": "false",
    "birthPayload": "",
    "closeTopic": "",
    "closeQos": "0",
    "closeRetain": "false",
    "closePayload": "",
    "willTopic": "",
    "willQos": "0",
    "willRetain": "false",
    "willPayload": ""
  }
]
```

---

## Parte 5 – Flujo Emisor (Node-RED)

El nodo `inject` genera payload hex → nodo `function` construye el JSON del gateway → `mqtt out` publica a:

```
us915/gateway/0016c001f153a14c/event/up
```

**Ejemplo de payload JSON emitido:**

```json
{
 "gatewayId": "0016c001f153a14c",
 "rxInfo": [{ "rssi": -57, "snr": 5.5 }],
 "phyPayload": "Ch8DBQAAUQ=="
}
```

---

## Parte 6 – Flujo Receptor (Node-RED)

Suscríbete al topic:

```
application/1/device/70B3D57ED005ABCD/event/up
```

y muestra el mensaje en el panel Debug.
Deberías ver:

```json
{
 "applicationID":"1",
 "deviceName":"test",
 "devEui":"70B3D57ED005ABCD",
 "data":{"temperatura":25.91,"humedad":60,"presion":982,"voltaje":3.67,"alerta":"OK"}
}
```

---

## Parte 7 – Casos de prueba

| Caso | Payload (hex) | Temperatura | Humedad | Presión  | Voltaje       |
| ---- | ------------- | ----------- | ------- | -------- | ------------- |
| 1    | 0A1F3C03D60A7 | 25.91 °C    | 60 %    | 982 hPa  | 3.67 V        |
| 2    | 09C43203E8032 | 25.00 °C    | 50 %    | 1000 hPa | 2.50 V (Baja) |
| 3    | 0FA03203E80B4 | 40.00 °C    | 50 %    | 1000 hPa | 3.80 V        |

---

## Parte 8 – Evaluación y Entrega

### Entregables

1. Captura de pantalla de Node-RED mostrando uplink recibido y decodificado.
2. Export del flow Node-RED (.json).
3. Captura del codec JS dentro de ChirpStack.
4. Breve informe PDF explicando flujo de datos (MQTT topics y payloads).

### Rúbrica de evaluación

| Criterio                                   | Peso | Indicadores                                                             |
| ------------------------------------------ | ---- | ----------------------------------------------------------------------- |
| **Funcionamiento técnico**                 | 40 % | Uplink recibido en ChirpStack y codec decodifica correctamente.         |
| **Integración MQTT Node-RED ↔ ChirpStack** | 30 % | Publicación en topic de gateway y recepción en application confirmadas. |
| **Documentación y claridad en el flow**    | 20 % | Nodos nombrados, comentarios, estructura limpia.                        |
| **Análisis de casos de prueba**            | 10 % | Resultados coherentes y reflexión sobre alerta de batería.              |

**Total = 100 %**

---

## Parte 9 – Troubleshooting rápido

| Síntoma                          | Posible causa             | Solución                                                                              |
| -------------------------------- | ------------------------- | ------------------------------------------------------------------------------------- |
| ChirpStack no recibe uplinks     | Topic incorrecto          | Verifica prefijo `us915/gateway/.../event/up` en mqtt out.                            |
| Codec no ejecuta                 | Perfil sin codec asociado | Abre Device Profile → Codec → Custom JS.                                              |
| Node-RED no muestra decodificado | Topic mal suscrito        | Usa `application/1/device/.../event/up`.                                              |
| Error de formato Base64          | Payload mal construido    | Asegura que los 6 bytes se codifican con `Buffer.from(hex,"hex").toString("base64")`. |

---

## Parte 10 – Limpieza final

```bash
docker compose stop
docker compose down
```

✅ Con esto habrás cerrado el circuito completo Node-RED → ChirpStack → Node-RED.


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)