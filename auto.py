import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from collections import Counter

def get_total_sorteos(url):
    """
    Obtiene la cantidad total de sorteos disponibles desde la página principal.

    Args:
        url (str): URL de la página principal de resultados.

    Returns:
        int: Número total de sorteos disponibles.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        sorteo_element = soup.find('strong', string=re.compile(r'^SORTEO #\d+$'))
        if not sorteo_element:
            raise ValueError("No se encontró el número de sorteo en la página principal.")

        sorteo_number = int(re.search(r'\d+', sorteo_element.text).group())
        return sorteo_number

    except requests.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None
    except ValueError as e:
        print(e)
        return None

def get_sorteos_existentes(file_path):
    """
    Obtiene una lista de los números de sorteos ya registrados en el archivo JSON.

    Args:
        file_path (str): Ruta del archivo JSON.

    Returns:
        set: Conjunto de números de sorteos existentes.
    """
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            sorteos_existentes = {sorteo["numero"] for sorteo in json_data.get("sorteos", [])}
            return sorteos_existentes
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def get_sorteo_data(url):
    """
    Extrae los datos del sorteo desde la URL especificada.

    Args:
        url (str): URL de la página donde se encuentra el sorteo.

    Returns:
        dict: Datos del sorteo encontrado, incluyendo número, fecha, balotas, acumulado y total de ganadores.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        sorteo_element = soup.find('strong', string=re.compile(r'^SORTEO #\d+$'))
        if not sorteo_element:
            raise ValueError("No se pudo encontrar el elemento del sorteo en la página.")

        sorteo_number = int(re.search(r'\d+', sorteo_element.text).group())

        fecha_element = soup.find('div', class_='fs-5')
        fecha = fecha_element.text.strip() if fecha_element else "Fecha no disponible"

        dia_element = soup.find('div', class_='fs-2')
        dia = dia_element.text.strip() if dia_element else "Día no disponible"

        balotas_elements = soup.find_all('div', class_='yellow-ball')
        balotas = [int(balota.text.strip()) for balota in balotas_elements] if balotas_elements else []

        acumulado_element = soup.find('div', class_='results-accumulated-number shadow-inner')
        acumulado = acumulado_element.text.strip() if acumulado_element else "Acumulado no disponible"

        ganadores_element = soup.find('div', class_='fs-2 pink-light')
        total_ganadores = int(ganadores_element.text.replace('.', '').strip()) if ganadores_element else 0

        return {
            "numero": sorteo_number,
            "fecha": fecha,
            "dia": dia,
            "balotas": balotas,
            "acumulado": int(acumulado.replace('$', '').replace('.', ''))*1000000,
            "total_ganadores": total_ganadores
        }

    except requests.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None
    except ValueError as e:
        print(e)
        return None

def update_json_file(data, file_path):
    """
    Actualiza un archivo JSON con los nuevos datos del sorteo.

    Args:
        data (dict): Datos del sorteo a agregar.
        file_path (str): Ruta del archivo JSON.
    """
    try:
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            json_data = {
                "cantidadSorteos": 0,
                "fechaUltimoSorteo": None,
                "fechaUltimaConsulta": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "sorteos": []
            }

        if not any(sorteo["numero"] == data["numero"] for sorteo in json_data["sorteos"]):
            json_data["sorteos"].append(data)
            json_data["fechaUltimoSorteo"] = data["fecha"]

        json_data["cantidadSorteos"] = max(sorteo["numero"] for sorteo in json_data["sorteos"])

        json_data["fechaUltimaConsulta"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

        print("Archivo JSON actualizado correctamente.")

    except Exception as e:
        print(f"Error al actualizar el archivo JSON: {e}")

def analizar_numeros_frecuentes(file_path):
    """
    Analiza los números más frecuentes en los sorteos almacenados en el archivo JSON.

    Args:
        file_path (str): Ruta del archivo JSON.

    Returns:
        dict: Números más frecuentes y sus conteos.
    """
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        balotas = []
        for sorteo in json_data.get("sorteos", []):
            balotas.extend(sorteo.get("balotas", []))

        frecuencia = Counter(balotas)
        return dict(frecuencia.most_common())

    except FileNotFoundError:
        print("El archivo JSON no existe.")
        return {}
    except json.JSONDecodeError:
        print("Error al leer el archivo JSON.")
        return {}

def menu():
    """
    Muestra un menú para actualizar el JSON o analizar los números frecuentes.
    """
    print("\nMenú:")
    print("1. Actualizar sorteos.")
    print("2. Analizar números frecuentes.")
    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        main_url = "https://baloto.com/miloto/resultados"
        base_url = "https://baloto.com/miloto/resultados-miloto/"
        json_file = "resultados.json"

        total_sorteos = get_total_sorteos(main_url)
        if total_sorteos:
            print(f"Número total de sorteos disponibles: {total_sorteos}")

            sorteos_existentes = get_sorteos_existentes(json_file)
            print(f"Sorteos existentes en local: {sorted(sorteos_existentes)}")

            sorteos_faltantes = [sorteo_id for sorteo_id in range(1, total_sorteos + 1) if sorteo_id not in sorteos_existentes]

            print(f"Sorteos que faltan por descargar: {sorteos_faltantes}")

            if not sorteos_faltantes:
                print("¡Todos los sorteos ya están actualizados!")
            else:
                for sorteo_id in sorteos_faltantes:
                    url = f"{base_url}{sorteo_id}"
                    sorteo_data = get_sorteo_data(url)

                    if sorteo_data:
                        print(f"Datos del sorteo {sorteo_id} extraídos: {sorteo_data}")
                        update_json_file(sorteo_data, json_file)
                    else:
                        print(f"No se pudo obtener los datos del sorteo {sorteo_id}.")
        else:
            print("No se pudo obtener el número total de sorteos.")

    elif opcion == "2":
        json_file = "resultados.json"
        frecuencias = analizar_numeros_frecuentes(json_file)

        total_numeros = sum(frecuencias.values())
        total_juegos = get_total_sorteos("https://baloto.com/miloto/resultados")

        print("\nNúmeros más frecuentes y sus probabilidades:")
        for numero, conteo in frecuencias.items():
            probabilidad = (conteo / total_numeros) * 100
            probabilidad_por_juego = (conteo / total_juegos) * 100
            print(f"Número {numero}: {conteo} veces ({probabilidad:.2f}% de probabilidad, {probabilidad_por_juego:.2f}% por sorteo)")
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    menu()
