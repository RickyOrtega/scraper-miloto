from utils import revisar_json, crear_json_vacio
from extractor import get_total_sorteos, get_sorteo_data, get_sorteos_existentes, update_json_file
from analisis import (
    numeros_mas_frecuentes,
    numeros_menos_frecuentes,
    promedio_por_sorteo,
    diferencia_mayor_menor,
    conteo_pares_impares,
    conteo_por_rangos,
    pares_mas_comunes,
    tripletas_mas_comunes,
    numeros_repetidos_entre_sorteos,
    combinaciones_completas_mas_comunes,
    co_ocurrencia_de_numeros,
    numeros_que_no_han_salido,
    co_ocurrencias_del_numero_mas_frecuente,
    generar_jugadas_optimas,
    generar_jugadas_optimas_v2,
    generar_jugadas_por_patrones_determinista,
    )

def menu():
    file_path = "resultados.json"
    url_main = "https://baloto.com/miloto/resultados/"
    url_base = "https://baloto.com/miloto/resultados-miloto/"

    print("\nMenú:")
    print("1. Actualizar sorteos.")
    print("2. Analizar números frecuentes.")
    print("3. Mostrar dashboard.")
    print("4. Salir.")
    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        print("Obteniendo el total de sorteos disponibles...")
        total = get_total_sorteos(url_main)

        if not total:
            print("No se pudo obtener el número total de sorteos.")
            return

        print(f"Total de sorteos en línea: {total}")
        existentes = get_sorteos_existentes(file_path)
        print(f"Sorteos ya descargados localmente: {len(existentes)}")

        faltantes = [i for i in range(1, total + 1) if i not in existentes]

        if not faltantes:
            print("Todos los sorteos están actualizados.")
            return

        print(f"Sorteos que faltan: {faltantes}")

        for i in faltantes:
            print(f"Descargando sorteo #{i}...")
            sorteo = get_sorteo_data(f"{url_base}{i}/")
            if sorteo:
                update_json_file(sorteo, file_path)
                print(f"Sorteo #{i} guardado.")
            else:
                print(f"No se pudo obtener el sorteo #{i}. Probablemente ya no exista o hubo un error.")

    elif opcion == "2":
        print("\nAnálisis disponibles:")
        print("1. Números más frecuentes")
        print("2. Números menos frecuentes")
        print("3. Promedio por sorteo")
        print("4. Diferencia entre mayor y menor")
        print("5. Conteo pares e impares")
        print("6. Conteo por rangos")
        print("7. Pares más comunes")
        print("8. Tripletas más comunes")
        print("9. Repetición entre sorteos")
        print("10. Combinaciones exactas más comunes")
        print("11. Co-ocurrencia de números (números que suelen salir juntos)")
        print("12. Números que no han salido en los últimos sorteos")
        print("13. Números que más co-ocurren con el número más frecuente")
        print("14. Generar jugadas óptimas")
        sub_opcion = input("Seleccione una opción: ")

        if sub_opcion == "1":
            for n, c in numeros_mas_frecuentes(file_path):
                print(f"Número {n}: {c} veces")
        elif sub_opcion == "2":
            for n, c in numeros_menos_frecuentes(file_path):
                print(f"Número {n}: {c} veces")
        elif sub_opcion == "3":
            print(f"Promedio general por sorteo: {promedio_por_sorteo(file_path)}")
        elif sub_opcion == "4":
            data = diferencia_mayor_menor(file_path)
            print(f"Diferencia promedio: {data['promedio']}, mínima: {data['minima']}, máxima: {data['maxima']}")
        elif sub_opcion == "5":
            datos = conteo_pares_impares(file_path)
            print(f"Pares: {datos['pares']}, Impares: {datos['impares']}")
        elif sub_opcion == "6":
            rangos = conteo_por_rangos(file_path)
            for r, c in rangos.items():
                print(f"{r}: {c}")
        elif sub_opcion == "7":
            for par, c in pares_mas_comunes(file_path):
                print(f"{par}: {c} veces")
        elif sub_opcion == "8":
            for tripleta, c in tripletas_mas_comunes(file_path):
                print(f"{tripleta}: {c} veces")
        elif sub_opcion == "9":
            datos = numeros_repetidos_entre_sorteos(file_path)
            print(f"Repeticiones totales: {datos['repeticiones_totales']}")
            print(f"Promedio de repeticiones por sorteo: {datos['promedio_por_sorteo']}")
        elif sub_opcion == "10":
            combinaciones = combinaciones_completas_mas_comunes(file_path)
            if not combinaciones:
                print("Ninguna combinación exacta se ha repetido más de una vez.")
            else:
                for comb, veces in combinaciones:
                    print(f"{comb}: {veces} veces")
        elif sub_opcion == "11":
            asociaciones = co_ocurrencia_de_numeros(file_path)
            for numero, compañeros in sorted(asociaciones.items()):
                print(f"\nNúmero {numero} suele aparecer con:")
                for comp, veces in compañeros:
                    print(f"  - {comp}: {veces} veces")
        elif sub_opcion == "12":
            try:
                ultimos = int(input("¿Cuántos sorteos recientes quieres analizar?: "))
            except ValueError:
                print("Número inválido.")
                return
            frios = numeros_que_no_han_salido(file_path, ultimos)
            print(f"\nNúmeros que no han salido en los últimos {ultimos} sorteos:")
            print(", ".join(map(str, frios)))
        elif sub_opcion == "13":
            resultado = co_ocurrencias_del_numero_mas_frecuente(file_path)
            n_principal = resultado["numero_principal"]
            print(f"\nNúmero más frecuente: {n_principal}")
            print("Co-ocurre más frecuentemente con:")
            for num, veces in resultado["coocurrencias"]:
                print(f"  - Número {num}: {veces} veces")
        elif sub_opcion == "14":
            try:
                jugadas = int(input("¿Cuántas jugadas óptimas deseas generar?: "))
            except ValueError:
                print("Número inválido.")
                return
            jugadas_optimas = generar_jugadas_por_patrones_determinista(file_path, jugadas)
            print(f"\nJugadas óptimas generadas:")
            for jugada in jugadas_optimas:
                print(jugada)
        else:
            print("Opción no válida.")
    elif opcion == "3":
        from dashboard import mostrar_dashboard
        mostrar_dashboard(file_path)
    elif opcion == "4":
        print("Saliendo del programa...")
        return

if __name__ == "__main__":
    file_path = "resultados.json"
    if not revisar_json(file_path):
        crear_json_vacio(file_path)
    menu()
