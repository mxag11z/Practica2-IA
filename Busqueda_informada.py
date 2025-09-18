import heapq
import random

def crear_laberinto(filas, columnas, densidad_obstaculos=0.3):
    """
    Genera un laberinto aleatorio con obstáculos.
    '0' representa un camino libre.
    '1' representa un obstáculo.
    """
    # Inicia un laberinto completamente libre
    laberinto = [['0' for _ in range(columnas)] for _ in range(filas)]

    # Coloca obstáculos aleatoriamente
    num_obstaculos = int(filas * columnas * densidad_obstaculos)
    for _ in range(num_obstaculos):
        fila = random.randint(0, filas - 1)
        columna = random.randint(0, columnas - 1)
        laberinto[fila][columna] = '1'

    # Define el punto de partida y la salida, asegurando que no sean obstáculos
    inicio = (0, 0)
    salida = (filas - 1, columnas - 1)
    laberinto[inicio[0]][inicio[1]] = '0'
    laberinto[salida[0]][salida[1]] = '0'

    return laberinto, inicio, salida

def heuristica(a, b):
    """
    Calcula la distancia de Manhattan entre dos puntos (nodos).
    Es una heurística admisible porque nunca sobreestima el costo real.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_estrella(laberinto, inicio, salida):
    """
    Implementación del algoritmo de búsqueda A* para encontrar el camino más corto.
    """
    filas, columnas = len(laberinto), len(laberinto[0])
    
    # Nodos vecinos (movimientos posibles: arriba, abajo, izquierda, derecha)
    vecinos = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    # open_set es una cola de prioridad para los nodos por visitar.
    # Se almacena como (f_score, posicion_actual).
    open_set = []
    heapq.heappush(open_set, (0, inicio))

    # Diccionario para reconstruir el camino. Mapea un nodo a su predecesor.
    vino_de = {}

    # g_score: costo del camino desde el inicio hasta el nodo actual.
    # Se inicializa con infinito para todos los nodos.
    g_score = { (f, c): float('inf') for f in range(filas) for c in range(columnas) }
    g_score[inicio] = 0

    # f_score: costo total estimado (g_score + heurística) desde el inicio hasta la salida
    # pasando por el nodo actual. Se inicializa con infinito.
    f_score = { (f, c): float('inf') for f in range(filas) for c in range(columnas) }
    f_score[inicio] = heuristica(inicio, salida)

    while open_set:
        # Obtiene el nodo de open_set con el f_score más bajo
        _, actual = heapq.heappop(open_set)

        # Si hemos llegado a la salida, reconstruimos y devolvemos el camino
        if actual == salida:
            camino = []
            while actual in vino_de:
                camino.append(actual)
                actual = vino_de[actual]
            camino.append(inicio)
            return camino[::-1] # Devuelve el camino invertido (de inicio a fin)

        # Explora los vecinos del nodo actual
        for df, dc in vecinos:
            vecino = (actual[0] + df, actual[1] + dc)

            # Verifica si el vecino está dentro de los límites del laberinto
            if 0 <= vecino[0] < filas and 0 <= vecino[1] < columnas:
                # Si el vecino es un obstáculo, lo ignora
                if laberinto[vecino[0]][vecino[1]] == '1':
                    continue

                # El costo para moverse a un vecino es 1
                tentative_g_score = g_score[actual] + 1

                # Si este camino hacia el vecino es mejor que el anterior registrado
                if tentative_g_score < g_score[vecino]:
                    vino_de[vecino] = actual
                    g_score[vecino] = tentative_g_score
                    f_score[vecino] = g_score[vecino] + heuristica(vecino, salida)
                    # Si el vecino no está en open_set, lo añade
                    if vecino not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[vecino], vecino))

    # Si el bucle termina y no se ha encontrado la salida, no hay camino posible
    return None

def imprimir_laberinto(laberinto, inicio, salida, camino=None):
    """
    Imprime el laberinto en la consola, marcando el inicio, la salida y el camino.
    """
    # Crea una copia para no modificar el laberinto original
    laberinto_impreso = [list(fila) for fila in laberinto]

    # Marca el camino en la copia, si se encontró uno
    if camino:
        for pos in camino:
            if pos != inicio and pos != salida:
                laberinto_impreso[pos[0]][pos[1]] = '*' # Símbolo para el camino

    # Marca el inicio y la salida
    laberinto_impreso[inicio[0]][inicio[1]] = 'S' # Símbolo para el inicio
    laberinto_impreso[salida[0]][salida[1]] = 'E' # Símbolo para la salida

    # Imprime el laberinto
    for fila in laberinto_impreso:
        linea = []
        for celda in fila:
            if celda == '1':
                linea.append('⬛') # Obstáculo
            elif celda == '0':
                linea.append('⬜') # Camino libre
            elif celda == 'S':
                linea.append('🟢') # Inicio
            elif celda == 'E':
                linea.append('🏁') # Salida
            elif celda == '*':
                linea.append('🔹') # Camino encontrado
        print(" ".join(linea))


# --- Bloque principal de ejecución ---
if __name__ == "__main__":
    # Define las dimensiones del laberinto
    FILAS = 20
    COLUMNAS = 20

    # Crea el laberinto, el punto de inicio y la salida
    laberinto, inicio, salida = crear_laberinto(FILAS, COLUMNAS)

    print("--- Laberinto Generado ---")
    print(f"Buscando ruta desde {inicio} hasta {salida}\n")
    imprimir_laberinto(laberinto, inicio, salida)

    # Ejecuta el algoritmo A*
    camino_encontrado = a_estrella(laberinto, inicio, salida)

    print("\n\n--- Solución ---")
    if camino_encontrado:
        print("¡Se encontró un camino! 🎉\n")
        imprimir_laberinto(laberinto, inicio, salida, camino_encontrado)
    else:
        print("No se pudo encontrar un camino. 😔")