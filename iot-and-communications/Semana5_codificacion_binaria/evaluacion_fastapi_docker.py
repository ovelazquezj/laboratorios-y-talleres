
"""
Evaluación – Semana 5: Codificación y Comunicación Binaria con FastAPI
-----------------------------------------------------------------------

Este archivo contiene los algoritmos paso a paso que los alumnos deben convertir en código funcional.
No incluye funciones escritas, solo los pasos lógicos que deben desarrollar.

Instrucción: convierte cada conjunto de pasos en funciones o scripts dentro de tu solución.
"""

# ------------------------------------------------------------------------------
# PARTE 1 – ALGORITMO PARA CODIFICAR TEXTO EN BINARIO
# ------------------------------------------------------------------------------

# Objetivo: Convertir un texto cualquiera (ej. "hola") en su representación binaria.

# PASOS A IMPLEMENTAR:
# 1. Crea una función que reciba como entrada un texto (string).
# 2. Inicializa una lista vacía donde guardarás los binarios.
# 3. Recorre letra por letra el texto.
# 4. Por cada letra:
#    a. Convierte la letra a su valor ASCII usando una función como ord().
#    b. Convierte ese número a binario usando una función como bin().
#    c. Asegúrate de que el binario resultante tenga exactamente 8 bits (rellena con ceros a la izquierda si hace falta).
# 5. Guarda cada binario como un string en la lista.
# 6. Une todos los binarios separados por un espacio y devuelve el resultado.

# Ejemplo esperado de salida (sin codificar): '01101000 01101111 01101100 01100001'


# ------------------------------------------------------------------------------
# PARTE 2 – ALGORITMO PARA DECODIFICAR BINARIO A TEXTO
# ------------------------------------------------------------------------------

# Objetivo: Convertir una cadena de bits en texto legible.

# PASOS A IMPLEMENTAR:
# 1. Crea una función que reciba como entrada un string con varios binarios separados por espacio.
# 2. Separa el string en una lista usando split().
# 3. Inicializa una lista vacía para guardar las letras.
# 4. Para cada binario en la lista:
#    a. Convierte el binario a número entero usando int(binario, 2).
#    b. Convierte ese número en letra usando chr().
#    c. Agrega la letra a la lista.
# 5. Une las letras y devuelve el texto completo como string.

# Ejemplo de entrada: '01101000 01101111 01101100 01100001'
# Ejemplo esperado de salida (sin decodificar): 'hola'


# ------------------------------------------------------------------------------
# PARTE 3 – ENVÍO DEL MENSAJE USANDO FASTAPI + CURL
# ------------------------------------------------------------------------------

# Objetivo: Exponer un endpoint FastAPI que reciba un texto plano, lo codifique en binario y lo envíe al receptor.

# PASOS A IMPLEMENTAR:
# 1. Crea una aplicación FastAPI para el EMISOR.
# 2. Define una ruta POST en "/enviar" que reciba un JSON con el campo "mensaje" (texto plano).
# 3. Usa tu función de codificación para convertir ese mensaje a binario.
# 4. Usa requests.post() para enviar ese binario al endpoint remoto del receptor (ej. http://receptor:8000/mensaje).
# 5. Devuelve la respuesta del receptor o un mensaje de confirmación.

# EJEMPLO DE CURL PARA PROBAR ESTE ENDPOINT:
# curl -X POST http://localhost:8000/enviar \
#      -H "Content-Type: application/json" \
#      -d '{"mensaje": "hola mundo"}'


# ------------------------------------------------------------------------------
# PARTE 4 – SERVIDOR RECEPTOR FASTAPI
# ------------------------------------------------------------------------------

# Objetivo: Crear un receptor en FastAPI que reciba el mensaje codificado, lo decodifique y lo imprima.

# PASOS A IMPLEMENTAR:
# 1. Usa FastAPI para crear una aplicación web receptora.
# 2. Define una ruta POST en "/mensaje".
# 3. Espera un JSON con el campo "contenido_binario".
# 4. Usa tu función de decodificación para convertirlo a texto.
# 5. Imprime el texto en consola.
# 6. Devuelve una respuesta JSON de confirmación.

# EJEMPLO DE CURL PARA PROBAR ESTE ENDPOINT DIRECTAMENTE:
# curl -X POST http://localhost:8001/mensaje \
#      -H "Content-Type: application/json" \
#      -d '{"contenido_binario": "01101000 01101111 01101100 01100001"}'


# ------------------------------------------------------------------------------
# RESTRICCIÓN IMPORTANTE:
# - No debes usar bibliotecas que hagan toda la codificación o decodificación automáticamente.
# - El objetivo es que tú mismo construyas el proceso a partir de los pasos lógicos.