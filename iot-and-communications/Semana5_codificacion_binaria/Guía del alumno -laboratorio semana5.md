# Laboratorio Semana 5 – Comunicaciones e IoT

**Codificación, protocolos y observación de tráfico en red local**

## Organización del laboratorio

| Día       | Actividad principal                                                 |
|-----------|---------------------------------------------------------------------|
| Miércoles | Levantar ChirpStack + configurar gateway físico en banda US915     |
| Viernes   | Publicar mensajes MQTT con MQTT Explorer y capturarlos con Wireshark |


## Requisitos previos
Antes de iniciar el laboratorio, asegúrate de tener lo siguiente:

1. **Docker y Docker Compose** instalados en tu sistema.
2. **Wireshark** instalado y funcional.
3. **Imágenes Docker ya descargadas**:
   ```bash
   docker pull chirpstack/chirpstack
   docker pull chirpstack/chirpstack-gateway-bridge
   docker pull nginx
   docker pull smeagolworms4/mqtt-explorer
   ```
4. **Gateway físico** para LoRaWAN (El maestro lo proveerá), configurado para la banda **US915** y con packet forwarder apuntando al puerto **1700** del host local.
5. **Anaconda y Jupyther Notebooks** instalado y listo para usar el notebook del laboratorio.

# Día 1 – Miércoles: Instalar y levantar ChirpStack con gateway

### Paso 1: Clonar el repositorio oficial de ChirpStack
```bash
git clone https://github.com/chirpstack/chirpstack-docker.git
cd chirpstack-docker
```

### Paso 2: Configurar región en archivo `.env`
Abre el archivo `.env` y edita esta línea:
```env
NETWORK_SERVER__BAND__NAME=US915
```
Guarda el archivo.

### Paso 3: Levantar ChirpStack con Docker Compose
```bash
docker-compose up -d
```
Este comando iniciará los servicios necesarios (PostgreSQL, Redis, Gateway Bridge, LNS, etc.).

### Paso 4: Acceder a la interfaz web de ChirpStack
Abre tu navegador y entra a:
```
http://localhost:8080
```
Credenciales por defecto:
- Usuario: `admin`
- Contraseña: `admin`

### Paso 5: Registrar tu gateway en ChirpStack
1. En el menú izquierdo, ve a **Gateways > Add Gateway**.
2. Llena los campos:
   - Gateway ID (debe coincidir con el EUI real del equipo físico).
   - Nombre descriptivo.
   - Region: US915.
   - Server: `mqtt://mosquitto:1883` (valor por defecto).

### Paso 6: Verificar conexión del gateway
- Asegúrate de que el **packet forwarder** del gateway esté apuntando a:
  ```
  UDP: IP del host local, puerto 1700
  ```
- En la interfaz de ChirpStack, debe aparecer como "Last seen: just now".

### ✔️ Verifica
```bash
docker ps
```
Confirma que los servicios estén activos.

---

# Día 2 – Viernes: Publicar mensajes MQTT y analizarlos con Wireshark

En esta actividad vamos a usar **MQTT Explorer** (ejecutándose en contenedor) para publicar mensajes tipo MQTT en nuestra red local. La idea es que puedas:

- Ver cómo se construyen los paquetes MQTT.
- Observarlos en Wireshark en tiempo real.
- Comparar su estructura con otros protocolos.

### Paso 1: Crear carpeta de trabajo para MQTT Explorer
```bash
mkdir ~/mqtt-lab && cd ~/mqtt-lab
```

### Paso 2: Crear archivo `docker-compose.yml` para MQTT Explorer
Dentro de la carpeta `~/mqtt-lab`, crea un archivo llamado `docker-compose.yml` con el siguiente contenido:

```yaml
version: '3'
services:
  mqtt-explorer:
    image: smeagolworms4/mqtt-explorer
    container_name: mqtt-explorer
    ports:
      - "9001:9001"
    environment:
      - HTTP_PORT=9001
    volumes:
      - ./config:/mqtt-explorer/config
```

### Paso 3: Levantar el contenedor de MQTT Explorer
```bash
docker-compose up -d
```
Esto descargará (si es necesario) y levantará el contenedor de MQTT Explorer.

### Paso 4: Acceder a MQTT Explorer
Abre tu navegador web y entra a:
```
http://localhost:9001
```

Deberías ver la interfaz de conexión de MQTT Explorer.

### Paso 5: Conectarse a un broker MQTT de prueba
Vamos a usar un broker público solo con fines de visualización. En la interfaz de MQTT Explorer:

1. Haz clic en **New Connection**.
2. Llena los campos:
   - **Name:** Prueba MQTT
   - **Host:** `broker.hivemq.com`
   - **Port:** `1883`
   - **Client ID:** TuNombreAlumno
3. Clic en **Connect**.

### Paso 6: Publicar un mensaje MQTT
Una vez conectado:

1. En el menú lateral izquierdo, haz clic en **Publish Message**.
2. Llena los siguientes campos:
   - **Topic:** `iot/test`
   - **Payload:** `mensaje de prueba desde MQTT Explorer`
   - **QoS:** 0 (por defecto)
3. Clic en **Publish**.

### Paso 7: Abrir Wireshark y capturar el mensaje
1. Abre **Wireshark**.
2. Selecciona la interfaz de red correspondiente (`docker0`, `eth0`, `wlan0`, etc.).
3. Usa el filtro:
```
mqtt
```
4. Regresa a MQTT Explorer y publica otro mensaje.
5. En Wireshark deberías ver el paquete MQTT:
   - Tipo de paquete: `PUBLISH`
   - Topic: `iot/test`
   - Payload visible en texto plano


## Preguntas que debes poder responder
- ¿Cómo identificas el topic en el paquete MQTT?
- ¿El contenido es visible? ¿Está cifrado?
- ¿Qué diferencias ves con HTTP o UDP?
- ¿Qué parte del mensaje es sensible a ataques?



## Entregables del laboratorio

- Capturas de pantalla de Wireshark mostrando el paquete MQTT.
- Captura de la interfaz de MQTT Explorer publicando el mensaje.
- Documento con tus respuestas a las preguntas anteriores.





---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)