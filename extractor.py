import requests, re
from bs4 import BeautifulSoup
from datetime import datetime
from utils import cargar_json, guardar_json

def get_total_sorteos(url):
    try:
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        sorteo_element = soup.find('strong', string=re.compile(r'^SORTEO #\d+$'))
        return int(re.search(r'\d+', sorteo_element.text).group()) if sorteo_element else None
    except:
        return None

def get_sorteo_data(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    all_strongs = soup.find_all('strong')
    num = int(re.search(r'\d+', soup.find('strong', string=re.compile(r'^SORTEO #\d+$')).text).group())
    fecha = soup.find('div', class_='fs-5').text.strip()
    dia = soup.find('div', class_='fs-2').text.strip()
    balotas = [int(b.text.strip()) for b in soup.find_all('div', class_='yellow-ball')]
    acumulado = int(soup.find('div', class_='results-accumulated-number shadow-inner').text.strip().replace('$', '').replace('.', '')) * 1_000_000
    ganadores = int(soup.find('div', class_='fs-2 pink-light').text.strip().replace('.', ''))
    return {
        "numero": num, "fecha": fecha, "dia": dia,
        "balotas": balotas, "acumulado": acumulado, "total_ganadores": ganadores
    }

def get_sorteos_existentes(file_path):
    try:
        data = cargar_json(file_path)
        return {s["numero"] for s in data.get("sorteos", [])}
    except:
        return set()

def update_json_file(sorteo, file_path):
    data = cargar_json(file_path)
    if not any(s["numero"] == sorteo["numero"] for s in data["sorteos"]):
        data["sorteos"].append(sorteo)
        data["fechaUltimoSorteo"] = sorteo["fecha"]
        data["cantidadSorteos"] = max(s["numero"] for s in data["sorteos"])
    data["fechaUltimaConsulta"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    guardar_json(data, file_path)
