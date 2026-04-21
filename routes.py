# routes.py - ENDPOINTS independientes
from flask import Blueprint, jsonify
from datetime import datetime
import random
import threading
import time
import csv
from io import StringIO
from flask import Response

data_bp = Blueprint('data', __name__)

# Datos simulados
SENSOR_DATA = {'temp': 25.0, 'humidity': 60.0, 'rain': 10.0, 'time': '00:00:00', 'modulos_conectados': True, 'total_registros': 0}
HISTORIAL = []

def simular_datos():
    global SENSOR_DATA, HISTORIAL
    while True:
        time.sleep(3)
        now = datetime.now()
        SENSOR_DATA.update({
            'temp': round(random.uniform(18, 32), 1),
            'humidity': round(random.uniform(45, 80), 1),
            'rain': round(random.uniform(0, 20), 1),
            'time': now.strftime('%H:%M:%S'),
            'modulos_conectados': True
        })
        registro = {
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'temp': SENSOR_DATA['temp'],
            'humidity': SENSOR_DATA['humidity'],
            'rain': SENSOR_DATA['rain']
        }
        HISTORIAL.append(registro)
        if len(HISTORIAL) > 2000:
            HISTORIAL = HISTORIAL[-2000:]
        SENSOR_DATA['total_registros'] = len(HISTORIAL)

threading.Thread(target=simular_datos, daemon=True).start()

@data_bp.route('/data')
def get_data():
    time_history = [r['time'][-5:] for r in HISTORIAL[-50:]]
    return jsonify({
        'temp': SENSOR_DATA['temp'],
        'humidity': SENSOR_DATA['humidity'],
        'rain': SENSOR_DATA['rain'],
        'time': SENSOR_DATA['time'],
        'modulos_conectados': SENSOR_DATA['modulos_conectados'],
        'total_registros': SENSOR_DATA['total_registros'],
        'time_history': time_history,
        'temp_history': [r['temp'] for r in HISTORIAL[-50:]],
        'humidity_history': [r['humidity'] for r in HISTORIAL[-50:]],
        'rain_history': [r['rain'] for r in HISTORIAL[-50:]],
        'csv_history': HISTORIAL[-20:]
    })

@data_bp.route('/data_full')
def get_data_full():
    return jsonify({'csv_history': HISTORIAL})

@data_bp.route('/csv')
def download_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Fecha', 'Temperatura', 'Humedad', 'Precipitacion'])
    for r in HISTORIAL[-1000:]:
        writer.writerow([r['time'], r['temp'], r['humidity'], r['rain']])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=datos.csv'}
    )
