#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
import subprocess
import sys
import re

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except Exception as e:
        print(f"❌ Error instalando {package}: {str(e)}")
        return False

def check_intel_gpu_opencl():
    """Detección alternativa de GPU Intel via OpenCL"""
    print("\n" + "="*50)
    print("Búsqueda alternativa de GPU Intel (OpenCL)")
    print("="*50)
    
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        
        intel_gpu_found = False
        for platform in platforms:
            if 'intel' in platform.name.lower():
                devices = platform.get_devices(device_type=cl.device_type.GPU)
                for device in devices:
                    if 'intel' in device.vendor.lower():
                        intel_gpu_found = True
                        print(f"✅ GPU Intel detectada via OpenCL:")
                        print(f"  Nombre: {device.name}")
                        print(f"  Versión OpenCL: {device.version}")
                        print(f"  Memoria: {device.global_mem_size//(1024**2)} MB")
        
        if not intel_gpu_found:
            print("❌ No se encontraron GPUs Intel via OpenCL")
    
    except ImportError:
        print("⚠️ pyopencl no instalado. Usa: 'pip install pyopencl'")
    except Exception as e:
        print(f"❌ Error en detección OpenCL: {str(e)}")

def check_cpu_info():
    """Detalles avanzados de CPU"""
    print("\n" + "="*50)
    print("Información Detallada de CPU")
    print("="*50)
    
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        print(f"Procesador: {info['brand_raw']}")
        print(f"Arquitectura: {info['arch']}")
        print(f"Núcleos físicos: {info['count']}")
        print(f"Extensiones: {', '.join(info['flags'])}")
        
        # Detectar si es CPU Intel
        if 'GenuineIntel' in info['flags']:
            print("✅ CPU Intel detectada")
            # Detectar generación
            if re.search(r'i\d-\d{4}', info['brand_raw']):
                gen = re.search(r'i\d-(\d{4})', info['brand_raw']).group(1)
                print(f"  Generación: {gen[0]}° gen ({gen})")
    except ImportError:
        print("⚠️ Instala 'py-cpuinfo': pip install py-cpuinfo")

def check_oneapi_status():
    """Verificar estado de oneAPI"""
    print("\n" + "="*50)
    print("Diagnóstico de Intel oneAPI")
    print("="*50)
    
    try:
        # Verificar si setvars.sh fue ejecutado
        result = subprocess.run(['which', 'icpx'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ oneAPI toolkit detectado")
            print(f"  Compilador C++: {result.stdout.strip()}")
            
            # Verificar versión
            version_result = subprocess.run(['icpx', '--version'], capture_output=True, text=True)
            match = re.search(r'\(ICC\) (\d+\.\d+\.\d+)', version_result.stdout)
            if match:
                print(f"  Versión: {match.group(1)}")
        else:
            print("❌ oneAPI no configurado. Ejecuta:")
            print("   source /opt/intel/oneapi/setvars.sh")
    except Exception as e:
        print(f"❌ Error verificando oneAPI: {str(e)}")

if __name__ == "__main__":
    print("="*50)
    print("DIAGNÓSTICO AVANZADO DE HARDWARE INTEL")
    print("="*50)
    
    # Información básica del sistema
    print(f"Sistema operativo: {platform.system()} {platform.release()}")
    print(f"Versión Python: {platform.python_version()}")
    
    # Verificaciones
    check_cpu_info()
    check_oneapi_status()
    check_intel_gpu_opencl()

