import requests
from bs4 import BeautifulSoup
import re
import json
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter

def revisar_json(file_path):
    """
    Revisa si el archivo JSON existe y tiene datos válidos.

    Args:
        file_path (str): Ruta del archivo JSON.

    Returns:
        bool: True si el archivo es válido, False en caso contrario.
    """
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            
            return isinstance(json_data, dict) and "sorteos" in json_data
    except (FileNotFoundError, json.JSONDecodeError):
        print("El archivo JSON no existe o está corrupto. Creando uno nuevo.")
        return False
    

def crear_json_vacio(file_path):
    """
    Crea un archivo JSON vacío con la estructura inicial.

    Args:
        file_path (str): Ruta del archivo JSON.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump({
                "cantidadSorteos": 0,
                "fechaUltimoSorteo": None,
                "fechaUltimaConsulta": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "sorteos": []
            }, file, indent=4)
        print("Archivo JSON creado correctamente.")
    except Exception as e:
        print(f"Error al crear el archivo JSON: {e}")

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

def mostrar_dashboard(file_path):
    """
    Muestra un dashboard visual con análisis de frecuencias de números sorteados.
    
    Args:
        file_path (str): Ruta del archivo JSON con los sorteos.
    """
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        
        balotas = []
        for sorteo in json_data.get("sorteos", []):
            balotas.extend(sorteo.get("balotas", []))

        if not balotas:
            print("No hay datos de balotas para analizar.")
            return

        frecuencia = Counter(balotas)

        # Ordenamos las frecuencias por número
        numeros = sorted(frecuencia.keys())
        conteos = [frecuencia[num] for num in numeros]

        # --------- GRÁFICO DE BARRAS ---------
        # plt.figure(figsize=(12,6))
        # plt.bar(numeros, conteos)
        # plt.xlabel('Número de Balota')
        # plt.ylabel('Frecuencia de aparición')
        # plt.title('Frecuencia de números en MiLoto')
        # plt.grid(axis='y', linestyle='--', alpha=0.7)
        # plt.xticks(numeros)
        # plt.tight_layout()
        # plt.show()

        # # --------- HISTOGRAMA ---------
        # plt.figure(figsize=(12,6))
        # plt.hist(balotas, bins=range(1, 41), edgecolor='black', align='left')
        # plt.xlabel('Número de Balota')
        # plt.ylabel('Cantidad')
        # plt.title('Distribución de balotas en MiLoto')
        # plt.grid(axis='y', linestyle='--', alpha=0.7)
        # plt.xticks(range(1, 40))
        # plt.tight_layout()
        # plt.show()

        # --------- TOP 5 MÁS FRECUENTES ---------
        top_5_mas = frecuencia.most_common(5)
        print("\n🎯 Top 5 números más frecuentes:")
        for numero, cantidad in top_5_mas:
            print(f"  Número {numero}: {cantidad} veces")

        # --------- TOP 5 MENOS FRECUENTES ---------
        top_5_menos = sorted(frecuencia.items(), key=lambda x: x[1])[:5]
        print("\n💤 Top 5 números menos frecuentes:")
        for numero, cantidad in top_5_menos:
            print(f"  Número {numero}: {cantidad} veces")

    except FileNotFoundError:
        print("El archivo JSON no existe.")
    except json.JSONDecodeError:
        print("Error al leer el archivo JSON.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

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
    print("3. Mostrar dashboard de resultados.")
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
    
    elif opcion == "3":
        json_file = "resultados.json"
        mostrar_dashboard(json_file)
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    json_file = "resultados.json"

    if not revisar_json(json_file):
        crear_json_vacio(json_file)

    menu()
