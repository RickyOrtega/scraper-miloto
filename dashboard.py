import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import json
import datetime
from collections import Counter

FILE_PATH = "resultados.json"
año_actual = datetime.datetime.now().year

# Secciones dinámicas
SECCIONES = {
    "historial_total": {
        "titulo": "📚 Historial completo",
        "filtro": lambda sorteos: sorteos
    },
    "año_actual": {
        "titulo": f"📅 Año {año_actual}",
        "filtro": lambda sorteos: [s for s in sorteos if "fecha" in s and str(año_actual) in s["fecha"]]
    },
    "ultimos_50": {
        "titulo": "🎯 Últimos 50 sorteos",
        "filtro": lambda sorteos: sorted(sorteos, key=lambda x: x["numero"])[-50:]
    }
}

# Funciones de análisis visual
def graf_frecuencia(data):
    freqs = Counter(n for s in data for n in s.get("balotas", []))
    items = freqs.most_common(10)
    nums = [str(n) for n, _ in items]
    vals = [c for _, c in items]

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(nums, vals)
    ax.set_title("Más frecuentes")
    return fig

def graf_menos_frecuentes(data):
    freqs = Counter(n for s in data for n in s.get("balotas", []))
    items = sorted(freqs.items(), key=lambda x: x[1])[:10]
    nums = [str(n) for n, _ in items]
    vals = [c for _, c in items]

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(nums, vals, color='orange')
    ax.set_title("Menos frecuentes")
    return fig

def graf_pares_impares(data):
    todos = [n for s in data for n in s.get("balotas", [])]
    pares = sum(1 for n in todos if n % 2 == 0)
    impares = len(todos) - pares

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.pie([pares, impares], labels=["Pares", "Impares"], autopct='%1.1f%%', startangle=90)
    ax.set_title("Pares vs Impares")
    return fig

def graf_promedio(data):
    promedios = [sum(s["balotas"]) / len(s["balotas"]) for s in data if s.get("balotas")]
    promedio = round(sum(promedios) / len(promedios), 2) if promedios else 0

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(["Promedio"], [promedio], color="green")
    ax.set_title("Promedio por sorteo")
    return fig

def graf_diferencia(data):
    diferencias = [max(s["balotas"]) - min(s["balotas"]) for s in data if s.get("balotas")]
    if not diferencias:
        return plt.Figure(figsize=(6, 4))
    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(["Min", "Prom", "Max"], [min(diferencias), sum(diferencias)/len(diferencias), max(diferencias)], color="purple")
    ax.set_title("Diferencia mayor-menor")
    return fig

def graf_coocurrencias(data):
    todos = [n for s in data for n in s.get("balotas", [])]
    if not todos:
        return plt.Figure(figsize=(6, 4))

    principal = Counter(todos).most_common(1)[0][0]
    cooc = Counter()
    for s in data:
        b = s.get("balotas", [])
        if principal in b:
            cooc.update(n for n in b if n != principal)
    items = cooc.most_common(5)
    nums = [str(n) for n, _ in items]
    vals = [c for _, c in items]

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(nums, vals, color="red")
    ax.set_title(f"Co-ocurrencias con #{principal}")
    return fig

def graf_histograma_balotas(data):
    todos = [n for s in data for n in s.get("balotas", [])]
    if not todos:
        return plt.Figure(figsize=(6, 4))

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.hist(todos, bins=range(1, 41), edgecolor="black", align='left')
    ax.set_title("Histograma de Balotas")
    ax.set_xlabel("Número de Balota")
    ax.set_ylabel("Frecuencia")
    return fig

# Lista de funciones gráficas
GRAFICAS = [
    graf_frecuencia,
    graf_menos_frecuentes,
    graf_pares_impares,
    graf_promedio,
    graf_diferencia,
    graf_coocurrencias
]

def mostrar_grafica(figura, padre, fila, columna):
    canvas = FigureCanvasTkAgg(figura, master=padre)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")
    padre.grid_columnconfigure(columna, weight=1)

# Cargar sorteos desde JSON
with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
sorteos = data.get("sorteos", [])

# Tkinter: ventana principal
root = tk.Tk()
root.title("📊 Dashboard MiLoto - Secciones por período")
root.state("zoomed")

# Canvas con scroll
main_canvas = tk.Canvas(root)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=main_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

main_canvas.configure(yscrollcommand=scrollbar.set)
main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

frame_contenedor = ttk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=frame_contenedor, anchor="nw")

# Renderizar secciones
for seccion_idx, (clave, meta) in enumerate(SECCIONES.items()):
    frame_seccion = ttk.LabelFrame(frame_contenedor, text=meta["titulo"], padding=10)
    frame_seccion.grid(row=seccion_idx, column=0, padx=10, pady=20, sticky="ew")
    for col in range(3):
        frame_seccion.grid_columnconfigure(col, weight=1)

    data_filtrada = meta["filtro"](sorteos)
    
    # Gráficas estándar
    for idx, generar in enumerate(GRAFICAS):
        fila = (idx // 3) + (1 if clave == "historial_total" else 0)
        columna = idx % 3
        fig = generar(data_filtrada)
        mostrar_grafica(fig, frame_seccion, fila, columna)

    # Gráfica adicional solo para historial total
    if clave == "historial_total":
        fig_histograma = graf_histograma_balotas(data_filtrada)
        canvas = FigureCanvasTkAgg(fig_histograma, master=frame_seccion)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")



root.mainloop()
