# -*- coding: utf-8 -*-
"""
Lanzador de tests con salida detallada.

Uso:
    python run_tests.py            # Todos los tests
    python run_tests.py -k grupos  # Solo tests con 'grupos' en el nombre
    python run_tests.py --help     # Mas opciones

Los tests estan en la carpeta tests/ y usan unittest.
"""
import unittest
import sys

if __name__ == "__main__":
    # Carga todos los tests descubiertos en la carpeta tests/
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Codigo de salida util para CI/CD
    sys.exit(0 if result.wasSuccessful() else 1)
