# Evaluación Avanzada – Semana 7
# Curso: Comunicaciones e IoT
# Tema: Modulación digital en bandas libres con condiciones reales

"""
Objetivo Didáctico:
Simularás un sistema de transmisión de datos entre sensores IoT y un gateway usando modulación digital (FSK o GFSK) y condiciones de canal con ruido. Esta actividad permitirá comprender la relación entre la codificación de datos, la elección de parámetros de modulación, y la integridad de la transmisión.
"""

# -------------------- PSEUDOCÓDIGO EN LENGUAJE NATURAL --------------------
"""
Inicio de la simulación

1. Crear tres sensores virtuales: temperatura, humedad y luz.
    - Asignar a cada uno un valor numérico entero (por ejemplo, 22 ºC, 55 %, 130 lux).

2. Codificar los valores numéricos en binario de 8 bits.
    - Convertir cada número entero a binario y completar con ceros si es necesario (padding).

3. Concatenar los tres valores binarios en una sola trama de bits.
    - Por ejemplo: temperatura = 22 → 00010110; humedad = 55 → 00110111; luz = 130 → 10000010
    - Trama final = 000101100011011110000010 (24 bits)

4. Definir el esquema de modulación digital:
    - Para FSK:
        - bit 0 → frecuencia 910 MHz
        - bit 1 → frecuencia 920 MHz
    - Para GFSK:
        - bit 0 → frecuencia 910 MHz ± pequeño ruido gaussiano
        - bit 1 → frecuencia 920 MHz ± pequeño ruido gaussiano

5. Generar la señal modulada:
    - Recorrer cada bit de la trama:
        - Si el esquema es FSK:
            - Asociar la frecuencia correspondiente al bit (910 o 920 MHz)
        - Si el esquema es GFSK:
            - Asociar frecuencia correspondiente + desplazamiento gaussiano pequeño (simula la forma realista de GFSK)
    - Guardar la señal como una lista de frecuencias (una por bit)

6. Inyectar ruido al canal:
    - Definir un parámetro SNR (Relación Señal a Ruido) como valor entero (por ejemplo, 10 dB)
    - Calcular desviación estándar del ruido
    - Generar ruido blanco gaussiano
    - Sumarlo a la señal modulada para obtener la señal recibida

7. Decodificar la señal recibida:
    - Usar un umbral entre 910 y 920 MHz (por ejemplo, 915 MHz)
    - Si frecuencia > umbral → bit = 1; si no → bit = 0
    - Recuperar y mostrar la secuencia de bits recibidos

8. Comparar la trama original con la recibida:
    - Calcular tasa de error de bits (BER = bits incorrectos / total bits)
    - Mostrar ambos resultados: original y recibido

9. Visualizar los resultados:
    - Generar gráfica de la señal recibida
    - Eje X: posición del bit
    - Eje Y: frecuencia en MHz
    - Incluir líneas guía para FSK ideal

10. Reflexión guiada:
    - ¿Cuántos bits se alteraron tras pasar por el canal ruidoso?
    - ¿Qué impacto tuvo el valor de SNR en la fidelidad de la señal?
    - ¿Qué esquema mostró mayor robustez frente al ruido: FSK o GFSK? ¿Por qué?
    - ¿Cómo se relaciona esto con la operación real de LoRa, Zigbee o BLE?
    - ¿Qué parámetros cambiarías para reducir la tasa de error en una red real?

Fin de la simulación
"""

# -------------------- BLOQUE DE CÓDIGO ENTREGADO A LOS ESTUDIANTES --------------------

import numpy as np
import matplotlib.pyplot as plt

# PASO 1: Crear sensores virtuales
# Asigna valores numéricos enteros a los sensores: temperatura, humedad, luz
# Ejemplo: temperatura = 22

# PASO 2: Codificar cada valor en binario de 8 bits
# Utiliza bin() y zfill() para representar cada número como binario con padding

# PASO 3: Concatenar los binarios en una sola trama
# Concatena los strings binarios en una secuencia de 24 bits totales

# PASO 4: Definir esquema de modulación
# Elige entre FSK o GFSK. Define las reglas de mapeo de bit a frecuencia

# PASO 5: Modulación
# Recorre la trama de bits y genera una lista de frecuencias moduladas
# Para GFSK, agrega un pequeño valor aleatorio gaussiano a cada frecuencia

# PASO 6: Inyectar ruido al canal
# Define el valor de SNR en dB
SNR_dB = 10

# Función para canal con ruido (ya implementada)
def canal_con_ruido(senal, snr):
    ruido_std = np.mean(senal) / (10 ** (snr / 20))
    ruido = np.random.normal(0, ruido_std, len(senal))
    return senal + ruido

# PLACEHOLDER: Asigna aquí tu señal modulada (lista de frecuencias generada previamente)
senal_modulada = [910, 920, 910, 920, 920, 910, 910, 920]  # Ejemplo
senal_ruidosa = canal_con_ruido(np.array(senal_modulada), SNR_dB)

# PASO 7: Decodificación
# Aplica el umbral de decisión para convertir la señal ruidosa en bits
umbral = 915
recuperado = ['1' if f > umbral else '0' for f in senal_ruidosa]

# PASO 8: Comparación de secuencias
# Calcula cuántos bits son distintos entre la secuencia original y la recuperada
# PLACEHOLDER: Escribe aquí la secuencia binaria original para compararla
original = list("10101010")  # ejemplo
BER = sum([o != r for o, r in zip(original, recuperado)]) / len(original)
print("BER:", BER)

# PASO 9: Visualización
x = np.arange(len(senal_ruidosa))
plt.plot(x, senal_ruidosa, label='Señal recibida', drawstyle='steps-post')
plt.hlines([910, 920], 0, len(x), linestyles='dashed', colors='gray', label='FSK ideal')
plt.title(f"Modulación simulada con SNR = {SNR_dB} dB")
plt.xlabel("Símbolo")
plt.ylabel("Frecuencia (MHz)")
plt.grid(True)
plt.legend()
plt.show()

# PASO 10: Reflexión guiada
# Responde en tu bitácora:
# - ¿Cuántos bits se alteraron tras pasar por el canal ruidoso?
# - ¿Qué impacto tuvo el valor de SNR en la fidelidad de la señal?
# - ¿Qué esquema mostró mayor robustez frente al ruido: FSK o GFSK? ¿Por qué?
# - ¿Cómo se relaciona esto con la operación real de LoRa, Zigbee o BLE?
# - ¿Qué parámetros cambiarías para reducir la tasa de error en una red real?
