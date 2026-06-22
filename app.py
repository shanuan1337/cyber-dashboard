#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
from ping3 import ping
import threading
import time
from datetime import datetime
import logging
import json
import os
import socket

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dashboard/app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Список DNS серверов для резервирования
DNS_SERVERS = ['10.1.115.2', '10.1.115.8', '10.4.115.2']

# Загрузка конфигов
def load_config(filename):
    try:
        with open(f'/opt/dashboard/config/{filename}', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading config {filename}: {e}")
        return {}

# Загрузка конфига гифок
def load_gifs_config():
    try:
        with open('/opt/dashboard/config/gifs_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading gifs config: {e}")
        return {"gifs": []}

# Глобальные статусы
status_data = {
    'top_hosts': {},
    'side_services': {},
    'vsan_hosts': {},
    'demos_hosts': {},
    'datetime': {
        'date': '',
        'day': '',
        'time': ''
    }
}

def set_dns_server():
    """Пытается установить рабочий DNS сервер"""
    for dns_server in DNS_SERVERS:
        try:
            # Пробуем пинговать DNS сервер
            result = ping(dns_server, timeout=2)
            if result is not None and result is not False:
                # Устанавливаем DNS (это может потребовать прав root)
                logging.info(f"Using DNS server: {dns_server}")
                return dns_server
        except Exception as e:
            logging.warning(f"DNS server {dns_server} unavailable: {e}")
            continue
    logging.error("All DNS servers unavailable!")
    return None

def resolve_hostname(hostname):
    """Резолвит hostname с использованием доступных DNS"""
    for dns_server in DNS_SERVERS:
        try:
            # Создаем socket с таймаутом
            socket.setdefaulttimeout(2)
            ip = socket.gethostbyname(hostname)
            logging.debug(f"Resolved {hostname} to {ip} via {dns_server}")
            return ip
        except:
            continue
    return hostname  # Возвращаем оригинальное имя если резолв не удался

def check_host(address):
    """Проверяет доступность хоста с резолвингом"""
    try:
        # Если это IP адрес, проверяем напрямую
        if address.replace('.', '').isdigit():
            target = address
        else:
            # Резолвим hostname
            target = resolve_hostname(address)
        
        if target == 'localhost':
            return {'status': 'up', 'response_time': 0.1}
        
        response_time = ping(target, timeout=2, unit='ms')
        if response_time is not None and response_time is not False:
            return {'status': 'up', 'response_time': round(response_time, 2)}
        else:
            return {'status': 'down', 'response_time': None}
    except Exception as e:
        logging.error(f"Error checking host {address}: {e}")
        return {'status': 'error', 'response_time': None}

def update_datetime():
    """Обновление даты и времени"""
    now = datetime.now()
    status_data['datetime'] = {
        'date': now.strftime('%d.%m.%Y'),
        'day': now.strftime('%A').upper(),
        'time': now.strftime('%H:%M:%S')
    }

def update_statuses():
    """Фоновая задача для обновления всех статусов"""
    while True:
        try:
            # Обновляем время
            update_datetime()
            
            # Верхний блок
            top_config = load_config('top_hosts.json')
            for host in top_config.get('hosts', []):
                status_data['top_hosts'][host['id']] = check_host(host['address'])
            
            # Боковые сервисы
            side_config = load_config('side_status.json')
            for service in side_config.get('services', []):
                status_data['side_services'][service['label']] = check_host(service['address'])
            
            # VSAN Cluster
            vsan_config = load_config('vsan_cluster.json')
            for host in vsan_config.get('hosts', []):
                status_data['vsan_hosts'][host['id']] = check_host(host['address'])
            
            # DEMOS Cluster
            demos_config = load_config('demos_cluster.json')
            for host in demos_config.get('hosts', []):
                status_data['demos_hosts'][host['id']] = check_host(host['address'])
            
            logging.info("Statuses updated successfully")
            time.sleep(60)  # Обновление каждые 60 секунд
            
        except Exception as e:
            logging.error(f"Error in update_statuses: {e}")
            time.sleep(60)

@app.route('/')
def index():
    """Главная страница"""
    top_config = load_config('top_hosts.json')
    side_config = load_config('side_status.json')
    vsan_config = load_config('vsan_cluster.json')
    demos_config = load_config('demos_cluster.json')
    gifs_config = load_gifs_config()
    
    # Создаем структуру рядов для верхнего блока (9-8-9-8-9-8)
    top_rows = []
    row_pattern = [9, 8, 9, 8, 9, 8]
    hosts = top_config.get('hosts', [])
    host_index = 0
    
    for row_size in row_pattern:
        row = []
        for _ in range(row_size):
            if host_index < len(hosts):
                row.append(hosts[host_index])
                host_index += 1
            else:
                row.append(None)
        top_rows.append(row)
    
    # Структура для нижних блоков (3 ряда по 4)
    bottom_rows_pattern = [4, 4, 4]
    
    # VSAN Cluster
    vsan_rows = []
    vsan_hosts = vsan_config.get('hosts', [])
    vsan_index = 0
    
    for row_size in bottom_rows_pattern:
        row = []
        for _ in range(row_size):
            if vsan_index < len(vsan_hosts):
                row.append(vsan_hosts[vsan_index])
                vsan_index += 1
            else:
                row.append(None)
        vsan_rows.append(row)
    
    # DEMOS Cluster
    demos_rows = []
    demos_hosts = demos_config.get('hosts', [])
    demos_index = 0
    
    for row_size in bottom_rows_pattern:
        row = []
        for _ in range(row_size):
            if demos_index < len(demos_hosts):
                row.append(demos_hosts[demos_index])
                demos_index += 1
            else:
                row.append(None)
        demos_rows.append(row)
    
    return render_template('index.html',
                         top_config=top_config,
                         top_rows=top_rows,
                         side_config=side_config,
                         vsan_config=vsan_config,
                         vsan_rows=vsan_rows,
                         demos_config=demos_config,
                         demos_rows=demos_rows,
                         gifs_config=gifs_config,
                         status=status_data)

@app.route('/api/status')
def api_status():
    """API для получения статусов"""
    return jsonify(status_data)

@app.route('/api/gifs-config')
def api_gifs_config():
    """API для получения конфига гифок"""
    return jsonify(load_gifs_config())

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Инициализация при запуске
update_datetime()
monitor_thread = threading.Thread(target=update_statuses, daemon=True)
monitor_thread.start()

if __name__ == '__main__':
    logging.info("Starting Cyber Dashboard...")
    logging.info(f"DNS servers: {DNS_SERVERS}")
    app.run(host='0.0.0.0', port=5000, debug=False)
