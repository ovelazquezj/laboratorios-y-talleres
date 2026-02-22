===============================================================================
                    SEMANA 2: MODULACION Y DEMODULACION DIGITAL
                         GUIA PARA EL ESTUDIANTE
===============================================================================

¡Hola! Este paquete contiene tu material de estudio para la Semana 2 del curso
de Comunicaciones e IoT. Vas a aprender a implementar modulación digital
(ASK, FSK, BPSK) en canales con ruido.

===============================================================================
QUE VAS A APRENDER
===============================================================================

- Como convertir ecuaciones matemáticas en código Python funcional
- Implementar moduladores y demoduladores digitales
- Analizar el efecto del ruido en las comunicaciones
- Calcular y interpretar curvas BER (Bit Error Rate)
- Usar herramientas de simulación de sistemas de comunicaciones

===============================================================================
CONTENIDO DE TU PAQUETE
===============================================================================

1. Semana2_Modulacion_AWGN.ipynb     - Tu material de estudio completo
2. semana2_demodulacion_awgn.py      - Tu reto de programación
3. requirements.txt                  - Librerías que necesitas
4. README.txt                        - Esta guía

===============================================================================
ARCHIVO 1: TU MATERIAL DE ESTUDIO (Notebook)
===============================================================================

PARA QUE SIRVE:
Este notebook es tu "libro de texto interactivo". Contiene TODA la teoría
y implementación completa que necesitas saber. Es tu referencia principal.

QUE ENCONTRARAS:
- Las 3 ecuaciones fundamentales explicadas paso a paso
- Código Python que funciona al 100%
- Gráficas que muestran como se ven las señales reales
- Análisis completo de rendimiento (tablas BER)
- Ejemplos visuales de constelaciones

LAS ECUACIONES QUE VAS A DOMINAR:

ASK - Modulación por Amplitud:
   Cuando quieres transmitir '1': enciendes la portadora
   Cuando quieres transmitir '0': apagas la portadora
   Formula: s(t) = A * b(t) * cos(2πfct)

FSK - Modulación por Frecuencia:  
   Cuando quieres transmitir '1': usas frecuencia alta
   Cuando quieres transmitir '0': usas frecuencia baja
   Formula: s(t) = A * cos(2πfit)

BPSK - Modulación por Fase:
   Cuando quieres transmitir '1': fase normal (0°)
   Cuando quieres transmitir '0': fase invertida (180°)
   Formula: s(t) = A * m(t) * cos(2πfct)

COMO USAR TU NOTEBOOK:

OPCION A - Google Colab (MAS FACIL):
1. Ve a https://colab.research.google.com
2. Sube tu archivo Semana2_Modulacion_AWGN.ipynb
3. Ejecuta la primera celda para instalar las librerías
4. Ejecuta todas las celdas una por una (o usa Run All)
5. Observa todas las gráficas que se generan
6. Al final descargarás un archivo CSV con resultados

OPCION B - En tu computadora:
1. Instala Python 3.9 o superior
2. Ejecuta: pip install -r requirements.txt
3. Ejecuta: pip install jupyter
4. Ejecuta: jupyter notebook Semana2_Modulacion_AWGN.ipynb

QUE DEBES HACER CON EL NOTEBOOK:
 Leer cada celda cuidadosamente
 Ejecutar todas las celdas paso a paso
 Estudiar las gráficas generadas
 Entender como cada ecuación se convierte en código
 Tomar notas de los algoritmos de demodulación
 Usar este notebook como tu "hoja de respuestas" cuando hagas el reto

RESULTADOS QUE VERAS:
- Gráficas de bits digitales (0s y 1s como escalones)
- Señales moduladas (ondas sinusoidales con diferentes patrones)
- Señales con ruido (las ondas se ven "sucias")
- Constelación BPSK (puntos dispersos en un plano)
- Tabla mostrando que BPSK es mejor que FSK que es mejor que ASK

===============================================================================
ARCHIVO 2: TU RETO DE PROGRAMACION (Script Python)
===============================================================================

PARA QUE SIRVE:
Aquí es donde vas a demostrar que entendiste la teoría. Tienes que completar
el código siguiendo los algoritmos que te damos paso a paso.

QUE ESTA HECHO (no lo toques):
 Todas las funciones de modulación (ASK, FSK, BPSK)  
 El canal con ruido (AWGN)
 Las gráficas y la interfaz de comandos
 La estructura completa del programa

LO QUE TU DEBES HACER:
 ask_demodulate() - Detector de energía
 fsk_demodulate() - Detector por correlación  
 bpsk_demodulate() - Detector coherente

COMO FUNCIONA TU RETO:

PASO 1 - Entiende el algoritmo:
Cada función tiene el algoritmo escrito en español claro:

Para ASK (detector de energía):
"Si la señal tiene mucha energía, es un '1', si no, es un '0'"

Para FSK (detector por correlación):
"Compara con dos frecuencias de referencia, elige la que se parece más"

Para BPSK (detector coherente):
"Si la señal está en fase, es '1', si está desfasada 180°, es '0'"

PASO 2 - Completa los # TODO:
Dentro de cada función hay comentarios que te dicen exactamente qué hacer:

   # TODO: Calcular índice inicial
   start_idx = i * self.samples_per_bit
   
   # TODO: Extraer segmento de señal  
   bit_signal = received_signal[start_idx:end_idx]
   
   # TODO: Calcular energía
   energy = np.sum(bit_signal**2)

PASO 3 - Prueba tu código:
Usa comandos simples para verificar que funciona.

COMO PROGRAMAR TU RETO:

PREPARACION:
1. Abre una terminal/consola de comandos
2. Navega a la carpeta donde están tus archivos
3. Crea un entorno virtual:
   python -m venv mi_entorno
4. Actívalo:
   Windows: mi_entorno\Scripts\activate
   Mac/Linux: source mi_entorno/bin/activate
5. Instala las librerías:
   pip install -r requirements.txt

TUS PRIMERAS PRUEBAS:

PRUEBA 1 - ¿Funciona mi código?
python semana2_demodulacion_awgn.py --scheme bpsk --snr 10 --N 10 --test

Esto te mostrará:
BITS TRANSMITIDOS: [1 0 1 1 0 1 0 0 1 0]
BITS DETECTADOS:   [1 0 1 1 0 1 0 0 1 0]  (si tu código es correcto)
BER: 0.000000  (¡perfecto!)

PRUEBA 2 - ¿Cómo se ven las gráficas?
python semana2_demodulacion_awgn.py --scheme ask --snr 5 --N 20 --plot

Verás 4 gráficas:
1. Los bits que quieres transmitir (escalones de 0 y 1)
2. La señal modulada sin ruido (ondas limpias)
3. La señal recibida con ruido (ondas "sucias")  
4. Los bits que tu código detectó

PRUEBA 3 - ¿Qué tan bueno es mi algoritmo?
python semana2_demodulacion_awgn.py --scheme fsk --snr 0 --N 1000 --out mis_resultados.csv

Esto probará tu código con 1000 bits y ruido fuerte, y guardará el resultado.

PARAMETROS QUE PUEDES USAR:
--scheme ask        Prueba tu detector ASK
--scheme fsk        Prueba tu detector FSK  
--scheme bpsk       Prueba tu detector BPSK
--snr 10           Ruido suave (fácil)
--snr 0            Ruido medio (normal)
--snr -5           Ruido fuerte (difícil)
--N 100            Pocos bits (pruebas rápidas)
--N 10000          Muchos bits (resultados confiables)
--plot             Muestra gráficas
--test             Muestra bits uno por uno
--out archivo.csv  Guarda resultados

EJEMPLOS PASO A PASO:

EJEMPLO 1 - Empezar con BPSK:
python semana2_demodulacion_awgn.py --scheme bpsk --snr 15 --N 50 --test --plot

¿Por qué BPSK primero? Es el más fácil de programar.
¿Por qué SNR 15? Con poco ruido es más fácil ver si funciona.
¿Por qué N 50? Suficientes bits para ver patrones, no muchos para que sea lento.

EJEMPLO 2 - Probar con ruido:
python semana2_demodulacion_awgn.py --scheme bpsk --snr 0 --N 1000

Una vez que BPSK funciona bien con poco ruido, pruébalo con más ruido.

EJEMPLO 3 - Probar ASK (más difícil):
python semana2_demodulacion_awgn.py --scheme ask --snr 10 --N 100 --plot

ASK es más susceptible al ruido, así que necesita SNR más alto.

COMO SABER SI TU CODIGO ESTA BIEN:

EL PROGRAMA TE DICE AUTOMATICAMENTE:
 "¡EXCELENTE!" si BER < 0.001
 "¡BIEN!" si BER < 0.01  
 "Podría mejorarse" si BER < 0.1
 "Necesita revisión" si BER >= 0.1

VALORES BER ESPERADOS (con N=10000):
SNR=20dB: BER ≈ 0.00001 (casi perfecto)
SNR=10dB: BER ≈ 0.0005 (muy bueno)  
SNR=5dB:  BER ≈ 0.01 (bueno)
SNR=0dB:  BER ≈ 0.05 (aceptable)

PROBLEMAS COMUNES Y SOLUCIONES:

ERROR: "ERROR en tu implementación"
CAUSA: No completaste todos los # TODO
SOLUCION: Revisa que todas las líneas con # TODO tengan código

ERROR: BER = 0.5 exacto
CAUSA: Tu detector siempre dice 0 o siempre dice 1
SOLUCION: Revisa la lógica de decisión (los if/else)

ERROR: BER muy alto (>0.3)
CAUSA: Tienes la lógica invertida
SOLUCION: Revisa que 1 sea 1 y 0 sea 0 en tu decisión

ERROR: "índices fuera de rango"  
CAUSA: Mal cálculo de start_idx o end_idx
SOLUCION: start_idx = i * self.samples_per_bit

CONSEJOS PARA TENER EXITO:

1. LEE EL NOTEBOOK PRIMERO: Es tu "libro de respuestas"
2. EMPIEZA CON BPSK: Es el más fácil de programar
3. USA POCOS BITS PRIMERO: N=10 para debug rápido
4. USA SNR ALTO PRIMERO: SNR=20 para empezar fácil
5. USA --test SIEMPRE: Para ver qué está pasando
6. COMPARA CON EL NOTEBOOK: Tus resultados deben ser similares

===============================================================================
TU PLAN DE TRABAJO SUGERIDO
===============================================================================

SESION 1 (45 minutos): ESTUDIAR
-  Ejecutar completamente el notebook
-  Leer todas las explicaciones
-  Entender las 3 ecuaciones básicas
-  Observar todas las gráficas generadas

SESION 2 (60 minutos): PROGRAMAR BPSK
-  Abrir el archivo semana2_demodulacion_awgn.py
-  Leer el algoritmo de bpsk_demodulate()
-  Completar todos los # TODO de BPSK
-  Probar: python script.py --scheme bpsk --snr 15 --N 20 --test

SESION 3 (45 minutos): PROGRAMAR ASK Y FSK  
-  Completar ask_demodulate()
-  Completar fsk_demodulate()
-  Probar ambos con diferentes SNR

SESION 4 (30 minutos): VALIDAR Y ANALIZAR
-  Comparar tus resultados BER con los del notebook
-  Generar gráficas de verificación
-  Experimentar con diferentes parámetros

CRITERIOS DE EVALUACION:
- ¿Tu código corre sin errores? ✓
- ¿Los 3 detectores dan BER razonable? ✓  
- ¿BPSK da mejor BER que FSK que ASK? ✓
- ¿Entiendes por qué funcionan los algoritmos? ✓

===============================================================================
RECURSOS ADICIONALES
===============================================================================

SI TE ATORAS:
1. Vuelve al notebook y mira cómo está implementado ahí
2. Usa Google para buscar "energy detection algorithm"
3. Consulta el libro del curso
4. Pregunta a tus compañeros de clase

ARCHIVOS QUE VAS A GENERAR:
- Semana2_BER_results.csv (del notebook)
- mis_resultados.csv (del script, si usas --out)
- señales.npy (si usas --export)

QUE HACER DESPUES:
Una vez que domines esto, puedes experimentar con:
- Modulaciones más complejas (QPSK, QAM)
- Diferentes tipos de ruido
- Codificación de canal
- Sincronización

===============================================================================
CONTACTO Y AYUDA
===============================================================================

ANTES DE PEDIR AYUDA:
- ¿Ejecuté completamente el notebook?
- ¿Leí los algoritmos paso a paso?  
- ¿Completé TODOS los # TODO?
- ¿Probé con diferentes valores de SNR y N?
- ¿Comparé mis resultados con el notebook?

DEBUGGING BASICO:
1. Empieza con N=10, SNR=20, usa --test
2. Verifica que start_idx y end_idx son correctos
3. Imprime valores intermedios (energía, correlación)
4. Asegúrate que las referencias (cosenos) son correctas

¡HAPPY HACKING!
Recuerda: la clave está en entender la teoría primero (notebook) 
y luego aplicarla paso a paso (reto de programación).