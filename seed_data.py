# -*- coding: utf-8 -*-
# =============================================================================
# seed_data.py — Datos de ejemplo (ficticios) con solucion verificada
# =============================================================================
# Ofrece 2 proyectos semilla precocinados:
#   1. "Limpieza aulas (DATOS FICTICIOS)" — sin grupos, facil
#   2. "Acompanamiento alumnos (DATOS FICTICIOS)" — con grupos AND/OR

PROJECTS = [
    {"name": "🧹 Apoyo limpieza aulas (DATOS FICTICIOS)",
     "teachers": [
        {"name":"Ana","max_hours":8,"max_hours_per_day":5,"turno":"Manana","color":"#6366f1","email":"ana@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
        {"name":"Carlos","max_hours":8,"max_hours_per_day":5,"turno":"Manana","color":"#ef4444","email":"carlos@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
        {"name":"Maria","max_hours":8,"max_hours_per_day":5,"turno":"Manana","color":"#10b981","email":"maria@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
        {"name":"Jose","max_hours":8,"max_hours_per_day":5,"turno":"Manana","color":"#8b5cf6","email":"jose@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
        {"name":"Laura","max_hours":6,"max_hours_per_day":4,"turno":"Tarde","color":"#f59e0b","email":"laura@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"David","max_hours":6,"max_hours_per_day":4,"turno":"Tarde","color":"#06b6d4","email":"david@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"Sofia","max_hours":6,"max_hours_per_day":4,"turno":"Tarde","color":"#ec4899","email":"sofia@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"Pablo","max_hours":6,"max_hours_per_day":5,"turno":"Cualquiera","color":"#3b82f6","email":"pablo@ies.edu","groups":[],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-22","start":"15:00","end":"18:00"},
                       {"date":"2026-06-23","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"15:00","end":"18:00"}]},
     ],
     "needs": [
        # MONDAY: 5 morning teachers, 4 afternoon teachers
        # MORNING BLOCK 09-11: 3 needs, total min 2+1+1=4, avail 5
        {"name":"Limpiar aulas A-101 y A-102","date":"2026-06-22","start":"09:00","end":"11:00","min":2,"max":3,"groups":""},
        {"name":"Desinfectar pomos","date":"2026-06-22","start":"09:00","end":"10:30","min":1,"max":2,"groups":""},
        {"name":"Ordenar armarios aula","date":"2026-06-22","start":"09:00","end":"11:00","min":1,"max":2,"groups":""},
        # MORNING BLOCK 11-13: 3 needs, total min 2+1+1=4, avail 5
        {"name":"Limpiar ventanas planta baja","date":"2026-06-22","start":"11:00","end":"13:00","min":2,"max":3,"groups":""},
        {"name":"Limpiar ventanas planta alta","date":"2026-06-22","start":"11:00","end":"12:30","min":1,"max":2,"groups":""},
        {"name":"Recoger patio exterior","date":"2026-06-22","start":"12:00","end":"13:00","min":1,"max":2,"groups":""},
        # AFTERNOON BLOCK 15-17: 2 needs, total min 2+1=3, avail 4
        {"name":"Ordenar almacen material","date":"2026-06-22","start":"15:00","end":"17:00","min":2,"max":3,"groups":""},
        {"name":"Limpiar sala profesores","date":"2026-06-22","start":"15:00","end":"16:30","min":1,"max":2,"groups":""},
        # AFTERNOON BLOCK 17-18:30: 3 needs, total min 2+1+1=4, avail 4
        {"name":"Fregar suelos pasillos","date":"2026-06-22","start":"17:00","end":"18:30","min":2,"max":3,"groups":""},
        {"name":"Limpiar banos","date":"2026-06-22","start":"17:00","end":"18:00","min":1,"max":2,"groups":""},
        # TUESDAY (same teachers, similar pattern)
        {"name":"Limpiar aulas B-201 y B-202","date":"2026-06-23","start":"09:00","end":"11:00","min":2,"max":3,"groups":""},
        {"name":"Ordenar biblioteca","date":"2026-06-23","start":"09:00","end":"11:00","min":1,"max":2,"groups":""},
        {"name":"Limpiar aula B-203","date":"2026-06-23","start":"09:00","end":"10:30","min":1,"max":2,"groups":""},
        {"name":"Limpiar cristales gimnasio","date":"2026-06-23","start":"11:00","end":"13:00","min":2,"max":3,"groups":""},
        {"name":"Ventanas sala usos multiples","date":"2026-06-23","start":"11:00","end":"12:30","min":1,"max":2,"groups":""},
        {"name":"Recogida de residuos","date":"2026-06-23","start":"12:00","end":"13:00","min":1,"max":2,"groups":""},
        {"name":"Fregar suelos planta alta","date":"2026-06-23","start":"15:00","end":"17:00","min":2,"max":3,"groups":""},
        {"name":"Limpiar vestuarios","date":"2026-06-23","start":"15:00","end":"16:30","min":1,"max":2,"groups":""},
        {"name":"Recogida final","date":"2026-06-23","start":"17:00","end":"18:30","min":2,"max":3,"groups":""},
        {"name":"Limpiar ba\u00f1os segunda planta","date":"2026-06-23","start":"17:00","end":"18:00","min":1,"max":2,"groups":""},
     ]},
    {"name": "🏫 Acompanamiento alumnos (DATOS FICTICIOS)",
     "teachers": [
        {"name":"Ana","max_hours":10,"max_hours_per_day":5,"turno":"Manana","color":"#6366f1","email":"ana@ies.edu","groups":["1ESO A","1ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"09:00","end":"14:00"}]},
        {"name":"Carlos","max_hours":10,"max_hours_per_day":5,"turno":"Manana","color":"#ef4444","email":"carlos@ies.edu","groups":["2ESO A","2ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"09:00","end":"14:00"}]},
        {"name":"Maria","max_hours":8,"max_hours_per_day":4,"turno":"Tarde","color":"#10b981","email":"maria@ies.edu","groups":["3ESO A","3ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"Jose","max_hours":8,"max_hours_per_day":4,"turno":"Tarde","color":"#8b5cf6","email":"jose@ies.edu","groups":["4ESO A","4ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"Laura","max_hours":10,"max_hours_per_day":5,"turno":"Manana","color":"#f59e0b","email":"laura@ies.edu","groups":["1BAT A","1BAT B"],
         "time_slots":[{"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"09:00","end":"14:00"}]},
        {"name":"Sofia","max_hours":6,"max_hours_per_day":4,"turno":"Manana","color":"#ec4899","email":"sofia@ies.edu","groups":["1ESO A","1ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"09:00","end":"13:00"},{"date":"2026-06-23","start":"09:00","end":"13:00"}]},
        {"name":"Pablo","max_hours":10,"max_hours_per_day":5,"turno":"Cualquiera","color":"#3b82f6","email":"pablo@ies.edu","groups":["2ESO A","2ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"09:00","end":"14:00"},{"date":"2026-06-22","start":"15:00","end":"18:00"},
                       {"date":"2026-06-23","start":"09:00","end":"14:00"},{"date":"2026-06-23","start":"15:00","end":"18:00"}]},
        {"name":"Elena","max_hours":10,"max_hours_per_day":5,"turno":"Manana","color":"#f97316","email":"elena@ies.edu","groups":["1ESO A","1ESO B","2ESO A"],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
        {"name":"Ramon","max_hours":8,"max_hours_per_day":4,"turno":"Tarde","color":"#14b8a6","email":"ramon@ies.edu","groups":["3ESO A","3ESO B"],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"Miguel","max_hours":10,"max_hours_per_day":5,"turno":"Manana","color":"#e11d48","email":"miguel@ies.edu","groups":["2ESO A","2ESO B","3ESO A"],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
        {"name":"David","max_hours":8,"max_hours_per_day":4,"turno":"Tarde","color":"#06b6d4","email":"david@ies.edu","groups":["2BAT A","2BAT B"],
         "time_slots":[{"date":"2026-06-22","start":"15:00","end":"19:00"},{"date":"2026-06-23","start":"15:00","end":"19:00"}]},
        {"name":"Andres","max_hours":10,"max_hours_per_day":5,"turno":"Manana","color":"#a855f7","email":"andres@ies.edu","groups":["1ESO A","1ESO B","4ESO A"],
         "time_slots":[{"date":"2026-06-22","start":"08:00","end":"13:00"},{"date":"2026-06-23","start":"08:00","end":"13:00"}]},
     ],
     "needs": [
        # MON 22 MANANA (Ana 1ESO, Carlos 2ESO, Laura 1BAT, Sofia 1ESO, Pablo 2ESO, Elena 1ESO+2ESO, Miguel 2ESO, Andres 1ESO)
        # BLOCK 09-11: 4 needs, total min 2+1+1+1=5, avail 8 morning teachers (but need matching groups)
        {"name":"Acomp. 1ESO A a biblioteca","date":"2026-06-22","start":"09:00","end":"11:00","min":2,"max":3,"groups":"1ESO A"},
        {"name":"Acomp. 2ESO A a laboratorio","date":"2026-06-22","start":"09:00","end":"11:00","min":1,"max":2,"groups":"2ESO A"},
        {"name":"Acomp. 2ESO B a salon actos","date":"2026-06-22","start":"09:00","end":"11:00","min":1,"max":2,"groups":"2ESO B"},
        {"name":"Acomp. 1BAT A a museo","date":"2026-06-22","start":"09:00","end":"13:00","min":1,"max":2,"groups":"1BAT A"},
        # BLOCK 11-13: 4 needs
        {"name":"Acomp. 1ESO B a taller","date":"2026-06-22","start":"11:00","end":"13:00","min":1,"max":2,"groups":"1ESO B"},
        {"name":"Acomp. 1ESO A+2ESO A mixto","date":"2026-06-22","start":"11:00","end":"13:00","min":1,"max":2,"groups":"1ESO A+2ESO A"},
        {"name":"Acomp. 4ESO A a teatro","date":"2026-06-22","start":"09:00","end":"13:00","min":1,"max":2,"groups":"4ESO A"},
        {"name":"Recoger patio comida","date":"2026-06-22","start":"11:00","end":"13:00","min":2,"max":3,"groups":""},
        # MON 22 TARDE (Maria 3ESO, Jose 4ESO, Ramon 3ESO, David 2BAT, Pablo 2ESO)
        # BLOCK 15-17: 3 needs
        {"name":"Acomp. 3ESO A a piscina","date":"2026-06-22","start":"15:00","end":"17:00","min":1,"max":2,"groups":"3ESO A"},
        {"name":"Acomp. 2BAT A a universidad","date":"2026-06-22","start":"15:00","end":"17:00","min":1,"max":2,"groups":"2BAT A"},
        {"name":"Supervisar patio comida","date":"2026-06-22","start":"15:00","end":"16:30","min":1,"max":2,"groups":""},
        # TUE 23 MANANA (same 8 morning teachers)
        {"name":"Acomp. 1ESO A a parque","date":"2026-06-23","start":"09:00","end":"11:00","min":2,"max":3,"groups":"1ESO A"},
        {"name":"Acomp. 2ESO A a fabrica","date":"2026-06-23","start":"09:00","end":"12:00","min":1,"max":2,"groups":"2ESO A"},
        {"name":"Acomp. 2ESO B a exposicion","date":"2026-06-23","start":"09:00","end":"11:00","min":1,"max":2,"groups":"2ESO B"},
        {"name":"Acomp. 1BAT A a teatro ingles","date":"2026-06-23","start":"09:00","end":"13:00","min":1,"max":2,"groups":"1BAT A"},
        {"name":"Acomp. 1ESO B a acuario","date":"2026-06-23","start":"11:00","end":"13:00","min":1,"max":2,"groups":"1ESO B"},
        {"name":"Acomp. mixto 1ESO+2ESO","date":"2026-06-23","start":"11:00","end":"13:00","min":1,"max":2,"groups":"1ESO A+2ESO A, 1ESO B+2ESO B"},
        {"name":"Acomp. 4ESO A a concierto","date":"2026-06-23","start":"09:00","end":"13:00","min":1,"max":2,"groups":"4ESO A"},
        {"name":"Supervisar recogida","date":"2026-06-23","start":"11:00","end":"13:00","min":1,"max":2,"groups":""},
        # TUE 23 TARDE
        {"name":"Acomp. 3ESO B a ruta","date":"2026-06-23","start":"15:00","end":"17:00","min":1,"max":2,"groups":"3ESO B"},
        {"name":"Acomp. 2BAT B a debate","date":"2026-06-23","start":"15:00","end":"17:00","min":1,"max":2,"groups":"2BAT B"},
        {"name":"Supervisar patio comida","date":"2026-06-23","start":"15:00","end":"16:30","min":1,"max":2,"groups":""},
     ]},
]


def get_seed_projects():
    return [{"name": p["name"],
             "teachers": [dict(t) for t in p["teachers"]],
             "needs": [dict(n) for n in p["needs"]]}
            for p in PROJECTS]

def get_seed_project(index=0):
    return get_seed_projects()[index]
