import json
from datetime import datetime

def revisar_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            return isinstance(json_data, dict) and "sorteos" in json_data
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def crear_json_vacio(file_path):
    with open(file_path, 'w') as file:
        json.dump({
            "cantidadSorteos": 0,
            "fechaUltimoSorteo": None,
            "fechaUltimaConsulta": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "sorteos": []
        }, file, indent=4)

def cargar_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def guardar_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
