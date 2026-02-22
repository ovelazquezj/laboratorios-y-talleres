# Laboratorio LoRaWAN + Node-RED + Docker

Material para el laboratorio de decodificación de payloads LoRaWAN.

---

## 📦 Archivos (5 total)

### 1. **GUIA_LABORATORIO.md** ← **EMPIEZA AQUÍ**
Guía didáctica completa paso a paso. Explica:
- Por qué usamos Docker
- Cómo funciona cada comando
- Formato de payloads LoRaWAN
- Cómo decodificar
- Troubleshooting

### 2. **docker-compose.yml**
Configuración de contenedores (Node-RED + Mosquitto).

### 3. **mosquitto.conf**
Configuración del broker MQTT.

### 4. **flow_completo_lorawan.json**
Flujos de Node-RED listos para importar:
- Flujo EMISOR (simula dispositivos)
- Flujo RECEPTOR (decodifica payloads)

### 5. **ejemplos_payloads_lorawan.md**
Casos de prueba con payloads de ejemplo.

---

## 🚀 Inicio Rápido

```bash
# 1. Preparar directorios
mkdir -p mosquitto/config mosquitto/data mosquitto/log
cp mosquitto.conf mosquitto/config/

# 2. Iniciar contenedores
docker-compose up -d

# 3. Abrir Node-RED
# http://localhost:1880

# 4. Importar flow_completo_lorawan.json
# Menú ☰ → Import → Seleccionar archivo

# 6. Deploy y probar
```

**Todo está explicado en `GUIA_LABORATORIO.md`**

---

## 📖 Orden de Uso

### Para Profesores:
1. Leer `GUIA_LABORATORIO.md` completa
2. Probar el laboratorio en tu máquina
3. Distribuir archivos a alumnos

### Para Alumnos:
1. **Leer** `GUIA_LABORATORIO.md` paso a paso
2. **Seguir** las instrucciones (no saltarse pasos)
3. **Probar** con `ejemplos_payloads_lorawan.md`
4. **Entregar** flujos modificados

---

## ❓ ¿Qué archivo uso para...?

| Necesito... | Archivo |
|-------------|---------|
| Aprender todo | `GUIA_LABORATORIO.md` |
| Configurar Docker | `docker-compose.yml` + `mosquitto.conf` |
| Los flujos de Node-RED | `flow_completo_lorawan.json` |
| Probar mi decodificador | `ejemplos_payloads_lorawan.md` |

---

## 🛑 NO instalar manualmente

Este laboratorio **NO requiere** instalar Node.js, npm, Node-RED ni Mosquitto en tu sistema.

Todo funciona dentro de Docker.

---

**Última actualización:** 12 de noviembre de 2025


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)