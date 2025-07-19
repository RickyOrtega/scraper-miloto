from collections import Counter
from collections import defaultdict
from itertools import combinations
from utils import cargar_json

def co_ocurrencia_de_numeros(file_path):
    data = cargar_json(file_path)
    sorteos = data.get("sorteos", [])

    coocurrencias = defaultdict(lambda: defaultdict(int))

    for sorteo in sorteos:
        balotas = sorteo.get("balotas", [])
        for i in range(len(balotas)):
            for j in range(len(balotas)):
                if i != j:
                    coocurrencias[balotas[i]][balotas[j]] += 1

    resultado = {}
    for numero, co in coocurrencias.items():
        ordenado = sorted(co.items(), key=lambda x: x[1], reverse=True)
        resultado[numero] = ordenado[:5]  # Top 5 compañeros - OJO: no precisamente deben ser las más comunes en general

    return resultado

from collections import Counter, defaultdict
from utils import cargar_json

def co_ocurrencias_del_numero_mas_frecuente(file_path):
    data = cargar_json(file_path)
    sorteos = data.get("sorteos", [])

    balotas = [num for sorteo in sorteos for num in sorteo.get("balotas", [])]
    frecuencia = Counter(balotas)

    numero_principal, _ = frecuencia.most_common(1)[0]

    coocurrencias = Counter()
    for sorteo in sorteos:
        balotas = sorteo.get("balotas", [])
        if numero_principal in balotas:
            for num in balotas:
                if num != numero_principal:
                    coocurrencias[num] += 1

    # Paso 4: devolver el resultado
    return {
        "numero_principal": numero_principal,
        "coocurrencias": coocurrencias.most_common(5)
    }


def obtener_balotas(file_path):
    data = cargar_json(file_path)
    return [s["balotas"] for s in data.get("sorteos", [])]

def numeros_mas_frecuentes(file_path):
    balotas = [num for juego in obtener_balotas(file_path) for num in juego]
    frecuencia = Counter(balotas)
    return frecuencia.most_common(10)

def numeros_menos_frecuentes(file_path):
    balotas = [num for juego in obtener_balotas(file_path) for num in juego]
    frecuencia = Counter(balotas)
    return sorted(frecuencia.items(), key=lambda x: x[1])[:10]

def promedio_por_sorteo(file_path):
    balotas = obtener_balotas(file_path)
    promedios = [sum(juego) / len(juego) for juego in balotas]
    return round(sum(promedios) / len(promedios), 2)

def diferencia_mayor_menor(file_path):
    balotas = obtener_balotas(file_path)
    diferencias = [max(j) - min(j) for j in balotas]
    return {
        "promedio": round(sum(diferencias) / len(diferencias), 2),
        "minima": min(diferencias),
        "maxima": max(diferencias)
    }

def conteo_pares_impares(file_path):
    balotas = [num for juego in obtener_balotas(file_path) for num in juego]
    pares = sum(1 for n in balotas if n % 2 == 0)
    impares = len(balotas) - pares
    return {"pares": pares, "impares": impares}

def conteo_por_rangos(file_path):
    rangos = {"1-10": 0, "11-20": 0, "21-30": 0, "31-40": 0}
    balotas = [num for juego in obtener_balotas(file_path) for num in juego]
    for n in balotas:
        if 1 <= n <= 10:
            rangos["1-10"] += 1
        elif 11 <= n <= 20:
            rangos["11-20"] += 1
        elif 21 <= n <= 30:
            rangos["21-30"] += 1
        elif 31 <= n <= 40:
            rangos["31-40"] += 1
    return rangos

def pares_mas_comunes(file_path):
    juegos = obtener_balotas(file_path)
    pares = Counter()
    for j in juegos:
        pares.update(combinations(sorted(j), 2))
    return pares.most_common(5)

def tripletas_mas_comunes(file_path):
    juegos = obtener_balotas(file_path)
    tripletas = Counter()
    for j in juegos:
        tripletas.update(combinations(sorted(j), 3))
    return tripletas.most_common(5)

def numeros_repetidos_entre_sorteos(file_path):
    juegos = obtener_balotas(file_path)
    repeticiones = 0
    total_comparaciones = 0
    for i in range(1, len(juegos)):
        anterior = set(juegos[i-1])
        actual = set(juegos[i])
        repeticiones += len(anterior.intersection(actual))
        total_comparaciones += 1
    promedio = round(repeticiones / total_comparaciones, 2)
    return {
        "repeticiones_totales": repeticiones,
        "promedio_por_sorteo": promedio
    }

def combinaciones_completas_mas_comunes(file_path):
    balotas = obtener_balotas(file_path)
    combinaciones = Counter(tuple(sorted(jugada)) for jugada in balotas)
    combinaciones_repetidas = [ (list(k), v) for k, v in combinaciones.items() if v > 1 ]
    return sorted(combinaciones_repetidas, key=lambda x: x[1], reverse=True)

def numeros_que_no_han_salido(file_path, ultimos_n=10):
    data = cargar_json(file_path)
    sorteos = sorted(data.get("sorteos", []), key=lambda x: x["numero"], reverse=True)
    recientes = sorteos[:ultimos_n]

    numeros_salidos = set()
    for sorteo in recientes:
        numeros_salidos.update(sorteo.get("balotas", []))

    universo = set(range(1, 39))
    numeros_frios = sorted(universo - numeros_salidos)
    return numeros_frios

def ranking_de_numeros(file_path):
    frecuencias = dict(Counter([n for jugada in obtener_balotas(file_path) for n in jugada]))
    co_ocurrencias = co_ocurrencias_del_numero_mas_frecuente(file_path)["coocurrencias"]
    
    score = {}
    for n in range(1, 39):
        freq = frecuencias.get(n, 0)
        cooc = sum(v for num, v in co_ocurrencias if num == n)
        score[n] = freq + (cooc * 0.5)  # ejemplo de ponderación

    return sorted(score.items(), key=lambda x: x[1], reverse=True)

def generar_jugadas_optimas(file_path, cantidad=5):
    ranking = [num for num, _ in ranking_de_numeros(file_path)]
    jugadas = []
    for i in range(cantidad):
        jugadas.append(sorted(ranking[i*6:(i+1)*6]))
    return jugadas
