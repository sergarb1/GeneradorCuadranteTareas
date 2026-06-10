# -*- coding: utf-8 -*-
# =============================================================================
# seed_data.py — Datos de ejemplo (ficticios) para XarxaLlibres
# =============================================================================
# Este archivo contiene dos listas principales:
#   - SEED_TEACHERS: 8 profesores con distinta disponibilidad horaria
#   - SEED_NEEDS: 25 tareas del proceso XarxaLlibres (recogida, clasificación,
#     empaquetado, distribución y cierre de libros de texto)
#
# Se usan para cargar datos de demostración con un solo clic.
# Cada profesor tiene: nombre, límite total de horas, límite por día,
# y una lista de franjas horarias (date, start, end).
# Cada necesidad tiene: nombre, fecha, hora inicio/fin y min/max profesores.
# =============================================================================


# =============================================================================
# LISTA DE PROFESORES DE EJEMPLO
# =============================================================================
# Cada entrada representa un docente con su disponibilidad semanal.
# Los horarios simulan un centro real durante la semana de recogida de libros.
# -----------------------------------------------------------------------------
SEED_TEACHERS = [
    {
        # --- Ana Alumnez: disponibilidad mixta (mañana y tarde) ---
        "name": "Ana Alumnez",
        "max_hours": 20,              # Límite total de horas en la semana
        "max_hours_per_day": 6,       # Máximo de horas en un mismo día
        "time_slots": [
            # Lunes 22 — mañana completa + tarde parcial
            {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-22", "start": "15:30", "end": "18:30"},
            # Martes 23
            {"date": "2026-06-23", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-23", "start": "15:30", "end": "18:30"},
            # Miércoles 24
            {"date": "2026-06-24", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-24", "start": "15:30", "end": "18:30"},
            # Jueves 25
            {"date": "2026-06-25", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-25", "start": "15:30", "end": "18:30"},
            # Viernes 26 — solo mañana
            {"date": "2026-06-26", "start": "09:00", "end": "14:00"},
        ],
    },
    {
        # --- Carlos Profesorez: disponible toda la mañana (8-15) toda la semana ---
        "name": "Carlos Profesorez",
        "max_hours": 25,
        "max_hours_per_day": 7,
        "time_slots": [
            {"date": "2026-06-22", "start": "08:00", "end": "15:00"},
            {"date": "2026-06-23", "start": "08:00", "end": "15:00"},
            {"date": "2026-06-24", "start": "08:00", "end": "15:00"},
            {"date": "2026-06-25", "start": "08:00", "end": "15:00"},
            {"date": "2026-06-26", "start": "08:00", "end": "15:00"},
        ],
    },
    {
        # --- Maria Inventadez: solo por la tarde (16-20), menos días ---
        "name": "Maria Inventadez",
        "max_hours": 12,
        "max_hours_per_day": 4,
        "time_slots": [
            {"date": "2026-06-22", "start": "16:00", "end": "20:00"},
            {"date": "2026-06-23", "start": "16:00", "end": "20:00"},
            {"date": "2026-06-24", "start": "16:00", "end": "20:00"},
            {"date": "2026-06-25", "start": "16:00", "end": "20:00"},
            # Nota: viernes NO disponible (solo 4 días)
        ],
    },
    {
        # --- Jose Ficticiez: mixto, con jornada intensiva ambos turnos ---
        "name": "Jose Ficticiez",
        "max_hours": 20,
        "max_hours_per_day": 6,
        "time_slots": [
            {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-22", "start": "15:00", "end": "19:00"},
            {"date": "2026-06-23", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-23", "start": "15:00", "end": "19:00"},
            {"date": "2026-06-24", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-24", "start": "15:00", "end": "19:00"},
            {"date": "2026-06-25", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-25", "start": "15:00", "end": "19:00"},
        ],
    },
    {
        # --- Laura Ejemplarez: mixto con horario partido ---
        "name": "Laura Ejemplarez",
        "max_hours": 18,
        "max_hours_per_day": 6,
        "time_slots": [
            {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-22", "start": "16:00", "end": "19:00"},
            {"date": "2026-06-23", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-23", "start": "16:00", "end": "19:00"},
            {"date": "2026-06-24", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-24", "start": "16:00", "end": "19:00"},
            {"date": "2026-06-25", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-25", "start": "16:00", "end": "19:00"},
            {"date": "2026-06-26", "start": "09:00", "end": "14:00"},
        ],
    },
    {
        # --- David Simuladez: jornada partida (8-12 y 14-18), máxima carga ---
        "name": "David Simuladez",
        "max_hours": 25,
        "max_hours_per_day": 8,
        "time_slots": [
            {"date": "2026-06-22", "start": "08:00", "end": "12:00"},
            {"date": "2026-06-22", "start": "14:00", "end": "18:00"},
            {"date": "2026-06-23", "start": "08:00", "end": "12:00"},
            {"date": "2026-06-23", "start": "14:00", "end": "18:00"},
            {"date": "2026-06-24", "start": "08:00", "end": "12:00"},
            {"date": "2026-06-24", "start": "14:00", "end": "18:00"},
            {"date": "2026-06-25", "start": "08:00", "end": "12:00"},
            {"date": "2026-06-25", "start": "14:00", "end": "18:00"},
            # Viernes también completo
            {"date": "2026-06-26", "start": "08:00", "end": "12:00"},
            {"date": "2026-06-26", "start": "14:00", "end": "18:00"},
        ],
    },
    {
        # --- Sofia Irrealmez: solo mañanas reducidas (9-12) ---
        "name": "Sofia Irrealmez",
        "max_hours": 10,
        "max_hours_per_day": 4,
        "time_slots": [
            {"date": "2026-06-22", "start": "09:00", "end": "12:00"},
            {"date": "2026-06-23", "start": "09:00", "end": "12:00"},
            {"date": "2026-06-24", "start": "09:00", "end": "12:00"},
            {"date": "2026-06-25", "start": "09:00", "end": "12:00"},
            {"date": "2026-06-26", "start": "09:00", "end": "12:00"},
        ],
    },
    {
        # --- Pablo Fingirez: solo tardes (14-19) toda la semana ---
        "name": "Pablo Fingirez",
        "max_hours": 18,
        "max_hours_per_day": 6,
        "time_slots": [
            {"date": "2026-06-22", "start": "14:00", "end": "19:00"},
            {"date": "2026-06-23", "start": "14:00", "end": "19:00"},
            {"date": "2026-06-24", "start": "14:00", "end": "19:00"},
            {"date": "2026-06-25", "start": "14:00", "end": "19:00"},
            {"date": "2026-06-26", "start": "14:00", "end": "19:00"},
        ],
    },
]


# =============================================================================
# LISTA DE NECESIDADES / TAREAS DE EJEMPLO
# =============================================================================
# Simula el proceso completo de XarxaLlibres durante 5 días (22-26 junio 2026):
#   Día 1 (lunes):     Recogida masiva de libros de 1º y 2º ESO + clasificación
#   Día 2 (martes):    Recogida de 1º Bachillerato + clasificación
#   Día 3 (miércoles): Clasificación de 3º, 4º ESO y Bachilleratos + empaquetado
#   Día 4 (jueves):    Preparación de lotes por curso
#   Día 5 (viernes):   Distribución a aulas + cierre del proceso
#
# Cada necesidad especifica: nombre, fecha, hora inicio, hora fin,
# número MÍNIMO de profesores requerido (min) y número MÁXIMO (max).
# -----------------------------------------------------------------------------
SEED_NEEDS = [
    # --- LUNES 22: RECOGIDA Y CLASIFICACIÓN PRELIMINAR ---
    {"name": "Recogida libros 1º ESO A", "date": "2026-06-22", "start": "09:00", "end": "11:00", "min": 2, "max": 4},
    {"name": "Recogida libros 1º ESO B", "date": "2026-06-22", "start": "09:00", "end": "11:00", "min": 2, "max": 3},
    {"name": "Recogida libros 2º ESO A", "date": "2026-06-22", "start": "11:00", "end": "13:00", "min": 2, "max": 3},
    {"name": "Recogida libros 2º ESO B", "date": "2026-06-22", "start": "11:00", "end": "13:00", "min": 2, "max": 3},
    {"name": "Clasificación preliminar",     "date": "2026-06-22", "start": "16:00", "end": "18:00", "min": 2, "max": 4},

    # --- MARTES 23: RECOGIDA DE BACHILLERATO Y CLASIFICACIÓN ---
    {"name": "Recogida libros 1º Batx A", "date": "2026-06-23", "start": "09:00", "end": "11:00", "min": 2, "max": 3},
    {"name": "Recogida libros 1º Batx B", "date": "2026-06-23", "start": "09:00", "end": "11:00", "min": 1, "max": 2},
    {"name": "Clasificación 1º ESO",         "date": "2026-06-23", "start": "11:30", "end": "13:30", "min": 2, "max": 3},
    {"name": "Clasificación 2º ESO",         "date": "2026-06-23", "start": "11:30", "end": "13:30", "min": 2, "max": 3},
    {"name": "Clasificación y empaquetado",   "date": "2026-06-23", "start": "16:00", "end": "18:00", "min": 2, "max": 4},

    # --- MIÉRCOLES 24: CLASIFICACIÓN FINA Y EMPAQUETADO ---
    {"name": "Clasificación 3º ESO",         "date": "2026-06-24", "start": "09:00", "end": "11:00", "min": 2, "max": 3},
    {"name": "Clasificación 4º ESO",         "date": "2026-06-24", "start": "09:00", "end": "11:00", "min": 2, "max": 3},
    {"name": "Clasificación 1º Batx",        "date": "2026-06-24", "start": "11:30", "end": "13:30", "min": 1, "max": 2},
    {"name": "Clasificación 2º Batx",        "date": "2026-06-24", "start": "11:30", "end": "13:30", "min": 1, "max": 2},
    {"name": "Empaquetado por cursos",       "date": "2026-06-24", "start": "16:00", "end": "18:00", "min": 2, "max": 4},

    # --- JUEVES 25: PREPARACIÓN DE LOTES ---
    {"name": "Preparación lotes 1º ESO",     "date": "2026-06-25", "start": "09:00", "end": "11:00", "min": 2, "max": 4},
    {"name": "Preparación lotes 2º ESO",     "date": "2026-06-25", "start": "09:00", "end": "11:00", "min": 2, "max": 3},
    {"name": "Preparación lotes 3º ESO",     "date": "2026-06-25", "start": "11:30", "end": "13:30", "min": 1, "max": 2},
    {"name": "Preparación lotes 4º ESO",     "date": "2026-06-25", "start": "11:30", "end": "13:30", "min": 1, "max": 2},
    {"name": "Revisión y recuento final",    "date": "2026-06-25", "start": "16:00", "end": "18:00", "min": 2, "max": 3},

    # --- VIERNES 26: DISTRIBUCIÓN Y CIERRE ---
    {"name": "Distribución 1º ESO",          "date": "2026-06-26", "start": "09:00", "end": "11:00", "min": 1, "max": 2},
    {"name": "Distribución 2º ESO",          "date": "2026-06-26", "start": "09:00", "end": "11:00", "min": 1, "max": 2},
    {"name": "Distribución 3º ESO",          "date": "2026-06-26", "start": "11:00", "end": "13:00", "min": 1, "max": 2},
    {"name": "Distribución 4º ESO",          "date": "2026-06-26", "start": "11:00", "end": "13:00", "min": 1, "max": 2},
    {"name": "Cierre XarxaLlibres",          "date": "2026-06-26", "start": "15:00", "end": "17:00", "min": 2, "max": 3},
]


# =============================================================================
# FUNCIONES DE ACCESO
# =============================================================================
# Devuelven copias profundas (dicts nuevos) para evitar que las modificaciones
# en la GUI alteren los datos semilla originales.
# -----------------------------------------------------------------------------

def get_seed_teachers():
    """Devuelve una copia de la lista de profesores de ejemplo."""
    return [dict(t) for t in SEED_TEACHERS]


def get_seed_needs():
    """Devuelve una copia de la lista de necesidades de ejemplo."""
    return [dict(n) for n in SEED_NEEDS]


def get_seed_data():
    """Devuelve un dict completo con nombre de proyecto y necesidades."""
    return {
        # Nombre del proyecto de demostración
        "project_name": "XarxaLlibres 2026 - Recogida y distribución",
        # Lista de necesidades copiada
        "needs": get_seed_needs(),
    }
