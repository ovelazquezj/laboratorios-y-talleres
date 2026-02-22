# Evaluación Semana 6 – Simulación de Detección y Corrección de Errores

# Objetivo general:
# Aplicar y comprender tres técnicas fundamentales para detección y corrección de errores,
# tal como se usan en sistemas reales como WiFi, LoRa y protocolos IoT. 
# Estas técnicas son esenciales para garantizar confiabilidad en redes con ruido o pérdida de datos.

# Los estudiantes simularán los siguientes mecanismos:
# 1. Bit de Paridad
# 2. CRC (Cyclic Redundancy Check)
# 3. Código de Hamming (7,4)

# ======================================
# DATOS BASE PARA TODAS LAS SIMULACIONES
# ======================================
# Mensaje original a transmitir (8 bits): "11010011"
# Mensajes simulados con error:
# - Error 1: bit 2 alterado → "10010011"
# - Error 2: bit 5 alterado → "11011011"

# ======================================
# 1. Bit de Paridad (Detección simple de error)
# ======================================

# Aplicación típica: Tramas cortas o simples (por ejemplo, UART, Zigbee)
# ¿Qué hace?: Añade un bit al mensaje para que el número total de 1's sea par (o impar)
# Detecta errores simples (1 bit), pero NO los puede corregir.

# Pseudocódigo:
# Paso 1: Contar cuántos unos hay en el mensaje.
# Paso 2: Si hay una cantidad impar → agregar un bit 1 al final (paridad par).
#         Si hay una cantidad par → agregar un bit 0.
# Paso 3: Transmitir ese mensaje extendido.
# Paso 4: En la recepción, volver a contar los unos (incluyendo el bit de paridad).
# Paso 5: Si la cuenta es impar → hay error. Si es par → no hay error.

# Resultado esperado: Mostrar si el mensaje recibido tiene error o no.

# ======================================
# 2. CRC – Detección robusta
# ======================================

# Aplicación típica: Ethernet, LoRaWAN, discos duros
# ¿Qué hace?: Usa un algoritmo de división polinomial binaria para generar un código de verificación.
# Puede detectar múltiples errores, pero no puede corregirlos.

# Pseudocódigo:
# Paso 1: Elegir un polinomio generador (por ejemplo, "1011")
# Paso 2: Agregar ceros al final del mensaje original (tantos como el grado del generador)
# Paso 3: Realizar división binaria (XOR secuencial):
#         - Tomar bloques del tamaño del generador.
#         - Hacer XOR con el generador si el primer bit es 1.
#         - Bajar siguiente bit y repetir.
# Paso 4: El residuo final es el CRC.
# Paso 5: Adjuntar el CRC al mensaje original.
# Paso 6: En la recepción, repetir la división.
# Paso 7: Si el residuo es 0 → mensaje correcto. Si no → hay error.

# Resultado esperado: Imprimir CRC y resultado de la validación.

# ======================================
# 3. Código de Hamming (7,4) – Corrección
# ======================================

# Aplicación típica: Memoria RAM, protocolos de radio antiguos
# ¿Qué hace?: Codifica 4 bits de datos en 7 bits añadiendo 3 de paridad.
# Permite detectar y CORREGIR errores de 1 solo bit.

# Pseudocódigo detallado:

# Paso 1: Tomar un bloque de 4 bits de datos. Ejemplo: [1, 0, 1, 1]

# Paso 2: Colocar los datos en las posiciones 3, 5, 6 y 7 del mensaje codificado:
#         - posición 3 ← bit 1
#         - posición 5 ← bit 2
#         - posición 6 ← bit 3
#         - posición 7 ← bit 4

# Paso 3: Calcular los bits de paridad:
#         - p1 en posición 1 → cubre posiciones 1,3,5,7 (XOR entre bits en 3,5,7)
#         - p2 en posición 2 → cubre posiciones 2,3,6,7 (XOR entre bits en 3,6,7)
#         - p4 en posición 4 → cubre posiciones 4,5,6,7 (XOR entre bits en 5,6,7)

# Paso 4: Armar el mensaje completo en orden: [p1, p2, d1, p4, d2, d3, d4]

# Paso 5: Simular la transmisión y forzar un error (por ejemplo, cambiar el bit en posición 6)

# Paso 6: En la recepción:
#         a) Calcular de nuevo los bits de paridad usando los mismos grupos
#         b) Comparar con los bits de paridad recibidos
#         c) Si hay diferencias, sumar las posiciones con error → esto da el índice del bit dañado

# Paso 7: Si el índice es 0 → mensaje correcto
#         Si no es 0 → invertir el bit en esa posición para corregirlo

# Paso 8: Extraer los bits de datos (posiciones 3,5,6,7) para obtener el mensaje original corregido

# Resultado esperado: Imprimir mensaje original, codificado, mensaje con error, posición del error y mensaje corregido.

# ======================================
# INSTRUCCIONES PARA LOS ESTUDIANTES
# ======================================
# - Implementa los 3 mecanismos anteriores en este archivo .py
# - NO usar librerías externas
# - Añade comentarios explicando tu razonamiento
# - Incluye ejemplos con errores simulados y muestra el resultado
# - El archivo debe poder ejecutarse correctamente en consola
# - Usa IA, recuerda colocar el prompt que usaste
