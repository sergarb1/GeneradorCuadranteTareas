# -*- coding: utf-8 -*-
# =============================================================================
# scheduler.py — Modelo de optimización CP-SAT
# =============================================================================
# Este archivo implementa el corazón del asignador: un modelo de optimización
# combinatoria usando Google OR-Tools CP-SAT.
#
# PROBLEMA:
#   Dados N profesores con disponibilidad horaria y límites de carga,
#   y M necesidades (tareas) con fechas, horas y rango de profesores
#   requeridos [min, max], encontrar la asignación óptima.
#
# VARIABLES DE DECISIÓN:
#   x[n, p] ∈ {0, 1}  — 1 si el profesor p se asigna a la necesidad n
#
# RESTRICCIONES:
#   1. Capacidad:   min_n ≤ Σ x[n, p] ≤ max_n  (para cada necesidad n)
#   2. Solapamiento: x[ni, p] + x[nj, p] ≤ 1   (mismo profesor, mismo tiempo)
#   3. Carga total: Σ duración(n) * x[n, p] ≤ max_hours(p)
#   4. Carga diaria: Σ duración(n) * x[n, p] ≤ max_hours_per_day(p)  (por día)
#   5. Disponibilidad: x[n, p] = 0 si el profesor no cubre el horario
#
# FUNCIÓN OBJETIVO:
#   Maximizar Σ x[n, p]  (tantas asignaciones como sea posible)
#
# Así el solver intenta cubrir cada necesidad hasta su máximo,
# no solo hasta el mínimo.
# =============================================================================

# Import del modelo CP-SAT de Google OR-Tools
from ortools.sat.python import cp_model


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def duration_min(need):
    """Calcula la duración de una necesidad en minutos.
    
    Parámetros:
        need (dict): Diccionario con claves "start" y "end" en formato "HH:MM".
    
    Retorna:
        int: Diferencia en minutos entre start y end.
    
    Ejemplo:
        duration_min({"start": "09:00", "end": "11:30"}) → 150
    """
    # Extrae horas y minutos de cada timestamp
    sh, sm = map(int, need["start"].split(":"))  # Hora de inicio
    eh, em = map(int, need["end"].split(":"))     # Hora de fin
    
    # Convierte todo a minutos y calcula la diferencia
    return (eh * 60 + em) - (sh * 60 + sm)


def overlaps(n1, n2):
    """Determina si dos necesidades se solapan en el tiempo.
    
    Dos tareas se solapan si ocurren el mismo día y sus intervalos
    horarios se cruzan. Usa la lógica estándar de intersección
    de intervalos: A solapa B si A.start < B.end AND B.start < A.end.
    
    Parámetros:
        n1, n2 (dict): Necesidades con claves "date", "start", "end".
    
    Retorna:
        bool: True si las necesidades solapan, False en caso contrario.
    """
    # Si son días distintos, no hay solapamiento posible
    if n1["date"] != n2["date"]:
        return False
    
    # Comprueba intersección de intervalos horarios
    return n1["start"] < n2["end"] and n2["start"] < n1["end"]


# =============================================================================
# CLASE PRINCIPAL: TeacherScheduler
# =============================================================================

class TeacherScheduler:
    """Encapsula el modelo CP-SAT y su resolución.
    
    Uso típico:
        scheduler = TeacherScheduler(teachers, needs)
        scheduler.build_model()
        status = scheduler.solve()
        asignaciones = scheduler.extract_assignment()
    """
    
    def __init__(self, teachers, needs):
        """Inicializa el scheduler con los datos del problema.
        
        Parámetros:
            teachers (list): Lista de dicts con datos de profesores.
            needs (list): Lista de dicts con datos de necesidades/tareas.
        """
        # Guarda referencias a los datos de entrada
        self.teachers = teachers          # Lista de profesores
        self.needs = needs                # Lista de necesidades
        
        # Modelo CP-SAT (contiene variables y restricciones)
        self.model = cp_model.CpModel()
        
        # Solver CP-SAT (ejecuta la búsqueda)
        self.solver = cp_model.CpSolver()
        
        # Variables de decisión: x[(n_idx, p_idx)] → BoolVar
        self.x = {}
        
        # Resultado de la asignación (lista de dicts)
        self.assignment = None
        
        # Pares (n, p) válidos (profesor disponible para la necesidad)
        # Se calcula en build_model() para reutilizar
        self._valid_pairs = []
    
    # =========================================================================
    # VERIFICACIÓN DE DISPONIBILIDAD
    # =========================================================================
    
    def _teacher_available(self, teacher, need):
        """Comprueba si un profesor está disponible para una necesidad.
        
        Un profesor está disponible si existe al menos una franja horaria
        en su lista de time_slots que contenga completamente el intervalo
        de la necesidad (misma fecha, start <= need.start, end >= need.end).
        
        Parámetros:
            teacher (dict): Datos del profesor (contiene "time_slots").
            need (dict): Datos de la necesidad (contiene "date", "start", "end").
        
        Retorna:
            bool: True si el profesor puede cubrir la necesidad.
        """
        # Recorre todas las franjas del profesor buscando una que cubra la necesidad
        return any(
            # Condición: misma fecha y franja que contiene a la necesidad
            s["date"] == need["date"]
            and s["start"] <= need["start"]
            and s["end"] >= need["end"]
            for s in teacher.get("time_slots", [])  # time_slots por defecto []
        )
    
    # =========================================================================
    # CONSTRUCCIÓN DEL MODELO
    # =========================================================================
    
    def build_model(self, locked=None):
        """Construye el modelo CP-SAT completo.
        
        Este método:
        1. Identifica todos los pares (necesidad, profesor) válidos
        2. Crea las variables binarias x[n, p]
        3. Añade las restricciones de capacidad, solapamiento, carga total y diaria
        4. Define la función objetivo (maximizar asignaciones)
        
        Parámetros:
            locked (dict|None): Diccionario {(need_idx, teacher_idx): True}
                para asignaciones que deben forzarse a 1.
        
        No retorna nada; modifica self.model y self._valid_pairs.
        """
        self.locked = locked or {}
        # Índices de necesidades y profesores
        N = list(range(len(self.needs)))       # [0, 1, ..., M-1]
        P = list(range(len(self.teachers)))    # [0, 1, ..., N-1]
        
        # Conjunto de fechas únicas (para restricciones por día)
        DAYS = sorted({n["date"] for n in self.needs})
        
        # ---------------------------------------------------------------
        # Paso 1: Parejas válidos (profesor disponible para la necesidad)
        # ---------------------------------------------------------------
        # Siempre incluir pares bloqueados aunque el profe no esté disponible
        # (asumimos que el usuario sabe lo que hace)
        locked_set = set(self.locked.keys())
        self._valid_pairs = [
            (n, p) for n in N for p in P
            if (n, p) in locked_set or self._teacher_available(self.teachers[p], self.needs[n])
        ]
        
        # ---------------------------------------------------------------
        # Paso 2: Variables de decisión
        # ---------------------------------------------------------------
        for n, p in self._valid_pairs:
            var = self.model.NewBoolVar(f"x_n{n}_p{p}")
            self.x[(n, p)] = var
            # Si está bloqueado, forzar a 1
            if (n, p) in self.locked:
                self.model.Add(var == 1)
        
        # ---------------------------------------------------------------
        # Restricción 1: Capacidad mínima y máxima por necesidad
        # ---------------------------------------------------------------
        # Para cada necesidad n:
        #   min_n ≤ Σ x[n, p] ≤ max_n    (sumando sobre todos los profesores)
        for n in N:
            # Variables de todos los profesores para esta necesidad
            vars_n = [self.x[(n, p)] for p in P if (n, p) in self.x]
            
            # Límite inferior: al menos min profesores
            self.model.Add(sum(vars_n) >= self.needs[n]["min"])
            
            # Límite superior: a lo sumo max profesores
            self.model.Add(sum(vars_n) <= self.needs[n]["max"])
        
        # ---------------------------------------------------------------
        # Restricción 2: Sin solapamientos para un mismo profesor
        # ---------------------------------------------------------------
        # Si dos necesidades se solapan en el tiempo, un profesor no puede
        # estar asignado a ambas simultáneamente:
        #   x[ni, p] + x[nj, p] ≤ 1
        for p in P:
            # Necesidades que este profesor puede cubrir
            t_needs = [n for n in N if (n, p) in self.x]
            
            # Examina todos los pares de necesidades para este profesor
            for i in range(len(t_needs)):
                for j in range(i + 1, len(t_needs)):
                    ni, nj = t_needs[i], t_needs[j]
                    
                    # Si las dos necesidades solapan, restringe
                    if overlaps(self.needs[ni], self.needs[nj]):
                        self.model.Add(self.x[(ni, p)] + self.x[(nj, p)] <= 1)
        
        # ---------------------------------------------------------------
        # Restricción 3: Límite de horas totales por profesor
        # ---------------------------------------------------------------
        for p in P:
            # Máximo de horas (convertido a minutos)
            max_min = self.teachers[p].get("max_hours", 0) * 60
            
            if max_min > 0:  # 0 = sin límite
                # Suma ponderada: duración * variable_de_asignación
                terms = [
                    duration_min(self.needs[n]) * self.x[(n, p)]
                    for n in N if (n, p) in self.x
                ]
                if terms:
                    self.model.Add(sum(terms) <= max_min)
        
        # ---------------------------------------------------------------
        # Restricción 4: Límite de horas por día por profesor
        # ---------------------------------------------------------------
        for p in P:
            # Máximo de horas por día (convertido a minutos)
            max_day = self.teachers[p].get("max_hours_per_day", 0) * 60
            
            if max_day > 0:  # 0 = sin límite
                # Aplica el límite para cada fecha del proyecto
                for day in DAYS:
                    # Suma ponderada solo para necesidades en este día
                    terms = [
                        duration_min(self.needs[n]) * self.x[(n, p)]
                        for n in N
                        if (n, p) in self.x and self.needs[n]["date"] == day
                    ]
                    if terms:
                        self.model.Add(sum(terms) <= max_day)
        
        # ---------------------------------------------------------------
        # Función Objetivo: Maximizar el número total de asignaciones
        # ---------------------------------------------------------------
        # Sumamos todas las variables de decisión. El solver intentará
        # dar el valor 1 al mayor número posible de ellas, lo que significa
        # cubrir cada necesidad hasta su límite máximo.
        all_vars = [self.x[(n, p)] for n, p in self._valid_pairs]
        self.model.Maximize(sum(all_vars))
    
    # =========================================================================
    # RESOLUCIÓN
    # =========================================================================
    
    def solve(self, time_limit=30):
        """Ejecuta el solver CP-SAT.
        
        Parámetros:
            time_limit (int): Límite de tiempo en segundos (por defecto 30).
        
        Retorna:
            int: Estado de la solución (cp_model.OPTIMAL, FEASIBLE, INFEASIBLE...).
        """
        # Configura el límite de tiempo (evita bloqueos infinitos)
        self.solver.parameters.max_time_in_seconds = time_limit
        
        # Número de hilos de búsqueda paralela
        self.solver.parameters.num_search_workers = 4
        
        # Ejecuta la búsqueda y retorna el estado
        return self.solver.Solve(self.model)
    
    # =========================================================================
    # SOLUCIÓN MÚLTIPLE: Generar varias opciones para elegir
    # =========================================================================
    # El solver CP-SAT de OR-Tools es determinista: misma entrada → misma salida.
    # Para obtener soluciones distintas variamos la semilla aleatoria del solver
    # (random_seed), lo que cambia las heurísticas de búsqueda.
    #
    # solve_multiple(n_opciones, tiempo_por_opcion) ejecuta el modelo varias
    # veces con semillas diferentes y recolecta las asignaciones obtenidas.
    # Luego la GUI muestra las opciones para que el usuario elija.
    # =========================================================================
    
    def solve_with_seed(self, seed, time_limit=15):
        """Ejecuta el solver con una semilla concreta.
        
        Útil para obtener soluciones variadas: cada semilla produce una
        exploración distinta del árbol de búsqueda.
        
        Parámetros:
            seed (int): Semilla para el randomizador del solver.
            time_limit (int): Límite de tiempo en segundos.
        
        Retorna:
            list | None: Lista de asignaciones si hay solución, None si no.
        """
        # Crea un solver nuevo para evitar contaminación entre ejecuciones
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = 4
        solver.parameters.random_seed = seed          # Semilla distinta cada vez
        solver.parameters.randomize_search = True     # Activa búsqueda aleatoria
        
        status = solver.Solve(self.model)
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            # Extrae asignaciones para este solver concreto
            assignments = []
            for n, p in self._valid_pairs:
                if solver.Value(self.x[(n, p)]) == 1:
                    assignments.append({
                        "need": self.needs[n],
                        "need_idx": n,
                        "teacher": self.teachers[p],
                        "teacher_idx": p,
                    })
            return assignments
        return None
    
    def solve_multiple(self, n_options=5, time_limit=15):
        """Genera múltiples opciones de asignación variando la semilla.
        
        Parámetros:
            n_options (int): Número de opciones a generar (por defecto 5).
            time_limit (int): Límite de tiempo por cada ejecución (segundos).
        
        Retorna:
            list[dict]: Cada opción contiene:
                - id: número de opción (1-based)
                - assignment: lista de asignaciones
                - n_assignments: número total de asignaciones
                - n_covered: número de necesidades distintas cubiertas
                - total_needs: número total de necesidades
                - total_minutes: minutos totales asignados
                - teacher_hours: dict {nombre: minutos}
        """
        options = []
        semillas_usadas = set()  # Para evitar duplicados
        
        for i in range(n_options):
            # Calcula una semilla que no se haya usado antes
            seed = (i * 137 + 42) % 1000000
            while seed in semillas_usadas:
                seed = (seed + 1) % 1000000
            semillas_usadas.add(seed)
            
            # Ejecuta el solver con esta semilla
            result = self.solve_with_seed(seed, time_limit)
            
            if result is None:
                continue  # Esta semilla no produjo solución
            
            # Calcula estadísticas de esta opción
            needs_cubiertas = set(a["need_idx"] for a in result)
            total_min = sum(
                duration_min(a["need"]) for a in result
            )
            teacher_hours = {}
            for a in result:
                name = a["teacher"]["name"]
                teacher_hours[name] = teacher_hours.get(name, 0) + duration_min(a["need"])
            
            # Agrupa opciones que tengan la misma "huella" (mismas asignaciones)
            # para no mostrar opciones idénticas
            huella = tuple(sorted(
                (a["need_idx"], a["teacher_idx"]) for a in result
            ))
            
            # Solo añade si esta huella es nueva
            if not any(
                tuple(sorted(
                    (aa["need_idx"], aa["teacher_idx"]) for aa in op["assignment"]
                )) == huella
                for op in options
            ):
                options.append({
                    "id": len(options) + 1,
                    "assignment": result,
                    "n_assignments": len(result),
                    "n_covered": len(needs_cubiertas),
                    "total_needs": len(self.needs),
                    "total_minutes": total_min,
                    "teacher_hours": teacher_hours,
                })
        
        return options
    
    # =========================================================================
    # EXTRACCIÓN DE RESULTADOS
    # =========================================================================
    
    def extract_assignment(self):
        """Extrae la asignación resultado del modelo resuelto.
        
        Recorre todos los pares válidos y, para aquellos donde
        x[n, p] == 1, crea un dict con los datos completos.
        
        Retorna:
            list[dict]: Lista de asignaciones, cada una con:
                - need: dict de la necesidad
                - need_idx: índice de la necesidad
                - teacher: dict del profesor
                - teacher_idx: índice del profesor
        """
        self.assignment = []
        
        for n, p in self._valid_pairs:
            # Si el solver asignó este par (variable = 1)
            if self.solver.Value(self.x[(n, p)]) == 1:
                self.assignment.append({
                    "need": self.needs[n],        # Datos completos de la necesidad
                    "need_idx": n,                 # Índice por si se necesita referencia
                    "teacher": self.teachers[p],   # Datos completos del profesor
                    "teacher_idx": p,              # Índice del profesor
                })
        
        return self.assignment
    
    def get_teacher_stats(self):
        """Calcula estadísticas de carga por profesor.
        
        Retorna:
            dict: {nombre_profesor: minutos_asignados}
        """
        # Si no hay asignación, retorna vacío
        if not self.assignment:
            return {}
        
        stats = {}
        for a in self.assignment:
            name = a["teacher"]["name"]
            # Acumula minutos de cada asignación
            stats[name] = stats.get(name, 0) + duration_min(a["need"])
        
        return stats
