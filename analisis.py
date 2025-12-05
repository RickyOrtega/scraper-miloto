from collections import Counter
from collections import defaultdict
from itertools import combinations
from utils import cargar_json
import random

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

    universo = set(range(1, 40))
    numeros_frios = sorted(universo - numeros_salidos)
    return numeros_frios

def ranking_de_numeros(file_path):
    frecuencias = dict(Counter([n for jugada in obtener_balotas(file_path) for n in jugada]))
    co_ocurrencias_generales = co_ocurrencia_de_numeros(file_path)
    
    score = {}
    for n in range(1, 40):
            freq = frecuencias.get(n, 0)

            cooc = sum(v for num, v in co_ocurrencias_generales.get(n, []))

            score[n] = (freq * 1.0) + (cooc * 0.2)

    return sorted(score.items(), key=lambda x: x[1], reverse=True)

def ranking_de_numeros_correlacion_prioritaria(file_path):
    frecuencias = dict(Counter([n for jugada in obtener_balotas(file_path) for n in jugada]))
    cooc_puntero_data = co_ocurrencias_del_numero_mas_frecuente(file_path)
    cooc_puntero = dict(cooc_puntero_data["coocurrencias"])
    
    score = {}
    for n in range(1, 40):
        freq = frecuencias.get(n, 0)
        
        score_cooc_puntero = cooc_puntero.get(n, 0) 
        score[n] = (freq * 1.0) + (score_cooc_puntero * 0.5)
    
    return sorted(score.items(), key=lambda x: x[1], reverse=True)

def generar_jugadas_optimas(file_path, cantidad=5):
    ranking = [num for num, _ in ranking_de_numeros(file_path)]
    jugadas = []
    for i in range(cantidad):
        jugadas.append(sorted(ranking[i*5:(i+1)*5]))
    return jugadas

def generar_jugadas_optimas_v2(file_path, cantidad=5):
    ranking = [num for num, _ in ranking_de_numeros_correlacion_prioritaria(file_path)]

    top_calientes = ranking[:10]
    medio = ranking[10:-10]
    bottom_frios = ranking[-10:]

    jugadas = []
    for _ in range(cantidad):
        jugada = set()
        
        # 2 Calientes (Top 10)
        jugada.update(random.sample(top_calientes, 2))
        
        # 2 Medios
        jugada.update(random.sample(medio, 2))
        
        # 1 Frío (Bottom 10)
        jugada.add(random.choice(bottom_frios))
        
        # En caso de que se repita un número (casi imposible), ajustamos.
        while len(jugada) < 5:
            jugada.add(random.choice(ranking))

        jugadas.append(sorted(list(jugada)))
        
    return jugadas

def generar_jugadas_por_patrones(file_path, cantidad=5):
    """
    Genera jugadas tomando los Pares y Tripletas más comunes y 
    completando la jugada con números fríos para el balance.
    """
    
    ranking = [num for num, _ in ranking_de_numeros_correlacion_prioritaria(file_path)]
    
    # Obtener patrones calientes
    top_pares = [list(p[0]) for p in pares_mas_comunes(file_path)]
    top_tripletas = [list(t[0]) for t in tripletas_mas_comunes(file_path)]
    
    # Obtener números fríos (los menos rankeados o que no han salido)
    frios_del_ranking = ranking[-10:] # Los 10 números menos probables según el ranking
    
    jugadas = []
    
    for i in range(cantidad):
        jugada = set()
        
        if i % 2 == 0 and top_tripletas:
            tripleta = top_tripletas[i % len(top_tripletas)]
            jugada.update(tripleta)
            
            complemento = random.sample(frios_del_ranking, min(2, len(frios_del_ranking)))
            jugada.update(complemento)
            
        elif top_pares:
            par = top_pares[i % len(top_pares)]
            jugada.update(par)
            
            media_fria = ranking[15:]
            complemento = random.sample(media_fria, min(3, len(media_fria)))
            jugada.update(complemento)
            
        while len(jugada) < 5:
            jugada.add(random.choice(ranking)) 

        jugada = {n for n in jugada if 1 <= n <= 39}
        while len(jugada) < 5:
            jugada.add(random.randint(1, 39))

        jugadas.append(sorted(list(jugada)))
        
    return jugadas

def generar_jugadas_por_patrones_determinista(file_path, cantidad=5):
    """
    Genera jugadas de forma determinista tomando los Pares y Tripletas más comunes y
    completando la jugada con números rankeados, eliminando el componente aleatorio.
    """

    # 1. Obtener datos de ranking y patrones (Determinista)
    ranking = [num for num, _ in ranking_de_numeros_correlacion_prioritaria(file_path)]
    top_pares = [list(p[0]) for p in pares_mas_comunes(file_path)]
    top_tripletas = [list(t[0]) for t in tripletas_mas_comunes(file_path)]

    # Categorías del Ranking (Determinista)
    # Calientes (Top 10), Frios (Bottom 10)
    top_calientes = ranking[:10]
    frios_del_ranking = ranking[-10:]

    jugadas = []

    for i in range(cantidad):
        jugada = set()

        # Usamos los patrones más comunes de forma secuencial
        idx_tripleta = i % len(top_tripletas) if top_tripletas else -1
        idx_par = i % len(top_pares) if top_pares else -1

        # Lógica de construcción
        if i % 2 == 0 and top_tripletas:
            # Opción A: Usar una tripleta común
            tripleta = top_tripletas[idx_tripleta]
            jugada.update(tripleta)

            # Complemento: 2 números del ranking más alto (no incluidos)
            complemento_candidatos = [n for n in ranking if n not in jugada]
            # Seleccionamos los 2 mejores rankeados de los que quedan
            complemento = sorted(complemento_candidatos, key=lambda n: ranking.index(n))[:2]
            jugada.update(complemento)

        elif top_pares:
            # Opción B: Usar un par común
            par = top_pares[idx_par]
            jugada.update(par)

            # Complemento: 3 números del ranking que no estén ya en la jugada
            complemento_candidatos = [n for n in ranking if n not in jugada]
            # Seleccionamos los 3 mejores rankeados de los que quedan
            complemento = sorted(complemento_candidatos, key=lambda n: ranking.index(n))[:3]
            jugada.update(complemento)

        # Llenado determinista si la jugada no tiene 5 números (Debería ser raro, pero es un seguro)
        while len(jugada) < 5:
            # Usa los números del ranking que no están en la jugada, priorizando los más calientes
            for num in ranking:
                if num not in jugada:
                    jugada.add(num)
                    if len(jugada) == 5:
                        break
        
        # Filtrar por el rango de balotas si aplica (1 a 39)
        jugada = {n for n in jugada if 1 <= n <= 39}

        # Asegurar 5 números, usando los mejores del ranking que falten.
        if len(jugada) < 5:
             # Usamos el ranking para rellenar
             relleno_candidatos = [n for n in ranking if n not in jugada]
             jugada.update(relleno_candidatos[:5 - len(jugada)])
             
             # Si aún faltan (ej. ranking pequeño), rellenar con el universo
             if len(jugada) < 5:
                  universo_completo = set(range(1, 40))
                  jugada.update(universo_completo - jugada)
                  jugada = set(list(jugada)[:5])


        jugadas.append(sorted(list(jugada)))

    return jugadas

