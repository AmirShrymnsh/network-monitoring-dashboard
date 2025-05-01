# Network Monitoring Dashboard

A simple Flask-based web application that monitors the status of network devices.

## Features

- Real-time monitoring of network devices
- Automatic status updates every 30 seconds
- Clean, responsive Bootstrap UI
- JSON-based device configuration
- REST API endpoint for status updates

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the dashboard at `http://localhost:5000`

## Configuration

The application uses a `devices.json` file to store device information. By default, it creates three sample devices:
- Router (192.168.1.1)
- Server (192.168.1.100)
- Printer (192.168.1.200)

You can modify the `devices.json` file to add or remove devices. Each device should have:
- name: Device name
- ip: IP address
- status: Online/Offline (automatically updated)
- last_checked: Timestamp of last status check (automatically updated)

## API Endpoints

- `/`: Main dashboard page
- `/api/status`: JSON endpoint for device statuses

## Requirements

- Python 3.6+
- Flask
- python-ping3
- python-dotenv 