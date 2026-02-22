# semana4_evaluacion_modulacion.py
# Evaluación Semana 4 - Comunicaciones e IoT
# Proyecto Centauri: Validación de Módulo de Comunicación

"""
INSTRUCCIONES GENERALES:
-------------------------
Este archivo está dividido en dos partes:
1. ALGORITMO para que implementes la modulación FSK.
2. DEMODULADOR (ya resuelto) para validar si tu señal fue correctamente generada.

Tu objetivo es:
- Implementar la modulación FSK de una cadena binaria.
- Usar los parámetros establecidos.
- Ejecutar la validación usando el demodulador.

NO MODIFIQUES la sección 2.
Documenta cualquier uso de herramientas de IA al final del archivo.
"""

# ======================================================================
# PARTE 1: IMPLEMENTA AQUÍ LA MODULACIÓN FSK (SIGUE LOS PASOS)
# ======================================================================

"""
PASO 1: Define la cadena binaria a transmitir.
- Puedes elegir cualquier secuencia, por ejemplo: "101101" o "11001100"
"""
binary_data = "11001100"  # <- Puedes cambiarla para hacer pruebas

"""
PASO 2: Define los parámetros de modulación:
- freq0: frecuencia para bit 0 (Hz)
- freq1: frecuencia para bit 1 (Hz)
- bit_duration: duración de cada bit en segundos (e.g., 0.1)
- sample_rate: frecuencia de muestreo (e.g., 44100)
"""
freq0 = 1000      # Hz
freq1 = 2000      # Hz
bit_duration = 0.1  # segundos
sample_rate = 44100  # muestras por segundo

"""
PASO 3: Calcula el número de muestras por bit.
- Usa la fórmula: muestras_por_bit = int(sample_rate * bit_duration)
"""
# TU CÓDIGO AQUÍ

"""
PASO 4: Inicializa un arreglo de señal vacío (tipo NumPy).
- Usa np.array([]) o una lista para ir concatenando fragmentos.
- Asegúrate de importar numpy como np.
"""
# TU CÓDIGO AQUÍ

"""
PASO 5: Para cada bit en la cadena:
  a) Elige freq0 o freq1 según el bit.
  b) Genera un vector de tiempo para ese bit: t = np.linspace(...)
  c) Crea una onda senoidal con esa frecuencia.
  d) Agrega la onda generada a la señal final.

Repite para todos los bits.
"""
# TU CÓDIGO AQUÍ

"""
PASO 6: Guarda la señal modulada en un archivo .npy llamado "mi_modulacion.npy"
- Usa np.save()
"""
# TU CÓDIGO AQUÍ

# ======================================================================
# PARTE 2: NO MODIFICAR - VALIDACIÓN AUTOMÁTICA DE LA MODULACIÓN
# ======================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

# Carga la señal generada
try:
    signal = np.load("mi_modulacion.npy")
except FileNotFoundError:
    raise Exception("No se encontró el archivo 'mi_modulacion.npy'. Asegúrate de haberlo guardado.")

# Reprocesado por bloques
samples_per_bit = int(sample_rate * bit_duration)
bits_detected = []

for i in range(0, len(signal), samples_per_bit):
    segment = signal[i:i+samples_per_bit]
    if len(segment) < samples_per_bit:
        continue

    spectrum = np.abs(fft(segment))[:samples_per_bit//2]
    freqs = np.fft.fftfreq(samples_per_bit, 1/sample_rate)[:samples_per_bit//2]
    dominant_freq = freqs[np.argmax(spectrum)]

    # Clasifica la frecuencia
    bit = '1' if abs(dominant_freq - freq1) < abs(dominant_freq - freq0) else '0'
    bits_detected.append(bit)

print("Bits originales:  ", binary_data)
print("Bits detectados: ", ''.join(bits_detected))

# Grafica para inspección visual
plt.figure(figsize=(10, 2))
plt.plot(signal[:5*samples_per_bit])
plt.title("Vista de los primeros 5 bits modulados")
plt.xlabel("Muestras")
plt.ylabel("Amplitud")
plt.tight_layout()
plt.show()

# ======================================================================
# USO DE IA (si aplica)
# ======================================================================
"""
Incluye aquí los prompts usados, si consultaste alguna herramienta:
- Prompt 1:
- Prompt 2:

Referencias APA:
OpenAI. (2025). ChatGPT (versión GPT-4) [Modelo de lenguaje grande]. https://chat.openai.com
"""
