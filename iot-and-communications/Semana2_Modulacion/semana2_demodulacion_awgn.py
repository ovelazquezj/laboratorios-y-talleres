#!/usr/bin/env python3
"""
Semana 2: RETO DE DEMODULACIÓN - Modulación Digital en Canales AWGN
Curso: Comunicaciones e IoT

INSTRUCCIONES PARA EL ESTUDIANTE:
Este archivo contiene la estructura base y algoritmos paso a paso para implementar
la demodulación de señales ASK, FSK y BPSK. 

TU TAREA: Completar las funciones marcadas con "# TODO: IMPLEMENTAR"
siguiendo los algoritmos proporcionados y las ecuaciones matemáticas.

Usa el notebook como referencia para entender la implementación completa.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys
from typing import Tuple, Optional

# =============================================================================
# ECUACIONES DE REFERENCIA
# =============================================================================
"""
ASK (Amplitude Shift Keying):
    s(t) = A * b(t) * cos(2πfct)
    donde: b(t) = 1 para bit '1', b(t) = 0 para bit '0'

FSK (Frequency Shift Keying):
    s(t) = A * cos(2πfit)
    donde: fi = f0 para bit '0', fi = f1 para bit '1'

BPSK (Binary Phase Shift Keying):
    s(t) = A * m(t) * cos(2πfct)
    donde: m(t) = +1 para bit '1', m(t) = -1 para bit '0'

Canal AWGN:
    r(t) = s(t) + n(t)
    donde: n(t) ~ N(0, σ²), σ² = Ps / (10^(SNR_dB/10))
"""

class DigitalDemodulationChallenge:
    """
    CLASE BASE PARA EL RETO DE DEMODULACIÓN
    
    Las funciones de modulación están implementadas como referencia.
    TU TAREA: Implementar las funciones de demodulación siguiendo los algoritmos.
    """
    
    def __init__(self, fc: float = 1000, fs: float = 8000, tb: float = 0.001, A: float = 1.0):
        """Inicializar parámetros del sistema (YA IMPLEMENTADO)"""
        self.fc = fc
        self.fs = fs
        self.tb = tb
        self.A = A
        self.samples_per_bit = int(fs * tb)
        self.t_bit = np.linspace(0, tb, self.samples_per_bit, endpoint=False)
        
        print(f"Sistema inicializado:")
        print(f"  - Frecuencia portadora: {fc} Hz")
        print(f"  - Frecuencia muestreo: {fs} Hz")
        print(f"  - Duración bit: {tb} s")
        print(f"  - Muestras por bit: {self.samples_per_bit}")
    
    def generate_bits(self, N: int, seed: Optional[int] = None) -> np.ndarray:
        """Generar N bits aleatorios (YA IMPLEMENTADO)"""
        if seed is not None:
            np.random.seed(seed)
        return np.random.randint(0, 2, N)
    
    # =========================================================================
    # FUNCIONES DE MODULACIÓN (YA IMPLEMENTADAS COMO REFERENCIA)
    # =========================================================================
    
    def ask_modulate(self, bits: np.ndarray) -> np.ndarray:
        """MODULACIÓN ASK - REFERENCIA IMPLEMENTADA"""
        signal_mod = np.array([])
        
        for bit in bits:
            if bit == 1:
                # Bit '1': portadora con amplitud A
                s_bit = self.A * np.cos(2 * np.pi * self.fc * self.t_bit)
            else:
                # Bit '0': sin portadora (amplitud 0)
                s_bit = np.zeros_like(self.t_bit)
            
            signal_mod = np.concatenate([signal_mod, s_bit])
        
        return signal_mod
    
    def fsk_modulate(self, bits: np.ndarray, f0: Optional[float] = None, f1: Optional[float] = None) -> np.ndarray:
        """MODULACIÓN FSK - REFERENCIA IMPLEMENTADA"""
        if f0 is None:
            f0 = self.fc - self.fc * 0.1  # 10% menor
        if f1 is None:
            f1 = self.fc + self.fc * 0.1  # 10% mayor
            
        signal_mod = np.array([])
        
        for bit in bits:
            if bit == 1:
                # Bit '1': frecuencia f1
                s_bit = self.A * np.cos(2 * np.pi * f1 * self.t_bit)
            else:
                # Bit '0': frecuencia f0
                s_bit = self.A * np.cos(2 * np.pi * f0 * self.t_bit)
            
            signal_mod = np.concatenate([signal_mod, s_bit])
        
        return signal_mod
    
    def bpsk_modulate(self, bits: np.ndarray) -> np.ndarray:
        """MODULACIÓN BPSK - REFERENCIA IMPLEMENTADA"""
        signal_mod = np.array([])
        
        for bit in bits:
            if bit == 1:
                # Bit '1': fase 0° (m(t) = +1)
                m_t = 1
            else:
                # Bit '0': fase 180° (m(t) = -1)
                m_t = -1
            
            s_bit = self.A * m_t * np.cos(2 * np.pi * self.fc * self.t_bit)
            signal_mod = np.concatenate([signal_mod, s_bit])
        
        return signal_mod
    
    def awgn_channel(self, signal: np.ndarray, snr_db: float) -> np.ndarray:
        """CANAL AWGN - REFERENCIA IMPLEMENTADA"""
        # Calcular potencia de la señal
        signal_power = np.mean(signal**2)
        
        # Convertir SNR de dB a lineal
        snr_linear = 10**(snr_db / 10)
        
        # Calcular potencia del ruido
        noise_power = signal_power / snr_linear
        
        # Generar ruido gaussiano
        noise = np.sqrt(noise_power) * np.random.randn(len(signal))
        
        return signal + noise
    
    # =========================================================================
    # RETO: FUNCIONES DE DEMODULACIÓN A IMPLEMENTAR
    # =========================================================================
    
    def ask_demodulate(self, received_signal: np.ndarray, N: int) -> np.ndarray:
        """
        RETO 1: DEMODULACIÓN ASK
        
        ALGORITMO DETECTOR DE ENERGÍA:
        Para cada bit i (i = 0, 1, ..., N-1):
        1. Extraer segmento de señal recibida correspondiente al bit i
        2. Calcular energía del segmento: E = Σ(r²[n]) para n en el segmento
        3. Comparar con umbral de decisión
        4. Si E > umbral: bit detectado = 1, sino: bit detectado = 0
        
        FÓRMULAS:
        - Índices: start = i * samples_per_bit, end = (i+1) * samples_per_bit
        - Energía: E = Σ(r[start:end]²)
        - Umbral sugerido: threshold = (A² * samples_per_bit) / 4
        
        Args:
            received_signal: Señal recibida r(t) con ruido
            N: Número de bits a detectar
            
        Returns:
            Array de bits detectados (0s y 1s)
        """
        detected_bits = np.zeros(N, dtype=int)
        
        # TODO: IMPLEMENTAR ALGORITMO DE DEMODULACIÓN ASK
        # Pista: Usar un bucle for para procesar cada bit
        for i in range(N):
            # TODO: Paso 1 - Extraer segmento del bit i
            start_idx = # TODO: Calcular índice inicial
            end_idx = # TODO: Calcular índice final  
            bit_signal = # TODO: Extraer segmento de received_signal
            
            # TODO: Paso 2 - Calcular energía del segmento
            energy = # TODO: Sumar cuadrados de las muestras
            
            # TODO: Paso 3 - Definir umbral de decisión
            threshold = # TODO: Usar fórmula sugerida arriba
            
            # TODO: Paso 4 - Tomar decisión
            detected_bits[i] = # TODO: 1 si energy > threshold, sino 0
        
        return detected_bits
    
    def fsk_demodulate(self, received_signal: np.ndarray, N: int, f0: Optional[float] = None, f1: Optional[float] = None) -> np.ndarray:
        """
        RETO 2: DEMODULACIÓN FSK
        
        ALGORITMO DETECTOR POR CORRELACIÓN:
        Para cada bit i (i = 0, 1, ..., N-1):
        1. Extraer segmento de señal recibida correspondiente al bit i
        2. Generar señales de referencia para f0 y f1
        3. Calcular correlación con cada señal de referencia
        4. Decidir el bit según cuál correlación es mayor
        
        FÓRMULAS:
        - Señal referencia f0: ref_0 = cos(2π*f0*t)
        - Señal referencia f1: ref_1 = cos(2π*f1*t)
        - Correlación f0: corr_0 = Σ(r[n] * ref_0[n])
        - Correlación f1: corr_1 = Σ(r[n] * ref_1[n])
        - Decisión: bit = 1 si corr_1 > corr_0, sino bit = 0
        
        Args:
            received_signal: Señal recibida r(t) con ruido
            N: Número de bits a detectar
            f0, f1: Frecuencias para bits '0' y '1'
            
        Returns:
            Array de bits detectados (0s y 1s)
        """
        # Usar frecuencias por defecto si no se especifican
        if f0 is None:
            f0 = self.fc - self.fc * 0.1
        if f1 is None:
            f1 = self.fc + self.fc * 0.1
        
        detected_bits = np.zeros(N, dtype=int)
        
        # TODO: IMPLEMENTAR SEÑALES DE REFERENCIA
        # Usar self.t_bit como vector de tiempo
        ref_0 = # TODO: Generar coseno para frecuencia f0
        ref_1 = # TODO: Generar coseno para frecuencia f1
        
        # TODO: IMPLEMENTAR ALGORITMO DE DEMODULACIÓN FSK
        for i in range(N):
            # TODO: Paso 1 - Extraer segmento del bit i
            start_idx = # TODO: Calcular índice inicial
            end_idx = # TODO: Calcular índice final
            bit_signal = # TODO: Extraer segmento
            
            # TODO: Paso 2 - Calcular correlaciones
            corr_0 = # TODO: Correlación con ref_0 (producto punto)
            corr_1 = # TODO: Correlación con ref_1 (producto punto)
            
            # TODO: Paso 3 - Tomar decisión
            detected_bits[i] = # TODO: 1 si corr_1 > corr_0, sino 0
        
        return detected_bits
    
    def bpsk_demodulate(self, received_signal: np.ndarray, N: int) -> np.ndarray:
        """
        RETO 3: DEMODULACIÓN BPSK
        
        ALGORITMO DETECTOR COHERENTE:
        Para cada bit i (i = 0, 1, ..., N-1):
        1. Extraer segmento de señal recibida correspondiente al bit i
        2. Generar señal de referencia (portadora coherente)
        3. Calcular correlación (producto punto)
        4. Decidir bit según signo de la correlación
        
        FÓRMULAS:
        - Señal referencia: ref = cos(2π*fc*t)
        - Correlación: corr = Σ(r[n] * ref[n])
        - Decisión: bit = 1 si corr > 0, sino bit = 0
        
        NOTA: La correlación positiva indica fase 0° (bit '1'),
              correlación negativa indica fase 180° (bit '0')
        
        Args:
            received_signal: Señal recibida r(t) con ruido
            N: Número de bits a detectar
            
        Returns:
            Array de bits detectados (0s y 1s)
        """
        detected_bits = np.zeros(N, dtype=int)
        
        # TODO: IMPLEMENTAR SEÑAL DE REFERENCIA
        # Usar self.fc y self.t_bit
        ref_signal = # TODO: Generar coseno coherente
        
        # TODO: IMPLEMENTAR ALGORITMO DE DEMODULACIÓN BPSK
        for i in range(N):
            # TODO: Paso 1 - Extraer segmento del bit i
            start_idx = # TODO: Calcular índice inicial
            end_idx = # TODO: Calcular índice final
            bit_signal = # TODO: Extraer segmento
            
            # TODO: Paso 2 - Calcular correlación coherente
            correlation = # TODO: Producto punto con ref_signal
            
            # TODO: Paso 3 - Tomar decisión basada en signo
            detected_bits[i] = # TODO: 1 si correlation > 0, sino 0
        
        return detected_bits
    
    # =========================================================================
    # FUNCIONES AUXILIARES (YA IMPLEMENTADAS)
    # =========================================================================
    
    def calculate_ber(self, transmitted_bits: np.ndarray, received_bits: np.ndarray) -> float:
        """Calcular Bit Error Rate (YA IMPLEMENTADO)"""
        errors = np.sum(transmitted_bits != received_bits)
        return errors / len(transmitted_bits)
    
    def modulate_signal(self, scheme: str, bits: np.ndarray) -> np.ndarray:
        """Wrapper para modular según esquema (YA IMPLEMENTADO)"""
        if scheme.lower() == 'ask':
            return self.ask_modulate(bits)
        elif scheme.lower() == 'fsk':
            return self.fsk_modulate(bits)
        elif scheme.lower() == 'bpsk':
            return self.bpsk_modulate(bits)
        else:
            raise ValueError(f"Esquema '{scheme}' no soportado. Use: ask, fsk, bpsk")
    
    def demodulate_signal(self, scheme: str, received_signal: np.ndarray, N: int) -> np.ndarray:
        """
        Wrapper para demodular según esquema
        ESTA FUNCIÓN LLAMARÁ A TUS IMPLEMENTACIONES
        """
        if scheme.lower() == 'ask':
            return self.ask_demodulate(received_signal, N)
        elif scheme.lower() == 'fsk':
            return self.fsk_demodulate(received_signal, N)
        elif scheme.lower() == 'bpsk':
            return self.bpsk_demodulate(received_signal, N)
        else:
            raise ValueError(f"Esquema '{scheme}' no soportado. Use: ask, fsk, bpsk")


# =============================================================================
# FUNCIONES DE VISUALIZACIÓN Y E/S (YA IMPLEMENTADAS)
# =============================================================================

def plot_signals(modulator, bits, modulated, received, detected, scheme, snr_db):
    """Generar gráficas de señales (YA IMPLEMENTADO)"""
    N = len(bits)
    t = np.linspace(0, N * modulator.tb, len(modulated))
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    
    # Bits originales
    t_bits = np.linspace(0, N * modulator.tb, N * 10)
    bit_signal = np.repeat(bits, 10)
    axes[0].plot(t_bits * 1000, bit_signal, 'k-', linewidth=2)
    axes[0].set_title('Bits Transmitidos')
    axes[0].set_ylabel('Amplitud')
    axes[0].set_ylim([-0.5, 1.5])
    axes[0].grid(True, alpha=0.3)
    
    # Señal modulada
    axes[1].plot(t * 1000, modulated, 'b-', linewidth=1)
    axes[1].set_title(f'Señal Modulada ({scheme.upper()}) - Sin Ruido')
    axes[1].set_ylabel('Amplitud')
    axes[1].grid(True, alpha=0.3)
    
    # Señal recibida
    axes[2].plot(t * 1000, received, 'r-', linewidth=1, alpha=0.8)
    axes[2].set_title(f'Señal Recibida - Con Ruido AWGN (SNR = {snr_db} dB)')
    axes[2].set_ylabel('Amplitud')
    axes[2].grid(True, alpha=0.3)
    
    # Bits detectados
    detected_signal = np.repeat(detected, 10)
    axes[3].plot(t_bits * 1000, detected_signal, 'g-', linewidth=2)
    axes[3].set_title('Bits Detectados (TU IMPLEMENTACIÓN)')
    axes[3].set_ylabel('Amplitud')
    axes[3].set_xlabel('Tiempo (ms)')
    axes[3].set_ylim([-0.5, 1.5])
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def save_results(filename: str, scheme: str, snr_db: float, ber: float, N: int):
    """Guardar resultados en CSV (YA IMPLEMENTADO)"""
    results = {
        'Timestamp': [pd.Timestamp.now()],
        'Scheme': [scheme.upper()],
        'SNR_dB': [snr_db],
        'N_bits': [N],
        'BER': [ber],
        'Errors': [int(ber * N)]
    }
    
    df = pd.DataFrame(results)
    
    try:
        existing_df = pd.read_csv(filename)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(filename, index=False)
    except FileNotFoundError:
        df.to_csv(filename, index=False)
    
    print(f"✓ Resultados guardados en: {filename}")

# =============================================================================
# FUNCIÓN PRINCIPAL CON INTERFAZ CLI
# =============================================================================

def main():
    """Función principal - Interfaz de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="RETO: Implementar Demodulación Digital en Canales AWGN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
INSTRUCCIONES:
1. Completa las funciones ask_demodulate(), fsk_demodulate() y bpsk_demodulate()
2. Usa el notebook como referencia para entender la implementación
3. Sigue los algoritmos paso a paso proporcionados en cada función
4. Prueba tu implementación con diferentes esquemas y SNR

EJEMPLOS DE USO:
  python %(prog)s --scheme bpsk --snr 10 --N 100 --plot --test
  python %(prog)s --scheme ask --snr 5 --N 1000 --out mi_resultado.csv
  python %(prog)s --scheme fsk --snr 0 --N 500 --export rx.npy det.npy
        """
    )
    
    # Argumentos obligatorios
    parser.add_argument('--scheme', choices=['ask', 'fsk', 'bpsk'], required=True,
                       help='Esquema de modulación a implementar')
    parser.add_argument('--snr', type=float, required=True,
                       help='SNR en dB')
    parser.add_argument('--N', type=int, required=True,
                       help='Número de bits a transmitir')
    
    # Parámetros del sistema
    parser.add_argument('--fc', type=float, default=1000,
                       help='Frecuencia portadora en Hz (default: 1000)')
    parser.add_argument('--fs', type=float, default=8000,
                       help='Frecuencia de muestreo en Hz (default: 8000)')
    parser.add_argument('--tb', type=float, default=0.001,
                       help='Duración de bit en segundos (default: 0.001)')
    parser.add_argument('--A', type=float, default=1.0,
                       help='Amplitud de la señal (default: 1.0)')
    
    # Opciones de salida
    parser.add_argument('--plot', action='store_true',
                       help='Mostrar gráficas para verificar tu implementación')
    parser.add_argument('--out', type=str,
                       help='Archivo CSV para guardar resultados')
    parser.add_argument('--export', nargs=2, metavar=('RX_FILE', 'DET_FILE'),
                       help='Exportar señal recibida y bits detectados a archivos .npy')
    parser.add_argument('--seed', type=int, default=42,
                       help='Semilla para reproducibilidad (default: 42)')
    parser.add_argument('--test', action='store_true',
                       help='Modo de prueba: mostrar bits transmitidos vs detectados')
    
    args = parser.parse_args()
    
    # Validaciones
    if args.fs <= 2 * args.fc:
        print("❌ Error: fs debe ser > 2*fc (criterio de Nyquist)")
        sys.exit(1)
    
    if args.N <= 0:
        print("❌ Error: N debe ser positivo")
        sys.exit(1)
    
    # Crear instancia del demodulador
    print("🚀 INICIANDO RETO DE DEMODULACIÓN")
    print("=" * 50)
    
    demod = DigitalDemodulationChallenge(args.fc, args.fs, args.tb, args.A)
    
    print(f"\n📋 PARÁMETROS DE SIMULACIÓN:")
    print(f"   Esquema: {args.scheme.upper()}")
    print(f"   SNR: {args.snr} dB")
    print(f"   Número de bits: {args.N}")
    print()
    
    # Generar bits de prueba
    bits = demod.generate_bits(args.N, args.seed)
    
    if args.test and args.N <= 20:
        print(f"🔍 BITS TRANSMITIDOS: {bits}")
    
    # Modular (usando funciones de referencia implementadas)
    print("📡 Modulando señal...")
    modulated_signal = demod.modulate_signal(args.scheme, bits)
    
    # Canal AWGN
    print(f"🌊 Aplicando canal AWGN (SNR = {args.snr} dB)...")
    received_signal = demod.awgn_channel(modulated_signal, args.snr)
    
    # DEMODULAR - AQUÍ ES DONDE TU IMPLEMENTACIÓN SERÁ PROBADA
    print("🔧 Demodulando con TU implementación...")
    try:
        detected_bits = demod.demodulate_signal(args.scheme, received_signal, args.N)
        
        if args.test and args.N <= 20:
            print(f"🎯 BITS DETECTADOS:   {detected_bits}")
            print(f"✅ BITS CORRECTOS:    {bits}")
            print(f"❌ ERRORES:           {bits != detected_bits}")
        
        # Calcular BER
        ber = demod.calculate_ber(bits, detected_bits)
        errors = int(ber * args.N)
        
        print("\n📊 RESULTADOS DE TU IMPLEMENTACIÓN:")
        print(f"   BER: {ber:.6f}")
        print(f"   Errores: {errors}/{args.N}")
        print(f"   Exactitud: {(1-ber)*100:.2f}%")
        
        # Evaluación de rendimiento
        if ber < 0.001:
            print("🏆 ¡EXCELENTE! Tu implementación funciona muy bien")
        elif ber < 0.01:
            print("✅ ¡BIEN! Tu implementación es correcta")
        elif ber < 0.1:
            print("⚠️  Tu implementación funciona pero podría mejorarse")
        else:
            print("❌ Tu implementación necesita revisión")
        
    except Exception as e:
        print(f"❌ ERROR en tu implementación: {e}")
        print("💡 SUGERENCIAS:")
        print("   1. Verifica que completaste todos los # TODO")
        print("   2. Revisa las fórmulas matemáticas")
        print("   3. Consulta el notebook para ejemplos")
        sys.exit(1)
    
    # Gráficas
    if args.plot:
        print("\n📈 Generando gráficas...")
        plot_N = min(20, args.N)  # Limitar para visualización
        plot_samples = plot_N * demod.samples_per_bit
        
        plot_signals(
            demod,
            bits[:plot_N],
            modulated_signal[:plot_samples],
            received_signal[:plot_samples],
            detected_bits[:plot_N],
            args.scheme,
            args.snr
        )
    
    # Guardar resultados
    if args.out:
        save_results(args.out, args.scheme, args.snr, ber, args.N)
    
    # Exportar arrays
    if args.export:
        rx_file, det_file = args.export
        np.save(rx_file, received_signal)
        np.save(det_file, detected_bits)
        print(f"✓ Señal recibida: {rx_file}")
        print(f"✓ Bits detectados: {det_file}")
    
    print("\n🎉 ¡RETO COMPLETADO!")
    print("💡 Próximos pasos:")
    print("   - Prueba con diferentes valores de SNR")
    print("   - Compara tu BER con el del notebook")
    print("   - Experimenta con diferentes parámetros del sistema")


if __name__ == "__main__":
    # Mensaje de bienvenida
    print("🎓 RETO DE DEMODULACIÓN - SEMANA 2")
    print("📚 Comunicaciones e IoT")
    print("🎯 Objetivo: Implementar demoduladores ASK, FSK, BPSK")
    print()
    
main()