# Evaluación - Semana 4
# Curso: Estructuras de Datos y Compiladores
# Universidad: Global University
# Profesor: Omar Velázquez
# Tema: Listas simples y tablas de símbolos

"""
Instrucciones:
A continuación se describe el escenario de evaluación de esta semana.
Deberás implementar un programa que resuelva el problema descrito siguiendo las instrucciones en pseudocódigo.
Este archivo contiene solo las instrucciones, no el código.
"""

# -----------------------------------------------------------------------------
# PROBLEMA:
# Sistema de Registro de Contactos tipo 'LinkedIn' con Detección de Duplicados
# -----------------------------------------------------------------------------
# 
# Escenario:
# Estás diseñando un sistema simple que almacene usuarios de una red social en
# una lista enlazada. Cada usuario tiene un identificador único (nombre o ID).
# Además, mantendrás una tabla de símbolos que registre estos identificadores.
# La tabla de símbolos servirá para detectar duplicados.
#
# Objetivo:
# Implementar una lista enlazada simple que permita:
# 1. Insertar elementos al final de la lista.
# 2. Consultar si un identificador ya existe antes de insertarlo.
# 3. Imprimir la lista completa al final del programa.
#
# Además, deberás construir una tabla de símbolos (puede ser un diccionario o
# cualquier estructura que permita búsquedas eficientes) que almacene los
# identificadores y evite duplicados.

# -----------------------------------------------------------------------------
# PSEUDOCÓDIGO EN LENGUAJE NATURAL
# -----------------------------------------------------------------------------

# 1. Crear la clase Nodo con los atributos:
#    - valor (string o número que representa el ID del usuario)
#    - siguiente (referencia al siguiente nodo)

# 2. Crear la clase ListaEnlazada con los métodos:
#    - insertar(valor): inserta al final solo si no está en la tabla de símbolos
#    - imprimir(): imprime los nodos de la lista

# 3. Crear una tabla de símbolos vacía (estructura para guardar IDs únicos)

# 4. Leer una lista de nombres o identificadores (puedes usar una lista fija
#    en el código, por ejemplo: ["ana", "luis", "ana", "pedro", "luis"])

# 5. Para cada identificador:
#    - Verificar si ya existe en la tabla de símbolos
#    - Si no existe:
#         - Insertarlo en la lista enlazada
#         - Agregarlo a la tabla de símbolos
#    - Si existe:
#         - Imprimir mensaje: "Duplicado detectado: <nombre>"

# 6. Al final, imprimir la lista completa de contactos únicos y graficar los nodos
