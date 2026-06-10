#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# main.py — Punto de entrada del Generador de Cuadrantes de Apoyo al Profesorado
# =============================================================================
# Este archivo arranca la aplicación PyQt6. Crea la instancia QApplication,
# aplica el estilo Fusion (nativo, multiplataforma) y lanza la ventana
# principal contenida en gui.py -> App.
# =============================================================================

import sys       # Argumentos de línea de comandos y salida del proceso
import os       # Para insertar en sys.path el directorio raíz

# Asegura que el directorio raíz del proyecto esté en el path de Python
# para que los imports relativos funcionen aunque se ejecute desde otro lugar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication  # Framework GUI
from gui import App                      # Ventana principal de la aplicación


def main():
    """Punto de entrada principal: configura Qt y lanza la ventana."""
    # Instancia única de QApplication (obligatoria en toda app PyQt)
    app = QApplication(sys.argv)
    # Fusion: estilo moderno y consistente en Windows, Linux y macOS
    app.setStyle("Fusion")

    # Crea y muestra la ventana principal
    window = App()
    window.showMaximized()

    # Bucle de eventos de Qt; sys.exit() asegura código de salida correcto
    sys.exit(app.exec())


# Estándar Python: solo ejecuta main() si este archivo es el punto de entrada
if __name__ == "__main__":
    main()
