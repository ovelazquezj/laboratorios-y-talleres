#!/usr/bin/env python3
"""
Application Server para ChirpStack v4
Recibe eventos HTTP desde ChirpStack
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

def format_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_separator():
    print("─" * 80)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint que recibe eventos de ChirpStack"""
    
    # Obtener parámetro 'event' de la URL
    event_type = request.args.get('event', 'unknown')
    
    # Obtener el JSON del body
    data = request.get_json()
    
    print_separator()
    print(f"[{format_timestamp()}] 📡 EVENTO RECIBIDO: {event_type.upper()}")
    print_separator()
    
    # Mostrar toda la información
    if event_type == "up":
        display_uplink(data)
    elif event_type == "join":
        display_join(data)
    elif event_type == "ack":
        display_ack(data)
    elif event_type == "txack":
        display_txack(data)
    elif event_type == "error":
        display_error(data)
    else:
        print(json.dumps(data, indent=2))
    
    print()
    
    # Responder OK a ChirpStack
    return jsonify({"status": "ok"}), 200


def display_uplink(data):
    """Muestra evento de uplink (datos recibidos)"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Application:    {device_info.get('applicationName', 'N/A')}")
    print(f"Tenant:         {device_info.get('tenantName', 'N/A')}")
    
    print(f"\nFPort:          {data.get('fPort', 'N/A')}")
    print(f"Frame Counter:  {data.get('fCnt', 'N/A')}")
    print(f"Data Rate:      {data.get('dr', 'N/A')}")
    print(f"Device Address: {data.get('devAddr', 'N/A')}")
    
    # Payload en HEX
    if data.get('data'):
        print(f"\nPayload (Base64): {data.get('data')}")
        try:
            import base64
            decoded = base64.b64decode(data.get('data'))
            print(f"Payload (HEX):    {decoded.hex().upper()}")
        except:
            pass
    
    # Datos decodificados
    if 'objectJson' in data and data['objectJson']:
        print(f"\n✓ Datos Decodificados:")
        try:
            decoded_data = json.loads(data['objectJson'])
            print(json.dumps(decoded_data, indent=2))
        except:
            print(data.get('objectJson'))
    
    # RX Info
    if data.get('rxInfo'):
        print(f"\nGateway RX Info:")
        for i, rx in enumerate(data.get('rxInfo', []), 1):
            print(f"  Gateway {i}:")
            print(f"    - RSSI:       {rx.get('rssi', 'N/A')} dBm")
            print(f"    - SNR:        {rx.get('snr', 'N/A')}")
            if rx.get('location'):
                print(f"    - Latitude:   {rx['location'].get('latitude', 'N/A')}")
                print(f"    - Longitude:  {rx['location'].get('longitude', 'N/A')}")
    
    # TX Info
    if data.get('txInfo'):
        tx = data.get('txInfo', {})
        print(f"\nTX Info:")
        freq_mhz = float(tx.get('frequency', 0)) / 1e6
        print(f"  Frequency:      {freq_mhz:.1f} MHz")
        if tx.get('lora'):
            lora = tx['lora']
            print(f"  SF:             SF{lora.get('spreadingFactor', 'N/A')}")
            bw = float(lora.get('bandwidth', 0)) / 1000
            print(f"  Bandwidth:      {bw:.0f} kHz")
            print(f"  Code Rate:      {lora.get('codeRate', 'N/A')}")


def display_join(data):
    """Muestra evento de join"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Application:    {device_info.get('applicationName', 'N/A')}")
    print(f"DevAddr:        {data.get('devAddr', 'N/A')}")


def display_ack(data):
    """Muestra evento de ACK"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Frame Counter:  {data.get('fCnt', 'N/A')}")


def display_txack(data):
    """Muestra evento de TXACK"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Frame Counter:  {data.get('fCnt', 'N/A')}")


def display_error(data):
    """Muestra evento de error"""
    
    device_info = data.get("deviceInfo", {})
    print(f"Device Name:    {device_info.get('deviceName', 'N/A')}")
    print(f"DevEUI:         {device_info.get('devEui', 'N/A')}")
    print(f"Error:          {data.get('error', 'N/A')}")


if __name__ == "__main__":
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ChirpStack HTTP Integration Server" + " " * 24 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print("[INFO] Iniciando servidor en http://0.0.0.0:8000")
    print("[INFO] Webhook endpoint: http://0.0.0.0:8000/webhook")
    print("[INFO] Presiona Ctrl+C para detener\n")
    
    # Ejecutar en puerto 8000
    app.run(host='0.0.0.0', port=8000, debug=False)
    