# Autor: Omar Velázquez (https://www.linkedin.com/in/ovelazquezj)
# Licencia: CC BY 4.0 (2025)

"""
EJERCICIO: SISTEMA DE ABORTO DE MISIÓN DE COHETE

CONTEXTO:
Durante el ascenso de un cohete, los sistemas de control monitorean constantemente
la desviación angular respecto a la trayectoria planificada. Si la desviación
supera un umbral crítico de 15°, se considera que la misión está en riesgo y
debe activarse un procedimiento de aborto de emergencia.

ESCENARIO:
- Altitud crítica: 120,000 metros
- Desviación detectada: 15° (umbral máximo permitido)
- Acción requerida: Aborto de misión con separación de cápsula

OBJETIVO:
Implementar un sistema que:
1. Simule el vuelo del cohete paso a paso
2. Detecte cuando la desviación supera el umbral crítico
3. Active el procedimiento de aborto de misión
4. Registre todos los eventos en una bitácora

TAREAS DEL ESTUDIANTE:
- Completar las funciones con código funcional
- Implementar la lógica de detección
- Programar el procedimiento de aborto
- Crear el sistema de registro de eventos
"""

# ==============================================================================
# PARTE 1: CONFIGURACIÓN Y CONSTANTES
# ==============================================================================

# TODO: Definir las constantes del sistema
# - UMBRAL_DESVIACION_CRITICA: Ángulo máximo permitido (15 grados)
# - ALTITUD_MAXIMA: Altitud objetivo de la misión (200,000 metros)
# - ALTITUD_CRITICA: Altitud donde ocurre el problema (120,000 metros)
# - INCREMENTO_ALTITUD: Cuánto sube el cohete en cada paso de simulación


# ==============================================================================
# PARTE 2: ESTRUCTURA DE DATOS DEL COHETE
# ==============================================================================

# TODO: Crear una clase o diccionario llamado 'Cohete' que contenga:
# - altitud_actual: Altura actual en metros (inicia en 0)
# - desviacion_angular: Desviación en grados (inicia en 0)
# - estado_mision: String que indica el estado ("activa", "abortada", "completada")
# - motores_encendidos: Booleano que indica si los motores están activos
# - capsula_separada: Booleano que indica si la cápsula se separó


# ==============================================================================
# PARTE 3: FUNCIÓN DE DETECCIÓN DE DESVIACIÓN CRÍTICA
# ==============================================================================

def detectar_desviacion_critica(desviacion_actual, umbral):
    """
    Determina si la desviación angular supera el umbral crítico.
    
    PARÁMETROS:
    - desviacion_actual: Ángulo de desviación en grados (float)
    - umbral: Ángulo máximo permitido en grados (float)
    
    RETORNA:
    - True si la desviación supera el umbral (situación crítica)
    - False si la desviación está dentro de límites seguros
    
    EJEMPLO:
    Si desviacion_actual = 16° y umbral = 15°, debe retornar True
    Si desviacion_actual = 10° y umbral = 15°, debe retornar False
    """
    
    # TODO: Implementar la lógica de comparación
    # Pista: Usar el valor absoluto de la desviación para considerar
    # desviaciones tanto positivas como negativas
    
    pass  # Reemplazar con tu código


# ==============================================================================
# PARTE 4: PROCEDIMIENTO DE ABORTO DE MISIÓN
# ==============================================================================

def procedimiento_aborto(cohete, altitud, desviacion):
    """
    Ejecuta la secuencia de aborto de misión en caso de emergencia.
    
    PARÁMETROS:
    - cohete: Objeto o diccionario con los datos del cohete
    - altitud: Altitud actual donde ocurre el aborto (metros)
    - desviacion: Ángulo de desviación que causó el aborto (grados)
    
    SECUENCIA DE ABORTO:
    1. Apagar motores principales inmediatamente
    2. Activar sistema de separación de cápsula
    3. Desplegar paracaídas de emergencia
    4. Cambiar estado de misión a "abortada"
    5. Registrar evento en bitácora con timestamp
    
    RETORNA:
    - Diccionario con el reporte del aborto que incluya:
      * timestamp: Momento del aborto
      * altitud: Altura donde ocurrió
      * causa: Descripción de la causa
      * acciones_tomadas: Lista de acciones ejecutadas
    """
    
    # TODO: PASO 1 - Apagar motores principales
    # Cambiar el atributo 'motores_encendidos' del cohete a False
    
    
    # TODO: PASO 2 - Separar cápsula de tripulación
    # Cambiar el atributo 'capsula_separada' del cohete a True
    
    
    # TODO: PASO 3 - Activar sistema de paracaídas
    # En una implementación real, esto activaría hardware físico
    # Para este ejercicio, solo documenta la acción en comentarios
    
    
    # TODO: PASO 4 - Actualizar estado de la misión
    # Cambiar el atributo 'estado_mision' del cohete a "abortada"
    
    
    # TODO: PASO 5 - Generar reporte de aborto
    # Crear un diccionario con:
    # - timestamp: usar datetime.now() o time.time()
    # - altitud: valor recibido como parámetro
    # - desviacion: valor recibido como parámetro
    # - causa: string explicativo (ej: "Desviación angular crítica")
    # - acciones_tomadas: lista con strings descriptivos de cada paso
    
    
    pass  # Reemplazar con tu código


# ==============================================================================
# PARTE 5: SIMULADOR DE VUELO
# ==============================================================================

def simular_vuelo(cohete):
    """
    Simula el vuelo del cohete paso a paso, monitoreando desviación.
    
    PARÁMETROS:
    - cohete: Objeto o diccionario con los datos del cohete
    
    LÓGICA DE SIMULACIÓN:
    1. Mientras la altitud sea menor que la máxima Y el estado sea "activa":
       a. Incrementar la altitud del cohete
       b. Simular desviación (puede ser aleatoria o fija en 120,000m)
       c. Verificar si hay desviación crítica
       d. Si hay desviación crítica -> llamar a procedimiento_aborto()
       e. Si no hay problema -> continuar ascenso
       f. Registrar datos del paso actual
    
    2. Si se completa sin abortos, cambiar estado a "completada"
    
    RETORNA:
    - Diccionario con historial del vuelo:
      * altitudes: lista de altitudes alcanzadas
      * desviaciones: lista de desviaciones en cada paso
      * eventos: lista de eventos importantes (aborto, fases, etc.)
      * exito: booleano indicando si se completó la misión
    """
    
    # TODO: Crear variables para almacenar el historial
    # - lista_altitudes = []
    # - lista_desviaciones = []
    # - lista_eventos = []
    
    
    # TODO: Crear bucle principal de simulación
    # while (condiciones de vuelo activo):
    
        # PASO A: Incrementar altitud
        # cohete.altitud_actual += INCREMENTO_ALTITUD
        
        
        # PASO B: Simular desviación angular
        # Opción 1: Si altitud >= ALTITUD_CRITICA (120,000m), asignar desviacion = 15°
        # Opción 2: Generar desviación aleatoria que aumente con la altitud
        # Opción 3: Usar una fórmula que haga la desviación crítica a 120,000m
        
        
        # PASO C: Detectar si hay desviación crítica
        # Llamar a la función detectar_desviacion_critica()
        # Almacenar el resultado en una variable (ej: es_critica)
        
        
        # PASO D: Tomar decisión basada en detección
        # if es_critica:
        #     reporte = procedimiento_aborto(cohete, altitud_actual, desviacion_actual)
        #     agregar reporte a lista_eventos
        #     salir del bucle (break)
        
        
        # PASO E: Si no hay problema, continuar
        # Registrar altitud y desviación actuales en las listas
        
        
        # PASO F: Verificar si alcanzó la altitud objetivo
        # if altitud_actual >= ALTITUD_MAXIMA:
        #     cambiar estado a "completada"
        #     agregar evento de éxito a lista_eventos
        #     salir del bucle (break)
    
    
    # TODO: Retornar diccionario con resultados
    # return {
    #     'altitudes': lista_altitudes,
    #     'desviaciones': lista_desviaciones,
    #     'eventos': lista_eventos,
    #     'exito': (cohete.estado_mision == "completada")
    # }
    
    pass  # Reemplazar con tu código


# ==============================================================================
# PARTE 6: SISTEMA DE REGISTRO (BITÁCORA)
# ==============================================================================

def registrar_en_bitacora(evento, archivo="bitacora_vuelo.txt"):
    """
    Registra eventos importantes en un archivo de texto.
    
    PARÁMETROS:
    - evento: Diccionario con información del evento (timestamp, tipo, datos)
    - archivo: Nombre del archivo donde guardar (opcional)
    
    FORMATO DEL REGISTRO:
    [TIMESTAMP] TIPO_EVENTO: Descripción detallada
    
    EJEMPLO:
    [2025-09-30 14:35:22] ABORTO_MISION: Desviación crítica de 15° a 120,000m
    """
    
    # TODO: Implementar escritura en archivo
    # 1. Abrir archivo en modo append ('a')
    # 2. Formatear el string con la información del evento
    # 3. Escribir en el archivo
    # 4. Cerrar el archivo
    
    # Pista: Usar 'with open(archivo, 'a') as f:' para manejo seguro
    
    pass  # Reemplazar con tu código


# ==============================================================================
# PARTE 7: VISUALIZACIÓN DE RESULTADOS
# ==============================================================================

def generar_reporte_final(resultados):
    """
    Genera un reporte legible en consola con los resultados de la simulación.
    
    PARÁMETROS:
    - resultados: Diccionario retornado por simular_vuelo()
    
    DEBE MOSTRAR:
    - Resumen ejecutivo (éxito o aborto)
    - Altitud máxima alcanzada
    - Número total de pasos simulados
    - Lista de eventos críticos
    - Si hubo aborto: detalles del momento y causa
    
    NO RETORNA NADA: Solo muestra información en consola
    """
    
    # TODO: Implementar la generación del reporte
    # 1. Mostrar encabezado decorativo
    # 2. Analizar el diccionario 'resultados'
    # 3. Formatear y mostrar cada sección del reporte
    # 4. Usar emojis o caracteres especiales para mejor legibilidad
    
    pass  # Reemplazar con tu código


# ==============================================================================
# PARTE 8: FUNCIÓN PRINCIPAL (PUNTO DE ENTRADA)
# ==============================================================================

def main():
    """
    Función principal que ejecuta la simulación completa.
    
    FLUJO DEL PROGRAMA:
    1. Crear instancia del cohete con valores iniciales
    2. Mostrar mensaje de inicio de simulación
    3. Ejecutar simulación de vuelo
    4. Generar y mostrar reporte final
    5. Guardar eventos en bitácora
    """
    
    # TODO: PASO 1 - Inicializar el cohete
    # Crear el objeto o diccionario 'cohete' con valores iniciales
    
    
    # TODO: PASO 2 - Mensaje de inicio
    # Mostrar en consola que la simulación está comenzando
    
    
    # TODO: PASO 3 - Ejecutar simulación
    # resultados = simular_vuelo(cohete)
    
    
    # TODO: PASO 4 - Generar reporte
    # generar_reporte_final(resultados)
    
    
    # TODO: PASO 5 - Guardar en bitácora
    # Para cada evento en resultados['eventos']:
    #     registrar_en_bitacora(evento)
    
    pass  # Reemplazar con tu código


# ==============================================================================
# EJECUCIÓN DEL PROGRAMA
# ==============================================================================

# TODO: Descomentar la siguiente línea cuando hayas completado el código
# if __name__ == "__main__":
#     main()


# ==============================================================================
# NOTAS PARA EL ESTUDIANTE
# ==============================================================================

"""
CONSEJOS PARA RESOLVER ESTE EJERCICIO:

1. COMIENZA POR LO SIMPLE:
   - Primero define las constantes y la estructura del cohete
   - Luego implementa las funciones más simples (detectar_desviacion_critica)
   - Finalmente integra todo en el simulador

2. PRUEBA CADA FUNCIÓN:
   - Después de implementar cada función, pruébala individualmente
   - Usa print() temporales para verificar que funciona correctamente
   - Ejemplo: print(detectar_desviacion_critica(16, 15))  # Debe ser True

3. MANEJO DE DATOS:
   - Puedes usar diccionarios o clases para representar el cohete
   - Diccionario es más simple: cohete = {'altitud': 0, 'desviacion': 0, ...}
   - Clase es más estructurado: class Cohete: def __init__(self): ...

4. SIMULACIÓN DE DESVIACIÓN:
   - Opción fácil: if altitud >= 120000: desviacion = 15
   - Opción realista: desviacion = random.uniform(0, altitud/10000)
   - Opción intermedia: desviacion = (altitud / 120000) * 15

5. FORMATO DE SALIDA:
   - Usa f-strings para formatear: f"Altitud: {altitud:,.0f}m"
   - Usa separadores visuales: print("="*50)
   - Añade emojis para mejor UX: print("🚀 Iniciando misión...")

6. DEBUGGING:
   - Si algo no funciona, agrega prints para ver valores intermedios
   - Verifica que las condiciones del while sean correctas
   - Asegúrate de que el break se ejecute cuando debe

RECURSOS ÚTILES:
- Documentación de Python: https://docs.python.org/es/3/
- Manejo de archivos: https://docs.python.org/es/3/tutorial/inputoutput.html
- Formato de strings: https://docs.python.org/es/3/tutorial/inputoutput.html#fancier-output-formatting

¡BUENA SUERTE CON TU IMPLEMENTACIÓN! 🚀

Autor: Mtro. Omar Velázquez
LinkedIn: https://www.linkedin.com/in/ovelazquezj
"""