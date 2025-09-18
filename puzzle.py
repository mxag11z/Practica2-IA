# ------------------------------------------------------------
# 15-puzzle (4x4) con búsquedas a ciegas:
#   - BFS  : garantiza mínima cantidad de movimientos (óptima)
#   - IDDFS: DFS con profundización iterativa (poca memoria)
#
# Representación de estado:
#   Tupla de 16 números (0..15). 0 es el hueco.
#     Ejemplo objetivo: (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0)
# ------------------------------------------------------------

from collections import deque
import random, time, sys, argparse

# ===== 1) Parámetros base del problema =====
N = 4  # tablero 4x4
GOAL = tuple(list(range(1, N*N)) + [0])  # estado meta (1..15, 0)

# ===== 2) Utilidades de índice y formato =====
def idx_rc(i):
    """Convierte un índice lineal [0..15] a (fila, columna)."""
    return divmod(i, N)

def swap(t, i, j):
    """Regresa una tupla nueva intercambiando posiciones i <-> j."""
    l = list(t)          # convertir a lista para poder mutar
    l[i], l[j] = l[j], l[i]
    return tuple(l)      # volver a tupla (inmutable = hashable)

def pretty(state):
    """Impresión amigable de un estado."""
    w = len(str(N*N-1))  # ancho para alinear (2 dígitos)
    filas = []
    for i in range(0, N*N, N):
        fila = ["." if x == 0 else f"{x:>{w}}" for x in state[i:i+N]]
        filas.append(" ".join(fila))
    return "\n".join(filas)

# ===== 3) Generación de vecinos (movimientos) =====
def neighbors(state):
    """
    Devuelve una lista de pares (acción, nuevo_estado).
    Acciones: U/D/L/R moviendo el HUECO (0) si cabe.
    """
    z = state.index(0)       # posición del hueco
    r, c = idx_rc(z)
    res = []
    if r > 0:   res.append(("U", swap(state, z, z-N)))  # subir
    if r < N-1: res.append(("D", swap(state, z, z+N)))  # bajar
    if c > 0:   res.append(("L", swap(state, z, z-1)))  # izquierda
    if c < N-1: res.append(("R", swap(state, z, z+1)))  # derecha
    return res

# ===== 4) Comprobación de solvencia (paridad) =====
def inversions(arr):
    """Cuenta inversiones ignorando el 0 (criterio clásico del 15-puzzle)."""
    a = [x for x in arr if x != 0]
    inv = 0
    for i in range(len(a)):
        for j in range(i+1, len(a)):
            if a[i] > a[j]:
                inv += 1
    return inv

def is_solvable(state):
    """
    Para tableros 4x4: (inversiones + fila_del_cero_desde_abajo) debe ser impar.
    Si no se cumple, ese estado NUNCA llega al objetivo.
    """
    inv = inversions(state)
    z = state.index(0)
    r, _ = idx_rc(z)
    row_from_bottom = N - r  # 1 = última fila (abajo), 4 = fila de arriba
    return (inv + row_from_bottom) % 2 == 1

# ===== 5) Reconstrucción de la ruta (acciones) =====
def rebuild(parent, goal):
    """
    parent: dict estado -> (padre, acción_para_llegar)
    Recorre hacia atrás desde goal hasta el inicial y arma la lista de acciones.
    """
    path = []
    s = goal
    while True:
        ps, a = parent[s]
        if ps is None:       # llegamos al inicial
            break
        path.append(a)
        s = ps
    path.reverse()
    return path

# ===== 6) BFS: búsqueda en anchura (a ciegas) =====
def solve_bfs(start):
    """
    Usa cola FIFO. Visita por niveles.
    Como todos los pasos cuestan 1, la primera vez que vemos el objetivo
    tenemos la solución con MENOR número de movimientos.
    """
    t0 = time.time()
    q = deque([start])
    parent = {start: (None, None)}  # quién me generó y con qué acción
    expanded = 0

    while q:
        s = q.popleft()
        if s == GOAL:
            path = rebuild(parent, s)
            return dict(algo="BFS", path=path, expanded=expanded, time=time.time()-t0)

        # Generar vecinos y encolar los NUEVOS (evitamos repetidos)
        for a, ns in neighbors(s):
            if ns not in parent:
                parent[ns] = (s, a)
                q.append(ns)
        expanded += 1

    # Si se vacía la cola sin encontrar objetivo (poco usual con mezclas cortas)
    return dict(algo="BFS", path=None, expanded=expanded, time=time.time()-t0)

# ===== 7) IDDFS: DFS con profundización iterativa (a ciegas) =====
def dls(state, depth, parent, en_rama):
    """
    DFS limitada a 'depth'.
    - 'parent' guarda el árbol de generación.
    - 'en_rama' evita ciclos en la rama actual (stack de DFS).
    """
    if state == GOAL:
        return True
    if depth == 0:
        return False

    en_rama.add(state)
    for a, ns in neighbors(state):
        if ns in en_rama:   # no regresar al mismo estado en la rama
            continue
        if ns not in parent:
            parent[ns] = (state, a)
        if dls(ns, depth-1, parent, en_rama):
            return True
    en_rama.remove(state)
    return False

def solve_iddfs(start, max_depth=40):
    """
    Ejecuta DFS repetidamente con límites 0,1,2,...,max_depth.
    Ventaja: usa poca memoria como DFS, pero es completa si subimos el límite.
    """
    t0 = time.time()
    total_expanded = 0  # aproximación: contamos cuántos estados llegaron a parent

    for limit in range(max_depth + 1):
        parent = {start: (None, None)}
        found = dls(start, limit, parent, set())
        total_expanded += len(parent)
        if found:
            path = rebuild(parent, GOAL)
            return dict(algo=f"IDDFS(d={limit})", path=path,
                        expanded=total_expanded, time=time.time()-t0)

    return dict(algo="IDDFS", path=None, expanded=total_expanded, time=time.time()-t0)

# ===== 8) Utilidades: mezclar estado y parsear entrada =====
def scramble_from_goal(steps=12, seed=None):
    """
    Mezcla el tablero aplicando 'steps' movimientos válidos al objetivo.
    Con esto GARANTIZAMOS que el resultado sí es resoluble.
    """
    if seed is not None:
        random.seed(seed)
    s = GOAL
    prev = None
    for _ in range(steps):
        ops = neighbors(s)
        if prev is not None:
            # evita deshacer inmediatamente el movimiento anterior
            ops = [x for x in ops if x[1] != prev]
        a, ns = random.choice(ops)
        prev, s = s, ns
    return s

def parse_state(s):
    """
    Convierte un string "1 2 3 ... 0" a tupla (valida rango y que no se repitan).
    """
    nums = [int(x) for x in s.replace(",", " ").split()]
    if len(nums) != 16 or sorted(nums) != list(range(16)):
        raise ValueError("Debes dar 16 números 0..15 sin repetir.")
    return tuple(nums)

# ===== 9) CLI mínimo para probar desde terminal =====
def main():
    ap = argparse.ArgumentParser(description="15-puzzle con búsquedas a ciegas (BFS / IDDFS)")
    ap.add_argument("--algo", choices=["bfs", "iddfs"], default="bfs",
                    help="Selecciona el algoritmo a ciegas")
    ap.add_argument("--start", type=str,
                    help='Estado inicial: 16 números, p. ej. "1 2 3 4 5 6 7 8 9 10 11 12 13 14 0 15"')
    ap.add_argument("--scramble", type=int, default=12,
                    help="Número de movimientos aleatorios desde el objetivo")
    ap.add_argument("--seed", type=int, default=None, help="Semilla aleatoria (reproducible)")
    ap.add_argument("--max-depth", type=int, default=40, help="Límite máximo para IDDFS")
    args = ap.parse_args()

    # Elegir estado inicial: dado por el usuario o mezclado desde el objetivo
    start = parse_state(args.start) if args.start else scramble_from_goal(args.scramble, args.seed)

    print("\nEstado inicial:")
    print(pretty(start))

    # Si metiste --start, verificamos solvencia (si no, avisamos y salimos)
    if not is_solvable(start):
        print("\n⚠️  Ese estado NO es resoluble para 4×4.", file=sys.stderr)
        sys.exit(1)

    # Resolver con el algoritmo pedido
    if args.algo == "bfs":
        res = solve_bfs(start)
    else:
        res = solve_iddfs(start, args.max_depth)

    # Reporte compacto
    print(f"\n[{res['algo']}]  tiempo={res['time']:.3f}s  nodos≈{res['expanded']}")
    if res["path"] is None:
        print("No se encontró solución con los límites dados.")
        return
    print(f"Longitud de solución: {len(res['path'])} movimientos")
    print("Secuencia:", " ".join(res['path']))

if __name__ == "__main__":
    main()
