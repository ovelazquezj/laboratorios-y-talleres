# Evaluación – Pseudocódigo para el problema de los autobuses por color
# Curso: Estructuras de Datos y Compiladores
# Semana: Evaluación Tiempo-Espacio
# Profesor: Omar Velázquez

# Descripción general del problema:
# Se tienen 1000 pasajeros, cada uno asignado aleatoriamente a uno de cinco colores: azul, amarillo, rojo, anaranjado o lila.
# Existen autobuses de esos cinco colores, y cada autobús solo puede transportar pasajeros de su mismo color.
# Cada color tiene exactamente 3 autobuses disponibles.
# Cada autobús puede tener una capacidad de 4, 15 o 40 pasajeros (decisión del alumno).
# Los autobuses no pueden mezclarse entre colores.
# Cada autobús debe regresar antes de poder volver a transportar pasajeros (mínimo un ciclo de espera).

# Objetivo: Diseñar un algoritmo que transporte a la mayor cantidad posible de pasajeros
# respetando las restricciones anteriores, y medir las siguientes métricas:
# - Tiempo total (ciclos requeridos para concluir el transporte)
# - Número de autobuses utilizados (por tipo y en total)
# - Número total de ciclos usados
# - Promedio de pasajeros transportados por ciclo
# - Pasajeros que no pudieron ser transportados


# Paso 1: Inicialización
# Ya está implementado abajo en código funcional: se generan 1000 pasajeros aleatorios por color
# y se inicializan 15 autobuses (3 por color) con capacidad asignada por el alumno.

import random

colores = ["azul", "amarillo", "rojo", "anaranjado", "lila"]

# Crear los pasajeros
total_pasajeros = 1000
pasajeros = []
for i in range(1, total_pasajeros + 1):
    pasajeros.append({"id": i, "color": random.choice(colores)})

# Crear los autobuses: 3 por color, con capacidades elegidas por el alumno
capacidades = [40, 15, 4]  # El alumno puede modificar este patrón por color

autobuses = []
bus_id = 1
for color in colores:
    for cap in capacidades:
        autobuses.append({
            "id": f"{color[:2].upper()}-{bus_id}",
            "color": color,
            "capacidad": cap,
            "estado": "disponible",
            "ciclo_retorno": 0
        })
        bus_id += 1


# --- PSEUDOCÓDIGO DIDÁCTICO ---

# Paso 2: Agrupamiento de pasajeros
# - Crear una estructura por color que contenga la lista de pasajeros pendientes de ser transportados.
#   Ejemplo: una lista llamada "pendientes_azul", otra "pendientes_rojo", etc.
# - Para cada pasajero en la lista general:
#     - Agregarlo a la lista de su color correspondiente.


# Paso 3: Simulación por ciclos
# - Inicializar un contador de ciclos en cero.
# - Repetir mientras:
#     - Haya al menos un pasajero sin transportar (en cualquier lista de color), o
#     - Haya autobuses aún en estado "en_viaje" (es decir, esperando regresar).

# Dentro de cada ciclo:
# 1. Incrementar el contador de ciclos.

# 2. Marcar autobuses que estaban "en_viaje" en el ciclo anterior y que ya pueden regresar:
#    - Para cada autobús:
#        - Si su estado es "en_viaje" y su campo "ciclo_retorno" coincide con el ciclo actual:
#            - Cambiar su estado a "disponible"

# 3. Para cada color:
#    - Obtener la lista de pasajeros pendientes de ese color.
#    - Identificar autobuses disponibles de ese color.
#    - Para cada autobús disponible:
#         - Si hay suficientes pasajeros:
#             - Tomar hasta el número de pasajeros igual a la capacidad del autobús.
#             - Marcar el autobús como "en_viaje".
#             - Establecer su "ciclo_retorno" como ciclo actual + 1 (simulando que tardan un ciclo en volver).
#             - Quitar los pasajeros de la lista de pendientes.
#             - Sumar cuántos pasajeros fueron enviados en este ciclo.


# Paso 4: Finalización de la simulación
# - Cuando no queden pasajeros sin enviar y todos los autobuses estén disponibles,
#   se termina el ciclo principal.


# Paso 5: Cálculo de métricas
# - Calcular el número total de ciclos que se ejecutaron.
# - Calcular el total de pasajeros transportados (debería ser <= 1000).
# - Calcular el número de autobuses utilizados (contar cuántos autobuses fueron enviados al menos una vez).
# - Calcular el promedio de pasajeros enviados por ciclo (acumulado / ciclos).
# - Contar cuántos pasajeros no lograron ser transportados (si los hay).


# Paso 6: Visualización de resultados
# - Mostrar en pantalla las métricas anteriores.
# - Si deseas, también puedes mostrar la distribución de colores de pasajeros,
#   cuántos fueron transportados por cada tipo de autobús, o un resumen por color.


# --- FIN DEL PSEUDOCÓDIGO ---

# Nota: Este pseudocódigo NO debe resolverse directamente como está.
# Cada paso debe ser interpretado, diseñado, y transformado en código por el alumno.
# Las estructuras de datos pueden variar (listas, diccionarios, colas, etc.), y se busca
# fomentar la exploración de distintas soluciones y su eficiencia computacional.
