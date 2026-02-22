Evaluación – Semana 3
Tema: Modelo de Comunicación Digital

Objetivo:
Implementar paso a paso los componentes del modelo digital de comunicación:
Emisor → Codificador → Modulador → Canal → Demodulador → Decodificador → Receptor

Estructura del repositorio:
- semana3_modelo_comunicacion.ipynb → Notebook guía para repaso de conceptos
- semana3_evaluacion_modelo_comunicacion.py → Archivo de evaluación a completar
- README.txt → Instrucciones generales
- environment.yml → Archivo para crear entorno de trabajo reproducible

-----------------------------------------------------
🔧 Configuración del entorno con Conda
-----------------------------------------------------

1. Asegúrate de tener Miniconda o Anaconda instalado en tu equipo.

2. Abre una terminal y navega a la carpeta donde descargaste los archivos.

3. Crea el entorno con:

   conda env create -f environment.yml

4. Activa el entorno con:

   conda activate modelo_digital

6. Modifica el archivo `.py` desde tu IDE de preferencia

-----------------------------------------------------
Instrucciones para la evaluación
-----------------------------------------------------

1. Abre el archivo `semana3_evaluacion_modelo_comunicacion.py`.

2. Deberás implementar las siguientes funciones siguiendo los algoritmos descritos en los comentarios:
   - `emisor(texto)`
   - `codificador(bits, samples_per_bit=100)`
   - `decodificador(senal_envolvente, samples_per_bit=100)`
   - `receptor(bits)`

   Las funciones `modulador`, `canal` y `demodulador` ya están implementadas como apoyo.

3. Cada función incluye:
   - Un glosario de términos clave
   - Un algoritmo paso a paso que debes traducir a código

4. Una vez que hayas completado las funciones, crea un bloque `main` al final del archivo:
   - Ingresa una cadena corta, por ejemplo: `"Hola"`
   - Procesa la cadena a través de todos los bloques
   - Imprime la cadena original y la reconstruida al final

-----------------------------------------------------
Evaluación
-----------------------------------------------------
- Tu entrega debe incluir el archivo `.py` completo con tu implementación.
- El resultado final debe imprimir la cadena original y la recibida sin errores.
- Se evaluará:
   ✔ Correcta interpretación del modelo
   ✔ Traducción clara de los algoritmos a código
   ✔ Modularidad y organización del programa

-----------------------------------------------------
Recomendaciones
-----------------------------------------------------
- No modifiques la estructura ni borres los comentarios guía.
- Usa el notebook de repaso (`.ipynb`) como referencia conceptual y visual.
- Apóyate en matplotlib para visualizar señales si es necesario.
- El entorno creado con `environment.yml` asegura compatibilidad y reproducibilidad.
