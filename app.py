from flask import Flask, render_template, jsonify, request
from ping3 import ping
import json
import os
from datetime import datetime
import time
import threading

app = Flask(__name__)

# Configuration file path
CONFIG_FILE = 'devices.json'

def load_devices():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_devices(devices):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(devices, f, indent=4)

def check_device_status(device):
    try:
        response = ping(device['ip'], timeout=1)
        return 'Online' if response is not None else 'Offline'
    except:
        return 'Offline'

def update_device_statuses():
    while True:
        devices = load_devices()
        for device in devices:
            device['status'] = check_device_status(device)
            device['last_checked'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_devices(devices)
        time.sleep(30)  # Update every 30 seconds

@app.route('/')
def index():
    devices = load_devices()
    return render_template('index.html', devices=devices)

@app.route('/api/status')
def get_status():
    devices = load_devices()
    return jsonify(devices)

@app.route('/api/add_device', methods=['POST'])
def add_device():
    data = request.json
    devices = load_devices()
    
    # Check if device with same IP already exists
    if any(device['ip'] == data['ip'] for device in devices):
        return jsonify({'success': False, 'message': 'Device with this IP already exists'})
    
    # Add new device
    devices.append({
        'name': data['name'],
        'ip': data['ip'],
        'type': data['type'],
        'status': check_device_status(data),
        'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    save_devices(devices)
    return jsonify({'success': True})

@app.route('/api/delete_device', methods=['POST'])
def delete_device():
    data = request.json
    devices = load_devices()
    
    # Remove device with matching IP
    devices = [device for device in devices if device['ip'] != data['ip']]
    
    save_devices(devices)
    return jsonify({'success': True})

if __name__ == '__main__':
    # Start the background thread for status updates
    status_thread = threading.Thread(target=update_device_statuses, daemon=True)
    status_thread.start()
    
    # Create empty devices.json if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        save_devices([])
    
    app.run(debug=True, port=5002) 