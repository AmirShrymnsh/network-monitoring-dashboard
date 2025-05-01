# Network Monitoring Dashboard

A simple Flask-based web application that monitors the status of network devices.

## Features

- Real-time monitoring of network devices
- Automatic status updates every 30 seconds
- Clean, responsive Bootstrap UI
- JSON-based device configuration
- REST API endpoint for status updates

## Configuration

You can modify to add or remove devices. Each device should have:
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
