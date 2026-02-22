"""
Experimento de Resonancia con Ondas Sonoras
Para clase de Ingeniería - Física de Ondas

Autor: Script generado para experimento educativo
Detecta automáticamente bocina Bluetooth y permite estudiar resonancia
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from scipy import signal
from scipy.fft import fft, fftfreq
import queue
import sys

class ExperimentoResonancia:
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 0.1  # Buffer de tamaño normal
        self.buffer_size = int(self.sample_rate * self.duration)
        self.frequency = 440.0  # Frecuencia inicial (La)
        self.amplitude = 0.3
        self.is_generating = False
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.phase = 0.0  # Para continuidad de fase
        
        # Variables para análisis
        self.frequencies = []
        self.magnitudes = []
        self.resonance_peaks = []
        
        # Configurar dispositivos de audio
        self.setup_audio_devices()
        
        # Crear interfaz gráfica
        self.create_gui()
        
    def setup_audio_devices(self):
        """Detecta y configura dispositivos de audio disponibles"""
        print("🎵 Detectando dispositivos de audio...")
        try:
            devices = sd.query_devices()
            
            self.output_devices = []
            self.input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    self.output_devices.append((i, device['name']))
                    print(f"🔊 Salida disponible [{i}]: {device['name']} (Canales: {device['max_output_channels']})")
                if device['max_input_channels'] > 0:
                    self.input_devices.append((i, device['name']))
            
            # Buscar dispositivos reales (no los virtuales de Realtek que causan problemas)
            self.bluetooth_devices = []
            valid_devices = []
            
            # Palabras clave para dispositivos Bluetooth/inalámbricos reales
            bluetooth_keywords = ['bluetooth', 'bt', 'wireless', 'airpods', 'buds', 'earphone', 'beats', 'sony', 'jbl', 'bose']
            
            # Palabras clave para evitar dispositivos virtuales problemáticos
            avoid_keywords = ['realtek', 'sst', 'virtual', 'wave', 'line']
            
            for idx, name in self.output_devices:
                name_lower = name.lower()
                
                # Verificar que no sea un dispositivo virtual problemático
                is_problematic = any(keyword in name_lower for keyword in avoid_keywords)
                
                # Verificar si es Bluetooth real
                is_bluetooth = any(keyword in name_lower for keyword in bluetooth_keywords)
                
                if is_bluetooth and not is_problematic:
                    self.bluetooth_devices.append((idx, name))
                    print(f"📱 Dispositivo Bluetooth real detectado: {name}")
                elif not is_problematic:
                    valid_devices.append((idx, name))
            
            # Seleccionar dispositivo automáticamente
            if self.bluetooth_devices:
                # Usar primer dispositivo Bluetooth real
                self.selected_output = self.bluetooth_devices[0][0]
                print(f"🎧 Seleccionado automáticamente: {self.bluetooth_devices[0][1]}")
            elif valid_devices:
                # Usar primer dispositivo válido que no sea problemático
                self.selected_output = valid_devices[0][0]
                print(f"🔊 Usando dispositivo válido: {valid_devices[0][1]}")
            else:
                # Usar dispositivo por defecto del sistema
                self.selected_output = None
                default_device = sd.query_devices(kind='output')
                print(f"🔊 Usando dispositivo por defecto: {default_device['name']}")
                
        except Exception as e:
            print(f"⚠️ Error al detectar dispositivos: {e}")
            self.selected_output = None
            self.bluetooth_devices = []
    
    def create_gui(self):
        """Crear la interfaz gráfica del experimento"""
        self.root = tk.Tk()
        self.root.title("🎵 Experimento de Resonancia - Física de Ondas")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="Experimento de Resonancia", 
                              font=('Arial', 20, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Análisis de Ondas Sonoras - Clase de Ingeniería", 
                                 font=('Arial', 12), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack()
        
        # Frame para controles
        control_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        control_frame.pack(pady=10, padx=20, fill='x')
        
        # Control de frecuencia
        freq_frame = tk.Frame(control_frame, bg='#34495e')
        freq_frame.pack(pady=10)
        
        tk.Label(freq_frame, text="Frecuencia (Hz):", font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(side='left', padx=5)
        
        self.freq_var = tk.StringVar(value=str(self.frequency))
        freq_entry = tk.Entry(freq_frame, textvariable=self.freq_var, font=('Arial', 12), width=8)
        freq_entry.pack(side='left', padx=5)
        
        # Botones de frecuencias preestablecidas
        preset_frame = tk.Frame(control_frame, bg='#34495e')
        preset_frame.pack(pady=5)
        
        presets = [
            ("Do (261.63 Hz)", 261.63),
            ("Re (293.66 Hz)", 293.66),
            ("Mi (329.63 Hz)", 329.63),
            ("Fa (349.23 Hz)", 349.23),
            ("Sol (392.00 Hz)", 392.00),
            ("La (440.00 Hz)", 440.00),
            ("Si (493.88 Hz)", 493.88)
        ]
        
        for name, freq in presets:
            btn = tk.Button(preset_frame, text=name, 
                           command=lambda f=freq: self.set_frequency(f),
                           bg='#3498db', fg='white', font=('Arial', 9))
            btn.pack(side='left', padx=2, pady=2)
        
        # Control de amplitud
        amp_frame = tk.Frame(control_frame, bg='#34495e')
        amp_frame.pack(pady=10)
        
        tk.Label(amp_frame, text="Amplitud:", font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(side='left', padx=5)
        
        self.amp_scale = tk.Scale(amp_frame, from_=0.1, to=1.0, resolution=0.1, 
                                 orient='horizontal', bg='#34495e', fg='#ecf0f1',
                                 command=self.update_amplitude)
        self.amp_scale.set(self.amplitude)
        self.amp_scale.pack(side='left', padx=5)
        
        # Botones de control
        button_frame = tk.Frame(control_frame, bg='#34495e')
        button_frame.pack(pady=10)
        
        self.generate_btn = tk.Button(button_frame, text="▶️ Generar Tono", 
                                     command=self.toggle_generation,
                                     bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                     width=15)
        self.generate_btn.pack(side='left', padx=5)
        
        self.record_btn = tk.Button(button_frame, text="🎤 Grabar Respuesta", 
                                   command=self.toggle_recording,
                                   bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                                   width=15)
        self.record_btn.pack(side='left', padx=5)
        
        self.analyze_btn = tk.Button(button_frame, text="📊 Analizar Resonancia", 
                                    command=self.analyze_resonance,
                                    bg='#9b59b6', fg='white', font=('Arial', 12, 'bold'),
                                    width=15)
        self.analyze_btn.pack(side='left', padx=5)
        
        self.devices_btn = tk.Button(button_frame, text="🎧 Cambiar Audio", 
                                    command=self.show_device_selector,
                                    bg='#f39c12', fg='white', font=('Arial', 12, 'bold'),
                                    width=15)
        self.devices_btn.pack(side='left', padx=5)
        
        # Frame para información de dispositivos
        device_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        device_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(device_frame, text="🎧 Dispositivos de Audio", 
                font=('Arial', 14, 'bold'), fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        # Lista de dispositivos Bluetooth
        if self.bluetooth_devices:
            for idx, name in self.bluetooth_devices:
                status = "✅ SELECCIONADO" if idx == self.selected_output else "⭕ Disponible"
                tk.Label(device_frame, text=f"{status}: {name}", 
                        font=('Arial', 10), fg='#bdc3c7', bg='#34495e').pack()
        else:
            tk.Label(device_frame, text="⚠️ Usando dispositivo por defecto", 
                    font=('Arial', 10), fg='#f39c12', bg='#34495e').pack()
        
        # Frame para información del experimento
        info_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        info_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(info_frame, text="📚 Información del Experimento", 
                font=('Arial', 14, 'bold'), fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        info_text = """
🎯 OBJETIVO: Estudiar el fenómeno de resonancia en ondas sonoras

🔬 PROCEDIMIENTO:
1. Selecciona una frecuencia objetivo
2. Activa 'Generar Tono' para emitir la onda por la bocina Bluetooth
3. Coloca tu diapasón cerca de la bocina
4. Usa 'Grabar Respuesta' para capturar la respuesta del sistema
5. Analiza los resultados para identificar frecuencias de resonancia

📊 ANÁLISIS:
- El espectro de frecuencias mostrará picos en las frecuencias de resonancia
- Las amplitudes indican la intensidad de la resonancia
- Compara diferentes frecuencias para encontrar las resonancias naturales

⚠️  NOTA: Asegúrate de que tu diapasón esté correctamente montado y que
la bocina Bluetooth esté conectada y cerca del micrófono.
        """
        
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('Arial', 10), fg='#bdc3c7', bg='#34495e',
                             justify='left', anchor='w')
        info_label.pack(pady=5, padx=10, fill='both')
    
    def show_device_selector(self):
        """Mostrar selector de dispositivos de audio"""
        device_window = tk.Toplevel(self.root)
        device_window.title("🎧 Selector de Dispositivos de Audio")
        device_window.geometry("600x400")
        device_window.configure(bg='#2c3e50')
        
        title_label = tk.Label(device_window, text="Seleccionar Dispositivo de Salida", 
                              font=('Arial', 16, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Frame para lista de dispositivos
        devices_frame = tk.Frame(device_window, bg='#34495e', relief='raised', bd=2)
        devices_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Variable para selección
        self.device_var = tk.IntVar(value=self.selected_output if self.selected_output else -1)
        
        tk.Label(devices_frame, text="Dispositivos de Salida Disponibles:", 
                font=('Arial', 12, 'bold'), fg='#ecf0f1', bg='#34495e').pack(pady=10)
        
        # Opción para dispositivo por defecto
        default_rb = tk.Radiobutton(devices_frame, text="🔊 Dispositivo por Defecto del Sistema", 
                                   variable=self.device_var, value=-1,
                                   font=('Arial', 11), fg='#ecf0f1', bg='#34495e',
                                   selectcolor='#3498db', activebackground='#34495e')
        default_rb.pack(anchor='w', padx=20, pady=5)
        
        # Lista todos los dispositivos de salida
        for idx, name in self.output_devices:
            # Identificar si es probable que sea Bluetooth/inalámbrico
            is_wireless = any(keyword in name.lower() for keyword in 
                            ['bluetooth', 'bt', 'wireless', 'headphone', 'speaker', 'airpods', 'buds'])
            icon = "📱" if is_wireless else "🔊"
            
            rb = tk.Radiobutton(devices_frame, text=f"{icon} {name}", 
                               variable=self.device_var, value=idx,
                               font=('Arial', 10), fg='#bdc3c7', bg='#34495e',
                               selectcolor='#3498db', activebackground='#34495e',
                               wraplength=500)
            rb.pack(anchor='w', padx=20, pady=2)
        
        # Botón para aplicar selección
        button_frame = tk.Frame(device_window, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        test_btn = tk.Button(button_frame, text="🔧 Probar Dispositivo", 
                            command=lambda: self.test_audio_device(),
                            bg='#3498db', fg='white', font=('Arial', 11))
        test_btn.pack(side='left', padx=10)
        
        apply_btn = tk.Button(button_frame, text="✅ Aplicar Selección", 
                             command=lambda: self.apply_device_selection(device_window),
                             bg='#27ae60', fg='white', font=('Arial', 12, 'bold'))
        apply_btn.pack(side='left', padx=10)
    
    def test_audio_device(self):
        """Probar el dispositivo seleccionado con un tono corto"""
        selected_idx = self.device_var.get()
        test_device = selected_idx if selected_idx != -1 else None
        
        try:
            print(f"🔧 Probando dispositivo...")
            
            # Generar tono de prueba limpio de 1 segundo
            duration = 1.0
            test_freq = 440.0
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            
            # Generar onda sinusoidal pura sin envelope complicado
            test_wave = 0.3 * np.sin(2 * np.pi * test_freq * t)
            
            # Solo aplicar fade muy corto al inicio y final para evitar click inicial/final
            fade_samples = int(self.sample_rate * 0.01)  # 10ms
            test_wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
            test_wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Reproducir tono de prueba
            sd.play(test_wave, samplerate=self.sample_rate, device=test_device)
            
            messagebox.showinfo("Prueba de Audio", 
                               f"🎵 Reproduciendo tono limpio (La - 440 Hz)\n"
                               f"¿Se escucha claro y sin ruido?")
            
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            messagebox.showerror("Error de Prueba", 
                               f"No se pudo probar el dispositivo:\n{e}\n\n"
                               f"Este dispositivo probablemente no funcione.")
    
    def apply_device_selection(self, window):
        """Aplicar selección de dispositivo"""
        selected_idx = self.device_var.get()
        
        if selected_idx == -1:
            self.selected_output = None
            device_name = "Dispositivo por Defecto"
        else:
            self.selected_output = selected_idx
            device_name = next(name for idx, name in self.output_devices if idx == selected_idx)
        
        print(f"🎧 Dispositivo seleccionado: {device_name}")
        messagebox.showinfo("Dispositivo Cambiado", f"Dispositivo de audio cambiado a:\n{device_name}")
        window.destroy()
    
    def set_frequency(self, freq):
        """Establecer frecuencia preestablecida"""
        self.frequency = freq
        self.freq_var.set(str(freq))
        print(f"🎵 Frecuencia establecida: {freq} Hz")
    
    def update_amplitude(self, value):
        """Actualizar amplitud"""
        self.amplitude = float(value)
        print(f"🔊 Amplitud: {self.amplitude}")
    
    def generate_sine_wave(self, freq, duration, amplitude):
        """Generar onda sinusoidal"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = amplitude * np.sin(2 * np.pi * freq * t)
        return wave
    
    def toggle_generation(self):
        """Alternar generación de audio"""
        if not self.is_generating:
            try:
                self.frequency = float(self.freq_var.get())
                self.start_generation()
                self.generate_btn.config(text="⏹️ Detener Tono", bg='#e74c3c')
                print(f"🎵 Generando tono de {self.frequency} Hz")
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa una frecuencia válida")
        else:
            self.stop_generation()
            self.generate_btn.config(text="▶️ Generar Tono", bg='#27ae60')
            print("⏹️ Generación detenida")
    
    def start_generation(self):
        """Iniciar generación continua de audio"""
        self.is_generating = True
        self.phase = 0.0  # Reiniciar fase
        
        def audio_callback(outdata, frames, time, status):
            if status:
                print(f"⚠️ Status: {status}")
            
            if self.is_generating:
                # Generar índices de tiempo continuos
                indices = np.arange(frames) + self.phase * self.sample_rate / (2 * np.pi * self.frequency)
                
                # Generar onda sinusoidal pura
                wave = self.amplitude * np.sin(2 * np.pi * self.frequency * indices / self.sample_rate)
                
                # Actualizar fase para el siguiente buffer (mantener continuidad)
                self.phase += 2 * np.pi * self.frequency * frames / self.sample_rate
                
                outdata[:, 0] = wave
            else:
                outdata.fill(0)
        
        # Intentar abrir el stream con manejo de errores
        try:
            # Validar dispositivo primero
            if self.selected_output is not None:
                device_info = sd.query_devices(self.selected_output)
                print(f"🎧 Intentando usar: {device_info['name']}")
                
                # Verificar que el dispositivo soporte salida
                if device_info['max_output_channels'] < 1:
                    raise sd.PortAudioError("El dispositivo no soporta salida de audio", -9999)
            
            self.output_stream = sd.OutputStream(
                device=self.selected_output,
                samplerate=self.sample_rate,
                channels=1,
                callback=audio_callback,
                blocksize=self.buffer_size
            )
            self.output_stream.start()
            print(f"✅ Stream de audio iniciado correctamente")
            
        except sd.PortAudioError as e:
            print(f"❌ Error de PortAudio: {e}")
            self.is_generating = False
            
            # Intentar con dispositivo por defecto
            try:
                print("🔄 Intentando con dispositivo por defecto...")
                self.selected_output = None
                
                self.output_stream = sd.OutputStream(
                    device=None,  # Dispositivo por defecto
                    samplerate=self.sample_rate,
                    channels=1,
                    callback=audio_callback,
                    blocksize=self.buffer_size
                )
                self.output_stream.start()
                self.is_generating = True
                print("✅ Usando dispositivo por defecto exitosamente")
                
                messagebox.showinfo("Dispositivo Cambiado", 
                    "El dispositivo seleccionado no funcionó.\nUsando dispositivo por defecto.")
                
            except Exception as fallback_error:
                print(f"❌ Error crítico: {fallback_error}")
                messagebox.showerror("Error de Audio", 
                    f"No se pudo inicializar ningún dispositivo de audio:\n{fallback_error}")
                
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            self.is_generating = False
            messagebox.showerror("Error", f"Error al inicializar audio: {e}")
    
    def stop_generation(self):
        """Detener generación de audio"""
        self.is_generating = False
        if hasattr(self, 'output_stream'):
            self.output_stream.stop()
            self.output_stream.close()
    
    def toggle_recording(self):
        """Alternar grabación de audio"""
        if not self.is_recording:
            self.start_recording()
            self.record_btn.config(text="⏹️ Detener Grabación", bg='#27ae60')
            print("🎤 Iniciando grabación...")
        else:
            self.stop_recording()
            self.record_btn.config(text="🎤 Grabar Respuesta", bg='#e74c3c')
            print("⏹️ Grabación detenida")
    
    def start_recording(self):
        """Iniciar grabación de audio"""
        self.is_recording = True
        self.audio_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"⚠️ Status: {status}")
            
            if self.is_recording:
                self.audio_data.extend(indata[:, 0])
        
        self.input_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=audio_callback,
            blocksize=self.buffer_size
        )
        self.input_stream.start()
    
    def stop_recording(self):
        """Detener grabación de audio"""
        self.is_recording = False
        if hasattr(self, 'input_stream'):
            self.input_stream.stop()
            self.input_stream.close()
            print(f"📊 Grabación completada: {len(self.audio_data)} muestras")
    
    def analyze_resonance(self):
        """Analizar datos grabados para encontrar resonancias"""
        if not hasattr(self, 'audio_data') or len(self.audio_data) == 0:
            messagebox.showwarning("Advertencia", "No hay datos de audio para analizar. Graba primero.")
            return
        
        print("📊 Analizando resonancia...")
        
        # Convertir a numpy array
        audio_array = np.array(self.audio_data)
        
        # Aplicar FFT
        fft_data = fft(audio_array)
        freqs = fftfreq(len(audio_array), 1/self.sample_rate)
        
        # Solo frecuencias positivas
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_data[:len(fft_data)//2])
        
        # Encontrar picos (resonancias)
        peaks, properties = signal.find_peaks(positive_fft, height=np.max(positive_fft)*0.1, distance=50)
        
        # Crear gráficas
        self.plot_analysis(positive_freqs, positive_fft, peaks, properties)
        
        # Mostrar resultados
        self.show_resonance_results(positive_freqs, positive_fft, peaks)
    
    def plot_analysis(self, freqs, fft_data, peaks, properties):
        """Crear gráficas de análisis"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Análisis de Resonancia - Física de Ondas', fontsize=16, fontweight='bold')
        
        # Gráfica del dominio del tiempo
        if hasattr(self, 'audio_data'):
            time_axis = np.linspace(0, len(self.audio_data)/self.sample_rate, len(self.audio_data))
            ax1.plot(time_axis[:min(len(time_axis), 4410)], 
                    self.audio_data[:min(len(self.audio_data), 4410)], 'b-', linewidth=0.8)
            ax1.set_title('Señal de Audio Grabada (Primeros 0.1s)', fontweight='bold')
            ax1.set_xlabel('Tiempo (s)')
            ax1.set_ylabel('Amplitud')
            ax1.grid(True, alpha=0.3)
        
        # Gráfica del espectro de frecuencias
        ax2.plot(freqs[:2000], fft_data[:2000], 'g-', linewidth=1, label='Espectro')
        ax2.plot(freqs[peaks], fft_data[peaks], 'ro', markersize=8, label='Resonancias')
        
        # Marcar frecuencia objetivo
        ax2.axvline(x=self.frequency, color='purple', linestyle='--', 
                   label=f'Frecuencia Objetivo: {self.frequency} Hz')
        
        ax2.set_title('Análisis de Frecuencias - Detección de Resonancias', fontweight='bold')
        ax2.set_xlabel('Frecuencia (Hz)')
        ax2.set_ylabel('Magnitud')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 1000)  # Limitar a frecuencias audibles relevantes
        
        plt.tight_layout()
        plt.show()
    
    def show_resonance_results(self, freqs, fft_data, peaks):
        """Mostrar resultados de resonancia en ventana emergente"""
        results_window = tk.Toplevel(self.root)
        results_window.title("📊 Resultados del Análisis de Resonancia")
        results_window.geometry("600x400")
        results_window.configure(bg='#2c3e50')
        
        title_label = tk.Label(results_window, text="🎯 Frecuencias de Resonancia Detectadas", 
                              font=('Arial', 16, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Frame con scroll para resultados
        canvas = tk.Canvas(results_window, bg='#34495e')
        scrollbar = ttk.Scrollbar(results_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar información del experimento
        info_text = f"""
🎵 Frecuencia Objetivo: {self.frequency} Hz
🔊 Amplitud: {self.amplitude}
📊 Total de muestras analizadas: {len(self.audio_data):,}
⏱️ Duración de grabación: {len(self.audio_data)/self.sample_rate:.2f} segundos
        """
        
        tk.Label(scrollable_frame, text=info_text, font=('Arial', 10), 
                fg='#bdc3c7', bg='#34495e', justify='left').pack(pady=5, padx=10)
        
        # Mostrar resonancias encontradas
        if len(peaks) > 0:
            tk.Label(scrollable_frame, text="🎯 Resonancias Identificadas:", 
                    font=('Arial', 12, 'bold'), fg='#e74c3c', bg='#34495e').pack(pady=5)
            
            for i, peak_idx in enumerate(peaks[:10]):  # Mostrar máximo 10 picos
                freq_val = freqs[peak_idx]
                magnitude = fft_data[peak_idx]
                
                # Determinar si está cerca de la frecuencia objetivo
                diff = abs(freq_val - self.frequency)
                status = "🎯 RESONANCIA PRINCIPAL" if diff < 10 else "🔍 Resonancia secundaria"
                
                result_text = f"{status}\nFrecuencia: {freq_val:.2f} Hz | Magnitud: {magnitude:.0f} | Diferencia: ±{diff:.2f} Hz"
                
                result_frame = tk.Frame(scrollable_frame, bg='#3498db' if diff < 10 else '#95a5a6', relief='raised', bd=1)
                result_frame.pack(fill='x', padx=10, pady=2)
                
                tk.Label(result_frame, text=result_text, font=('Arial', 9), 
                        fg='white', bg=result_frame['bg'], justify='left').pack(pady=2, padx=5)
        else:
            tk.Label(scrollable_frame, text="⚠️ No se detectaron resonancias significativas", 
                    font=('Arial', 12), fg='#f39c12', bg='#34495e').pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def run(self):
        """Ejecutar la aplicación"""
        print("🚀 Iniciando Experimento de Resonancia")
        print("=" * 50)
        self.root.mainloop()
    
    def __del__(self):
        """Limpieza al cerrar"""
        if hasattr(self, 'output_stream'):
            try:
                self.output_stream.stop()
                self.output_stream.close()
            except:
                pass
        
        if hasattr(self, 'input_stream'):
            try:
                self.input_stream.stop()
                self.input_stream.close()
            except:
                pass

def main():
    """Función principal"""
    print("🎵 Experimento de Resonancia - Física de Ondas")
    print("=" * 50)
    print("📚 Para clase de Ingeniería")
    print("🎯 Objetivo: Estudiar resonancia en sistemas acústicos")
    print("=" * 50)
    
    try:
        app = ExperimentoResonancia()
        app.run()
    except Exception as e:
        print(f"❌ Error al ejecutar el experimento: {e}")
        messagebox.showerror("Error crítico", f"No se pudo inicializar el experimento:\n{e}")
    finally:
        print("👋 Experimento finalizado")

if __name__ == "__main__":
    main()
