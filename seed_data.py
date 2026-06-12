# -*- coding: utf-8 -*-
# =============================================================================
# seed_data.py — Datos de ejemplo (ficticios) más estresantes
# =============================================================================
# 15 profesores con perfiles variados y ~50 necesidades en 5 días.
# Diseñado para poner a prueba el solver CP-SAT con solapamientos densos.

# Lista de colores HEX para asignar a cada profesor
TEACHER_COLORS = ["#6366f1","#ef4444","#10b981","#8b5cf6","#f59e0b","#06b6d4","#ec4899","#3b82f6","#f97316","#14b8a6","#84cc16","#e11d48","#0ea5e9","#a855f7","#22c55e"]

# Datos semilla de 15 profesores con turno, color y franjas de disponibilidad
SEED_TEACHERS = [
    # --- Original 8 conservados con turno y color ---
    {"name":"Ana Alumnez","max_hours":20,"max_hours_per_day":6,"turno":"Cualquiera","color":"#6366f1","email":"ana.alumnez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-22","start":"15:30","end":"18:30"},
         {"date":"2026-06-23","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"15:30","end":"18:30"},
         {"date":"2026-06-24","start":"09:00","end":"14:00"},{"date":"2026-06-24","start":"15:30","end":"18:30"},
         {"date":"2026-06-25","start":"09:00","end":"14:00"},{"date":"2026-06-25","start":"15:30","end":"18:30"},
         {"date":"2026-06-26","start":"09:00","end":"14:00"}]},
    {"name":"Carlos Profesorez","max_hours":25,"max_hours_per_day":7,"turno":"Mañana","color":"#ef4444","email":"carlos.profesorez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"08:00","end":"15:00"},{"date":"2026-06-23","start":"08:00","end":"15:00"},
         {"date":"2026-06-24","start":"08:00","end":"15:00"},{"date":"2026-06-25","start":"08:00","end":"15:00"},
         {"date":"2026-06-26","start":"08:00","end":"15:00"}]},
    {"name":"Maria Inventadez","max_hours":12,"max_hours_per_day":4,"turno":"Tarde","color":"#10b981","email":"maria.inventadez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"16:00","end":"20:00"},{"date":"2026-06-23","start":"16:00","end":"20:00"},
         {"date":"2026-06-24","start":"16:00","end":"20:00"},{"date":"2026-06-25","start":"16:00","end":"20:00"}]},
    {"name":"Jose Ficticiez","max_hours":20,"max_hours_per_day":6,"turno":"Cualquiera","color":"#8b5cf6","email":"jose.ficticiez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-22","start":"15:00","end":"19:00"},
         {"date":"2026-06-23","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"},
         {"date":"2026-06-24","start":"09:00","end":"14:00"},{"date":"2026-06-24","start":"15:00","end":"19:00"},
         {"date":"2026-06-25","start":"09:00","end":"14:00"},{"date":"2026-06-25","start":"15:00","end":"19:00"}]},
    {"name":"Laura Ejemplarez","max_hours":18,"max_hours_per_day":6,"turno":"Mañana","color":"#f59e0b","email":"laura.ejemplarez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-22","start":"16:00","end":"19:00"},
         {"date":"2026-06-23","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"16:00","end":"19:00"},
         {"date":"2026-06-24","start":"09:00","end":"14:00"},{"date":"2026-06-24","start":"16:00","end":"19:00"},
         {"date":"2026-06-25","start":"09:00","end":"14:00"},{"date":"2026-06-25","start":"16:00","end":"19:00"},
         {"date":"2026-06-26","start":"09:00","end":"14:00"}]},
    {"name":"David Simuladez","max_hours":25,"max_hours_per_day":8,"turno":"Mañana","color":"#06b6d4","email":"david.simuladez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"08:00","end":"12:00"},{"date":"2026-06-22","start":"14:00","end":"18:00"},
         {"date":"2026-06-23","start":"08:00","end":"12:00"},{"date":"2026-06-23","start":"14:00","end":"18:00"},
         {"date":"2026-06-24","start":"08:00","end":"12:00"},{"date":"2026-06-24","start":"14:00","end":"18:00"},
         {"date":"2026-06-25","start":"08:00","end":"12:00"},{"date":"2026-06-25","start":"14:00","end":"18:00"},
         {"date":"2026-06-26","start":"08:00","end":"12:00"},{"date":"2026-06-26","start":"14:00","end":"18:00"}]},
    {"name":"Sofia Irrealmez","max_hours":10,"max_hours_per_day":4,"turno":"Mañana","color":"#ec4899","email":"sofia.irrealmez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"09:00","end":"12:00"},{"date":"2026-06-23","start":"09:00","end":"12:00"},
         {"date":"2026-06-24","start":"09:00","end":"12:00"},{"date":"2026-06-25","start":"09:00","end":"12:00"},
         {"date":"2026-06-26","start":"09:00","end":"12:00"}]},
    {"name":"Pablo Fingirez","max_hours":18,"max_hours_per_day":6,"turno":"Tarde","color":"#3b82f6","email":"pablo.fingirez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"14:00","end":"19:00"},{"date":"2026-06-23","start":"14:00","end":"19:00"},
         {"date":"2026-06-24","start":"14:00","end":"19:00"},{"date":"2026-06-25","start":"14:00","end":"19:00"},
         {"date":"2026-06-26","start":"14:00","end":"19:00"}]},
    # --- 7 nuevos profesores para estrés ---
    {"name":"Elena Textualdez","max_hours":22,"max_hours_per_day":7,"turno":"Mañana","color":"#f97316","email":"elena.textualdez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"07:30","end":"14:30"},{"date":"2026-06-23","start":"07:30","end":"14:30"},
         {"date":"2026-06-24","start":"07:30","end":"14:30"},{"date":"2026-06-25","start":"07:30","end":"14:30"},
         {"date":"2026-06-26","start":"07:30","end":"14:30"}]},
    {"name":"Ramon Librez","max_hours":15,"max_hours_per_day":5,"turno":"Tarde","color":"#14b8a6","email":"ramon.librez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"15:00","end":"20:00"},{"date":"2026-06-23","start":"15:00","end":"20:00"},
         {"date":"2026-06-24","start":"15:00","end":"20:00"},{"date":"2026-06-25","start":"15:00","end":"20:00"},
         {"date":"2026-06-26","start":"15:00","end":"20:00"}]},
    {"name":"Beatriz Papelmez","max_hours":20,"max_hours_per_day":6,"turno":"Cualquiera","color":"#84cc16","email":"beatriz.papelmez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"09:00","end":"13:00"},{"date":"2026-06-22","start":"15:30","end":"19:30"},
         {"date":"2026-06-23","start":"09:00","end":"13:00"},{"date":"2026-06-23","start":"15:30","end":"19:30"},
         {"date":"2026-06-24","start":"09:00","end":"13:00"},{"date":"2026-06-24","start":"15:30","end":"19:30"},
         {"date":"2026-06-25","start":"09:00","end":"13:00"},{"date":"2026-06-25","start":"15:30","end":"19:30"}]},
    {"name":"Miguel Cuaderniez","max_hours":16,"max_hours_per_day":5,"turno":"Mañana","color":"#e11d48","email":"miguel.cuaderniez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"},
         {"date":"2026-06-24","start":"08:00","end":"13:00"},{"date":"2026-06-25","start":"08:00","end":"13:00"},
         {"date":"2026-06-26","start":"08:00","end":"13:00"}]},
    {"name":"Teresa Estucherez","max_hours":14,"max_hours_per_day":5,"turno":"Tarde","color":"#0ea5e9","email":"teresa.estucherez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"16:00","end":"21:00"},{"date":"2026-06-23","start":"16:00","end":"21:00"},
         {"date":"2026-06-24","start":"16:00","end":"21:00"},{"date":"2026-06-25","start":"16:00","end":"21:00"},
         {"date":"2026-06-26","start":"16:00","end":"21:00"}]},
    {"name":"Andres Mozillarez","max_hours":24,"max_hours_per_day":8,"turno":"Cualquiera","color":"#a855f7","email":"andres.mozillarez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"08:30","end":"12:30"},{"date":"2026-06-22","start":"13:30","end":"17:30"},
         {"date":"2026-06-23","start":"08:30","end":"12:30"},{"date":"2026-06-23","start":"13:30","end":"17:30"},
         {"date":"2026-06-24","start":"08:30","end":"12:30"},{"date":"2026-06-24","start":"13:30","end":"17:30"},
         {"date":"2026-06-25","start":"08:30","end":"12:30"},{"date":"2026-06-25","start":"13:30","end":"17:30"},
         {"date":"2026-06-26","start":"08:30","end":"12:30"},{"date":"2026-06-26","start":"13:30","end":"17:30"}]},
    {"name":"Carmen Blocdez","max_hours":10,"max_hours_per_day":4,"turno":"Mañana","color":"#22c55e","email":"carmen.blocdez@ies.edu",
     "time_slots":[
         {"date":"2026-06-22","start":"08:00","end":"12:00"},{"date":"2026-06-23","start":"08:00","end":"12:00"},
         {"date":"2026-06-24","start":"08:00","end":"12:00"},{"date":"2026-06-25","start":"08:00","end":"12:00"},
         {"date":"2026-06-26","start":"08:00","end":"12:00"}]},
]

# ~50 necesidades distribuidas en 5 días con solapamientos densos para estresar al solver
SEED_NEEDS = [
    # --- LUNES 22: RECOGIDA MASIVA + CLASIFICACIÓN ---
    {"name":"Recogida 1º ESO A","date":"2026-06-22","start":"08:30","end":"10:00","min":2,"max":4},
    {"name":"Recogida 1º ESO B","date":"2026-06-22","start":"08:30","end":"10:00","min":2,"max":3},
    {"name":"Recogida 1º ESO C","date":"2026-06-22","start":"08:30","end":"10:00","min":1,"max":2},
    {"name":"Recogida 2º ESO A","date":"2026-06-22","start":"10:00","end":"12:00","min":2,"max":3},
    {"name":"Recogida 2º ESO B","date":"2026-06-22","start":"10:00","end":"12:00","min":2,"max":3},
    {"name":"Recogida 2º ESO C","date":"2026-06-22","start":"10:00","end":"12:00","min":1,"max":2},
    {"name":"Recogida 3º ESO A","date":"2026-06-22","start":"12:00","end":"13:30","min":2,"max":3},
    {"name":"Recogida 3º ESO B","date":"2026-06-22","start":"12:00","end":"13:30","min":1,"max":2},
    {"name":"Clasif. inicial 1º-2º","date":"2026-06-22","start":"16:00","end":"18:00","min":2,"max":4},
    {"name":"Clasif. inicial 3º","date":"2026-06-22","start":"16:00","end":"18:00","min":1,"max":2},
    {"name":"Empaquetado urgente","date":"2026-06-22","start":"18:00","end":"19:30","min":1,"max":3},

    # --- MARTES 23: BACHILLERATO + CLASIFICACIÓN ---
    {"name":"Recogida 1º Batx A","date":"2026-06-23","start":"08:30","end":"10:00","min":2,"max":3},
    {"name":"Recogida 1º Batx B","date":"2026-06-23","start":"08:30","end":"10:00","min":1,"max":2},
    {"name":"Recogida 2º Batx A","date":"2026-06-23","start":"10:00","end":"11:30","min":1,"max":2},
    {"name":"Recogida 2º Batx B","date":"2026-06-23","start":"10:00","end":"11:30","min":1,"max":2},
    {"name":"Clasif. 1º ESO detallada","date":"2026-06-23","start":"09:00","end":"11:00","min":2,"max":3},
    {"name":"Clasif. 2º ESO detallada","date":"2026-06-23","start":"09:00","end":"11:00","min":2,"max":3},
    {"name":"Clasif. 3º ESO detallada","date":"2026-06-23","start":"11:00","end":"13:00","min":2,"max":3},
    {"name":"Clasif. 4º ESO detallada","date":"2026-06-23","start":"11:00","end":"13:00","min":1,"max":2},
    {"name":"Separación por curso","date":"2026-06-23","start":"16:00","end":"18:00","min":2,"max":4},
    {"name":"Control calidad lotes","date":"2026-06-23","start":"18:00","end":"19:30","min":1,"max":2},

    # --- MIÉRCOLES 24: CLASIFICACIÓN FINA + EMPAQUETADO ---
    {"name":"Clasif. 1º Batx detallada","date":"2026-06-24","start":"09:00","end":"11:00","min":1,"max":2},
    {"name":"Clasif. 2º Batx detallada","date":"2026-06-24","start":"09:00","end":"11:00","min":1,"max":2},
    {"name":"Empaquetado 1º ESO","date":"2026-06-24","start":"09:00","end":"11:00","min":2,"max":3},
    {"name":"Empaquetado 2º ESO","date":"2026-06-24","start":"11:00","end":"13:00","min":2,"max":3},
    {"name":"Empaquetado 3º ESO","date":"2026-06-24","start":"11:00","end":"13:00","min":1,"max":2},
    {"name":"Empaquetado 4º ESO","date":"2026-06-24","start":"11:00","end":"13:00","min":1,"max":2},
    {"name":"Empaquetado 1º Batx","date":"2026-06-24","start":"13:00","end":"14:30","min":1,"max":2},
    {"name":"Empaquetado 2º Batx","date":"2026-06-24","start":"13:00","end":"14:30","min":1,"max":2},
    {"name":"Etiquetado y verificación","date":"2026-06-24","start":"16:00","end":"18:00","min":2,"max":4},
    {"name":"Revisión dañados","date":"2026-06-24","start":"18:00","end":"19:30","min":1,"max":2},

    # --- JUEVES 25: PREPARACIÓN LOTES + TRASLADO ---
    {"name":"Lotes 1º ESO A","date":"2026-06-25","start":"08:30","end":"10:00","min":2,"max":3},
    {"name":"Lotes 1º ESO B","date":"2026-06-25","start":"08:30","end":"10:00","min":1,"max":2},
    {"name":"Lotes 2º ESO A","date":"2026-06-25","start":"10:00","end":"11:30","min":2,"max":3},
    {"name":"Lotes 2º ESO B","date":"2026-06-25","start":"10:00","end":"11:30","min":1,"max":2},
    {"name":"Lotes 3º ESO","date":"2026-06-25","start":"11:30","end":"13:00","min":1,"max":2},
    {"name":"Lotes 4º ESO","date":"2026-06-25","start":"11:30","end":"13:00","min":1,"max":2},
    {"name":"Lotes 1º Batx","date":"2026-06-25","start":"13:00","end":"14:30","min":1,"max":2},
    {"name":"Lotes 2º Batx","date":"2026-06-25","start":"13:00","end":"14:30","min":1,"max":2},
    {"name":"Traslado a aulas","date":"2026-06-25","start":"16:00","end":"18:00","min":2,"max":4},
    {"name":"Recuento inventario","date":"2026-06-25","start":"18:00","end":"19:30","min":1,"max":2},

    # --- VIERNES 26: DISTRIBUCIÓN + CIERRE ---
    {"name":"Distribución 1º ESO","date":"2026-06-26","start":"08:30","end":"10:00","min":2,"max":3},
    {"name":"Distribución 2º ESO","date":"2026-06-26","start":"08:30","end":"10:00","min":2,"max":3},
    {"name":"Distribución 3º ESO","date":"2026-06-26","start":"10:00","end":"11:30","min":1,"max":2},
    {"name":"Distribución 4º ESO","date":"2026-06-26","start":"10:00","end":"11:30","min":1,"max":2},
    {"name":"Distribución 1º Batx","date":"2026-06-26","start":"11:30","end":"13:00","min":1,"max":2},
    {"name":"Distribución 2º Batx","date":"2026-06-26","start":"11:30","end":"13:00","min":1,"max":2},
    {"name":"Recogida materiales","date":"2026-06-26","start":"13:00","end":"14:30","min":1,"max":2},
    {"name":"Cierre XarxaLlibres","date":"2026-06-26","start":"15:00","end":"17:00","min":2,"max":4},
    {"name":"Acta y documentación","date":"2026-06-26","start":"17:00","end":"18:30","min":1,"max":2},
]


def get_seed_teachers():
    # Retorna copias independientes de cada profesor para no mutar el original
    return [dict(t) for t in SEED_TEACHERS]

def get_seed_needs():
    # Retorna copias independientes de cada necesidad para no mutar el original
    return [dict(n) for n in SEED_NEEDS]

def get_seed_data():
    # Retorna un proyecto completo con nombre y necesidades (sin profesores)
    return {
        "project_name": "XarxaLlibres 2026 - Recogida y distribución (estresante)",
        "needs": get_seed_needs(),
    }
