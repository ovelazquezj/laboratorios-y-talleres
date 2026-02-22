# guT – Editor de Texto en Terminal para Global University

`guT` (Global University Terminal Editor) es un editor de texto educativo diseñado para la materia **Estructuras de Datos y Compiladores** de **Global University**. Construido en lenguaje C y utilizando la biblioteca `ncurses`, `guT` permite a los estudiantes explorar estructuras de datos como listas, manejo de archivos y control de flujo, todo desde la terminal.

## Características principales

* **Interfaz de terminal con `ncurses`**
* **Menú de Archivo** (F1 o atajos directos):

  * `Ctrl+N`: Nuevo archivo
  * `Ctrl+O`: Abrir archivo
  * `Ctrl+S`: Guardar archivo
  * `Ctrl+A`: Guardar como
  * `Ctrl+Q`: Salir con confirmación si hay cambios
* **Menú de Ayuda** (F2 o `Ctrl+H`):

  * Lista de atajos de teclado
  * Información del programa
* **Funciones de edición**:

  * Escribir, editar, borrar texto
  * Navegación con flechas
  * Inserción de nuevas líneas
  * Indicador de archivo modificado en barra de estado
* **Manejo de archivos `.gu`**:

  * Guarda automáticamente con extensión `.gu`
  * Abre archivos existentes
  * Pregunta si guardar cambios al salir

## Compilación y ejecución (WSL)

```bash
# 1. Instalar dependencias si es necesario
sudo apt update
sudo apt install libncurses5-dev libncursesw5-dev

# 2. Compilar el editor
gcc guT.c -o guT -lncurses

# 3. Ejecutar el editor
./guT
```

## Atajos de teclado

| Comando       | Acción               |
| ------------- | -------------------- |
| Ctrl + N      | Nuevo archivo        |
| Ctrl + O      | Abrir archivo        |
| Ctrl + S      | Guardar archivo      |
| Ctrl + A      | Guardar como         |
| Ctrl + Q      | Salir                |
| F1            | Menú de Archivo      |
| F2 / Ctrl + H | Menú de Ayuda        |
| Flechas       | Navegar por el texto |
| Backspace     | Borrar carácter      |
| Enter         | Insertar nueva línea |

## Barra de estado

En la parte inferior se muestra:

* El nombre del archivo actual
* Un asterisco (*) si hay cambios sin guardar
* La posición actual del cursor (línea y columna)

## Licencia

Este software se distribuye bajo la licencia **Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)**.

Puedes copiar, modificar y compartir el editor siempre que:

* Se reconozca la autoría.
* No se use con fines comerciales.
* Las obras derivadas se compartan bajo la misma licencia.

Más información: [https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

**Autor:** Maestro Omar Francisco Velázquez Juárez <ovelazquezj@gmail.com>
**Curso:** Estructuras de Datos y Compiladores
**Institución:** Global University, Aguascalientes, México (2025)

> guT es más que un editor: es una herramienta pedagógica para entender cómo la memoria, los eventos del usuario y las estructuras de datos se entrelazan en un entorno real de programación en C.
