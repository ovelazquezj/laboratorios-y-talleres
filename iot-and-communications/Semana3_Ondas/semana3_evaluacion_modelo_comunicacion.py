"""
Evaluación – Semana 3
Tema: Modelo de Comunicación Digital

Objetivo general:
Implementar los bloques clave del modelo digital de comunicación y comprender su funcionamiento
a través de la simulación paso a paso.

Modelo completo:
Emisor → Codificador → Modulador → Canal → Demodulador → Decodificador → Receptor

💡 Instrucciones:
- Debes **implementar tú mismo** las funciones: emisor, codificador, decodificador, receptor.
- Las funciones de modulador, canal y demodulador ya están implementadas y sirven como guía.
- No borres los comentarios, te ayudarán a guiarte paso a paso.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

fs = 8000  # Frecuencia de muestreo (Hz)

# =====================================================
# BLOQUE 1 – EMISOR (A COMPLETAR POR EL ALUMNO)
# =====================================================
def emisor(texto):
    """
    GLOSARIO:
    - ASCII: Código que representa cada carácter como un número.
    - Bit: Unidad binaria, puede ser 0 o 1.

    ALGORITMO:
    1. Crear una lista vacía llamada 'bits'.
    2. Para cada carácter en el texto:
        a. Obtener su código ASCII con `ord(caracter)`.
        b. Convertir ese número a binario con `format(..., '08b')`.
        c. Recorrer ese binario y convertir cada dígito ('0' o '1') a entero.
        d. Agregar cada bit a la lista.
    3. Retornar la lista de bits como salida.
    """
    pass


# =====================================================
# BLOQUE 2 – CODIFICADOR (A COMPLETAR POR EL ALUMNO)
# =====================================================
def codificador(bits, samples_per_bit=100):
    """
    GLOSARIO:
    - Señal digital: Secuencia de niveles (altos o bajos) que representan los bits.
    - NRZ: Codificación donde 1 se representa como nivel alto y 0 como bajo.
    - Muestreo: Representar una señal continua con valores discretos.

    ALGORITMO:
    1. Crear una lista vacía llamada 'senal'.
    2. Para cada bit en la lista:
        a. Si el bit es 1, agregar 'samples_per_bit' veces el valor 1 a 'senal'.
        b. Si el bit es 0, agregar 'samples_per_bit' veces el valor 0.
    3. Convertir 'senal' a un array de NumPy.
    4. Crear un vector de tiempo 't' usando np.linspace con la misma longitud que 'senal' y la frecuencia fs.
    5. Retornar 'senal' y 't'.
    """
    pass


# =====================================================
# BLOQUE 3 – MODULADOR (IMPLEMENTADO)
# =====================================================
def modulador(senal_digital, t, f_portadora=1000):
    """
    GLOSARIO:
    - Modulación ASK: Técnica donde la amplitud de una portadora varía según la señal digital.
    - Portadora: Señal senoidal que se modifica para transportar información.

    ✅ IMPLEMENTACIÓN:
    1. Crear una señal portadora usando np.sin(2πf·t).
    2. Multiplicar la señal digital por la portadora (elemento a elemento).
    3. Retornar la señal modulada.
    """
    portadora = np.sin(2 * np.pi * f_portadora * t)
    senal_modulada = senal_digital * portadora
    return senal_modulada


# =====================================================
# BLOQUE 4 – CANAL (IMPLEMENTADO)
# =====================================================
def canal(senal_modulada, ruido_std=0.5):
    """
    GLOSARIO:
    - Ruido blanco: Señal aleatoria que afecta todas las frecuencias.
    - Filtro paso banda: Permite solo un rango de frecuencias.

    ✅ IMPLEMENTACIÓN:
    1. Agregar ruido blanco a la señal.
    2. Definir un filtro pasa banda (800-1200 Hz) con scipy.signal.butter.
    3. Aplicar el filtro con scipy.signal.lfilter.
    4. Retornar la señal filtrada.
    """
    ruido = np.random.normal(0, ruido_std, len(senal_modulada))
    senal_ruidosa = senal_modulada + ruido

    nyq = 0.5 * fs
    low = 800 / nyq
    high = 1200 / nyq
    b, a = butter(4, [low, high], btype='band')
    senal_filtrada = lfilter(b, a, senal_ruidosa)

    return senal_filtrada


# =====================================================
# BLOQUE 5 – DEMODULADOR (IMPLEMENTADO)
# =====================================================
def demodulador(senal_recibida, ventana=100):
    """
    GLOSARIO:
    - Envolvente: Curva que representa la amplitud de una señal oscilante.
    - Suavizado: Técnica para reducir variaciones bruscas (media móvil).

    ✅ IMPLEMENTACIÓN:
    1. Obtener el valor absoluto de la señal.
    2. Aplicar suavizado con convolución (ventana de promedio).
    3. Retornar la señal suavizada (envolvente).
    """
    envolvente = np.abs(senal_recibida)
    kernel = np.ones(ventana) / ventana
    suavizada = np.convolve(envolvente, kernel, mode='same')
    return suavizada


# =====================================================
# BLOQUE 6 – DECODIFICADOR (A COMPLETAR POR EL ALUMNO)
# =====================================================
def decodificador(senal_envolvente, samples_per_bit=100):
    """
    GLOSARIO:
    - Umbral: Valor de referencia para decidir entre 0 y 1.

    ALGORITMO:
    1. Crear una lista vacía llamada 'bits'.
    2. Dividir la señal en bloques de 'samples_per_bit'.
    3. Para cada bloque:
        a. Calcular el promedio del bloque.
        b. Si el promedio > 0.5 → bit = 1
           Si no → bit = 0
        c. Agregar el bit a la lista.
    4. Retornar la lista de bits.
    """
    pass


# =====================================================
# BLOQUE 7 – RECEPTOR (A COMPLETAR POR EL ALUMNO)
# =====================================================
def receptor(bits):
    """
    GLOSARIO:
    - ASCII inverso: De bits a texto.

    ALGORITMO:
    1. Agrupar los bits en bloques de 8 (un byte).
    2. Para cada grupo:
        a. Convertir a cadena binaria.
        b. Usar int(..., 2) para obtener el número.
        c. Usar chr() para convertir a letra.
    3. Concatenar y retornar el texto.
    """
    pass

# ==================================================================
# BLOQUE 9 – CREA EL MAIN E IMPLEMENTA LAS ETAPAS DEL MODELO DIGITAL
# ==================================================================
"""
INSTRUCCIONES FINALES:

1. Crea una sección "main" (es decir, un bloque de código protegido por `if __name__ == "__main__":`)
2. Dentro de ese bloque, implementa todas las etapas en orden:
   - Emisor → Codificador → Modulador → Canal → Demodulador → Decodificador → Receptor

3. Usa una cadena corta de entrada como: "Hola" o "IoT"
4. Imprime la cadena original y la reconstruida para comparar los resultados.

Ejemplo esperado:
Texto original: Hola
Texto recibido: Hola
"""