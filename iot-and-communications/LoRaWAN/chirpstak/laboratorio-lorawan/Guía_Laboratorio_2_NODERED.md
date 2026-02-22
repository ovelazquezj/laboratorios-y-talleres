# Laboratorio: Decodificación de Payloads LoRaWAN con Node-RED y Docker

**Curso:** Internet de las Cosas  
**Duración:** 2 sesiones (4 horas)  
**Objetivo:** Aprender a crear, simular y decodificar uplinks LoRaWAN usando Node-RED con Docker

---

## ¿Qué vamos a hacer?

En este laboratorio crearás dos flujos de Node-RED:
1. **Flujo EMISOR:** Simula dispositivos LoRaWAN enviando datos hexadecimales
2. **Flujo RECEPTOR:** Decodifica los datos y valida su formato

Todo funcionará en tu computadora usando **Docker**, sin necesidad de hardware físico.

---

## Parte 1: Entendiendo Docker y Por Qué lo Usamos

### ¿Qué es Docker?

Docker es una herramienta que te permite ejecutar aplicaciones en "contenedores". Piensa en un contenedor como una caja aislada que tiene todo lo necesario para que una aplicación funcione.

### ¿Por qué usar Docker en este laboratorio?

**Sin Docker:**
```bash
# Tendrías que instalar manualmente:
sudo apt install nodejs npm    # Node.js para Node-RED
sudo npm install -g node-red   # Node-RED (puede tardar 10 min)
sudo apt install mosquitto     # Broker MQTT
# Configurar puertos, permisos, paths...
# Si algo falla, difícil de limpiar
```

**Con Docker:**
```bash
# Un solo comando:
docker-compose up -d
# Ya está todo listo
```

**Ventajas para aprendizaje:**
- ✅ Todos tienen el mismo ambiente (elimina "en mi máquina sí funciona")
- ✅ Si rompes algo: `docker-compose down -v` y empiezas de nuevo
- ✅ No ensucia tu sistema operativo
- ✅ Aprenderás Docker (habilidad muy demandada en IoT)

---

## Parte 2: Preparar el Ambiente del Laboratorio

### Paso 1: Crear la estructura de directorios

**¿Por qué crear directorios?**
Los contenedores de Docker son "efímeros" (se borran al detenerse). Para que Mosquitto guarde datos de forma persistente, necesitamos **volúmenes** que mapeen directorios de tu computadora al contenedor.

```bash
# Crear directorio del laboratorio
mkdir ~/laboratorio-lorawan
cd ~/laboratorio-lorawan

# Crear estructura para Mosquitto
mkdir -p mosquitto/config    # Configuración del broker
mkdir -p mosquitto/data      # Datos persistentes (mensajes guardados)
mkdir -p mosquitto/log       # Logs del broker

# Ver la estructura creada
tree .
# o si no tienes tree:
ls -R
```

**Resultado esperado:**
```
laboratorio-lorawan/
└── mosquitto/
    ├── config/
    ├── data/
    └── log/
```

### Paso 2: Copiar los archivos del laboratorio

**Archivos necesarios:**
1. `docker-compose.yml` - Configura qué contenedores usar
2. `mosquitto.conf` - Configura el broker MQTT
3. `flow_completo_lorawan.json` - Flujos de Node-RED
4. `ejemplos_payloads_lorawan.md` - Casos de prueba

```bash
# Copiar mosquitto.conf al directorio de configuración
cp mosquitto.conf mosquitto/config/

# Verificar que se copió
cat mosquitto/config/mosquitto.conf
```

### Paso 3: Entender el docker-compose.yml

Abre `docker-compose.yml` y analicemos QUÉ hace cada parte:

```yaml
version: '3.8'

services:
  # SERVICIO 1: Broker MQTT Mosquitto
  mosquitto:
    image: eclipse-mosquitto:2.0     # Imagen oficial de Mosquitto
    container_name: laboratorio-mosquitto
    restart: unless-stopped           # Si se cae, reinicia automáticamente
    ports:
      - "1885:1883"  # Puerto MQTT (izq=tu PC, der=contenedor)
      - "9001:9001"  # Puerto WebSocket
    volumes:
      # Mapear directorios locales → contenedor
      - ./mosquitto/config:/mosquitto/config    # Configuración
      - ./mosquitto/data:/mosquitto/data        # Datos
      - ./mosquitto/log:/mosquitto/log          # Logs
    networks:
      - lorawan-lab  # Red privada entre contenedores

  # SERVICIO 2: Node-RED
  nodered:
    image: nodered/node-red:latest   # Imagen oficial de Node-RED
    container_name: laboratorio-nodered
    restart: unless-stopped
    ports:
      - "1880:1880"  # Puerto de la interfaz web
    environment:
      - TZ=America/Mexico_City                  # Zona horaria
      - NODE_OPTIONS=--max_old_space_size=4096  # Más memoria
    volumes:
      - ./nodered-data:/data  # Guardar flujos y configuración
    networks:
      - lorawan-lab
    depends_on:
      - mosquitto  # Esperar a que Mosquitto inicie primero

networks:
  lorawan-lab:
    driver: bridge  # Red tipo bridge (los contenedores se ven entre sí)
```

**Conceptos clave:**
- **Imagen:** Plantilla para crear el contenedor (como un ISO de sistema operativo)
- **Contenedor:** Instancia ejecutándose de una imagen
- **Puerto:** `1880:1880` significa "el puerto 1880 de mi PC apunta al 1880 del contenedor"
- **Volumen:** Carpeta compartida entre tu PC y el contenedor
- **Red:** Permite que Mosquitto y Node-RED se comuniquen como `mosquitto:1885`

---

## Parte 4: Iniciar el Laboratorio

### Paso 1: Levantar los contenedores

```bash
# Desde el directorio laboratorio-lorawan/
docker-compose up -d
```

**¿Qué hace este comando?**
- `up`: Crear e iniciar contenedores
- `-d`: Detached (segundo plano, no bloquea la terminal)

**Primera vez (descarga imágenes):**
```
Pulling mosquitto ... done
Pulling nodered ... done
Creating laboratorio-mosquitto ... done
Creating laboratorio-nodered ... done
```

Esto puede tardar 2-3 minutos la primera vez (descarga ~200 MB).

**Siguientes veces (ya descargadas):**
```
Starting laboratorio-mosquitto ... done
Starting laboratorio-nodered ... done
```

Tarda solo 5 segundos.

### Paso 2: Verificar que los contenedores estén corriendo

```bash
docker-compose ps
```

**Salida esperada:**
```
NAME                    STATUS    PORTS
laboratorio-mosquitto   Up        0.0.0.0:1885->1883/tcp, 0.0.0.0:9001->9001/tcp
laboratorio-nodered     Up        0.0.0.0:1880->1880/tcp
```

Si alguno dice "Exited", ver logs:
```bash
docker-compose logs mosquitto
docker-compose logs nodered
```

### Paso 3: Ver logs en tiempo real

```bash
# Ver logs de ambos servicios
docker-compose logs -f

# Solo Mosquitto
docker-compose logs -f mosquitto

# Solo Node-RED
docker-compose logs -f nodered

# Salir: Ctrl+C
```

---

## Parte 5: Importar los Flujos en Node-RED

### Paso 1: Acceder a Node-RED

Abre tu navegador en: **http://localhost:1880**

Deberías ver la interfaz de Node-RED (fondo gris con paleta de nodos a la izquierda).

**Si no carga:**
```bash
# Ver logs de Node-RED
docker-compose logs nodered

# Verificar que el puerto no esté ocupado
sudo lsof -i :1880
```

### Paso 2: Importar el flujo completo

1. En Node-RED, clic en el menú **☰** (arriba derecha)
2. Seleccionar **Import**
3. Clic en **select a file to import**
4. Buscar y seleccionar `flow_completo_lorawan.json`
5. Clic en **Import**

Deberían aparecer **2 pestañas**:
- **EMISOR: Simulación de Uplinks LoRaWAN**
- **RECEPTOR: Decodificación de Payloads**

### Paso 3: Configurar la conexión MQTT

Los nodos MQTT ya vienen configurados para conectar a `mosquitto:1885` (nombre del contenedor en la red Docker).

**Verificar configuración:**
1. Doble clic en cualquier nodo `mqtt in` o `mqtt out`
2. Clic en el lápiz junto a "Mosquitto Local"
3. Verificar:
   - **Server:** `mosquitto` (NO `localhost`)
   - **Port:** `1885`
4. Clic en **Update** → **Done**

**¿Por qué "mosquitto" y no "localhost"?**
Dentro de la red Docker, los contenedores se ven por su nombre, no por IP. `mosquitto` es el nombre que le dimos en `docker-compose.yml`.

### Paso 4: Deploy (Desplegar)

Clic en el botón rojo **Deploy** (arriba derecha).

Los nodos MQTT deben mostrar un punto verde abajo con texto "connected".

---

## Parte 6: Probar el Sistema

### Paso 1: Abrir el panel Debug

Clic en el icono 🐛 (bug) en la barra derecha para abrir el panel de Debug.

### Paso 2: Generar un uplink de prueba

1. Ve a la pestaña **EMISOR**
2. Busca el nodo `🚀 Disparar Uplink`
3. Clic en el cuadrado azul a la izquierda del nodo

**¿Qué pasa?**
El nodo `inject` dispara el flujo → genera un payload hexadecimal → lo publica en MQTT

### Paso 3: Ver el uplink generado

En el panel Debug deberías ver algo como:

```json
{
  "devEUI": "70B3D57ED005ABCD",
  "fPort": 1,
  "fCnt": 1,
  "mensaje": "0A1F3C03D60A7",
  "valoresReales": {
    "temperatura": "25.91",
    "humedad": 60,
    "presion": 982,
    "voltaje": "3.67"
  },
  "rxInfo": {
    "rssi": -67,
    "snr": 8.3
  },
  "timestamp": 1699725600
}
```

### Paso 4: Ver el uplink decodificado

1. Ve a la pestaña **RECEPTOR**
2. En el panel Debug deberás ver la salida procesada:

```json
{
  "mensaje": "70B3D57ED005ABCD:1",
  "data": {
    "temperatura": 25.91,
    "humedad": 60,
    "presion": 982,
    "voltaje": 3.67
  },
  "estatus": "exito",
  "timestamp": 1699725600
}
```

✅ **¡Funciona!** Generaste y decodificaste tu primer uplink LoRaWAN.

---

## Parte 7: Entender el Formato del Payload

### ¿Por qué hexadecimal?

LoRaWAN tiene límites estrictos:
- **Máximo:** 51 bytes por mensaje (DR0, región EU868)
- **Más común:** 11-51 bytes

Enviar "temperatura=25.91" en texto ocupa 17 bytes.  
Enviarlo como `0A1F` ocupa solo 2 bytes. ¡8.5x más eficiente!

### Estructura del payload (6 bytes)

```
[Byte 0][Byte 1][Byte 2][Byte 3][Byte 4][Byte 5]
 Temp_H  Temp_L  Hum     Pres_H  Pres_L  Bat
```

**Ejemplo:** `0A 1F 3C 03 D6 A7`

### Decodificación paso a paso

#### Campo 1: Temperatura (2 bytes, int16, x100)

```
Hex: 0A 1F
Bin: 00001010 00011111
```

Convertir a decimal:
```javascript
temp_raw = (0x0A << 8) | 0x1F  // 0x0A1F = 2591
temperatura = temp_raw / 100.0  // 25.91°C
```

**¿Por qué multiplicar por 100?**
Para conservar 2 decimales sin usar float (que ocupa 4 bytes).

**¿Y si es negativo?**
```javascript
// Para -19.60°C
temp_raw = -1960
// En complemento a 2 (16 bits):
temp_raw = 65536 + (-1960) = 63576 = 0xF830

// Al decodificar:
if (temp_raw > 32767) {
    temp_raw = temp_raw - 65536  // -1960
}
temperatura = temp_raw / 100.0  // -19.60°C
```

#### Campo 2: Humedad (1 byte, uint8)

```
Hex: 3C
Dec: 60
```

Simple conversión a decimal = 60%

#### Campo 3: Presión (2 bytes, uint16)

```
Hex: 03 D6
Dec: (0x03 << 8) | 0xD6 = 982 hPa
```

#### Campo 4: Voltaje batería (1 byte, uint8)

```
Hex: A7
Dec: 167
Voltaje = (167 + 200) / 100.0 = 3.67V
```

**¿Por qué sumar 200?**
Offset para comprimir el rango 2.5-4.2V en 0-255.

---

## Parte 8: Modificar el Decodificador

### Ejercicio 1: Agregar validación de batería baja

Edita el nodo `🔓 Decodificar Payload LoRaWAN`:

```javascript
// Después de decodificar el voltaje
const voltaje = decodificarVoltaje(bytes[5]);

// NUEVO: Agregar validación de batería
if (voltaje < 3.0) {
    errores.push(`⚠️ BATERÍA BAJA: ${voltaje}V`);
}

// Agregar campo de alerta
msg.payload = {
    // ... campos existentes
    alerta_bateria: voltaje < 3.0 ? "CRÍTICO" : "OK"
};
```

**Deploy** y prueba con un payload que tenga batería baja:
```
Hex: 09C43203E8032
Voltaje: 2.50V
```

---

## Parte 9: Probar con MQTT desde la Terminal

**1. Descargar Mosquitto oficial para Windows**

Ve al sitio oficial de Eclipse Mosquitto:
👉 https://mosquitto.org/download

En la sección Windows, descarga el instalador más reciente:
mosquitto-2.x.x-install-windows-x64.exe
(por ejemplo: mosquitto-2.0.18-install-windows-x64.exe)
Ejecútalo con permisos de administrador.
Durante la instalación:

Marca la casilla “Install command line utilities” ✅
(esto instala mosquitto_pub.exe y mosquitto_sub.exe).

Desmarca “Run Mosquitto as a service” si no quieres que se inicie automáticamente al arrancar Windows.

⚙️ 2. Verificar instalación

Después de instalar, abre PowerShell o CMD y ejecuta:
```bash
cd "C:\Program Files\mosquitto"
.\mosquitto_sub.exe -h test.mosquitto.org -t "#" -v
```

Si ves tráfico (mensajes MQTT públicos), está funcionando correctamente.

3. Agregar Mosquitto al PATH (para usarlo desde cualquier carpeta)
Presiona Win + R, escribe:
```bash
sysdm.cpl
```

→ pestaña Opciones avanzadas → Variables de entorno.
En la variable del sistema Path, agrega:
```bash
C:\Program Files\mosquitto\
```

Cierra y vuelve a abrir PowerShell, luego prueba:
```bash
mosquitto_sub -h test.mosquitto.org -t "#" -v
```

### Suscribirse a todos los mensajes

```bash
# Desde tu PC (fuera de Docker)
mosquitto_sub -h localhost -p 1885 -t '#' -v
```

**¿Qué hace?**
- `mosquitto_sub`: Cliente MQTT para suscribirse
- `-h localhost`: Conectar al broker en localhost
- `-p 1885`: Puerto MQTT
- `-t '#'`: Topic (# = wildcard, todos los topics)
- `-v`: Verbose (mostrar topic + mensaje)

Deberías ver:
```
lorawan/uplink/raw {"devEUI":"70B3D57ED005ABCD",...}
```

### Publicar un uplink manualmente

```bash
mosquitto_pub -h localhost -p 1885 -t "lorawan/uplink/raw" -m '{
  "devEUI": "70B3D57ED005ABCD",
  "fPort": 1,
  "fCnt": 99,
  "mensaje": "0FA03203E80B4",
  "timestamp": 1699725600
}'
```

En Node-RED (pestaña RECEPTOR) verás el mensaje decodificado.

---

## Parte 10: Casos de Prueba

Usa los ejemplos del archivo `ejemplos_payloads_lorawan.md`:

### Caso 1: Temperatura alta
```json
{
  "mensaje": "0FA03203E80B4",
  "esperado": {
    "temperatura": 40.00,
    "humedad": 50,
    "presion": 1000,
    "voltaje": 3.80
  }
}
```

### Caso 2: Error - Humedad > 100%
```json
{
  "mensaje": "09C4FF03E80B4",
  "esperado": "error",
  "error": "Humedad fuera de rango: 255%"
}
```

---

## Parte 11: Comandos Docker Útiles

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar todo
docker-compose restart

# Detener (sin borrar datos)
docker-compose stop

# Iniciar de nuevo
docker-compose start

# Detener y eliminar contenedores (datos permanecen)
docker-compose down

# RESET COMPLETO (elimina TODO, incluyendo datos)
docker-compose down -v

# Ver recursos usados
docker stats

# Entrar a un contenedor
docker exec -it laboratorio-nodered /bin/bash
docker exec -it laboratorio-mosquitto /bin/sh
```

---

## Parte 12: Troubleshooting

### Problema: Puerto 1880 ocupado

```bash
# Ver qué está usando el puerto
sudo lsof -i :1880

# Opción 1: Matar el proceso
kill -9 [PID]

# Opción 2: Cambiar puerto en docker-compose.yml
ports:
  - "1881:1880"  # Ahora usa http://localhost:1881
```

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs [servicio]

# Recrear contenedor
docker-compose up -d --force-recreate
```

### Problema: Node-RED no guarda flujos

```bash
# Verificar permisos del volumen
docker exec -it laboratorio-nodered ls -la /data

# Arreglar permisos
docker-compose down
sudo chown -R 1000:1000 nodered-data
docker-compose up -d
```

---

## Evaluación

**Entregables:**
1. Flujos de Node-RED exportados (JSON)
2. Captura de pantalla mostrando uplink decodificado exitosamente
3. Al menos 3 payloads de prueba diferentes

**Criterios:**
- Funcionamiento correcto (40%)
- Manejo de errores (30%)
- Documentación en el código (30%)

---

## Limpieza Final

Al terminar el laboratorio:

```bash
# Opción 1: Detener pero guardar datos
docker-compose stop

# Opción 2: Eliminar todo
docker-compose down

# Opción 3: RESET completo (cuidado!)
docker-compose down -v
rm -rf nodered-data mosquitto/data mosquitto/log
```

---

**Elaborado por:** Lab IoT - Universidad de Alcalá  
**Última actualización:** 12 de noviembre de 2025

---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)