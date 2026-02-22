import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.patches as patches
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

class DigitalOscilloscope:
    def __init__(self):
        """
        Osciloscopio Digital para Experimentos de Modulación Digital
        Laboratorio: Tipos de datos y modulación digital en canales gaussianos
        """
        # Parámetros de la simulación
        self.fs = 1000  # Frecuencia de muestreo (Hz)
        self.fc = 50    # Frecuencia portadora (Hz)
        self.fb = 5     # Frecuencia de bits (Hz)
        self.duration = 2  # Duración de la señal (s)
        self.snr_db = 20   # Relación señal-ruido en dB
        
        # Datos binarios a transmitir
        self.data_bits = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
        
        # Variables de estado
        self.modulation_type = 'ASK'
        self.show_noise = True
        self.show_detection = True
        
        # Configurar la interfaz
        self.setup_gui()
        self.update_signals()
        
    def setup_gui(self):
        """Configurar la interfaz gráfica del osciloscopio"""
        # Crear figura principal más amplia
        self.fig = plt.figure(figsize=(18, 10))
        #self.fig.suptitle('OSCILOSCOPIO DIGITAL - MODULACIÓN EN CANALES GAUSSIANOS', 
        #                 fontsize=14, fontweight='bold', y=0.95)
        
        # Crear subplots con mejor distribución
        gs = self.fig.add_gridspec(3, 4, height_ratios=[1.2, 1.2, 0.6], 
                                  width_ratios=[1.2, 1.2, 1.2, 0.8], 
                                  hspace=0.35, wspace=0.25,
                                  top=0.90, bottom=0.08, left=0.06, right=0.96)
        
        # Señales principales (2x2 grid para las gráficas)
        self.ax_original = self.fig.add_subplot(gs[0, 0])
        self.ax_noisy = self.fig.add_subplot(gs[0, 1]) 
        self.ax_detected = self.fig.add_subplot(gs[1, 0])
        self.ax_constellation = self.fig.add_subplot(gs[1, 1])
        
        # Panel de controles (columna derecha, ocupando altura completa)
        self.ax_controls = self.fig.add_subplot(gs[0:2, 3])
        self.ax_controls.axis('off')
        
        # Panel de información de parámetros (segunda columna derecha)
        self.ax_params = self.fig.add_subplot(gs[0:2, 2])
        self.ax_params.axis('off')
        
        # Panel de métricas (fila inferior, ocupando 3 columnas)
        self.ax_metrics = self.fig.add_subplot(gs[2, 0:3])
        self.ax_metrics.axis('off')
        
        # Configurar controles
        self.setup_controls()
        
    def display_lab_info(self):
        """Mostrar información del laboratorio y preguntas guía"""
        info_text = """
        EXPERIMENTO: MODULACIÓN DIGITAL EN CANALES GAUSSIANOS
        
        PREGUNTAS PARA FORMULAR HIPÓTESIS:
        
        1. ¿Cuál de las modulaciones (ASK, FSK, PSK) será más robusta ante el ruido? ¿Por qué?
        2. ¿Cómo afectará el incremento del ruido (menor SNR) a la forma de onda de cada modulación?
        3. ¿A qué valor de SNR comenzarán a aparecer errores de detección significativos?
        4. ¿Qué diferencias esperarías ver en las constelaciones de cada modulación con ruido?
        5. ¿Cómo se relaciona la separación entre símbolos con la robustez ante ruido?
        
        INSTRUCCIONES: Ajusta los parámetros y observa cómo el ruido gaussiano afecta cada tipo de modulación.
        """
        
        self.ax_info.text(0.02, 0.95, info_text, transform=self.ax_info.transAxes,
                         fontsize=10, verticalalignment='top', fontfamily='monospace',
                         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
    def setup_controls(self):
        """Configurar controles interactivos"""
        # === PANEL DE CONTROLES ===
        self.ax_controls.text(0.5, 0.95, 'CONTROLES', ha='center', 
                             fontweight='bold', fontsize=12, 
                             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
        # Selector de modulación (más compacto)
        ax_radio = plt.axes([0.78, 0.75, 0.18, 0.12])  # [x, y, width, height]
        self.radio_mod = RadioButtons(ax_radio, ('ASK', 'FSK', 'PSK'))
        self.radio_mod.on_clicked(self.change_modulation)
        
        # Slider SNR (horizontal)
        ax_snr = plt.axes([0.78, 0.65, 0.18, 0.03])
        self.slider_snr = Slider(ax_snr, 'SNR (dB)', -10, 30, valinit=self.snr_db, 
                                valfmt='%0.1f dB')
        self.slider_snr.on_changed(self.change_snr)
        
        # Slider frecuencia portadora
        ax_fc = plt.axes([0.78, 0.58, 0.18, 0.03])
        self.slider_fc = Slider(ax_fc, 'Fc (Hz)', 20, 100, valinit=self.fc,
                               valfmt='%0.0f Hz')
        self.slider_fc.on_changed(self.change_fc)
        
        # Botones organizados horizontalmente
        ax_btn_noise = plt.axes([0.78, 0.48, 0.08, 0.04])
        self.btn_noise = Button(ax_btn_noise, 'Ruido\nON/OFF')
        self.btn_noise.on_clicked(self.toggle_noise)
        
        ax_btn_detect = plt.axes([0.88, 0.48, 0.08, 0.04])
        self.btn_detect = Button(ax_btn_detect, 'Detect\nON/OFF')
        self.btn_detect.on_clicked(self.toggle_detection)
        
        # Botón para nuevos datos
        ax_btn_data = plt.axes([0.78, 0.40, 0.18, 0.04])
        self.btn_data = Button(ax_btn_data, 'Generar Nuevos Datos')
        self.btn_data.on_clicked(self.generate_new_data)
        
        # === PANEL DE PARÁMETROS ===
        self.ax_params.text(0.5, 0.95, 'PARÁMETROS ACTUALES', ha='center',
                           fontweight='bold', fontsize=11,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
        
        # Área de texto para parámetros
        self.param_text = self.ax_params.text(0.05, 0.85, '', fontsize=10, 
                                             verticalalignment='top', fontfamily='monospace')
        
        # === INFORMACIÓN EXPERIMENTAL (en panel de parámetros) ===
        experiment_info = """
PREGUNTAS GUÍA:

¿Cuál modulación es más robusta?
¿Cómo afecta el SNR al BER?
¿Qué muestra la constelación?
¿Cuándo aparecen errores?

INSTRUCCIONES:
• Cambia modulación con botones
• Ajusta SNR y observa efectos  
• Compara constelaciones
• Registra tus observaciones
        """
        
        self.ax_params.text(0.05, 0.45, experiment_info, fontsize=9,
                           verticalalignment='top', 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    
    def update_parameters(self):
        """Actualizar información de parámetros en el panel"""
        param_info = f"""Modulación: {self.modulation_type}
SNR: {self.snr_db:.1f} dB
Fc: {self.fc:.0f} Hz  |  Fb: {self.fb:.1f} Hz

Estado:
• Ruido: {'ON' if self.show_noise else 'OFF'}
• Detección: {'ON' if self.show_detection else 'OFF'}

Datos: {len(self.data_bits)} bits
Secuencia: {' '.join(map(str, self.data_bits))}
Duración: {self.duration:.1f}s"""
        
        if hasattr(self, 'param_text'):
            self.param_text.set_text(param_info)
        
    def generate_time_vector(self):
        """Generar vector de tiempo"""
        return np.linspace(0, self.duration, int(self.fs * self.duration))
    
    def generate_data_signal(self, t):
        """Generar señal de datos binarios"""
        bit_duration = 1 / self.fb
        data_signal = np.zeros_like(t)
        
        for i, bit in enumerate(self.data_bits):
            start_idx = int(i * bit_duration * self.fs)
            end_idx = int((i + 1) * bit_duration * self.fs)
            if end_idx > len(data_signal):
                end_idx = len(data_signal)
            data_signal[start_idx:end_idx] = bit
            
        return data_signal
    
    def modulate_ask(self, data, t):
        """Modulación ASK (Amplitude Shift Keying)"""
        carrier = np.cos(2 * np.pi * self.fc * t)
        # ASK: A1 para '1', A0 para '0' (A0 = 0.1*A1 para visibilidad)
        modulated = np.where(data == 1, 1.0 * carrier, 0.1 * carrier)
        return modulated
    
    def modulate_fsk(self, data, t):
        """Modulación FSK (Frequency Shift Keying)"""
        f1 = self.fc          # Frecuencia para '1'
        f0 = self.fc * 0.7    # Frecuencia para '0'
        
        modulated = np.zeros_like(t)
        for i in range(len(t)):
            if data[i] == 1:
                modulated[i] = np.cos(2 * np.pi * f1 * t[i])
            else:
                modulated[i] = np.cos(2 * np.pi * f0 * t[i])
                
        return modulated
    
    def modulate_psk(self, data, t):
        """Modulación PSK (Phase Shift Keying)"""
        carrier = np.cos(2 * np.pi * self.fc * t)
        # PSK: fase 0 para '1', fase π para '0'
        modulated = np.where(data == 1, carrier, -carrier)
        return modulated
    
    def add_gaussian_noise(self, signal):
        """Añadir ruido gaussiano AWGN"""
        if not self.show_noise:
            return signal, np.zeros_like(signal)
            
        # Calcular potencia de la señal
        signal_power = np.mean(signal**2)
        
        # Calcular potencia del ruido basada en SNR
        snr_linear = 10**(self.snr_db/10)
        noise_power = signal_power / snr_linear
        
        # Generar ruido gaussiano
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        
        return signal + noise, noise
    
    def detect_signal(self, noisy_signal, t):
        """Detectar señal usando detección coherente"""
        if not self.show_detection:
            return np.zeros_like(noisy_signal)
            
        bit_duration = 1 / self.fb
        detected_bits = []
        
        for i in range(len(self.data_bits)):
            start_idx = int(i * bit_duration * self.fs)
            end_idx = int((i + 1) * bit_duration * self.fs)
            if end_idx > len(noisy_signal):
                end_idx = len(noisy_signal)
                
            segment = noisy_signal[start_idx:end_idx]
            t_segment = t[start_idx:end_idx]
            
            if self.modulation_type == 'ASK':
                # Detección por energía
                energy = np.mean(segment**2)
                threshold = 0.25  # Umbral adaptativo
                detected_bit = 1 if energy > threshold else 0
                
            elif self.modulation_type == 'FSK':
                # Detección por correlación con frecuencias
                f1_ref = np.cos(2 * np.pi * self.fc * t_segment)
                f0_ref = np.cos(2 * np.pi * self.fc * 0.7 * t_segment)
                
                corr_f1 = np.abs(np.mean(segment * f1_ref))
                corr_f0 = np.abs(np.mean(segment * f0_ref))
                
                detected_bit = 1 if corr_f1 > corr_f0 else 0
                
            elif self.modulation_type == 'PSK':
                # Detección por correlación
                ref_signal = np.cos(2 * np.pi * self.fc * t_segment)
                correlation = np.mean(segment * ref_signal)
                detected_bit = 1 if correlation > 0 else 0
                
            detected_bits.append(detected_bit)
        
        # Reconstruir señal detectada
        detected_signal = np.zeros_like(t)
        for i, bit in enumerate(detected_bits):
            start_idx = int(i * bit_duration * self.fs)
            end_idx = int((i + 1) * bit_duration * self.fs)
            if end_idx > len(detected_signal):
                end_idx = len(detected_signal)
            detected_signal[start_idx:end_idx] = bit
            
        return detected_signal
    
    def calculate_ber(self, detected_signal, t):
        """Calcular tasa de error de bits (BER)"""
        bit_duration = 1 / self.fb
        detected_bits = []
        
        for i in range(len(self.data_bits)):
            start_idx = int(i * bit_duration * self.fs)
            end_idx = int((i + 1) * bit_duration * self.fs)
            if end_idx > len(detected_signal):
                end_idx = len(detected_signal)
            
            bit_value = np.mean(detected_signal[start_idx:end_idx])
            detected_bits.append(1 if bit_value > 0.5 else 0)
        
        errors = sum(1 for orig, det in zip(self.data_bits, detected_bits) if orig != det)
        ber = errors / len(self.data_bits)
        
        return ber, detected_bits
    
    def create_constellation(self, modulated_signal, noisy_signal):
        """Crear diagrama de constelación"""
        if self.modulation_type == 'ASK':
            # Para ASK, mostrar amplitudes
            constellation_orig = []
            constellation_noisy = []
            
            bit_duration = 1 / self.fb
            for i in range(len(self.data_bits)):
                start_idx = int(i * bit_duration * self.fs)
                end_idx = int((i + 1) * bit_duration * self.fs)
                if end_idx > len(modulated_signal):
                    end_idx = len(modulated_signal)
                
                # Muestrear en el centro del bit
                mid_idx = (start_idx + end_idx) // 2
                constellation_orig.append(modulated_signal[mid_idx])
                constellation_noisy.append(noisy_signal[mid_idx])
                
            return np.array(constellation_orig), np.array(constellation_noisy), None, None
            
        elif self.modulation_type == 'PSK':
            # Para PSK, mostrar fase (I/Q)
            I_orig, Q_orig = [], []
            I_noisy, Q_noisy = [], []
            
            bit_duration = 1 / self.fb
            t = self.generate_time_vector()
            
            for i in range(len(self.data_bits)):
                start_idx = int(i * bit_duration * self.fs)
                end_idx = int((i + 1) * bit_duration * self.fs)
                if end_idx > len(modulated_signal):
                    end_idx = len(modulated_signal)
                
                # Demodulación coherente
                t_seg = t[start_idx:end_idx]
                cos_ref = np.cos(2 * np.pi * self.fc * t_seg)
                sin_ref = -np.sin(2 * np.pi * self.fc * t_seg)
                
                I_orig.append(np.mean(modulated_signal[start_idx:end_idx] * cos_ref))
                Q_orig.append(np.mean(modulated_signal[start_idx:end_idx] * sin_ref))
                I_noisy.append(np.mean(noisy_signal[start_idx:end_idx] * cos_ref))
                Q_noisy.append(np.mean(noisy_signal[start_idx:end_idx] * sin_ref))
                
            return np.array(I_orig), np.array(I_noisy), np.array(Q_orig), np.array(Q_noisy)
            
        else:  # FSK
            # Para FSK, mostrar energías de frecuencias
            f1_energy_orig, f0_energy_orig = [], []
            f1_energy_noisy, f0_energy_noisy = [], []
            
            bit_duration = 1 / self.fb
            t = self.generate_time_vector()
            
            for i in range(len(self.data_bits)):
                start_idx = int(i * bit_duration * self.fs)
                end_idx = int((i + 1) * bit_duration * self.fs)
                if end_idx > len(modulated_signal):
                    end_idx = len(modulated_signal)
                
                t_seg = t[start_idx:end_idx]
                f1_ref = np.cos(2 * np.pi * self.fc * t_seg)
                f0_ref = np.cos(2 * np.pi * self.fc * 0.7 * t_seg)
                
                f1_energy_orig.append(np.abs(np.mean(modulated_signal[start_idx:end_idx] * f1_ref)))
                f0_energy_orig.append(np.abs(np.mean(modulated_signal[start_idx:end_idx] * f0_ref)))
                f1_energy_noisy.append(np.abs(np.mean(noisy_signal[start_idx:end_idx] * f1_ref)))
                f0_energy_noisy.append(np.abs(np.mean(noisy_signal[start_idx:end_idx] * f0_ref)))
                
            return np.array(f1_energy_orig), np.array(f1_energy_noisy), \
                   np.array(f0_energy_orig), np.array(f0_energy_noisy)
    
    def setup_controls(self):
        """Configurar controles del osciloscopio"""
        # Crear áreas para controles
        ax_radio = plt.axes([0.72, 0.65, 0.15, 0.12])
        self.radio_mod = RadioButtons(ax_radio, ('ASK', 'FSK', 'PSK'))
        self.radio_mod.on_clicked(self.change_modulation)
        
        # Slider para SNR
        ax_snr = plt.axes([0.72, 0.55, 0.15, 0.03])
        self.slider_snr = Slider(ax_snr, 'SNR (dB)', -10, 30, valinit=self.snr_db)
        self.slider_snr.on_changed(self.change_snr)
        
        # Slider para frecuencia portadora
        ax_fc = plt.axes([0.72, 0.48, 0.15, 0.03])
        self.slider_fc = Slider(ax_fc, 'Fc (Hz)', 20, 100, valinit=self.fc)
        self.slider_fc.on_changed(self.change_fc)
        
        # Botones
        ax_btn_noise = plt.axes([0.72, 0.40, 0.07, 0.04])
        self.btn_noise = Button(ax_btn_noise, 'Ruido')
        self.btn_noise.on_clicked(self.toggle_noise)
        
        ax_btn_detect = plt.axes([0.80, 0.40, 0.07, 0.04])
        self.btn_detect = Button(ax_btn_detect, 'Detect')
        self.btn_detect.on_clicked(self.toggle_detection)
        
        # Botón para nuevos datos
        ax_btn_data = plt.axes([0.72, 0.32, 0.15, 0.04])
        self.btn_data = Button(ax_btn_data, 'Nuevos Datos')
        self.btn_data.on_clicked(self.generate_new_data)
    
    def change_modulation(self, label):
        """Cambiar tipo de modulación"""
        self.modulation_type = label
        self.update_signals()
    
    def change_snr(self, val):
        """Cambiar SNR"""
        self.snr_db = val
        self.update_signals()
    
    def change_fc(self, val):
        """Cambiar frecuencia portadora"""
        self.fc = val
        self.update_signals()
    
    def toggle_noise(self, event):
        """Activar/desactivar ruido"""
        self.show_noise = not self.show_noise
        self.update_signals()
    
    def toggle_detection(self, event):
        """Activar/desactivar detección"""
        self.show_detection = not self.show_detection
        self.update_signals()
    
    def generate_new_data(self, event):
        """Generar nueva secuencia de datos"""
        self.data_bits = np.random.randint(0, 2, 10)
        self.update_signals()
    
    def update_signals(self):
        """Actualizar todas las señales y gráficas"""
        # Generar vector de tiempo
        t = self.generate_time_vector()
        
        # Generar señal de datos
        data_signal = self.generate_data_signal(t)
        
        # Modular según el tipo seleccionado
        if self.modulation_type == 'ASK':
            modulated_signal = self.modulate_ask(data_signal, t)
        elif self.modulation_type == 'FSK':
            modulated_signal = self.modulate_fsk(data_signal, t)
        else:  # PSK
            modulated_signal = self.modulate_psk(data_signal, t)
        
        # Añadir ruido
        noisy_signal, noise = self.add_gaussian_noise(modulated_signal)
        
        # Detectar señal
        detected_signal = self.detect_signal(noisy_signal, t)
        
        # Calcular BER
        ber, detected_bits = self.calculate_ber(detected_signal, t)
        
        # Actualizar gráficas
        self.plot_signals(t, data_signal, modulated_signal, noisy_signal, 
                         detected_signal, noise)
        self.plot_constellation(modulated_signal, noisy_signal, t)
        self.update_metrics(ber, detected_bits)
        self.update_parameters()
        
        self.fig.canvas.draw()
    
    def plot_signals(self, t, data_signal, modulated_signal, noisy_signal, 
                    detected_signal, noise):
        """Graficar todas las señales en el osciloscopio"""
        
        # Señal original modulada
        self.ax_original.clear()
        self.ax_original.plot(t, modulated_signal, 'b-', linewidth=2, label=f'{self.modulation_type} Original')
        self.ax_original.plot(t, data_signal - 1.5, 'k-', linewidth=2, label='Datos Binarios')
        self.ax_original.set_title(f'Señal {self.modulation_type} Original', fontweight='bold')
        self.ax_original.set_ylabel('Amplitud')
        self.ax_original.grid(True, alpha=0.3)
        self.ax_original.legend(fontsize=8)
        self.ax_original.set_ylim(-2.5, 1.5)
        
        # Señal con ruido
        self.ax_noisy.clear()
        self.ax_noisy.plot(t, noisy_signal, 'r-', linewidth=1.5, alpha=0.8, 
                          label=f'{self.modulation_type} + Ruido')
        if self.show_noise:
            self.ax_noisy.plot(t, noise, 'g-', linewidth=1, alpha=0.6, label='Ruido AWGN')
        self.ax_noisy.set_title(f'Señal con Ruido Gaussiano (SNR={self.snr_db:.1f}dB)', 
                               fontweight='bold')
        self.ax_noisy.set_ylabel('Amplitud')
        self.ax_noisy.grid(True, alpha=0.3)
        self.ax_noisy.legend(fontsize=8)
        
        # Señal detectada
        self.ax_detected.clear()
        if self.show_detection:
            self.ax_detected.plot(t, detected_signal, 'g-', linewidth=3, 
                                 label='Señal Detectada')
        self.ax_detected.plot(t, data_signal, 'k--', linewidth=2, alpha=0.7, 
                             label='Datos Originales')
        self.ax_detected.set_title('Proceso de Detección', fontweight='bold')
        self.ax_detected.set_xlabel('Tiempo (s)')
        self.ax_detected.set_ylabel('Amplitud')
        self.ax_detected.grid(True, alpha=0.3)
        self.ax_detected.legend(fontsize=8)
    
    def plot_constellation(self, modulated_signal, noisy_signal, t):
        """Graficar diagrama de constelación"""
        self.ax_constellation.clear()
        
        # Obtener puntos de constelación
        const_orig, const_noisy, const_orig_q, const_noisy_q = \
            self.create_constellation(modulated_signal, noisy_signal)
        
        if self.modulation_type == 'ASK':
            # Diagrama unidimensional para ASK
            y_jitter_orig = np.random.normal(0, 0.01, len(const_orig))
            y_jitter_noisy = np.random.normal(0, 0.01, len(const_noisy))
            
            self.ax_constellation.scatter(const_orig, y_jitter_orig, c='blue', 
                                        s=50, alpha=0.8, label='Original')
            if self.show_noise:
                self.ax_constellation.scatter(const_noisy, y_jitter_noisy, c='red', 
                                            s=30, alpha=0.6, label='Con Ruido')
            
            self.ax_constellation.set_xlabel('Amplitud')
            self.ax_constellation.set_ylabel('Perturbación')
            self.ax_constellation.set_title('Constelación ASK')
            
        elif self.modulation_type == 'PSK':
            # Diagrama I-Q para PSK
            self.ax_constellation.scatter(const_orig, const_orig_q, c='blue', 
                                        s=50, alpha=0.8, label='Original')
            if self.show_noise:
                self.ax_constellation.scatter(const_noisy, const_noisy_q, c='red', 
                                            s=30, alpha=0.6, label='Con Ruido')
            
            self.ax_constellation.set_xlabel('I (En Fase)')
            self.ax_constellation.set_ylabel('Q (Cuadratura)')
            self.ax_constellation.set_title('Constelación PSK')
            self.ax_constellation.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax_constellation.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
        else:  # FSK
            # Diagrama de energías para FSK
            self.ax_constellation.scatter(const_orig, const_orig_q, c='blue', 
                                        s=50, alpha=0.8, label='Original')
            if self.show_noise:
                self.ax_constellation.scatter(const_noisy, const_noisy_q, c='red', 
                                            s=30, alpha=0.6, label='Con Ruido')
            
            self.ax_constellation.set_xlabel('Energía F1')
            self.ax_constellation.set_ylabel('Energía F0')
            self.ax_constellation.set_title('Constelación FSK')
        
        self.ax_constellation.grid(True, alpha=0.3)
        self.ax_constellation.legend(fontsize=8)
    
    def update_metrics(self, ber, detected_bits):
        """Actualizar panel de métricas"""
        self.ax_metrics.clear()
        self.ax_metrics.axis('off')
        
        # Calcular métricas adicionales
        snr_linear = 10**(self.snr_db/10)
        theoretical_ber = 0.5 * np.exp(-snr_linear/2)  # Aproximación para BPSK
        
        # Mostrar métricas
        metrics_text = f"""
        Datos Originales: {' '.join(map(str, self.data_bits))}
        Datos Detectados: {' '.join(map(str, detected_bits))}
        BER Medido: {ber:.3f} ({int(ber*100)}% de error)
        BER Teórico: {theoretical_ber:.3f} (aproximado)
        SNR: {self.snr_db:.1f} dB ({snr_linear:.2f} lineal)
        Frecuencia Portadora: {self.fc:.1f} Hz
        Frecuencia de Bits: {self.fb:.1f} Hz
        ANÁLISIS:
        Robustez: {'ALTA' if ber < 0.1 else 'MEDIA' if ber < 0.3 else 'BAJA'}
        Estado del Canal: {'BUENO' if self.snr_db > 15 else 'REGULAR' if self.snr_db > 5 else 'MALO'}
        """
        
        self.ax_metrics.text(0.02, 0.95, metrics_text, transform=self.ax_metrics.transAxes,
                           fontsize=10, verticalalignment='top', fontfamily='monospace',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
    
    def update_parameters(self):
        """Actualizar información de parámetros en el panel de control"""
        param_info = f"""
CONFIGURACIÓN:
Modulación: {self.modulation_type}
SNR: {self.snr_db:.1f} dB
Fc: {self.fc:.1f} Hz
Fb: {self.fb:.1f} Hz

ESTADO:
Ruido: {'ON' if self.show_noise else 'OFF'}
Detección: {'ON' if self.show_detection else 'OFF'}

DATOS:
Bits: {len(self.data_bits)}
Duración: {self.duration}s
        """
        
        if hasattr(self, 'param_text'):
            self.param_text.set_text(param_info)
    
    def run(self):
        """Ejecutar el osciloscopio"""
        print("="*60)
        print("OSCILOSCOPIO DIGITAL - MODULACIÓN EN CANALES GAUSSIANOS")
        print("="*60)
        print("\nINSTRUCCIONES DE USO:")
        print("1. Usa los controles para cambiar modulación (ASK/FSK/PSK)")
        print("2. Ajusta el SNR para simular diferentes niveles de ruido")
        print("3. Modifica la frecuencia portadora")
        print("4. Activa/desactiva ruido y detección")
        print("5. Genera nuevas secuencias de datos")
        print("\nOBSERVA:")
        print("- Formas de onda en tiempo real")
        print("- Diagramas de constelación")
        print("- Métricas de rendimiento (BER)")
        print("- Efectos del ruido gaussiano")
        print("\n¡Experimenta y formula tus hipótesis!")
        print("="*60)
        
        plt.show()

# Clase adicional para análisis avanzado
class ModulationAnalyzer:
    """Analizador avanzado para comparar técnicas de modulación"""
    
    @staticmethod
    def compare_modulations(snr_range=np.arange(-10, 21, 2)):
        """Comparar BER teórico vs práctico para diferentes modulaciones"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Datos de prueba
        test_data = np.random.randint(0, 2, 100)
        
        ber_ask = []
        ber_fsk = []
        ber_psk = []
        
        for snr_db in snr_range:
            # Simular cada modulación
            oscilloscope = DigitalOscilloscope()
            oscilloscope.snr_db = snr_db
            oscilloscope.data_bits = test_data[:10]  # Usar primeros 10 bits
            
            t = oscilloscope.generate_time_vector()
            data_signal = oscilloscope.generate_data_signal(t)
            
            # ASK
            oscilloscope.modulation_type = 'ASK'
            mod_ask = oscilloscope.modulate_ask(data_signal, t)
            noisy_ask, _ = oscilloscope.add_gaussian_noise(mod_ask)
            det_ask = oscilloscope.detect_signal(noisy_ask, t)
            ber_ask_val, _ = oscilloscope.calculate_ber(det_ask, t)
            ber_ask.append(ber_ask_val)
            
            # FSK
            oscilloscope.modulation_type = 'FSK'
            mod_fsk = oscilloscope.modulate_fsk(data_signal, t)
            noisy_fsk, _ = oscilloscope.add_gaussian_noise(mod_fsk)
            det_fsk = oscilloscope.detect_signal(noisy_fsk, t)
            ber_fsk_val, _ = oscilloscope.calculate_ber(det_fsk, t)
            ber_fsk.append(ber_fsk_val)
            
            # PSK
            oscilloscope.modulation_type = 'PSK'
            mod_psk = oscilloscope.modulate_psk(data_signal, t)
            noisy_psk, _ = oscilloscope.add_gaussian_noise(mod_psk)
            det_psk = oscilloscope.detect_signal(noisy_psk, t)
            ber_psk_val, _ = oscilloscope.calculate_ber(det_psk, t)
            ber_psk.append(ber_psk_val)
        
        # Graficar comparación BER
        ax1.semilogy(snr_range, ber_ask, 'b-o', label='ASK', linewidth=2)
        ax1.semilogy(snr_range, ber_fsk, 'g-s', label='FSK', linewidth=2)
        ax1.semilogy(snr_range, ber_psk, 'r-^', label='PSK', linewidth=2)
        
        # BER teórico para BPSK (referencia)
        snr_linear = 10**(snr_range/10)
        ber_theoretical = 0.5 * np.exp(-snr_linear/2)
        ax1.semilogy(snr_range, ber_theoretical, 'k--', alpha=0.7, 
                    label='BPSK Teórico')
        
        ax1.set_xlabel('SNR (dB)')
        ax1.set_ylabel('BER (Tasa de Error de Bits)')
        ax1.set_title('Comparación de Robustez ante Ruido')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_ylim(1e-3, 1)
        
        # Espectro de potencia
        oscilloscope_demo = DigitalOscilloscope()
        t_demo = oscilloscope_demo.generate_time_vector()
        data_demo = oscilloscope_demo.generate_data_signal(t_demo)
        
        # Calcular espectros
        freqs = np.fft.fftfreq(len(t_demo), 1/oscilloscope_demo.fs)
        freqs = freqs[:len(freqs)//2]  # Solo frecuencias positivas
        
        for mod_type, color in [('ASK', 'blue'), ('FSK', 'green'), ('PSK', 'red')]:
            oscilloscope_demo.modulation_type = mod_type
            if mod_type == 'ASK':
                modulated = oscilloscope_demo.modulate_ask(data_demo, t_demo)
            elif mod_type == 'FSK':
                modulated = oscilloscope_demo.modulate_fsk(data_demo, t_demo)
            else:
                modulated = oscilloscope_demo.modulate_psk(data_demo, t_demo)
            
            spectrum = np.fft.fft(modulated)
            spectrum = np.abs(spectrum[:len(spectrum)//2])
            spectrum_db = 20 * np.log10(spectrum + 1e-10)
            
            ax2.plot(freqs, spectrum_db, color=color, linewidth=2, 
                    alpha=0.8, label=f'{mod_type}')
        
        ax2.set_xlabel('Frecuencia (Hz)')
        ax2.set_ylabel('Magnitud (dB)')
        ax2.set_title('Espectro de Potencia')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_xlim(0, 150)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def noise_analysis():
        """Análisis detallado del ruido gaussiano"""
        
        # Generar ruido gaussiano
        samples = 10000
        noise = np.random.normal(0, 1, samples)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Histograma del ruido
        ax1.hist(noise, bins=50, density=True, alpha=0.7, color='lightblue', 
                edgecolor='black')
        x_gauss = np.linspace(-4, 4, 100)
        y_gauss = (1/np.sqrt(2*np.pi)) * np.exp(-0.5 * x_gauss**2)
        ax1.plot(x_gauss, y_gauss, 'r-', linewidth=2, label='Gaussiana Teórica')
        ax1.set_title('Distribución del Ruido AWGN')
        ax1.set_xlabel('Amplitud')
        ax1.set_ylabel('Densidad de Probabilidad')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Serie temporal del ruido
        time_samples = np.arange(0, 200)
        ax2.plot(time_samples, noise[:200], 'g-', linewidth=1)
        ax2.set_title('Muestra Temporal del Ruido')
        ax2.set_xlabel('Muestra')
        ax2.set_ylabel('Amplitud')
        ax2.grid(True, alpha=0.3)
        
        # Espectro del ruido
        freqs = np.fft.fftfreq(len(noise), 1)
        freqs = freqs[:len(freqs)//2]
        noise_spectrum = np.abs(np.fft.fft(noise))[:len(freqs)]
        
        ax3.plot(freqs[:1000], noise_spectrum[:1000], 'purple', linewidth=1)
        ax3.set_title('Espectro del Ruido (Banda Blanca)')
        ax3.set_xlabel('Frecuencia Normalizada')
        ax3.set_ylabel('Magnitud')
        ax3.grid(True, alpha=0.3)
        
        # Autocorrelación
        autocorr = np.correlate(noise, noise, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        lags = np.arange(0, min(100, len(autocorr)))
        
        ax4.plot(lags, autocorr[lags], 'orange', linewidth=2)
        ax4.set_title('Autocorrelación del Ruido')
        ax4.set_xlabel('Lag')
        ax4.set_ylabel('Autocorrelación')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Función principal para ejecutar el experimento
def run_modulation_experiment():
    """
    Función principal para ejecutar el experimento de laboratorio
    """
    print("INICIANDO EXPERIMENTO DE MODULACIÓN DIGITAL")
    print("==========================================")
    
    # Crear osciloscopio principal
    oscilloscope = DigitalOscilloscope()
    
    # Mostrar osciloscopio interactivo
    print("\n1. Abriendo Osciloscopio Digital Interactivo...")
    oscilloscope.run()
    
    # Ejecutar análisis comparativo
    print("\n2. ¿Deseas ejecutar análisis comparativo? (y/n)")
    response = input().lower()
    if response == 'y' or response == 'yes':
        print("Ejecutando análisis comparativo...")
        ModulationAnalyzer.compare_modulations()
    
    # Ejecutar análisis de ruido
    print("\n3. ¿Deseas analizar las propiedades del ruido gaussiano? (y/n)")
    response = input().lower()
    if response == 'y' or response == 'yes':
        print("Analizando ruido gaussiano...")
        ModulationAnalyzer.noise_analysis()

# Función de demostración rápida
def quick_demo():
    """Demostración rápida del experimento"""
    print("DEMOSTRACIÓN RÁPIDA - MODULACIÓN DIGITAL")
    print("=======================================")
    
    # Crear instancia del osciloscopio
    osc = DigitalOscilloscope()
    
    # Demostrar cada tipo de modulación
    modulations = ['ASK', 'FSK', 'PSK']
    snr_levels = [20, 10, 0]  # Diferentes niveles de ruido
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('DEMOSTRACIÓN: EFECTOS DEL RUIDO EN MODULACIONES DIGITALES', 
                fontsize=16, fontweight='bold')
    
    for i, mod_type in enumerate(modulations):
        for j, snr in enumerate(snr_levels):
            ax = axes[i, j]
            
            # Configurar parámetros
            osc.modulation_type = mod_type
            osc.snr_db = snr
            osc.show_noise = True
            
            # Generar señales
            t = osc.generate_time_vector()
            data_signal = osc.generate_data_signal(t)
            
            if mod_type == 'ASK':
                modulated = osc.modulate_ask(data_signal, t)
            elif mod_type == 'FSK':
                modulated = osc.modulate_fsk(data_signal, t)
            else:
                modulated = osc.modulate_psk(data_signal, t)
            
            noisy_signal, noise = osc.add_gaussian_noise(modulated)
            
            # Graficar
            ax.plot(t, modulated, 'b-', linewidth=1, alpha=0.7, label='Original')
            ax.plot(t, noisy_signal, 'r-', linewidth=1.5, label='Con Ruido')
            ax.set_title(f'{mod_type} - SNR={snr}dB')
            ax.set_ylabel('Amplitud')
            if i == 2:  # Última fila
                ax.set_xlabel('Tiempo (s)')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)
            ax.set_xlim(0, 1)  # Mostrar solo primer segundo
    
    plt.tight_layout()
    plt.show()

# Función educativa con explicaciones
def educational_guide():
    """Guía educativa con explicaciones teóricas"""
    
    explanations = {
        'canal_gaussiano': """
        CANAL GAUSSIANO:
        Un canal gaussiano es un modelo matemático donde la señal transmitida
        se ve afectada por ruido blanco gaussiano aditivo (AWGN).
        
        Características:
        - Ruido con distribución normal (gaussiana)
        - Media cero y varianza constante
        - Independiente de la señal transmitida
        - Modelo realista para muchos sistemas de comunicación
        """,
        
        'modulaciones': """
        TÉCNICAS DE MODULACIÓN DIGITAL:
        
        ASK (Amplitude Shift Keying):
        - Varía la amplitud de la portadora
        - '1' → Amplitud alta, '0' → Amplitud baja
        - Sensible a variaciones de amplitud y ruido
        
        FSK (Frequency Shift Keying):
        - Varía la frecuencia de la portadora
        - '1' → Frecuencia f1, '0' → Frecuencia f0
        - Más robusta que ASK ante ruido de amplitud
        
        PSK (Phase Shift Keying):
        - Varía la fase de la portadora
        - '1' → Fase 0°, '0' → Fase 180°
        - Generalmente la más robusta ante ruido
        """,
        
        'snr': """
        RELACIÓN SEÑAL-RUIDO (SNR):
        
        SNR = 10 * log10(Potencia_Señal / Potencia_Ruido)
        
        Interpretación:
        - SNR alto (>20dB): Canal de buena calidad
        - SNR medio (10-20dB): Canal regular
        - SNR bajo (<10dB): Canal ruidoso
        
        Impacto en BER:
        - Mayor SNR → Menor BER
        - Relación exponencial inversa
        """,
        
        'deteccion': """
        DETECCIÓN DE SEÑALES:
        
        Proceso para recuperar datos originales:
        1. Demodulación coherente/no coherente
        2. Filtrado y muestreo
        3. Decisión binaria (umbralización)
        
        Errores comunes:
        - Umbral inadecuado
        - Sincronización perdida
        - Ruido excesivo
        - Interferencia intersimbólica
        """
    }
    
    print("GUÍA EDUCATIVA - MODULACIÓN DIGITAL")
    print("="*50)
    
    for topic, explanation in explanations.items():
        print(f"\n{explanation}")
        input("Presiona Enter para continuar...")
    
    print("\n¡Ahora estás listo para el experimento!")

# Ejecutar el experimento completo
if __name__ == "__main__":
    print("LABORATORIO DE MODULACIÓN DIGITAL")
    print("=================================")
    print("\nSelecciona una opción:")
    print("1. Experimento completo (recomendado)")
    print("2. Demostración rápida")
    print("3. Guía educativa")
    print("4. Solo osciloscopio interactivo")
    
    try:
        choice = input("\nIngresa tu opción (1-4): ").strip()
        
        if choice == '1':
            educational_guide()
            run_modulation_experiment()
        elif choice == '2':
            quick_demo()
        elif choice == '3':
            educational_guide()
        elif choice == '4':
            oscilloscope = DigitalOscilloscope()
            oscilloscope.run()
        else:
            print("Opción no válida. Ejecutando experimento completo...")
            run_modulation_experiment()
            
    except KeyboardInterrupt:
        print("\n\nExperimento terminado por el usuario.")
    except Exception as e:
        print(f"\nError en el experimento: {e}")
        print("Ejecutando modo de seguridad...")
        oscilloscope = DigitalOscilloscope()
        oscilloscope.run()
