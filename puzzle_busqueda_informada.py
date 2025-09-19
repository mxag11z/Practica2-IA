import heapq

# Define el tamaño del tablero (4x4)
N = 4

# Define la configuración objetivo
GOAL_STATE = tuple(range(1, N*N)) + (0,)

class Node:
    """
    Clase para representar un estado del puzzle (un nodo en el árbol de búsqueda).
    """
    def __init__(self, board, g=0, parent=None):
        self.board = board  # Tupla que representa el tablero
        self.parent = parent
        self.g = g # Costo desde el inicio
        self.h = self.calculate_manhattan_distance() # Heurística
        self.f = self.g + self.h # Costo total estimado

    def calculate_manhattan_distance(self):
        """Calcula la distancia de Manhattan total para el tablero actual."""
        distance = 0
        for i in range(N * N):
            if self.board[i] == 0:
                continue
            
            # Posición actual (fila, columna)
            current_row, current_col = divmod(i, N)
            
            # Posición objetivo (fila, columna)
            # El valor de la pieza - 1 nos da su índice objetivo
            goal_index = self.board[i] - 1
            goal_row, goal_col = divmod(goal_index, N)
            
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
        return distance

    def get_successors(self):
        """Genera todos los posibles estados sucesores a partir del estado actual."""
        successors = []
        empty_index = self.board.index(0)
        row, col = divmod(empty_index, N)

        # Movimientos posibles: Arriba, Abajo, Izquierda, Derecha
        # (cambio_fila, cambio_columna)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < N and 0 <= new_col < N:
                new_board = list(self.board)
                new_index = new_row * N + new_col
                
                # Intercambiar el espacio vacío con la pieza adyacente
                new_board[empty_index], new_board[new_index] = new_board[new_index], new_board[empty_index]
                
                successors.append(Node(tuple(new_board), self.g + 1, self))
        return successors

    # Métodos para que la cola de prioridad (heapq) pueda comparar nodos
    def __lt__(self, other):
        return self.f < other.f
    
    # Método para que el conjunto (closed_list) pueda hashear el tablero
    def __hash__(self):
        return hash(self.board)

def print_board(board_tuple):
    """Imprime el tablero en un formato legible."""
    for i in range(N):
        row = board_tuple[i*N : (i+1)*N]
        print(" ".join(f"{num:2}" if num != 0 else "  " for num in row))
    print("-" * (N * 3))

def print_solution(node):
    """Imprime la secuencia de movimientos desde el inicio hasta la solución."""
    path = []
    current = node
    while current:
        path.append(current.board)
        current = current.parent
    
    step = 0
    for board in reversed(path):
        print(f"Paso {step}:")
        print_board(board)
        step += 1

def a_star_search(initial_board):
    """
    Implementación del algoritmo A* para resolver el 15-puzzle.
    """
    start_node = Node(initial_board)
    
    # La open_list es una cola de prioridad (min-heap) que ordena por f(n)
    open_list = [start_node]
    heapq.heapify(open_list)
    
    # La closed_list es un conjunto para búsquedas rápidas de estados ya visitados
    closed_list = set()

    while open_list:
        # Extraer el nodo con el menor costo f
        current_node = heapq.heappop(open_list)

        if current_node.board == GOAL_STATE:
            print(f"¡Solución encontrada en {current_node.g} movimientos!")
            print_solution(current_node)
            return

        if current_node.board in closed_list:
            continue

        closed_list.add(current_node.board)

        for successor in current_node.get_successors():
            if successor.board not in closed_list:
                heapq.heappush(open_list, successor)
    
    print("No se encontró una solución.")

# --- Programa Principal ---
if __name__ == "__main__":
    # Tablero inicial (representado como una tupla)
    # 0 es el espacio vacío.
    # Este ejemplo es resoluble y tiene una solución corta.
    initial_board = (
        1, 2, 3, 4,
        5, 6, 0, 8,
        9, 10, 7, 12,
        13, 14, 11, 15
    )
    
    print("Estado Inicial:")
    print_board(initial_board)
    
    a_star_search(initial_board)