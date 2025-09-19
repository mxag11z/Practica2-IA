from collections import deque

def bfs(graph, nodo_inicial, nodo_buscado):
    solution = []  ##Camino a tomar
    costs = 0      ##Costo en tiempo 
    nodos_frontera = deque()
    nodos_visitados = []

    nodos_frontera.append(nodo_inicial)
    nodos_visitados.append(nodo_inicial)

    while nodos_frontera:
        ##print("Queue",nodos_frontera)
        print("Nodos visitados",nodos_visitados)
        nodo_actual = nodos_frontera.popleft()
        solution.append(nodo_actual)
        if nodo_actual == nodo_buscado:
            break
        ##if not graph[nodo_actual]:  
           ## print(f"!!! {nodo_actual} es un callejón sin salida (pared)")
        for vecino in graph[nodo_actual]:
            if vecino not in nodos_visitados:
                nodos_frontera.append(vecino)
                nodos_visitados.append(vecino)

        costs+=1
    return costs, solution

graph = {
    "A": ["B"],
    "B": ["C"],
    "C": ["D", "G"],
    "D": ["E"],
    "E": ["F"],
    "F": [],
    "G": ["H"],
    "H": ["K", "I"],
    "K": ["L"],
    "L": ["M"],
    "M": ["N"],
    "N": [],
    "I": ["J"],
    "J": [],
}

cost, path = bfs(graph, "A", "N")
print("Costo:", cost)
print("Camino recorrido:", path)
