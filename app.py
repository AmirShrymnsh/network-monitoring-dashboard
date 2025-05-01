from flask import Flask, render_template, jsonify, request
from ping3 import ping
import json
import os
from datetime import datetime
import time
import threading

app = Flask(__name__, template_folder='docs')

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
        generate_static_html(devices)  # Generate static HTML after each update
        time.sleep(30)  # Update every 30 seconds

def generate_static_html(devices):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Monitoring Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .status-online {{ color: #28a745; }}
            .status-offline {{ color: #dc3545; }}
            .table-container {{ margin: 20px; }}
            .header {{ 
                background-color: #343a40;
                color: white;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .last-checked {{ font-size: 0.8em; color: #6c757d; }}
            .add-device-form {{
                margin: 20px;
                padding: 20px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>Network Monitoring Dashboard</h1>
            </div>
        </div>

        <div class="container">
            <div class="add-device-form">
                <h3>Add New Device</h3>
                <form id="addDeviceForm" class="row g-3">
                    <div class="col-md-4">
                        <label for="deviceName" class="form-label">Device Name</label>
                        <input type="text" class="form-control" id="deviceName" required>
                    </div>
                    <div class="col-md-4">
                        <label for="deviceIP" class="form-label">IP Address</label>
                        <input type="text" class="form-control" id="deviceIP" required>
                    </div>
                    <div class="col-md-4">
                        <label for="deviceType" class="form-label">Device Type</label>
                        <select class="form-select" id="deviceType" required>
                            <option value="router">Router</option>
                            <option value="server">Server</option>
                            <option value="printer">Printer</option>
                            <option value="computer">Computer</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="col-12">
                        <button type="submit" class="btn btn-primary">Add Device</button>
                    </div>
                </form>
            </div>

            <div class="table-container">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Device Name</th>
                            <th>Type</th>
                            <th>IP Address</th>
                            <th>Status</th>
                            <th>Last Checked</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="deviceTable">
                        {''.join([
                            f'''
                            <tr>
                                <td>{device['name']}</td>
                                <td>{device['type']}</td>
                                <td>{device['ip']}</td>
                                <td class="status-{device['status'].lower()}">{device['status']}</td>
                                <td class="last-checked">{device['last_checked']}</td>
                                <td>
                                    <button class="btn btn-danger btn-sm" onclick="deleteDevice('{device['ip']}')">Delete</button>
                                </td>
                            </tr>
                            ''' for device in devices
                        ])}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            function deleteDevice(ip) {{
                if (confirm('Are you sure you want to delete this device?')) {{
                    fetch('/api/delete_device', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ ip: ip }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            location.reload();
                        }}
                    }});
                }}
            }}

            document.getElementById('addDeviceForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                
                const deviceData = {{
                    name: document.getElementById('deviceName').value,
                    ip: document.getElementById('deviceIP').value,
                    type: document.getElementById('deviceType').value
                }};

                fetch('/api/add_device', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(deviceData)
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        location.reload();
                    }} else {{
                        alert(data.message || 'Error adding device');
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    with open('docs/index.html', 'w') as f:
        f.write(html_content)

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
    generate_static_html(devices)  # Generate static HTML after adding device
    return jsonify({'success': True})

@app.route('/api/delete_device', methods=['POST'])
def delete_device():
    data = request.json
    devices = load_devices()
    
    # Remove device with matching IP
    devices = [device for device in devices if device['ip'] != data['ip']]
    
    save_devices(devices)
    generate_static_html(devices)  # Generate static HTML after deleting device
    return jsonify({'success': True})

if __name__ == '__main__':
    # Start the background thread for status updates
    status_thread = threading.Thread(target=update_device_statuses, daemon=True)
    status_thread.start()
    
    # Create empty devices.json if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        save_devices([])
        generate_static_html([])  # Generate initial static HTML
    
    app.run(debug=True, port=5003) 
