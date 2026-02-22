import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, TextBox
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
        self.modulation_type = 'PSK'
        self.show_noise = True
        self.show_detection = True
        
        # Historial para análisis comparativo
        self.ber_history = {'ASK': [], 'FSK': [], 'PSK': []}
        self.snr_history = []
        
        # Configurar la interfaz
        self.setup_gui()
        self.update_signals()
        
    def setup_gui(self):
        """Configurar la interfaz gráfica del osciloscopio"""
        # Crear figura principal más grande
        self.fig = plt.figure(figsize=(20, 14))
        
        # Crear subplots con mejor distribución
        gs = self.fig.add_gridspec(4, 4, 
                                  height_ratios=[1.2, 1.2, 1.2, 0.8], 
                                  width_ratios=[1, 1, 1, 0.8], 
                                  hspace=0.3, wspace=0.3,
                                  left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        # Señales principales
        self.ax_original = self.fig.add_subplot(gs[0, :2])
        self.ax_noisy = self.fig.add_subplot(gs[1, :2])
        self.ax_detected = self.fig.add_subplot(gs[2, :2])
        self.ax_constellation = self.fig.add_subplot(gs[0:2, 2])
        
        # Panel de controles
        self.ax_controls = self.fig.add_subplot(gs[2:4, 2:])
        self.ax_controls.axis('off')
        
        # Panel de métricas optimizado
        self.ax_metrics = self.fig.add_subplot(gs[3, :2])
        self.ax_metrics.axis('off')
        
        # Configurar controles
        self.setup_controls()
        
    def setup_controls(self):
        """Configurar controles interactivos con campos de entrada de texto"""
        # Limpiar área de controles
        self.ax_controls.clear()
        self.ax_controls.axis('off')
        
        # Selector de modulación con índice correcto
        ax_radio = plt.axes([0.78, 0.70, 0.15, 0.12])
        # Determinar índice activo actual
        active_index = {'ASK': 0, 'FSK': 1, 'PSK': 2}[self.modulation_type]
        self.radio_mod = RadioButtons(ax_radio, ('ASK', 'FSK', 'PSK'), active=active_index)
        self.radio_mod.on_clicked(self.change_modulation)
        
        # CAMPO DE ENTRADA PARA SNR (en lugar de slider)
        ax_snr_label = plt.axes([0.78, 0.62, 0.06, 0.03])
        ax_snr_label.text(0.1, 0.5, 'SNR (dB):', fontsize=10, ha='left', va='center')
        ax_snr_label.axis('off')
        
        ax_snr_input = plt.axes([0.85, 0.62, 0.08, 0.03])
        self.textbox_snr = TextBox(ax_snr_input, '', initial=str(self.snr_db))
        self.textbox_snr.on_submit(self.change_snr_text)
        
        # CAMPO DE ENTRADA PARA FC (en lugar de slider)
        ax_fc_label = plt.axes([0.78, 0.57, 0.06, 0.03])
        ax_fc_label.text(0.1, 0.5, 'Fc (Hz):', fontsize=10, ha='left', va='center')
        ax_fc_label.axis('off')
        
        ax_fc_input = plt.axes([0.85, 0.57, 0.08, 0.03])
        self.textbox_fc = TextBox(ax_fc_input, '', initial=str(int(self.fc)))
        self.textbox_fc.on_submit(self.change_fc_text)
        
        # BOTONES CON MAYOR ALTURA para mostrar dos líneas de texto
        ax_btn_noise = plt.axes([0.78, 0.45, 0.07, 0.08])  # Altura aumentada de 0.04 a 0.08
        noise_status = 'ON' if self.show_noise else 'OFF'
        self.btn_noise = Button(ax_btn_noise, f'Ruido\n{noise_status}')
        self.btn_noise.on_clicked(self.toggle_noise)
        
        ax_btn_detect = plt.axes([0.86, 0.45, 0.07, 0.08])  # Altura aumentada de 0.04 a 0.08
        detect_status = 'ON' if self.show_detection else 'OFF'
        self.btn_detect = Button(ax_btn_detect, f'Detect\n{detect_status}')
        self.btn_detect.on_clicked(self.toggle_detection)
        
        ax_btn_data = plt.axes([0.78, 0.35, 0.15, 0.06])
        self.btn_data = Button(ax_btn_data, 'Generar Nuevos Datos')
        self.btn_data.on_clicked(self.generate_new_data)
        
        # Información compacta de parámetros
        param_info = f"""Modulación: {self.modulation_type}
SNR: {self.snr_db:.1f} dB | Fc: {self.fc:.0f} Hz
Ruido: {'ON' if self.show_noise else 'OFF'}
Detección: {'ON' if self.show_detection else 'OFF'}

Datos: {' '.join(map(str, self.data_bits))}"""
        
        self.ax_controls.text(0.02, 0.25, param_info, 
                             transform=self.ax_controls.transAxes,
                             fontsize=9, verticalalignment='top', 
                             fontfamily='monospace',
                             bbox=dict(boxstyle="round,pad=0.3", 
                                     facecolor="lightgray", alpha=0.7))
        
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
    
    def change_modulation(self, label):
        """Cambiar tipo de modulación"""
        self.modulation_type = label
        self.update_signals()
    
    def change_snr_text(self, text):
        """Cambiar SNR mediante entrada de texto (rango extendido para laboratorio)"""
        try:
            new_snr = float(text)
            if -15 <= new_snr <= 30:  # Rango extendido para experimentos
                self.snr_db = new_snr
                self.update_signals()
        except ValueError:
            pass
    
    def change_fc_text(self, text):
        """Cambiar frecuencia portadora mediante entrada de texto (rango extendido)"""
        try:
            new_fc = float(text)
            if 20 <= new_fc <= 120:  # Rango extendido para experimentos
                self.fc = new_fc
                self.update_signals()
        except ValueError:
            pass
    
    def toggle_noise(self, event):
        """Activar/desactivar ruido"""
        self.show_noise = not self.show_noise
        # Actualizar el texto del botón
        noise_status = 'ON' if self.show_noise else 'OFF'
        self.btn_noise.label.set_text(f'Ruido\n{noise_status}')
        self.update_signals()
    
    def toggle_detection(self, event):
        """Activar/desactivar detección"""
        self.show_detection = not self.show_detection
        # Actualizar el texto del botón
        detect_status = 'ON' if self.show_detection else 'OFF'
        self.btn_detect.label.set_text(f'Detect\n{detect_status}')
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
        self.setup_controls()  # Actualizar información de controles
        
        self.fig.canvas.draw()
    
    def plot_signals(self, t, data_signal, modulated_signal, noisy_signal, 
                    detected_signal, noise):
        """Graficar todas las señales en el osciloscopio"""
        
        # Señal original modulada
        self.ax_original.clear()
        self.ax_original.plot(t, modulated_signal, 'b-', linewidth=2, 
                             label=f'{self.modulation_type} Original')
        self.ax_original.plot(t, data_signal - 1.5, 'k-', linewidth=2, 
                             label='Datos Binarios')
        self.ax_original.set_title(f'Modulación {self.modulation_type} - Señal Original', 
                                  fontweight='bold', fontsize=12)
        self.ax_original.set_ylabel('Amplitud', fontsize=11)
        self.ax_original.grid(True, alpha=0.3)
        self.ax_original.legend(fontsize=10)
        self.ax_original.set_ylim(-2.5, 1.5)
        
        # Señal con ruido
        self.ax_noisy.clear()
        self.ax_noisy.plot(t, noisy_signal, 'r-', linewidth=1.5, alpha=0.8, 
                          label=f'{self.modulation_type} + Ruido')
        if self.show_noise:
            self.ax_noisy.plot(t, noise, 'g-', linewidth=1, alpha=0.6, 
                              label='Ruido AWGN')
        self.ax_noisy.set_title(f'Canal Gaussiano - SNR={self.snr_db:.1f}dB', 
                               fontweight='bold', fontsize=12)
        self.ax_noisy.set_ylabel('Amplitud', fontsize=11)
        self.ax_noisy.grid(True, alpha=0.3)
        self.ax_noisy.legend(fontsize=10)
        
        # Señal detectada
        self.ax_detected.clear()
        if self.show_detection:
            self.ax_detected.plot(t, detected_signal, 'g-', linewidth=3, 
                                 label='Señal Detectada')
        self.ax_detected.plot(t, data_signal, 'k--', linewidth=2, alpha=0.7, 
                             label='Datos Originales')
        self.ax_detected.set_title('Proceso de Detección y Recuperación', fontweight='bold', fontsize=12)
        self.ax_detected.set_xlabel('Tiempo (s)', fontsize=11)
        self.ax_detected.set_ylabel('Amplitud', fontsize=11)
        self.ax_detected.grid(True, alpha=0.3)
        self.ax_detected.legend(fontsize=10)
    
    def plot_constellation(self, modulated_signal, noisy_signal, t):
        """Graficar diagrama de constelación con análisis para laboratorio"""
        self.ax_constellation.clear()
        
        # Obtener puntos de constelación
        const_orig, const_noisy, const_orig_q, const_noisy_q = \
            self.create_constellation(modulated_signal, noisy_signal)
        
        if self.modulation_type == 'ASK':
            # Diagrama unidimensional para ASK
            y_jitter_orig = np.random.normal(0, 0.01, len(const_orig))
            y_jitter_noisy = np.random.normal(0, 0.01, len(const_noisy))
            
            self.ax_constellation.scatter(const_orig, y_jitter_orig, c='blue', 
                                        s=80, alpha=0.8, label='Original')
            if self.show_noise:
                self.ax_constellation.scatter(const_noisy, y_jitter_noisy, c='red', 
                                            s=50, alpha=0.6, label='Con Ruido')
                
                # Análisis para laboratorio: separación de clusters ASK
                amp_0_points = const_noisy[np.where(np.array(self.data_bits) == 0)]
                amp_1_points = const_noisy[np.where(np.array(self.data_bits) == 1)]
                if len(amp_0_points) > 0 and len(amp_1_points) > 0:
                    separation = np.abs(np.mean(amp_1_points) - np.mean(amp_0_points))
                    self.ax_constellation.set_title(f'Constelación ASK - Separación: {separation:.3f}', 
                                                  fontweight='bold', fontsize=12)
            
            self.ax_constellation.set_xlabel('Amplitud', fontsize=11)
            self.ax_constellation.set_ylabel('Perturbación', fontsize=11)
            if not self.show_noise:
                self.ax_constellation.set_title('Constelación ASK', fontweight='bold', fontsize=12)
            
        elif self.modulation_type == 'PSK':
            # Diagrama I-Q para PSK con análisis de dispersión
            self.ax_constellation.scatter(const_orig, const_orig_q, c='blue', 
                                        s=80, alpha=0.8, label='Original')
            if self.show_noise:
                self.ax_constellation.scatter(const_noisy, const_noisy_q, c='red', 
                                            s=50, alpha=0.6, label='Con Ruido')
                
                # Análisis para laboratorio: dispersión angular
                angles = np.arctan2(const_noisy_q, const_noisy)
                angle_std = np.std(angles) * 180 / np.pi
                self.ax_constellation.set_title(f'Constelación PSK - Dispersión: {angle_std:.1f}°', 
                                              fontweight='bold', fontsize=12)
            
            self.ax_constellation.set_xlabel('I (En Fase)', fontsize=11)
            self.ax_constellation.set_ylabel('Q (Cuadratura)', fontsize=11)
            if not self.show_noise:
                self.ax_constellation.set_title('Constelación PSK', fontweight='bold', fontsize=12)
            self.ax_constellation.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax_constellation.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            # Círculo de referencia para PSK
            circle = plt.Circle((0, 0), 0.5, fill=False, color='gray', linestyle='--', alpha=0.5)
            self.ax_constellation.add_patch(circle)
            
        else:  # FSK
            # Diagrama de energías para FSK
            self.ax_constellation.scatter(const_orig, const_orig_q, c='blue', 
                                        s=80, alpha=0.8, label='Original')
            if self.show_noise:
                self.ax_constellation.scatter(const_noisy, const_noisy_q, c='red', 
                                            s=50, alpha=0.6, label='Con Ruido')
                
                # Análisis para laboratorio: separación de clusters FSK
                cluster_distance = np.mean(np.abs(const_noisy - const_noisy_q))
                self.ax_constellation.set_title(f'Constelación FSK - Separación: {cluster_distance:.3f}', 
                                              fontweight='bold', fontsize=12)
            
            self.ax_constellation.set_xlabel('Energía F1', fontsize=11)
            self.ax_constellation.set_ylabel('Energía F0', fontsize=11)
            if not self.show_noise:
                self.ax_constellation.set_title('Constelación FSK', fontweight='bold', fontsize=12)
        
        self.ax_constellation.grid(True, alpha=0.3)
        self.ax_constellation.legend(fontsize=10)
        
        # Línea diagonal para FSK (ayuda visual)
        if self.modulation_type == 'FSK':
            max_val = max(np.max(const_orig), np.max(const_orig_q)) if len(const_orig) > 0 else 1
            self.ax_constellation.plot([0, max_val], [max_val, 0], 'k--', alpha=0.3, label='Decisión')
    
    def update_metrics(self, ber, detected_bits):
        """Panel de métricas DISTRIBUIDO EN TRES COLUMNAS SIN SOLAPAMIENTO"""
        self.ax_metrics.clear()
        self.ax_metrics.axis('off')
        
        # Calcular métricas adicionales
        snr_linear = 10**(self.snr_db/10)
        theoretical_ber = 0.5 * np.exp(-snr_linear/2) if self.modulation_type == 'PSK' else None
        errors = sum(1 for orig, det in zip(self.data_bits, detected_bits) if orig != det)
        
        # Análisis de calidad para el laboratorio
        if ber <= 0.01:
            quality = "EXCELENTE"
        elif ber <= 0.05:
            quality = "BUENA"
        elif ber <= 0.10:
            quality = "REGULAR"
        elif ber <= 0.30:
            quality = "MALA"
        else:
            quality = "CRÍTICA"
        
        # Análisis específico por modulación para el laboratorio
        robustez_analysis = ""
        if self.modulation_type == 'ASK':
            robustez_analysis = "ASK: Sensible a ruido de amplitud"
        elif self.modulation_type == 'FSK':
            f1 = self.fc
            f0 = self.fc * 0.7
            ratio = f1/f0
            robustez_analysis = f"FSK: f1/f0={ratio:.2f}, Robusta vs amplitud"
        elif self.modulation_type == 'PSK':
            robustez_analysis = "PSK: Amplitud constante, sensible a fase"
        
        # COLUMNAS BIEN DISTRIBUIDAS SIN SOLAPAMIENTO
        # Columna 1: posición 0.01 - 0.30 (29% del ancho)
        col1_text = f"""DATOS Y ANÁLISIS:
Original: {' '.join(map(str, self.data_bits))}
Detectado: {' '.join(map(str, detected_bits))}
Errores: {errors}/{len(self.data_bits)} bits
{robustez_analysis[:25]}"""
        
        # Columna 2: posición 0.32 - 0.61 (29% del ancho) - MOVIDA MÁS A LA IZQUIERDA
        col2_text = f"""RENDIMIENTO:
BER: {ber:.3f} ({ber*100:.1f}%)
Calidad: {quality}
Umbral 10%: {'✓' if ber <= 0.1 else '✗'}
{'BER Teór: '+str(theoretical_ber)[:5] if theoretical_ber else 'BER Teór: N/A'}"""
        
        # Columna 3: posición 0.63 - 0.98 (35% del ancho)
        col3_text = f"""CANAL Y CONFIG:
SNR: {self.snr_db:.1f} dB ({snr_linear:.1f} lin.)
Estado: {'BUENO' if self.snr_db > 15 else 'REGULAR' if self.snr_db > 5 else 'MALO' if self.snr_db > -5 else 'CRÍTICO'}
Fc: {self.fc:.0f} Hz | Fb: {self.fb:.0f} Hz
Cycles/bit: {int(self.fc/self.fb)} aprox"""
        
        # Posicionar las tres columnas SIN SOLAPAMIENTO
        self.ax_metrics.text(0.01, 0.85, col1_text, transform=self.ax_metrics.transAxes,
                           fontsize=8, verticalalignment='top', fontfamily='monospace',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
        self.ax_metrics.text(0.32, 0.85, col2_text, transform=self.ax_metrics.transAxes,
                           fontsize=8, verticalalignment='top', fontfamily='monospace',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
        
        self.ax_metrics.text(0.63, 0.85, col3_text, transform=self.ax_metrics.transAxes,
                           fontsize=8, verticalalignment='top', fontfamily='monospace',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

def run_oscilloscope():
    """Función principal para ejecutar el osciloscopio"""
    # Crear instancia del osciloscopio
    oscilloscope = DigitalOscilloscope()
    
    # Mostrar la interfaz
    plt.show()
    
    return oscilloscope

# Ejecutar el osciloscopio si el script se ejecuta directamente
if __name__ == "__main__":
    osc = run_oscilloscope()
