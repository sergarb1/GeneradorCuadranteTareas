# -*- coding: utf-8 -*-
"""
Tests del sistema de grupos AND/OR en el asignador de profesores.

══════════════════════════════════════════════════════════════════════
  Como usar estos tests
══════════════════════════════════════════════════════════════════════

  # Desde la raiz del proyecto, ejecuta:
  python -m unittest discover tests -v

  # O un archivo concreto:
  python -m unittest tests.test_scheduler_groups -v

  # O un test concreto:
  python -m unittest tests.test_scheduler_groups.TestParseGroupExpr.test_empty -v

══════════════════════════════════════════════════════════════════════
  Sintaxis de grupos (AND/OR)
══════════════════════════════════════════════════════════════════════

  Las necesidades pueden tener un campo "groups" con esta sintaxis:

    • "" (vacio)         → Cualquier profesor vale.
    • "1ESO A"           → El profesor debe dar 1ESO A (OR simple).
    • "1ESO A, 2ESO B"   → El profesor da 1ESO A O 2ESO B (OR).
    • "1ESO A+2ESO B"    → El profesor da 1ESO A Y 2ESO B (AND).
    • "1ESO A+2ESO B, 3ESO A"
                         → (1ESO A Y 2ESO B) O 3ESO A (AND dentro de OR).

  Internamente el scheduler parsea la expresion y obtiene una lista de
  conjuntos (cada uno es AND), donde la lista completa es OR:

    "1ESO A+2ESO B, 3ESO A"
      →  [{1ESO A, 2ESO B}, {3ESO A}]

  El profesor es valido si cumple AL MENOS UN conjunto, es decir, si
  su lista de grupos contiene TODOS los grupos de algun conjunto.

══════════════════════════════════════════════════════════════════════
"""
import unittest
from datetime import datetime
from scheduler import TeacherScheduler
from seed_data import get_seed_projects


# ====================================================================
#  Profesores y necesidades de ejemplo para los tests
# ====================================================================
#  Se definen al principio para que los tests sean legibles y se
#  puedan reutilizar.

ANA = {
    "name": "Ana Alumnez",
    "max_hours": 20,
    "max_hours_per_day": 6,
    "groups": ["1ESO A", "1ESO B"],
    "time_slots": [
        {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
    ],
}

CARLOS = {
    "name": "Carlos Profesorez",
    "max_hours": 20,
    "max_hours_per_day": 6,
    "groups": ["2ESO A", "2ESO B"],
    "time_slots": [
        {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
    ],
}

ELENA = {
    "name": "Elena Textualdez",
    "max_hours": 20,
    "max_hours_per_day": 6,
    "groups": ["1ESO A", "1ESO B", "2ESO A"],
    "time_slots": [
        {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
    ],
}

# Necesidades que se reutilizan en varios tests
NECESIDAD_1ESO_A = {
    "name": "Acompanar 1ESO A",
    "date": "2026-06-22",
    "start": "10:00",
    "end": "11:00",
    "min": 1,
    "max": 2,
    "groups": "1ESO A",          # OR simple: solo 1ESO A
}

NECESIDAD_AND = {
    "name": "Mixto 1ESO A + 2ESO A",
    "date": "2026-06-22",
    "start": "10:00",
    "end": "11:00",
    "min": 1,
    "max": 2,
    "groups": "1ESO A+2ESO A",   # AND: necesita AMBOS grupos
}

NECESIDAD_OR_AND = {
    "name": "Mixto combinado",
    "date": "2026-06-22",
    "start": "10:00",
    "end": "11:00",
    "min": 1,
    "max": 2,
    "groups": "1ESO A+2ESO A, 2ESO B",  # (1ESO A Y 2ESO A) O 2ESO B
}

NECESIDAD_SIN_GRUPOS = {
    "name": "Tarea generica",
    "date": "2026-06-22",
    "start": "10:00",
    "end": "11:00",
    "min": 1,
    "max": 2,
    "groups": "",                # vacio = cualquier profesor
}


# ====================================================================
class TestParseGroupExpr(unittest.TestCase):
    """Tests del metodo _parse_group_expr del scheduler.

    Este metodo convierte una expresion de grupos (string) en una lista
    de conjuntos, lista que se usa internamente para filtrar profesores.
    """

    def setUp(self):
        """Crea un scheduler ligero para acceder a _parse_group_expr."""
        self.s = TeacherScheduler([], [])

    # ── Test 1: Cadena vacia ──────────────────────────────────────────
    def test_empty(self):
        """groups vacio → None (sin restriccion)."""
        self.assertIsNone(
            self.s._parse_group_expr(""),
            "Campo groups vacio debe devolver None (= cualquiera vale)."
        )

    # ── Test 2: OR simple ─────────────────────────────────────────────
    def test_or_simple(self):
        """"1ESO A" → [{1ESO A}] (lista con un conjunto)."""
        result = self.s._parse_group_expr("1ESO A")
        esperado = [{"1ESO A"}]
        self.assertEqual(
            result, esperado,
            "Un solo grupo debe crear un unico conjunto de un elemento."
        )

    # ── Test 3: OR con dos opciones ───────────────────────────────────
    def test_or_dos_opciones(self):
        """"1ESO A, 2ESO B" → [{1ESO A}, {2ESO B}]."""
        result = self.s._parse_group_expr("1ESO A, 2ESO B")
        esperado = [{"1ESO A"}, {"2ESO B"}]
        self.assertEqual(
            result, esperado,
            "La coma separa opciones OR, cada una en su propio conjunto."
        )

    # ── Test 4: AND simple ────────────────────────────────────────────
    def test_and_simple(self):
        """"1ESO A+2ESO B" → [{1ESO A, 2ESO B}]."""
        result = self.s._parse_group_expr("1ESO A+2ESO B")
        esperado = [{"1ESO A", "2ESO B"}]
        self.assertEqual(
            result, esperado,
            "El + agrupa grupos dentro de un mismo conjunto (AND)."
        )

    # ── Test 5: AND dentro de OR ──────────────────────────────────────
    def test_and_inside_or(self):
        """"1ESO A+2ESO A, 2ESO B" → [{1ESO A, 2ESO A}, {2ESO B}]."""
        result = self.s._parse_group_expr("1ESO A+2ESO A, 2ESO B")
        esperado = [{"1ESO A", "2ESO A"}, {"2ESO B"}]
        self.assertEqual(
            result, esperado,
            "Primero se separa por comas (OR), luego cada parte por + (AND)."
        )

    # ── Test 6: Espacios sobrantes ────────────────────────────────────
    def test_whitespace(self):
        """Los espacios alrededor de grupos se ignoran."""
        result = self.s._parse_group_expr("  1ESO A  ,  2ESO B+3ESO A  ")
        esperado = [{"1ESO A"}, {"2ESO B", "3ESO A"}]
        self.assertEqual(
            result, esperado,
            "Los espacios alrededor de grupos y separadores deben ignorarse."
        )

    # ── Test 7: Lista (backward compatibility) ─────────────────────────
    def test_backward_compat_list(self):
        """Formato antiguo con lista → cada elemento tratado como OR simple."""
        result = self.s._parse_group_expr(["1ESO A", "2ESO B"])
        esperado = [{"1ESO A"}, {"2ESO B"}]
        self.assertEqual(
            result, esperado,
            "Datos antiguos con groups como lista deben seguir funcionando."
        )

    # ── Test 8: None ──────────────────────────────────────────────────
    def test_none(self):
        """None como entrada → None (sin restriccion)."""
        self.assertIsNone(
            self.s._parse_group_expr(None),
            "None debe tratarse igual que cadena vacia."
        )


# ====================================================================
class TestTeacherAvailableGroups(unittest.TestCase):
    """Tests del metodo _teacher_available con filtro de grupos.

    Verifica que el scheduler solo permite asignar un profesor a una
    necesidad si el profesor cumple los requisitos de grupos.
    """

    def setUp(self):
        """Crea un scheduler con los 3 profesores de ejemplo."""
        self.s = TeacherScheduler([ANA, CARLOS, ELENA], [])

    # ── Test 1: Sin restriccion de grupos ─────────────────────────────
    def test_sin_restriccion(self):
        """groups vacio → cualquier profesor con horario disponible."""
        for t in (ANA, CARLOS, ELENA):
            self.assertTrue(
                self.s._teacher_available(t, NECESIDAD_SIN_GRUPOS),
                f"{t['name']} deberia poder cubrir una necesidad sin grupos."
            )

    # ── Test 2: Grupo concreto (OR simple) ───────────────────────────
    def test_grupo_concreto(self):
        """groups='1ESO A' → solo profes que dan 1ESO A."""
        self.assertTrue(
            self.s._teacher_available(ANA, NECESIDAD_1ESO_A),
            "Ana da 1ESO A, deberia poder."
        )
        self.assertFalse(
            self.s._teacher_available(CARLOS, NECESIDAD_1ESO_A),
            "Carlos no da 1ESO A, no deberia poder."
        )

    # ── Test 3: AND (ambos grupos) ────────────────────────────────────
    def test_and_ambos_grupos(self):
        """groups='1ESO A+2ESO A' → solo quien da AMBOS grupos."""
        self.assertTrue(
            self.s._teacher_available(ELENA, NECESIDAD_AND),
            "Elena da 1ESO A y 2ESO A, deberia poder."
        )
        self.assertFalse(
            self.s._teacher_available(ANA, NECESIDAD_AND),
            "Ana da 1ESO A pero no 2ESO A, no deberia poder."
        )
        self.assertFalse(
            self.s._teacher_available(CARLOS, NECESIDAD_AND),
            "Carlos da 2ESO A pero no 1ESO A, no deberia poder."
        )

    # ── Test 4: AND dentro de OR ──────────────────────────────────────
    def test_and_inside_or(self):
        """(1ESO A+2ESO A) O 2ESO B → Elena (AND) o Carlos (OR simple)."""
        self.assertTrue(
            self.s._teacher_available(ELENA, NECESIDAD_OR_AND),
            "Elena cumple (1ESO A Y 2ESO A) → deberia poder."
        )
        self.assertTrue(
            self.s._teacher_available(CARLOS, NECESIDAD_OR_AND),
            "Carlos cumple 2ESO B → deberia poder."
        )
        self.assertFalse(
            self.s._teacher_available(ANA, NECESIDAD_OR_AND),
            "Ana no cumple ninguna opcion → no deberia poder."
        )

    # ── Test 5: Profesor sin grupos ───────────────────────────────────
    def test_teacher_sin_grupos(self):
        """Profesor sin campo groups no puede cubrir necesidades con grupos."""
        t_sin_grupos = {
            "name": "Invitado",
            "max_hours": 10,
            "max_hours_per_day": 5,
            "time_slots": [{"date": "2026-06-22", "start": "09:00", "end": "14:00"}],
        }
        self.assertFalse(
            self.s._teacher_available(t_sin_grupos, NECESIDAD_1ESO_A),
            "Profe sin grupos no deberia cubrir una necesidad que requiere grupos."
        )
        self.assertTrue(
            self.s._teacher_available(t_sin_grupos, NECESIDAD_SIN_GRUPOS),
            "Profe sin grupos SI deberia cubrir necesidad sin restriccion."
        )

    # ── Test 6: Horario insuficiente ──────────────────────────────────
    def test_horario_insuficiente(self):
        """Si un profesor no tiene horario, no puede cubrir aunque tenga el grupo."""
        t_sin_horario = {
            "name": "Ocupado",
            "max_hours": 10,
            "max_hours_per_day": 5,
            "groups": ["1ESO A"],
            "time_slots": [],  # Sin disponibilidad
        }
        self.assertFalse(
            self.s._teacher_available(t_sin_horario, NECESIDAD_1ESO_A),
            "Profe sin horario no puede cubrir ninguna necesidad."
        )


# ====================================================================
class TestSeedProjectsSolvable(unittest.TestCase):
    """Verifica que los proyectos de datos ficticios tengan solucion.

    Estos tests usan el solver CP-SAT real para confirmar que ambos
    proyectos semilla son resolubles. Si fallan, los datos de ejemplo
    estan mal y hay que ajustarlos.
    """

    def test_proyecto_limpieza(self):
        """Proyecto 'Apoyo limpieza aulas' debe tener solucion."""
        projects = get_seed_projects()
        p = projects[0]  # El primero es limpieza (sin grupos)
        s = TeacherScheduler(p["teachers"], p["needs"])
        s.build_model()
        status = s.solve(time_limit=30)
        from ortools.sat.python import cp_model
        self.assertIn(
            status, (cp_model.OPTIMAL, cp_model.FEASIBLE),
            f"El proyecto '{p['name']}' no tiene solucion. "
            "Revisa la disponibilidad de profesores vs necesidades."
        )

    def test_proyecto_acompanamiento(self):
        """Proyecto 'Acompanamiento alumnos' (con grupos) debe tener solucion."""
        projects = get_seed_projects()
        p = projects[1]  # El segundo es acompanamiento (con grupos)
        s = TeacherScheduler(p["teachers"], p["needs"])
        s.build_model()
        status = s.solve(time_limit=30)
        from ortools.sat.python import cp_model
        self.assertIn(
            status, (cp_model.OPTIMAL, cp_model.FEASIBLE),
            f"El proyecto '{p['name']}' no tiene solucion. "
            "Revisa restricciones de grupos y horarios."
        )

    def test_ambos_tienen_datos_ficticios(self):
        """Ambos proyectos deben contener '(DATOS FICTICIOS)' en el nombre."""
        projects = get_seed_projects()
        for p in projects:
            self.assertIn(
                "DATOS FICTICIOS", p["name"],
                f"El proyecto '{p['name']}' debe indicar que son datos ficticios."
            )


# ====================================================================
#  Punto de entrada
# ====================================================================
#  Si ejecutas este archivo directamente con:
#      python tests/test_scheduler_groups.py
#  se lanzan todos los tests con salida detallada.
if __name__ == "__main__":
    unittest.main(verbosity=2)
