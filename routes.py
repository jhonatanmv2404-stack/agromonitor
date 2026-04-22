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
    
 @data_bp.route('/csv_full')
 def csv_full():
        """✅ Botón Ver Registro Completo"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirigiendo...</title>
            <meta http-equiv="refresh" content="0; url=/csv_view.html">
            <style>
                body { 
                    font-family: 'Segoe UI', Arial; 
                    text-align: center; 
                    padding: 100px 20px; 
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white; 
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .container { max-width: 500px; margin: 0 auto; }
                h1 { font-size: 2.5em; margin-bottom: 20px; }
                p { font-size: 1.2em; margin-bottom: 30px; opacity: 0.9; }
                .btn { 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background: white; 
                    color: #4CAF50; 
                    text-decoration: none; 
                    border-radius: 50px; 
                    font-weight: 600; 
                    font-size: 1.1em;
                    margin: 10px;
                    transition: all 0.3s;
                }
                .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📋 Registro Completo</h1>
                <p>Cargando tabla de datos...</p>
                <a href="/csv_view.html" class="btn">Abrir Tabla Completa</a>
                <a href="/" class="btn">🏠 Volver Dashboard</a>
            </div>
        </body>
        </html>
        '''
