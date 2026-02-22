# Guía del Alumno: Ejecución del Laboratorio "Menú Infinito" en C usando WSL

## 🔍 Objetivo

Esta guía te ayudará a:

* Configurar tu entorno WSL (Windows Subsystem for Linux)
* Instalar GCC si no lo tienes
* Compilar y ejecutar el laboratorio en lenguaje C
* Ver y entender el funcionamiento del menú infinito en terminal de texto

---

## 1. 🌐 Activar WSL (si no está instalado)

Abre PowerShell como administrador y ejecuta:

```powershell
wsl --install
```

> Si ya tienes Ubuntu instalado en WSL, puedes omitir este paso.

Reinicia tu computadora si es necesario.

---

## 2. 🚀 Accede a Ubuntu desde WSL

Abre la terminal de Ubuntu desde el menú inicio:

```
Ubuntu
```

---

## 3. ⚙️ Verifica que GCC esté instalado

En la terminal, escribe:

```bash
gcc --version
```

Deberías ver una salida similar a:

```
gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
```

Si no lo tienes, instálalo con:

```bash
sudo apt update
sudo apt install build-essential
```

---

## 4. 📂 Crea el archivo del laboratorio

Crea un archivo llamado `Lab5_menu_infinito.c` con el código que te proporcionó el profesor. Puedes usar `nano`, `vim` o copiarlo desde Visual Studio Code a la carpeta de WSL.

Ejemplo con nano:

```bash
nano Lab5_menu_infinito.c
```

Pega el código y guarda con `Ctrl + O`, luego `Enter`, y sal con `Ctrl + X`.

---

## 5. 💪 Compila el programa

Ejecuta:

```bash
gcc Lab5_menu_infinito.c -o Lab5_menu_infinito
```

> Este comando genera un ejecutable llamado `Lab5_menu_infinito`

---

## 6. 🚩 Ejecuta el programa

En la misma terminal:

```bash
./Lab5_menu_infinito
```

> Se mostrará un menú de opciones. Usa las flechas para moverte. Presiona Enter para imprimir la opción seleccionada.

---

## 7. 🔍 Validación

Deberías ver:

* Menú siempre visible
* Texto impreso debajo del menú cuando seleccionas una opción
* Movimiento continuo con flechas

---

## 8. 🔧 Solución de errores comunes

* ⚠️ **Error: `no input files`**

  * Solución: Asegúrate de incluir el archivo fuente antes del `-o`
  * Correcto: `gcc Lab5_menu_infinito.c -o Lab5_menu_infinito`

* ⚠️ **Error: `command not found`**

  * Solución: Instala GCC con `sudo apt install build-essential`

---

## 🔹 Recomendaciones Finales

* Guarda cambios constantemente.
* Usa VSCode si prefieres editar código gráficamente en WSL.
* Documenta tu avance en la bitácora del proyecto.

---

Fin de la guía ✅


---

**Autor / Instructor:** Omar Francisco Velazquez Juarez · [ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)  
**Tutoría:** Contacta al instructor por correo para dudas y asesorías.  
**Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)