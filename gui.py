# ──────────────────────────────────────────────────────────────────────────
# gui.py — Interfaz gráfica (PyQt6) del Generador Cuadrante Tareas
# Proporciona la UI completa con pestañas, formularios, solapamiento
# de arrastrar y soltar, diálogos y generación del cuadrante vía CP-SAT.
# ──────────────────────────────────────────────────────────────────────────

import json, os, re, webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTabWidget, QScrollArea, QFrame, QTextEdit, QSizePolicy,
    QMessageBox, QDateEdit, QDialog, QFormLayout, QDialogButtonBox,
    QButtonGroup, QRadioButton, QFileDialog, QStatusBar, QMenu, QCheckBox,
    QListWidget, QListWidgetItem, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QDate, pyqtSignal, QMimeData, QThread, QObject, QRect, QPoint
from PyQt6.QtGui import QFont, QAction, QColor, QShortcut, QKeySequence, QPixmap, QPainter, QIcon, QDrag, QRegion
from PyQt6.QtWidgets import QColorDialog, QInputDialog

from ortools.sat.python import cp_model
from scheduler import TeacherScheduler, duration_min
from html_exporter import export_html_file
from seed_data import get_seed_teachers, get_seed_needs

# ── Colores ──────────────────────────────────────────────────────────────
C_PRI    = "#16a34a"
C_PRI_D  = "#15803d"
C_PRI_L  = "#4ade80"
C_ACCENT = "#f59e0b"
C_RED    = "#ef4444"
C_SLATE  = "#94a3b8"

C_BG      = "#f8fafc"
C_CARD    = "#ffffff"
C_BORDER  = "#e2e8f0"
C_TEXT    = "#0f172a"
C_TEXT2   = "#475569"

C_BG_D      = "#0f172a"
C_CARD_D    = "#1e293b"
C_BORDER_D  = "#334155"
C_TEXT_D    = "#f8fafc"
C_TEXT2_D   = "#94a3b8"

C_BG_HC      = "#000000"
C_CARD_HC    = "#1a1a1a"
C_BORDER_HC  = "#555555"
C_TEXT_HC    = "#ffffff"
C_TEXT2_HC   = "#cccccc"
C_PRI_HC     = "#ffff00"
C_PRI_D_HC   = "#ffcc00"
C_PRI_L_HC   = "#ffff66"

TEACHER_COLORS = [C_PRI, C_RED, "#10b981", "#8b5cf6", C_ACCENT, "#06b6d4", "#ec4899", "#3b82f6", "#f97316", "#14b8a6"]

DAYS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
TEACHERS_FILE = os.path.join(BASE_DIR, "teachers.json")

# ── QSS themes ───────────────────────────────────────────────────────────
LIGHT_QSS = f"""
QMainWindow {{ background: {C_BG}; }}
QTabWidget {{ background: {C_BG}; }}
QTabWidget::pane {{ background: {C_BG}; border: 1px solid {C_BORDER}; border-radius: 8px; }}
QWidget#tab_content {{ background: transparent; }}
QTabBar::tab {{ background: {C_BORDER}; color: {C_TEXT2}; padding: 6px 14px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 12px; }}
QTabBar::tab:selected {{ background: {C_CARD}; color: {C_PRI}; font-weight: bold; }}
QPushButton {{ background: {C_PRI}; color: #fff; border: none; padding: 6px 14px; border-radius: 5px; font-size: 12px; }}
QPushButton:hover {{ background: {C_PRI_D}; }}
QPushButton#danger {{ background: transparent; color: {C_RED}; border: none; padding: 4px 8px; border-radius: 4px; font-size: 14px; }}
QPushButton#danger:hover {{ background: #fee2e2; }}
QPushButton#secondary {{ background: {C_BORDER}; color: {C_TEXT}; border: 1px solid #cbd5e1; }}
QPushButton#secondary:hover {{ background: #cbd5e1; }}
QPushButton#cta {{ background: #ece5da; color: #3d2b1f; border: 1px solid #d4cbb8; }}
QPushButton#cta:hover {{ background: #e2d9ca; }}
QLineEdit {{ background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT}; }}
QComboBox {{ background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT}; }}
QLabel {{ color: {C_TEXT}; }}
QTextEdit {{ background: #f1f5f9; border: 1px solid {C_BORDER}; border-radius: 6px; color: {C_TEXT}; font-family: Consolas; }}
QScrollBar:vertical {{ background: {C_BG}; width: 6px; border-radius: 3px; }}
QScrollBar::handle:vertical {{ background: #cbd5e1; border-radius: 3px; min-height: 20px; }}
QScrollBar:horizontal {{ background: {C_BG}; height: 6px; border-radius: 3px; }}
QScrollBar::handle:horizontal {{ background: #cbd5e1; border-radius: 3px; min-width: 20px; }}
QFrame#card {{ background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 8px; }}
QFrame#sep {{ background: {C_BORDER}; max-height: 1px; }}
QFrame#row {{ background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 5px; }}
QFrame#row:hover {{ background: #f1f5f9; }}
QFrame#row_selected {{ background: #dbeafe; border: 1px solid {C_PRI}; border-radius: 5px; }}
QFrame#slot_row {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; }}
QFrame#need_row {{ background: #fefce8; border: 1px solid #fde68a; border-radius: 4px; }}
"""

DARK_QSS = f"""
QMainWindow {{ background: {C_BG_D}; }}
QTabWidget {{ background: {C_BG_D}; }}
QTabWidget::pane {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 8px; }}
QWidget#tab_content {{ background: transparent; }}
QTabBar::tab {{ background: {C_BORDER_D}; color: {C_TEXT2_D}; padding: 6px 14px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 12px; }}
QTabBar::tab:selected {{ background: {C_CARD_D}; color: {C_PRI_L}; font-weight: bold; }}
QPushButton {{ background: #065f46; color: #fff; border: none; padding: 6px 14px; border-radius: 5px; font-size: 12px; }}
QPushButton:hover {{ background: {C_PRI_L}; }}
QPushButton#danger {{ background: transparent; color: {C_RED}; border: none; padding: 4px 8px; border-radius: 4px; font-size: 14px; }}
QPushButton#danger:hover {{ background: #450a0a; }}
QPushButton#secondary {{ background: {C_BORDER_D}; color: {C_TEXT_D}; border: 1px solid #475569; }}
QPushButton#secondary:hover {{ background: #475569; }}
QPushButton#cta {{ background: #3d3026; color: #d4cbb8; border: 1px solid #5c4d3e; }}
QPushButton#cta:hover {{ background: #4d3d30; }}
QLineEdit {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT_D}; }}
QComboBox {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT_D}; }}
QLabel {{ color: {C_TEXT_D}; }}
QTextEdit {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 6px; color: #e2e8f0; font-family: Consolas; }}
QScrollBar:vertical {{ background: {C_BG_D}; width: 6px; border-radius: 3px; }}
QScrollBar::handle:vertical {{ background: #475569; border-radius: 3px; min-height: 20px; }}
QScrollBar:horizontal {{ background: {C_BG_D}; height: 6px; border-radius: 3px; }}
QScrollBar::handle:horizontal {{ background: #475569; border-radius: 3px; min-width: 20px; }}
QFrame#card {{ background: {C_CARD_D}; border: 1px solid {C_BORDER_D}; border-radius: 8px; }}
QFrame#sep {{ background: {C_BORDER_D}; max-height: 1px; }}
QFrame#row {{ background: {C_CARD_D}; border: 1px solid {C_BORDER_D}; border-radius: 5px; }}
QFrame#row:hover {{ background: #263548; }}
QFrame#row_selected {{ background: #064e3b; border: 1px solid {C_PRI_L}; border-radius: 5px; }}
QFrame#slot_row {{ background: #0a3d2a; border: 1px solid #166534; border-radius: 4px; }}
QFrame#need_row {{ background: #422006; border: 1px solid #713f12; border-radius: 4px; }}
"""

HIGH_CONTRAST_QSS = f"""
QMainWindow {{ background: {C_BG_HC}; }}
QTabWidget {{ background: {C_BG_HC}; }}
QTabWidget::pane {{ background: {C_BG_HC}; border: 2px solid {C_BORDER_HC}; border-radius: 8px; }}
QWidget#tab_content {{ background: transparent; }}
QTabBar::tab {{ background: {C_BORDER_HC}; color: {C_TEXT2_HC}; padding: 6px 14px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 12px; }}
QTabBar::tab:selected {{ background: {C_CARD_HC}; color: {C_PRI_HC}; font-weight: bold; }}
QPushButton {{ background: {C_PRI_HC}; color: #000; border: 2px solid {C_PRI_HC}; padding: 6px 14px; border-radius: 5px; font-size: 12px; font-weight: bold; }}
QPushButton:hover {{ background: {C_PRI_D_HC}; border-color: {C_PRI_D_HC}; }}
QPushButton#danger {{ background: transparent; color: #ff4444; border: 2px solid #ff4444; padding: 4px 8px; border-radius: 4px; font-size: 14px; }}
QPushButton#danger:hover {{ background: #330000; }}
QPushButton#secondary {{ background: {C_CARD_HC}; color: {C_TEXT_HC}; border: 2px solid {C_BORDER_HC}; }}
QPushButton#secondary:hover {{ background: #333333; }}
QPushButton#cta {{ background: #c4b8a8; color: #1a120a; border: 2px solid #a89884; }}
QPushButton#cta:hover {{ background: #b8aa98; }}
QLineEdit {{ background: {C_BG_HC}; border: 2px solid {C_BORDER_HC}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT_HC}; }}
QComboBox {{ background: {C_BG_HC}; border: 2px solid {C_BORDER_HC}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT_HC}; }}
QComboBox::drop-down {{ border: none; }}
QComboBox::down-arrow {{ image: none; }}
QLabel {{ color: {C_TEXT_HC}; }}
QTextEdit {{ background: {C_BG_HC}; border: 2px solid {C_BORDER_HC}; border-radius: 6px; color: {C_TEXT_HC}; font-family: Consolas; }}
QScrollBar:vertical {{ background: {C_BG_HC}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {C_BORDER_HC}; border-radius: 4px; min-height: 20px; }}
QScrollBar:horizontal {{ background: {C_BG_HC}; height: 8px; border-radius: 4px; }}
QScrollBar::handle:horizontal {{ background: {C_BORDER_HC}; border-radius: 4px; min-width: 20px; }}
QFrame#card {{ background: {C_CARD_HC}; border: 2px solid {C_BORDER_HC}; border-radius: 8px; }}
QFrame#sep {{ background: {C_BORDER_HC}; max-height: 2px; }}
QFrame#row {{ background: {C_CARD_HC}; border: 2px solid {C_BORDER_HC}; border-radius: 5px; }}
QFrame#row:hover {{ background: #2a2a2a; border-color: {C_PRI_HC}; }}
QFrame#row_selected {{ background: #333300; border: 2px solid {C_PRI_HC}; border-radius: 5px; }}
QFrame#slot_row {{ background: #0a2a0a; border: 2px solid #00cc00; border-radius: 4px; }}
QFrame#need_row {{ background: #332200; border: 2px solid #ffaa00; border-radius: 4px; }}
QMenu {{ background: {C_BG_HC}; border: 2px solid {C_BORDER_HC}; color: {C_TEXT_HC}; }}
QMenu::item {{ padding: 6px 20px; }}
QMenu::item:selected {{ background: #333333; color: {C_PRI_HC}; }}
"""

# ── Funciones auxiliares (independientes de UI) ─────────────────────────
def _ensure_dirs():
    """Crea el directorio de proyectos si no existe."""
    os.makedirs(PROJECTS_DIR, exist_ok=True)

def _load_teachers():
    """Carga la lista global de profesores desde teachers.json."""
    if os.path.exists(TEACHERS_FILE):
        try:
            with open(TEACHERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_teachers(teachers):
    """Guarda la lista global de profesores en teachers.json."""
    _ensure_dirs()
    with open(TEACHERS_FILE, "w", encoding="utf-8") as f:
        json.dump(teachers, f, ensure_ascii=False, indent=2)

def _list_projects():
    """Enumera los proyectos guardados (archivos .json, excluye _generated.json)."""
    _ensure_dirs()
    names = []
    for f in sorted(os.listdir(PROJECTS_DIR)):
        if not f.endswith(".json") or f.endswith("_generated.json"): continue
        try:
            with open(os.path.join(PROJECTS_DIR, f), "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    names.append(data.get("name", f.replace(".json", "")))
                else:
                    names.append(f.replace(".json", ""))
        except Exception:
            names.append(f.replace(".json", ""))
    return names

def _project_filename(name):
    """Convierte un nombre de proyecto en una ruta de archivo segura."""
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip() or "sin_titulo")
    return os.path.join(PROJECTS_DIR, f"{safe}.json")

def _save_project(name, needs):
    """Persiste un proyecto (nombre + necesidades) en un archivo JSON."""
    _ensure_dirs()
    with open(_project_filename(name), "w", encoding="utf-8") as f:
        json.dump({"name": name.strip() or "Sin título", "needs": needs}, f, ensure_ascii=False, indent=2)

def _load_project(name):
    """Carga un proyecto desde su archivo JSON."""
    with open(_project_filename(name), "r", encoding="utf-8") as f:
        return json.load(f)

def _delete_project_file(name):
    """Elimina el archivo del proyecto y sus opciones generadas asociadas."""
    p = _project_filename(name)
    if os.path.exists(p): os.remove(p)
    gp = _generated_options_filename(name)
    if os.path.exists(gp): os.remove(gp)

def _generated_options_filename(name):
    """Devuelve la ruta del archivo donde se guardan las opciones generadas."""
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip() or "sin_titulo")
    return os.path.join(PROJECTS_DIR, f"{safe}_generated.json")

def _fmt_slot(s):
    """Formatea una franja de disponibilidad para mostrarla en la UI."""
    try:
        d = datetime.strptime(s["date"], "%Y-%m-%d")
        df = d.strftime("%d/%m/%Y")
    except Exception:
        df = s.get("date", "?")
    return f"🕐 {df}  {s.get('start', '?')} - {s.get('end', '?')}"

# ── Componente Toast (notificación flotante) ──────────────────────────
class Toast(QFrame):
    """Notificación emergente temporal con color según tipo (success/warning/error)."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setStyleSheet("background: #059669; border-radius: 8px;")
        self.label = QLabel(self)
        self.label.setStyleSheet("color: white; font-size: 13px; padding: 10px 24px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()

    def show(self, message, msg_type="success"):
        """Muestra el toast centrado en la ventana padre durante 3.5 segundos."""
        colors = {"success": "#059669", "warning": "#d97706", "error": "#dc2626"}
        self.setStyleSheet(f"background: {colors.get(msg_type, '#059669')}; border-radius: 8px;")
        self.label.setText(message)
        self.label.setWordWrap(True)
        w = self.parent().width()
        mw = min(420, w - 40)
        self.label.setFixedWidth(mw - 48)
        self.setFixedWidth(mw)
        self.adjustSize()
        self.move((w - self.width()) // 2, 16)
        self.raise_()
        super().show()
        QTimer.singleShot(3500, self.hide)

def _str_to_qdate(s):
    """Convierte una fecha 'YYYY-MM-DD' a QDate de forma explícita y segura."""
    parts = s.split("-")
    return QDate(int(parts[0]), int(parts[1]), int(parts[2]))

# ── Frame clickeable (soporte para arrastrar y soltar) ─────────────────
class ClickFrame(QFrame):
    """Frame que emite señal onClick y permite arrastrar datos de profesor (drag)."""
    clicked = pyqtSignal(int, int)
    def __init__(self, a=0, b=0, parent=None):
        super().__init__(parent)
        self.a = a  # Índice de necesidad asociada
        self.b = b  # Índice de profesor asociado
        self._drag_start = None
    def mousePressEvent(self, e):
        """Guarda la posición inicial para detectar arrastre."""
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_start = e.position().toPoint()
        super().mousePressEvent(e)
    def mouseMoveEvent(self, e):
        """Inicia el drag si el cursor se movió lo suficiente desde el press."""
        if self._drag_start is None or self.a < 0 or self.b < 0:
            return
        if (e.position().toPoint() - self._drag_start).manhattanLength() < 10:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData("application/x-teacher", json.dumps([self.a, self.b]).encode())
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)
        self._drag_start = None
    def mouseReleaseEvent(self, e):
        """Emite la señal clicked si no hubo arrastre (detección de clic)."""
        if self._drag_start is not None:
            self.clicked.emit(self.a, self.b)
        self._drag_start = None
        super().mouseReleaseEvent(e)

class DropFrame(QFrame):
    """Frame que acepta drops de profesores arrastrados y emite señal con los índices (origen, destino, profesor)."""
    dropped = pyqtSignal(int, int, int)
    def __init__(self, need_idx, parent=None):
        super().__init__(parent)
        self.need_idx = need_idx  # Índice de la necesidad destino
        self.setAcceptDrops(True)
        self._drag_over = False
    def dragEnterEvent(self, e):
        """Acepta la entrada si arrastra datos de profesor y resalta el borde."""
        if e.mimeData().hasFormat("application/x-teacher"):
            self._drag_over = True
            self.setStyleSheet("border: 2px dashed #6366f1; border-radius: 8px;")
            e.acceptProposedAction()
    def dragMoveEvent(self, e):
        """Permite el movimiento mientras arrastra."""
        if e.mimeData().hasFormat("application/x-teacher"):
            e.acceptProposedAction()
    def dragLeaveEvent(self, e):
        """Limpia el resalte al salir del área de drop."""
        self._drag_over = False
        self.setStyleSheet("")
    def dropEvent(self, e):
        """Procesa el drop: lee los índices origen y emite la señal con destino."""
        self._drag_over = False
        self.setStyleSheet("")
        data = json.loads(e.mimeData().data("application/x-teacher").data().decode())
        src_need_idx, teacher_idx = data
        self.dropped.emit(src_need_idx, self.need_idx, teacher_idx)

# ── Diálogo de carga animado ──────────────────────────────────────────
class LoadingDialog(QDialog):
    """Diálogo modal compacto con spinner animado mientras el solver CP-SAT resuelve."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generando")
        self.setFixedSize(200, 80)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        c = QWidget(self)
        c.setStyleSheet(f"background: {C_CARD}; border-radius: 10px;")
        l = QVBoxLayout(c)
        l.setContentsMargins(16, 12, 16, 12)
        l.setSpacing(6)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner = QLabel("⣾")
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner.setStyleSheet(f"font-size: 22px; color: {C_PRI};")
        l.addWidget(self.spinner)
        self.msg = QLabel("Pensando...")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setStyleSheet(f"font-size: 12px; color: {C_TEXT2};")
        l.addWidget(self.msg)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(c)
        self._chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
        self._idx = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(120)
    def _tick(self):
        self._idx = (self._idx + 1) % len(self._chars)
        self.spinner.setText(self._chars[self._idx])
    def set_message(self, text):
        self.msg.setText(text)

# ── Worker para ejecutar el solver en segundo plano ───────────────────────
class SolverWorker(QObject):
    """Ejecuta TeacherScheduler en un hilo separado para no bloquear la UI."""
    finished = pyqtSignal(list)   # opciones generadas
    error = pyqtSignal(str)       # mensaje de error
    progress = pyqtSignal(str)    # cambio de estado
    def __init__(self, teachers, needs, locked=None, n_options=5, time_limit=10):
        super().__init__()
        self.teachers = teachers
        self.needs = needs
        self.locked = locked or {}
        self.n_options = n_options
        self.time_limit = time_limit
    def run(self):
        try:
            self.progress.emit("Construyendo modelo...")
            scheduler = TeacherScheduler(self.teachers, self.needs)
            scheduler.build_model(locked=self.locked if self.locked else None)
            self.progress.emit("Generando soluciones...")
            opciones = scheduler.solve_multiple(n_options=self.n_options, time_limit=self.time_limit)
            self.progress.emit("Finalizado")
            self.finished.emit(opciones)
        except Exception as e:
            self.error.emit(str(e))

# ── MultiOptionDialog ───────────────────────────────────────────────────
class MultiOptionDialog(QDialog):
    """Diálogo para elegir entre varias opciones de asignación generadas.

    Muestra una lista de opciones con estadísticas (asignaciones totales,
    necesidades cubiertas, horas totales) y permite al usuario seleccionar
    una haciendo clic en su botón de radio. Al pulsar "Aceptar" se retorna
    la opción seleccionada.
    """

    def __init__(self, options, parent=None):
        """Inicializa el diálogo con las opciones disponibles.

        Parámetros:
            options (list[dict]): Lista de opciones, cada una con:
                - id: número identificativo
                - n_assignments: total de asignaciones
                - n_covered: necesidades distintas cubiertas
                - total_needs: número total de necesidades
                - total_minutes: minutos totales asignados
                - teacher_hours: dict {nombre_profesor: minutos}
                - assignment: lista de asignaciones completa
        """
        super().__init__(parent)
        self.setWindowTitle("🎯 Elige una opción de cuadrante")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        self.options = options               # Todas las opciones disponibles
        self.selected_index = 0              # Índice de la opción seleccionada
        self.selected_option = None          # Opción final elegida (se retorna)

        # Layout principal
        v = QVBoxLayout(self)
        v.setSpacing(12)
        v.setContentsMargins(20, 16, 20, 16)

        # Título explicativo
        titulo = QLabel(f"🎯 Se encontraron {len(options)} opciones distintas")
        titulo.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {C_PRI};")
        v.addWidget(titulo)

        explicacion = QLabel(
            "Cada opción es una distribución distinta de profesores a tareas.\n"
            "Revisa las estadísticas y elige la que más te convenga."
        )
        explicacion.setStyleSheet(f"color: {C_TEXT2};")
        v.addWidget(explicacion)

        # Botones de radio para agrupar las opciones
        self.radio_group = QButtonGroup(self)

        # Área de scroll con las tarjetas de opciones
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        contenedor = QWidget()
        self.cards_layout = QVBoxLayout(contenedor)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(contenedor)
        v.addWidget(scroll, 1)

        # Crea una tarjeta para cada opción
        for i, op in enumerate(options):
            card = self._build_option_card(i, op)
            self.cards_layout.addWidget(card)

        # Botones de acción (Aceptar / Cancelar)
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        cancelar = QPushButton("❌ Cancelar")
        cancelar.setToolTip("Volver sin elegir ninguna opción")
        cancelar.setObjectName("secondary")
        cancelar.clicked.connect(self.reject)
        btn_lay.addWidget(cancelar)
        aceptar = QPushButton("✅ Aceptar opción seleccionada")
        aceptar.setToolTip("Usar la opción seleccionada como cuadrante principal")
        aceptar.setMinimumWidth(220)
        aceptar.clicked.connect(self._accept)
        btn_lay.addWidget(aceptar)
        v.addLayout(btn_lay)

        # Selecciona la primera opción por defecto
        if options:
            self.radio_group.button(0).setChecked(True)
            self.selected_index = 0

    def _build_option_card(self, idx, op):
        """Construye una tarjeta visual para una opción.

        Parámetros:
            idx (int): Índice de la opción en la lista.
            op (dict): Datos de la opción.

        Retorna:
            QFrame: Tarjeta con los datos de la opción.
        """
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("")  # Deja que QSS lo estilice
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        v_card = QVBoxLayout(card)
        v_card.setContentsMargins(14, 10, 14, 10)
        v_card.setSpacing(6)

        # Fila superior: radio button + título
        top = QHBoxLayout()
        radio = QRadioButton(f" Opción {op['id']}")
        radio.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {C_PRI};")
        self.radio_group.addButton(radio, idx)
        radio.toggled.connect(lambda checked, i=idx: self._on_select(i))
        top.addWidget(radio)
        top.addStretch()

        # Etiqueta de "mejor" si es la que más asignaciones tiene
        n_asign = op["n_assignments"]
        max_asign = max(o["n_assignments"] for o in self.options)
        if n_asign == max_asign:
            badge = QLabel("⭐ Más asignaciones")
            badge.setStyleSheet(
                f"background: #d4edda; color: #155724; border-radius: 4px; "
                f"padding: 2px 8px; font-size: 11px; font-weight: bold;"
            )
            top.addWidget(badge)

        # Etiqueta de "mejor cobertura"
        n_cub = op["n_covered"]
        max_cub = max(o["n_covered"] for o in self.options)
        if n_cub == max_cub and n_cub > 0:
            badge2 = QLabel(f"✅ {n_cub}/{op['total_needs']} necesidades")
            badge2.setStyleSheet(
                f"background: #cce5ff; color: #004085; border-radius: 4px; "
                f"padding: 2px 8px; font-size: 11px; font-weight: bold;"
            )
            top.addWidget(badge2)

        v_card.addLayout(top)

        # Estadísticas principales
        stats_text = (
            f"📌 {n_asign} asignaciones  ·  "
            f"📋 {op['n_covered']}/{op['total_needs']} necesidades cubiertas  ·  "
            f"⏱ {op['total_minutes'] // 60}h {op['total_minutes'] % 60:02d}m totales"
        )
        stats_lbl = QLabel(stats_text)
        stats_lbl.setStyleSheet(f"color: {C_TEXT2};")
        v_card.addWidget(stats_lbl)

        # Carga por profesor (compacto)
        if op["teacher_hours"]:
            prof_line = "👨‍🏫 " + "  ·  ".join(
                f"{nom}: {minu // 60}h{minu % 60:02d}m"
                for nom, minu in sorted(op["teacher_hours"].items())
            )
            prof_lbl = QLabel(prof_line)
            prof_lbl.setWordWrap(True)
            prof_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 11px;")
            v_card.addWidget(prof_lbl)

        return card

    def _on_select(self, idx):
        """Callback cuando se selecciona una opción."""
        self.selected_index = idx

    def _accept(self):
        """Confirma la selección y cierra el diálogo."""
        if self.options:
            self.selected_option = self.options[self.selected_index]
        self.accept()


# ── Clase principal de la aplicación ────────────────────────────────────
class App(QMainWindow):
    """Ventana principal de la aplicación. Gestiona toda la interfaz y la lógica de negocio."""
    def __init__(self):
        """Inicializa el estado, construye la UI, aplica el tema, carga datos y atajos."""
        super().__init__()
        self.setWindowTitle("📋 Generador Cuadrante Tareas Profesorado")
        self.setMinimumSize(1200, 720)

        self.teachers = _load_teachers()            # Lista global de profesores
        self.needs = []                              # Necesidades del proyecto actual
        self.project_name = ""
        self.last_assignment = None                 # Última asignación generada
        self.last_html_path = None                  # Ruta del último HTML generado
        self.generated_options = []                  # Opciones generadas por el solver
        self.generated_html_paths = []               # Rutas HTML de cada opción
        self.current_option_index = 0                # Índice de la opción visible
        self._dirty = False                          # Indica si hay cambios sin guardar
        self._selected_teacher_idx = None            # Profesor seleccionado en la lista
        self._theme_mode = 0                         # 0=claro, 1=oscuro, 2=alto contraste
        self._undo_stack = []                        # Pila de deshacer (hasta 50 estados)
        self._redo_stack = []                        # Pila de rehacer
        self._compact_view = False                   # Vista compacta del cuadrante
        self._locked_assignments = {}                # Asignaciones bloqueadas {(need_idx, teacher_idx): True}
        self._teacher_filter = ""
        self._need_filter = ""
        self._tslot_templates = []                   # Plantillas de franjas guardadas

        self._build_ui()
        self._apply_theme()
        self._refresh_project_list()
        self._rebuild_teacher_list()
        self._update_stats()

        # Timer de auto-guardado cada 2 minutos
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(120000)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start()

        # Atajos de teclado globales
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_current)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self._redo)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._new_project)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self._load_seed)
        QShortcut(QKeySequence("F1"), self).activated.connect(self._open_manual)
        QShortcut(QKeySequence("Escape"), self).activated.connect(lambda: self.status_bar.clearMessage())

        # Timer para limpiar mensajes de la barra de estado automáticamente
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status_bar.clearMessage())

        # Icono de la ventana
        self.setWindowIcon(self._make_icon())

        # Diálogo de bienvenida si no hay profesores (primera ejecución)
        if not self.teachers:
            QTimer.singleShot(300, self._show_welcome)

    # ── Tema (claro / oscuro / alto contraste) ───────────────────────
    def _apply_theme(self):
        """Aplica el tema correspondiente (QSS) según _theme_mode y actualiza el botón."""
        if self._theme_mode == 0:
            qss = LIGHT_QSS
            btn_text = "🌙 Oscuro"
        elif self._theme_mode == 1:
            qss = DARK_QSS
            btn_text = "♿ Alto contraste"
        else:
            qss = HIGH_CONTRAST_QSS
            btn_text = "☀️ Claro"
        QApplication.instance().setStyleSheet(qss)
        self.theme_btn.setText(btn_text)
        # La cabecera mantiene siempre el color primario
        self.header_bar.setStyleSheet(f"background: {C_PRI}; border-radius: 0;")
        # Actualizar grupos del toolbar según el tema
        if hasattr(self, '_group_frames'):
            if self._theme_mode == 0:
                ss = "QFrame#card { background: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 6px; padding: 2px 4px; }"
                lbl_ss = "font-size:10px; color:#64748b; padding-left:4px;"
                combo_ss = "QComboBox { font-size:12px; padding:2px 4px; background: transparent; border: none; color: #0f172a; }"
            elif self._theme_mode == 1:
                ss = "QFrame#card { background: #334155; border: 1px solid #475569; border-radius: 6px; padding: 2px 4px; }"
                lbl_ss = "font-size:10px; color:#94a3b8; padding-left:4px;"
                combo_ss = "QComboBox { font-size:12px; padding:2px 4px; background: transparent; border: none; color: #f8fafc; }"
            else:
                ss = "QFrame#card { background: #333333; border: 2px solid #555555; border-radius: 6px; padding: 2px 4px; }"
                lbl_ss = "font-size:10px; color:#cccccc; padding-left:4px;"
                combo_ss = "QComboBox { font-size:12px; padding:2px 4px; background: transparent; border: none; color: #ffffff; }"
            for f in self._group_frames:
                f.setStyleSheet(ss)
            self._view_group_label.setStyleSheet(lbl_ss)
            self._acciones_label.setStyleSheet(lbl_ss)
            self._exportar_label.setStyleSheet(lbl_ss)
            self.view_combo.setStyleSheet(combo_ss)

    def _toggle_theme(self):
        """Cambia al siguiente tema (modo 0→1→2→0)."""
        self._theme_mode = (self._theme_mode + 1) % 3
        self._apply_theme()

    # ── Construcción de la interfaz ──────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)

        # Header bar
        self.header_bar = QFrame()
        self.header_bar.setFixedHeight(40)
        hdr_lay = QHBoxLayout(self.header_bar)
        hdr_lay.setContentsMargins(20, 0, 20, 0)

        title = QLabel("📋  Generador Cuadrante Tareas Profesorado")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(title)

        hdr_lay.addStretch()

        self.help_btn = QPushButton("📖 Ayuda")
        self.help_btn.setFixedSize(90, 30)
        self.help_btn.setToolTip("Abrir manual de usuario detallado (F1)")
        self.help_btn.setStyleSheet("background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 4px;")
        self.help_btn.clicked.connect(self._open_manual)
        hdr_lay.addWidget(self.help_btn)

        self.theme_btn = QPushButton("☀️ Claro")
        self.theme_btn.setFixedSize(100, 30)
        self.theme_btn.setToolTip("Cambiar entre tema claro, oscuro y alto contraste (♿)")
        self.theme_btn.setStyleSheet("background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 4px;")
        self.theme_btn.clicked.connect(self._toggle_theme)
        hdr_lay.addWidget(self.theme_btn)

        main_v.addWidget(self.header_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        main_v.addWidget(self.tabs)

        self._build_project_tab()
        self._build_teachers_tab()
        self._build_needs_tab()
        self._build_generate_tab()
        self._build_schedule_tab()

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet(
            f"QStatusBar {{ background: {C_SLATE}; color: white; font-size: 11px; padding: 0 12px; }} "
            f"QStatusBar::item {{ border: none; }} "
        )
        self.status_bar.showMessage("💡 F1 Ayuda  ·  Ctrl+D Datos ejemplo  ·  Ctrl+S Guardar  ·  Ctrl+Z Deshacer  ·  Ctrl+Y Rehacer")
        main_v.addWidget(self.status_bar)

        # Toast overlay
        self.toast = Toast(self)

    def _tab_widget(self, scroll=True):
        """Crea un contenedor para pestaña, opcionalmente con scroll."""
        w = QWidget()
        w.setObjectName("tab_content")
        if scroll:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(w)
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            scroll_area.viewport().setAutoFillBackground(False)
            return scroll_area, w
        return w, w

    # ── Pestaña: Proyecto ────────────────────────────────────────────
    def _build_project_tab(self):
        """Construye la pestaña de inicio: selector de proyectos, estadísticas y acciones principales."""
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "🏠 Proyecto")
        v = QVBoxLayout(tab)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        # Heading
        # Selector row
        sel = QHBoxLayout()
        sel.setSpacing(6)
        self.project_selector = QComboBox()
        self.project_selector.setMinimumWidth(300)
        self.project_selector.setToolTip("Selecciona un proyecto guardado para cargarlo")
        self.project_selector.currentTextChanged.connect(self._on_project_selected)
        sel.addWidget(self.project_selector)

        def btn(text, tip, cmd, color=None):
            b = QPushButton(text)
            b.setToolTip(tip)
            b.clicked.connect(cmd)
            if color: b.setObjectName(color)
            sel.addWidget(b)
            return b
        btn("➕ Nuevo", "Crear un proyecto nuevo en blanco", self._new_project, "secondary")
        btn("📋 Duplicar", "Hacer una copia del proyecto actual", self._duplicate_project, "secondary")
        btn("💾 Guardar", "Guardar el proyecto actual (Ctrl+S)", self._save_current)
        btn("🗑️ Eliminar", "Eliminar el proyecto seleccionado permanentemente", self._delete_project, "secondary")
        sel.addStretch()
        v.addLayout(sel)

        v.addWidget(QLabel("📛 Nombre del proyecto:"))
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("P.ej.: XarxaLlibres 2026, Recogida septiembre, Apoyo exámenes...")
        self.project_name_input.setToolTip("Nombre descriptivo del proyecto. Se usará como nombre de archivo.")
        self.project_name_input.textChanged.connect(lambda: self._mark_dirty())
        v.addWidget(self.project_name_input)

        # Stats
        stats = QHBoxLayout()
        stats.setSpacing(6)
        self.info_teachers = QLabel("👨‍🏫 0 profesores")
        self.info_teachers.setToolTip("Número total de profesores registrados (compartidos entre proyectos)")
        self.info_teachers.setStyleSheet(f"font-weight: bold; color: {C_PRI};")
        self.info_needs = QLabel("📋 0 necesidades")
        self.info_needs.setToolTip("Número total de tareas/necesidades de apoyo en este proyecto")
        self.info_slots = QLabel("🗓 0 franjas profe")
        self.info_slots.setToolTip("Suma de todas las franjas de disponibilidad de todos los profesores")
        self.info_need_slots = QLabel("📅 0 franjas neces.")
        self.info_need_slots.setToolTip("Número de necesidades (tareas) en este proyecto")
        self.info_hours = QLabel("⏱ 0h disponibles")
        self.info_hours.setToolTip("Total de horas disponibles sumando todas las franjas de todos los profes")
        self.info_need_hours = QLabel("⏰ 0h necesarias (min)")
        self.info_need_hours.setToolTip("Horas mínimas necesarias (min × duración de cada necesidad)")
        for lbl in [self.info_teachers, self.info_needs, self.info_slots, self.info_need_slots, self.info_hours, self.info_need_hours]:
            stats.addWidget(lbl)
            stats.addSpacing(8)
        stats.addStretch()
        v.addLayout(stats)

        bf = QHBoxLayout()
        bf.setSpacing(6)
        btn("📦 Cargar datos ficticios", "Carga 15 profesores de ejemplo y 50 necesidades para probar", self._load_seed, "secondary")
        btn_imp_proj = QPushButton("📥 Importar proyecto...")
        btn_imp_proj.setToolTip("Importar proyecto completo desde archivo JSON (profesores + necesidades)")
        btn_imp_proj.setObjectName("secondary")
        btn_imp_proj.clicked.connect(self._import_project)
        bf.addWidget(btn_imp_proj)
        btn_exp_proj = QPushButton("📤 Exportar proyecto")
        btn_exp_proj.setToolTip("Exportar proyecto actual a archivo JSON (incluye profesores y necesidades)")
        btn_exp_proj.setObjectName("secondary")
        btn_exp_proj.clicked.connect(self._export_project)
        bf.addWidget(btn_exp_proj)
        btn_csv = QPushButton("📊 Exportar CSV")
        btn_csv.setToolTip("Exportar asignaciones a CSV para abrir en Excel/LibreOffice")
        btn_csv.setObjectName("secondary")
        btn_csv.clicked.connect(self._export_csv)
        bf.addWidget(btn_csv)
        btn_undo = QPushButton("↩️ Deshacer")
        btn_undo.setObjectName("secondary")
        btn_undo.setToolTip("Deshacer último cambio (Ctrl+Z)")
        btn_undo.clicked.connect(self._undo)
        bf.addWidget(btn_undo)
        btn_redo = QPushButton("🔁 Rehacer")
        btn_redo.setObjectName("secondary")
        btn_redo.setToolTip("Rehacer cambio deshecho (Ctrl+Y)")
        btn_redo.clicked.connect(self._redo)
        bf.addWidget(btn_redo)
        self._dirty_label = QLabel("")
        self._dirty_label.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px;")
        self._dirty_label.setToolTip("Hay cambios sin guardar — pulsa 💾 Guardar o espera al auto-guardado (cada 2 min)")
        bf.addWidget(self._dirty_label)
        bf.addStretch()
        v.addLayout(bf)

        v.addWidget(self._sep())

        # Workflow
        v.addWidget(QLabel("💡 Flujo de trabajo — pasos:"))
        info = QLabel(
            "1. 👨‍🏫 Gestiona los profesores con sus horarios — datos compartidos entre proyectos\n"
            "2. 🏠 Crea un proyecto o selecciona uno existente\n"
            "3. 📋 Añade necesidades de apoyo con fecha/hora y mínimo/máximo de profesores\n"
             "4. ⚙️ Genera el cuadrante — el solver CP-SAT genera varias opciones y tú eliges la mejor\n"
            "5. 📅 Abre el HTML, copia los correos e imprime como PDF"
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {C_TEXT2}; padding: 8px;")
        v.addWidget(info)
        v.addStretch()

    # ── Pestaña: Profesores ──────────────────────────────────────────
    def _build_teachers_tab(self):
        """Construye la pestaña de gestión de profesores: formulario de alta, lista, franjas de disponibilidad."""
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "👨‍🏫 Profes")
        v = QVBoxLayout(tab)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        hint = QLabel("💡 Los profesores se guardan automáticamente y se comparten entre todos los proyectos")
        hint.setStyleSheet(f"color: {C_SLATE}; padding: 4px 0;")
        hint.setToolTip("Los datos de profesores se almacenan en teachers.json y están disponibles siempre")
        v.addWidget(hint)

        ie_teachers = QHBoxLayout()
        ie_teachers.setSpacing(6)
        btn_imp_t = QPushButton("📥 Importar profesores...")
        btn_imp_t.setToolTip("Cargar profesores desde un archivo JSON (formato: array de objetos profesor)")
        btn_imp_t.setObjectName("secondary")
        btn_imp_t.clicked.connect(self._import_teachers)
        ie_teachers.addWidget(btn_imp_t)
        btn_exp_t = QPushButton("📤 Exportar profesores")
        btn_exp_t.setToolTip("Guardar todos los profesores en un archivo JSON")
        btn_exp_t.setObjectName("secondary")
        btn_exp_t.clicked.connect(self._export_teachers)
        ie_teachers.addWidget(btn_exp_t)
        ie_teachers.addStretch()
        v.addLayout(ie_teachers)

        # Add teacher form
        f = QHBoxLayout()
        f.setSpacing(4)
        f.addWidget(QLabel("👤 Nombre:"))
        self.t_name = QLineEdit()
        self.t_name.setPlaceholderText("P.ej.: Ana Alumnez, Carlos Pérez...")
        self.t_name.setToolTip("Nombre completo del profesor (único, no puede repetirse)")
        f.addWidget(self.t_name)
        f.addSpacing(4)
        f.addWidget(QLabel("⏱ Max tot:"))
        self.t_max = QLineEdit("20")
        self.t_max.setFixedWidth(40)
        self.t_max.setToolTip("Horas totales semanales que puede trabajar este profesor")
        f.addWidget(self.t_max)
        f.addSpacing(4)
        f.addWidget(QLabel("Max/día:"))
        self.t_maxd = QLineEdit("6")
        self.t_maxd.setFixedWidth(36)
        self.t_maxd.setToolTip("Horas máximas que puede trabajar en un solo día")
        f.addWidget(self.t_maxd)
        f.addSpacing(4)
        f.addWidget(QLabel("Turno:"))
        self.t_turno = QComboBox()
        self.t_turno.addItems(["Cualquiera", "Mañana", "Tarde"])
        self.t_turno.setFixedWidth(100)
        self.t_turno.setToolTip("Preferencia de turno: el solver prioriza asignar en este horario")
        f.addWidget(self.t_turno)
        f.addSpacing(4)
        f.addWidget(QLabel("📧 Email:"))
        self.t_email = QLineEdit()
        self.t_email.setPlaceholderText("profe@ies.edu")
        self.t_email.setFixedWidth(140)
        self.t_email.setToolTip("Correo electrónico del profesor (opcional, se usa en exportación ICS)")
        f.addWidget(self.t_email)
        f.addSpacing(4)
        self.t_color_btn = QPushButton("🎨")
        self.t_color_btn.setFixedWidth(32)
        self.t_color_btn.setToolTip("Elegir color personalizado para identificar al profesor en el cuadrante")
        self.t_color_btn.clicked.connect(self._pick_teacher_color)
        f.addWidget(self.t_color_btn)
        self._teacher_color_pick = C_PRI
        f.addSpacing(4)
        btn = QPushButton("➕ Añadir profe")
        btn.setToolTip("Dar de alta al profesor con los datos indicados")
        btn.clicked.connect(self._add_teacher)
        f.addWidget(btn)
        f.addStretch()
        v.addLayout(f)

        search_teach = QHBoxLayout()
        self.teacher_count = QLabel("0 profesores")
        self.teacher_count.setToolTip("Número de profesores visibles (con filtro aplicado)")
        self.teacher_count.setStyleSheet("font-weight: bold; font-size: 13px;")
        search_teach.addWidget(self.teacher_count)
        search_teach.addSpacing(8)
        self.teacher_slot_filter = QComboBox()
        self.teacher_slot_filter.addItems(["🗓 Todos", "🗓 Con franjas", "🗓 Sin franjas"])
        self.teacher_slot_filter.setFixedWidth(130)
        self.teacher_slot_filter.setToolTip("Filtrar profesores por si tienen franjas de disponibilidad o no")
        self.teacher_slot_filter.currentIndexChanged.connect(self._rebuild_teacher_list)
        search_teach.addWidget(self.teacher_slot_filter)
        search_teach.addStretch()
        self.teacher_search = QLineEdit()
        self.teacher_search.setPlaceholderText("🔍 Filtrar por nombre...")
        self.teacher_search.setToolTip("Escribe para filtrar la lista de profesores por nombre")
        self.teacher_search.setMinimumWidth(240)
        self.teacher_search.textChanged.connect(self._rebuild_teacher_list)
        search_teach.addWidget(self.teacher_search)
        v.addLayout(search_teach)

        self.teacher_scroll = QScrollArea()
        self.teacher_scroll.setWidgetResizable(True)
        self.teacher_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.teacher_container = QWidget()
        self.teacher_list_layout = QVBoxLayout(self.teacher_container)
        self.teacher_list_layout.setSpacing(3)
        self.teacher_list_layout.setContentsMargins(0, 0, 0, 0)
        self.teacher_list_layout.addStretch()
        self.teacher_scroll.setWidget(self.teacher_container)
        v.addWidget(self.teacher_scroll, 2)

        v.addWidget(self._sep())

        # ── Slot header + quick-add bar ──
        slot_top = QHBoxLayout()
        self.tslot_header = QLabel("📅 Franjas: (ningún profe)")
        self.tslot_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        slot_top.addWidget(self.tslot_header)
        slot_top.addStretch()
        tslot_hint = QLabel("💡 Selecciona un profe de la lista para gestionar sus franjas")
        tslot_hint.setStyleSheet(f"color: {C_SLATE}; font-size: 11px;")
        slot_top.addWidget(tslot_hint)
        v.addLayout(slot_top)

        # ── Add buttons (2 filas) ──
        presets1 = QHBoxLayout()
        presets1.setSpacing(6)
        presets1.addWidget(QLabel("📅 Fecha:"))
        self.tslot_date = QDateEdit()
        self.tslot_date.setCalendarPopup(True)
        self.tslot_date.setDisplayFormat("yyyy-MM-dd")
        self.tslot_date.setToolTip("Elige la fecha para la franja de disponibilidad")
        self.tslot_date.setDate(QDate(2026, 6, 22))
        presets1.addWidget(self.tslot_date)
        add_custom = QPushButton("➕ Personalitzada")
        add_custom.setToolTip("Añadir una franja con horario personalizado (cualquier hora de inicio y fin)")
        add_custom.clicked.connect(self._add_tslot_custom_dialog)
        presets1.addWidget(add_custom)
        for lbl, tip, s, e in [("☕ Mañana 09-14h", "Franja de mañana: de 09:00 a 14:00", "09:00", "14:00"),
                          ("🌤 Tarde 15-18h", "Franja de tarde: de 15:00 a 18:00", "15:00", "18:00"),
                          ("🌞 Completo 09-18h", "Franja completa: de 09:00 a 18:00", "09:00", "18:00")]:
            b = QPushButton(lbl)
            b.setToolTip(tip)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda checked, ss=s, ee=e: self._add_tslot_preset(ss, ee))
            presets1.addWidget(b)
        grid_btn = QPushButton("📅 Rejilla semanal")
        grid_btn.setToolTip("Abrir rejilla semanal: marca días y turnos con un clic")
        grid_btn.setObjectName("secondary")
        grid_btn.clicked.connect(self._weekly_grid_dialog)
        presets1.addWidget(grid_btn)
        presets1.addStretch()
        v.addLayout(presets1)

        presets2 = QHBoxLayout()
        presets2.setSpacing(6)
        btn_save_t = QPushButton("💾 Guardar plantilla")
        btn_save_t.setToolTip("Guardar las franjas del profesor actual como plantilla reutilizable")
        btn_save_t.setObjectName("secondary")
        btn_save_t.clicked.connect(self._save_tslot_template)
        presets2.addWidget(btn_save_t)
        btn_load_t = QPushButton("📂 Cargar plantilla")
        btn_load_t.setToolTip("Cargar una plantilla guardada para asignar sus franjas al profesor actual")
        btn_load_t.setObjectName("secondary")
        btn_load_t.clicked.connect(self._load_tslot_template)
        presets2.addWidget(btn_load_t)
        copy_sched_btn = QPushButton("👥 Copiar horario")
        copy_sched_btn.setToolTip("Copiar las franjas de otro profesor al profesor seleccionado")
        copy_sched_btn.setObjectName("secondary")
        copy_sched_btn.clicked.connect(self._copy_schedule_dialog)
        presets2.addWidget(copy_sched_btn)
        dup_slots_btn = QPushButton("📋 Duplicar franjas a otro día")
        dup_slots_btn.setToolTip("Copiar todas las franjas de una fecha a otra fecha para este profesor")
        dup_slots_btn.setObjectName("secondary")
        dup_slots_btn.clicked.connect(self._duplicate_slots_to_day)
        presets2.addWidget(dup_slots_btn)
        dup_all_btn = QPushButton("📋 Duplicar franjas a todos")
        dup_all_btn.setToolTip("Copiar las franjas de una fecha a otra para TODOS los profesores")
        dup_all_btn.setObjectName("secondary")
        dup_all_btn.clicked.connect(self._duplicate_slots_all_teachers)
        presets2.addWidget(dup_all_btn)
        presets2.addStretch()
        v.addLayout(presets2)

        self.tslot_scroll = QScrollArea()
        self.tslot_scroll.setWidgetResizable(True)
        self.tslot_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tslot_container = QWidget()
        self.tslot_layout = QVBoxLayout(self.tslot_container)
        self.tslot_layout.setSpacing(2)
        self.tslot_layout.setContentsMargins(0, 0, 0, 0)
        self.tslot_layout.addStretch()
        self.tslot_scroll.setWidget(self.tslot_container)
        v.addWidget(self.tslot_scroll, 3)

    # ── Pestaña: Necesidades (tareas) ────────────────────────────────
    def _build_needs_tab(self):
        """Construye la pestaña de necesidades: formulario de alta, lista con filtros y acciones."""
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "📋 Necesidades")
        v = QVBoxLayout(tab)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        ie_needs = QHBoxLayout()
        ie_needs.setSpacing(6)
        btn_imp_n = QPushButton("📥 Importar necesidades...")
        btn_imp_n.setToolTip("Cargar necesidades desde un archivo JSON (formato: array de objetos necesidad)")
        btn_imp_n.setObjectName("secondary")
        btn_imp_n.clicked.connect(self._import_needs)
        ie_needs.addWidget(btn_imp_n)
        btn_exp_n = QPushButton("📤 Exportar necesidades")
        btn_exp_n.setToolTip("Guardar las necesidades actuales en un archivo JSON")
        btn_exp_n.setObjectName("secondary")
        btn_exp_n.clicked.connect(self._export_needs)
        ie_needs.addWidget(btn_exp_n)
        ie_needs.addStretch()
        v.addLayout(ie_needs)

        f = QHBoxLayout()
        f.setSpacing(4)
        f.addWidget(QLabel("📝 Nombre:"))
        self.nd_name = QLineEdit()
        self.nd_name.setPlaceholderText("P.ej.: Recogida 1º ESO A, Apoyo matemáticas...")
        self.nd_name.setToolTip("Nombre descriptivo de la tarea o necesidad de apoyo")
        self.nd_name.setFixedWidth(200)
        f.addWidget(self.nd_name)
        f.addSpacing(4)
        f.addWidget(QLabel("📅 Fecha:"))
        self.nd_date = QDateEdit()
        self.nd_date.setCalendarPopup(True)
        self.nd_date.setDisplayFormat("yyyy-MM-dd")
        self.nd_date.setDate(QDate(2026, 6, 22))
        self.nd_date.setFixedWidth(120)
        self.nd_date.setToolTip("Fecha en que se necesita cubrir esta tarea")
        f.addWidget(self.nd_date)
        f.addSpacing(4)
        f.addWidget(QLabel("🕐 Inicio:"))
        self.nd_start = QLineEdit("09:00")
        self.nd_start.setFixedWidth(50)
        self.nd_start.setToolTip("Hora de inicio (formato HH:MM, 24h)")
        self.nd_start.setPlaceholderText("HH:MM")
        f.addWidget(self.nd_start)
        f.addSpacing(4)
        f.addWidget(QLabel("🕐 Fin:"))
        self.nd_end = QLineEdit("11:00")
        self.nd_end.setFixedWidth(50)
        self.nd_end.setToolTip("Hora de fin (formato HH:MM, 24h — debe ser posterior a Inicio)")
        self.nd_end.setPlaceholderText("HH:MM")
        f.addWidget(self.nd_end)
        f.addSpacing(4)
        f.addWidget(QLabel("👤 Min:"))
        self.nd_min = QLineEdit("2")
        self.nd_min.setFixedWidth(36)
        self.nd_min.setToolTip("Número mínimo de profesores que necesita esta tarea (≥ 1)")
        f.addWidget(self.nd_min)
        f.addSpacing(4)
        f.addWidget(QLabel("👤 Max:"))
        self.nd_max = QLineEdit("4")
        self.nd_max.setFixedWidth(36)
        self.nd_max.setToolTip("Número máximo de profesores que pueden asignarse a esta tarea")
        f.addWidget(self.nd_max)
        f.addSpacing(6)
        self.nd_tags = QLineEdit()
        self.nd_tags.setPlaceholderText("🏷️ etiquetas")
        self.nd_tags.setFixedWidth(120)
        self.nd_tags.setToolTip("Etiquetas separadas por coma (ej: mañana, 1ºESO, urgencia)")
        f.addWidget(self.nd_tags)
        f.addSpacing(4)
        b = QPushButton("➕➕ Añadir necesidad")
        b.setToolTip("Añadir esta tarea a la lista de necesidades del proyecto")
        b.clicked.connect(self._add_need)
        f.addWidget(b)
        f.addStretch()
        v.addLayout(f)

        search_needs = QHBoxLayout()
        self.need_count = QLabel("📋 0 necesidades")
        self.need_count.setToolTip("Número de necesidades visibles (con filtro aplicado)")
        self.need_count.setStyleSheet("font-weight: bold;")
        search_needs.addWidget(self.need_count)
        dup_needs_day_btn = QPushButton("📋 Duplicar necesidades a otro día")
        dup_needs_day_btn.setToolTip("Copiar todas las necesidades de una fecha a otra (incluyendo etiquetas)")
        dup_needs_day_btn.setObjectName("secondary")
        dup_needs_day_btn.clicked.connect(self._duplicate_needs_to_day)
        search_needs.addWidget(dup_needs_day_btn)
        search_needs.addStretch()
        self.need_search = QLineEdit()
        self.need_search.setPlaceholderText("🔍 Filtrar por nombre, fecha o etiqueta...")
        self.need_search.setToolTip("Escribe para filtrar la lista de necesidades por nombre, fecha o etiqueta")
        self.need_search.setFixedWidth(220)
        self.need_search.textChanged.connect(self._rebuild_need_list)
        search_needs.addWidget(self.need_search)
        v.addLayout(search_needs)

        self.need_scroll = QScrollArea()
        self.need_scroll.setWidgetResizable(True)
        self.need_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.need_container = QWidget()
        self.need_layout = QVBoxLayout(self.need_container)
        self.need_layout.setSpacing(2)
        self.need_layout.setContentsMargins(0, 0, 0, 0)
        self.need_layout.addStretch()
        self.need_scroll.setWidget(self.need_container)
        v.addWidget(self.need_scroll, 1)

    # ── Pestaña: Generar ─────────────────────────────────────────────
    def _build_generate_tab(self):
        """Construye la pestaña de generación: resumen, botón de generar y panel de log."""
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "⚙️ Generar")
        v = QVBoxLayout(tab)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        v.addWidget(QLabel("⚙️ Generar cuadrante de apoyo"))

        info_multi = QLabel(
            "🧠 El solver genera varias opciones distintas (variando la semilla de búsqueda).\n"
            "Una vez generadas, cambia entre ellas libremente desde la pestaña 📅 Cuadrante."
        )
        info_multi.setWordWrap(True)
        info_multi.setStyleSheet(f"color: {C_TEXT2}; background: #eef2ff; border: 1px solid {C_PRI_L}; border-radius: 6px; padding: 8px 12px;")
        v.addWidget(info_multi)

        self.gen_summary = QLabel("")
        self.gen_summary.setToolTip("Resumen de profesores, necesidades y horas disponibles")
        self.gen_summary.setStyleSheet(f"color: {C_SLATE};")
        v.addWidget(self.gen_summary)

        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("🔢 Opciones a generar:"))
        self._n_options_spin = QSpinBox()
        self._n_options_spin.setRange(1, 50)
        self._n_options_spin.setValue(5)
        self._n_options_spin.setToolTip("Número de opciones de cuadrante a generar (1-50).\nMás opciones = más variedad, pero tarda más tiempo.")
        opt_row.addWidget(self._n_options_spin)
        opt_row.addWidget(QLabel("(1-50)"))
        opt_row.addStretch()
        v.addLayout(opt_row)

        gen_btn = QPushButton("🚀 Generar Cuadrante")
        gen_btn.setToolTip("Iniciar el proceso de generación. El solver calculará el número de opciones indicado.\nPuede tardar varios minutos con 15 profesores y 50 necesidades.")
        gen_btn.setMinimumHeight(50)
        gen_btn.setStyleSheet(f"font-size: 18px; font-weight: bold; background: {C_PRI}; color: white; border-radius: 8px;")
        gen_btn.clicked.connect(self._generate)
        v.addWidget(gen_btn)

        v.addWidget(QLabel("📜 Log:"), alignment=Qt.AlignmentFlag.AlignBottom)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(200)
        self.status_text.setToolTip("Registro detallado del proceso de generación. Muestra asignaciones, tiempos y posibles errores.")
        self.status_text.append("🚀  GENERADOR CUADRANTE — Panel de log\n")
        self.status_text.append("📌  1. Define profesores con franjas en 👨‍🏫 Profes")
        self.status_text.append("📌  2. Crea necesidades en 📋 Necesidades")
        self.status_text.append("📌  3. Vuelve aquí y pulsa 🚀 Generar Cuadrante")
        self.status_text.append("📌  4. El solver generará las opciones que verás en 📅 Cuadrante")
        self.status_text.append("")
        v.addWidget(self.status_text, 1)

    # ── Pestaña: Cuadrante ───────────────────────────────────────────
    def _build_schedule_tab(self):
        """Construye la pestaña del cuadrante: toolbar, navegación entre opciones y vista de asignaciones."""
        w, tab = self._tab_widget(False)
        self.tabs.addTab(w, "📅 Cuadrante")
        v = QVBoxLayout(tab)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        # ── Toolbar: fila 1 — botones de acción ──
        tb1 = QHBoxLayout()
        tb1.setSpacing(6)

        # Helper para crear grupos con supertítulo
        def _make_group(label):
            w = QVBoxLayout()
            w.setSpacing(1)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size:10px; padding-left:4px;")
            w.addWidget(lbl)
            f = QFrame()
            f.setObjectName("card")
            f.setStyleSheet("QFrame#card { border-radius: 6px; padding: 2px 4px; }")
            lay = QHBoxLayout(f)
            lay.setContentsMargins(6, 2, 6, 2)
            lay.setSpacing(4)
            w.addWidget(f)
            return w, f, lay, lbl

        # ── Grupo: Generar HTML ──
        vg_w, vg_f, vg_lay, self._view_group_label = _make_group("Generar HTML")
        self._view_group_frame = vg_f
        self._group_frames = [vg_f]
        self.open_btn = QPushButton("🌐 Generar HTML")
        self.open_btn.setObjectName("cta")
        self.open_btn.setToolTip("Generar el HTML del cuadrante y abrirlo en el navegador")
        self.open_btn.clicked.connect(self._open_html)
        self.open_btn.setEnabled(False)
        vg_lay.addWidget(self.open_btn)
        self.view_combo = QComboBox()
        self.view_combo.setToolTip("Elige qué vista mostrar al abrir el navegador: cuadrante, por profesor, por tarea, estilo Word, o para imprimir")
        self.view_combo.addItems(["📅 Cuadrante", "👤 Por profesor", "📋 Por tarea", "📄 Estilo Word", "🖨️ Para imprimir"])
        self.view_combo.setCurrentIndex(4)
        self.view_combo.setStyleSheet("QComboBox { font-size:12px; padding:2px 4px; background: transparent; border: none; }")
        self.view_combo.setEnabled(False)
        vg_lay.addWidget(self.view_combo)
        tb1.addLayout(vg_w)

        # ── Grupo: Acciones ──
        ac_w, ac_f, ac_lay, self._acciones_label = _make_group("Acciones")
        self._group_frames.append(ac_f)
        self.lock_regenerate_btn = QPushButton("🔒 Regenerar Bloqueos")
        self.lock_regenerate_btn.setObjectName("cta")
        self.lock_regenerate_btn.setToolTip("Regenerar el cuadrante manteniendo fijas las asignaciones bloqueadas\n(bloquea haciendo clic en un profesor del cuadrante)")
        self.lock_regenerate_btn.clicked.connect(self._regenerate_with_locks)
        self.lock_regenerate_btn.setEnabled(False)
        ac_lay.addWidget(self.lock_regenerate_btn)
        self.dup_day_btn = QPushButton("📋 Duplicar día")
        self.dup_day_btn.setObjectName("cta")
        self.dup_day_btn.setToolTip("Copiar todas las necesidades y asignaciones de un día a otro, incluyendo las asignaciones actuales")
        self.dup_day_btn.clicked.connect(self._duplicate_day_from_schedule)
        self.dup_day_btn.setEnabled(False)
        ac_lay.addWidget(self.dup_day_btn)
        self.open_folder_btn = QPushButton("📂 Carpeta")
        self.open_folder_btn.setToolTip("Abrir la carpeta donde se guardan los archivos HTML generados")
        self.open_folder_btn.setObjectName("secondary")
        self.open_folder_btn.clicked.connect(self._open_folder)
        self.open_folder_btn.setEnabled(False)
        ac_lay.addWidget(self.open_folder_btn)
        self.stats_btn = QPushButton("📊 Stats")
        self.stats_btn.setToolTip("Ver estadísticas detalladas: carga por profesor, cobertura, horas totales")
        self.stats_btn.setObjectName("secondary")
        self.stats_btn.clicked.connect(self._show_stats)
        self.stats_btn.setEnabled(False)
        ac_lay.addWidget(self.stats_btn)
        self.compact_btn = QPushButton("📅 Compacta")
        self.compact_btn.setToolTip("Alternar entre vista normal (columnas separadas) y compacta (una sola columna)")
        self.compact_btn.setObjectName("secondary")
        self.compact_btn.clicked.connect(self._toggle_compact_view)
        self.compact_btn.setEnabled(False)
        ac_lay.addWidget(self.compact_btn)
        tb1.addLayout(ac_w)

        # ── Grupo: Exportar ──
        ex_w, ex_f, ex_lay, self._exportar_label = _make_group("Exportar")
        self._group_frames.append(ex_f)
        self.docx_btn = QPushButton("📄 DOCX")
        self.docx_btn.setObjectName("cta")
        self.docx_btn.setToolTip("Exportar el cuadrante como documento Word (formato DOC)")
        self.docx_btn.clicked.connect(self._export_docx)
        self.docx_btn.setEnabled(False)
        ex_lay.addWidget(self.docx_btn)
        self.ics_btn = QPushButton("📅 Calendario ICS")
        self.ics_btn.setToolTip("Exportar asignaciones como archivo ICS (Google Calendar, Outlook)")
        self.ics_btn.setObjectName("secondary")
        self.ics_btn.clicked.connect(self._export_ics)
        self.ics_btn.setEnabled(False)
        ex_lay.addWidget(self.ics_btn)
        self.md_btn = QPushButton("📝 MD")
        self.md_btn.setToolTip("Exportar el cuadrante como Markdown (tablas por día)")
        self.md_btn.setObjectName("secondary")
        self.md_btn.clicked.connect(self._export_md)
        self.md_btn.setEnabled(False)
        ex_lay.addWidget(self.md_btn)
        tb1.addLayout(ex_w)

        tb1.addStretch()
        v.addLayout(tb1)

        # ── Toolbar: fila 2 — navegación ──
        tb2 = QHBoxLayout()
        tb2.setSpacing(6)
        self.nav_prev_btn = QPushButton("◀")
        self.nav_prev_btn.setToolTip("Ver opción anterior")
        self.nav_prev_btn.setFixedWidth(36)
        self.nav_prev_btn.setFixedHeight(30)
        self.nav_prev_btn.setStyleSheet("font-size: 18px; padding: 0;")
        self.nav_prev_btn.setObjectName("secondary")
        self.nav_prev_btn.clicked.connect(self._prev_option)
        self.nav_prev_btn.setEnabled(False)
        tb2.addWidget(self.nav_prev_btn)

        self.nav_label = QLabel("")
        self.nav_label.setToolTip("Opción actual y número total de opciones generadas")
        self.nav_label.setStyleSheet(f"font-weight: bold; color: {C_PRI}; font-size: 13px;")
        tb2.addWidget(self.nav_label)

        self.nav_next_btn = QPushButton("▶")
        self.nav_next_btn.setToolTip("Ver opción siguiente")
        self.nav_next_btn.setFixedWidth(36)
        self.nav_next_btn.setFixedHeight(30)
        self.nav_next_btn.setStyleSheet("font-size: 18px; padding: 0;")
        self.nav_next_btn.setObjectName("secondary")
        self.nav_next_btn.clicked.connect(self._next_option)
        self.nav_next_btn.setEnabled(False)
        tb2.addWidget(self.nav_next_btn)

        self.clear_opts_btn = QPushButton("❌")
        self.clear_opts_btn.setToolTip("Eliminar todas las opciones generadas y limpiar el cuadrante")
        self.clear_opts_btn.setObjectName("danger")
        self.clear_opts_btn.setFixedWidth(28)
        self.clear_opts_btn.clicked.connect(self._clear_solutions)
        self.clear_opts_btn.setEnabled(False)
        tb2.addWidget(self.clear_opts_btn)

        tb2.addStretch()

        self.cal_summary = QLabel("")
        self.cal_summary.setToolTip("Resumen del cuadrante actual: necesidades, cobertura y asignaciones")
        self.cal_summary.setStyleSheet(f"color: {C_SLATE};")
        tb2.addWidget(self.cal_summary)
        v.addLayout(tb2)

        self.cal_scroll = QScrollArea()
        self.cal_scroll.setWidgetResizable(True)
        self.cal_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cal_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.cal_container = QWidget()
        self.cal_layout = QVBoxLayout(self.cal_container)
        self.cal_layout.setContentsMargins(0, 0, 0, 0)
        self.cal_scroll.setWidget(self.cal_container)
        v.addWidget(self.cal_scroll, 1)

        empty = QLabel(
            "📭 Aún no hay cuadrante generado.\n\n"
            "1. Asegúrate de tener 👨‍🏫 profesores con franjas de disponibilidad\n"
            "2. Define 📋 necesidades en este proyecto\n"
            "3. Ve a ⚙️ Generar y pulsa 🚀 Generar Cuadrante\n\n"
            "💡 O carga datos ficticios desde la pestaña 🏠 Proyecto para probar"
        )
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setWordWrap(True)
        empty.setStyleSheet(f"color: {C_SLATE}; font-size: 13px; padding: 20px;")
        self.cal_layout.addWidget(empty)

    # ── Helpers ────────────────────────────────────────────────────────
    def _status(self, msg, timeout=5000):
        """Muestra un mensaje temporal en la barra de estado inferior."""
        self.status_bar.showMessage(msg)
        self._status_timer.stop()
        self._status_timer.setInterval(timeout)
        self._status_timer.start()

    def _make_icon(self):
        """Genera un icono simple con las letras 'CT' para la ventana."""
        px = QPixmap(64, 64)
        px.fill(QColor(C_PRI))
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("#fff"))
        f = QFont("Segoe UI", 28)
        f.setBold(True)
        p.setFont(f)
        p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "CT")
        p.end()
        return QIcon(px)

    def _open_manual(self):
        """Abre el manual de usuario en el navegador web predeterminado."""
        manual_path = os.path.join(BASE_DIR, "manual", "index.html")
        if os.path.exists(manual_path):
            webbrowser.open(f"file://{os.path.abspath(manual_path)}")
            self._status("📖 Manual abierto en el navegador")
        else:
            self.toast.show("Manual no encontrado en manual/index.html", "error")

    def _show_welcome(self):
        """Muestra el diálogo de bienvenida con instrucciones rápidas para el usuario novel."""
        d = QDialog(self)
        d.setWindowTitle("🎉 ¡Bienvenido al Generador Cuadrante!")
        d.setMinimumSize(560, 460)
        d.setModal(True)
        v = QVBoxLayout(d)
        v.setSpacing(12)
        v.setContentsMargins(24, 20, 24, 20)

        title = QLabel("🎉 ¡Bienvenido al Generador Cuadrante Tareas!")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {C_PRI};")
        v.addWidget(title)

        desc = QLabel(
            "Esta aplicación te permite asignar profesores a tareas de apoyo\n"
            "de forma óptima usando inteligencia artificial (CP-SAT).\n\n"
            "Aquí tienes las pestañas principales:"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {C_TEXT2}; font-size: 13px;")
        v.addWidget(desc)

        steps = [
            ("👨‍🏫  Profes", "Gestiona profesores, horarios y disponibilidad.\n"
             "Los datos se guardan automáticamente y se comparten entre proyectos."),
            ("🏠  Proyecto", "Crea un proyecto, añade necesidades con fechas.\n"
             "Usa el botón «📦 Cargar datos ficticios» para probar con datos de ejemplo."),
            ("⚙️  Generar",              "Pulsa el botón grande y el solver CP-SAT genera varias opciones distintas.\n"
             "Puede tardar hasta 2 minutos — un spinner animado te indica que está trabajando."),
            ("📅  Cuadrante", "Navega entre opciones con ◀ ▶, bloquea asignaciones con clic,\n"
             "abre en el navegador para imprimir, exporta Markdown o copia correos."),
        ]
        for icon_title, body in steps:
            f = QFrame()
            f.setObjectName("card")
            f_v = QVBoxLayout(f)
            f_v.setContentsMargins(12, 8, 12, 8)
            f_v.setSpacing(2)
            t = QLabel(icon_title)
            t.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {C_PRI};")
            f_v.addWidget(t)
            b = QLabel(body)
            b.setWordWrap(True)
            b.setStyleSheet(f"color: {C_TEXT2}; font-size: 11px;")
            f_v.addWidget(b)
            v.addWidget(f)

        v.addSpacing(8)

        tip = QLabel(
            "💡 Trucos rápidos:  F1 = Manual completo  |  Ctrl+D = Cargar datos ejemplo  |  "
            "Ctrl+S = Guardar  |  Ctrl+Z = Deshacer"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {C_ACCENT}; font-size: 11px; padding: 6px; background: #fef3c7; border-radius: 4px;")
        v.addWidget(tip)

        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        close_btn = QPushButton("✅ ¡Entendido!")
        close_btn.setMinimumWidth(140)
        close_btn.clicked.connect(d.accept)
        btn_lay.addWidget(close_btn)
        v.addLayout(btn_lay)

        d.exec()

    def _sep(self):
        """Crea una línea separadora horizontal estilizada."""
        s = QFrame()
        s.setObjectName("sep")
        s.setFixedHeight(1)
        return s

    def _teacher_color(self, name):
        """Obtiene el color HEX de un profesor por su nombre; si no tiene, asigna uno de la paleta."""
        for t in self.teachers:
            if t["name"] == name and t.get("color"):
                return t["color"]
        idx = next((i for i, t in enumerate(self.teachers) if t["name"] == name), 0) % len(TEACHER_COLORS)
        return TEACHER_COLORS[idx]

    @staticmethod
    def _rgba(hexc, alpha=0.13):
        """Convierte un color HEX a rgba() con la opacidad indicada."""
        h = hexc.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    def _rebuild_teacher_list(self):
        """Reconstruye la lista visual de profesores aplicando el filtro de búsqueda y franjas."""
        filtro = self.teacher_search.text().strip().lower()
        slot_filter = self.teacher_slot_filter.currentText()
        # Limpia los widgets existentes (deja el stretch final)
        while self.teacher_list_layout.count() > 1:
            item = self.teacher_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        shown = 0
        for i, t in enumerate(self.teachers):
            # Filtra por nombre
            if filtro and filtro not in t["name"].lower():
                continue
            n_slots = len(t.get("time_slots", []))
            if slot_filter == "🗓 Con franjas" and n_slots == 0:
                continue
            if slot_filter == "🗓 Sin franjas" and n_slots > 0:
                continue
            shown += 1
            # Crea una fila clickeable para cada profesor
            frame = ClickFrame(i)
            if i == self._selected_teacher_idx:
                frame.setObjectName("row_selected")
            else:
                frame.setObjectName("row")
            frame.setStyleSheet("")
            frame.setCursor(Qt.CursorShape.PointingHandCursor)
            frame.clicked.connect(lambda a, b, idx=i: self._select_teacher(idx))

            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 6, 10, 6)
            color = self._teacher_color(t["name"])
            n_slots = len(t.get("time_slots", []))
            turno = t.get("turno", "Cualquiera")
            turno_icon = {"Mañana": "🌅", "Tarde": "🌆", "Cualquiera": "⏰"}
            # Punto de color indicador del profesor
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 18px;")
            row.addWidget(dot)
            pref = t.get("preferred_tasks", [])
            pref_str = f"  ⭐ {len(pref)} pref." if pref else ""
            email = t.get("email")
            email_str = f"  📧 {email}" if email else ""
            txt = QLabel(f"👤 {t['name']:16s}  ⏱ {t['max_hours']}h  📅 {t['max_hours_per_day']}h/d  🗓 {n_slots} franjas  {turno_icon.get(turno, '⏰')} {turno}{email_str}{pref_str}")
            txt.setToolTip("Doble clic para editar nombre")
            txt.mouseDoubleClickEvent = lambda e, idx=i: self._edit_teacher_name(idx)
            row.addWidget(txt, 1)
            # Botón de duplicar profesor
            dup_btn = QPushButton("📋")
            dup_btn.setFixedSize(28, 28)
            dup_btn.setToolTip("Duplicar profesor (crea una copia con todos sus datos y franjas)")
            dup_btn.clicked.connect(lambda checked, idx=i: self._duplicate_teacher(idx))
            row.addWidget(dup_btn)
            # Botón de eliminar profesor
            del_btn = QPushButton("❌")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.setToolTip("Eliminar profesor")
            del_btn.clicked.connect(lambda checked, idx=i: self._delete_teacher(idx))
            row.addWidget(del_btn)

            self.teacher_list_layout.insertWidget(self.teacher_list_layout.count()-1, frame)

        self.teacher_count.setText(f"{shown} profesores (de {len(self.teachers)})" if filtro else f"{len(self.teachers)} profesores")

    def _select_teacher(self, idx):
        """Selecciona un profesor de la lista y actualiza el panel de franjas."""
        if idx >= len(self.teachers): return
        self._selected_teacher_idx = idx
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()

    def _refresh_tslot_panel(self):
        """Reconstruye el panel de franjas del profesor seleccionado."""
        # Limpia los widgets existentes
        while self.tslot_layout.count() > 1:
            item = self.tslot_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Si no hay profesor seleccionado, muestra mensaje informativo
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.tslot_header.setText("📅 Franjas: (ningún profe seleccionado)")
            empty = QLabel(
                "👆 Selecciona un profesor de la lista de arriba para gestionar sus franjas de disponibilidad.\n\n"
                "💡 Las franjas indican cuándo está disponible cada profesor.\n"
                "Usa los botones ☕ 🌤 🌞 para añadir franjas rápidas o ➕ Personalitzada para horarios concretos."
            )
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {C_SLATE}; padding: 12px;")
            self.tslot_layout.insertWidget(0, empty)
            return

        t = self.teachers[self._selected_teacher_idx]
        self.tslot_header.setText(f"Franjas de: {t['name']}  ({len(t.get('time_slots', []))} franjas)")

        # Crea una fila visual por cada franja de disponibilidad
        for s in t.get("time_slots", []):
            frame = QFrame()
            frame.setObjectName("slot_row")
            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 4, 10, 4)
            slot_label = QLabel(_fmt_slot(s))
            slot_label.setToolTip("Doble clic para editar fecha u hora")
            slot_label.mouseDoubleClickEvent = lambda e, ref=s: self._edit_tslot(ref)
            row.addWidget(slot_label)
            # Botón de duplicar franja
            dup_btn = QPushButton("📋")
            dup_btn.setFixedSize(28, 28)
            dup_btn.setToolTip("Duplicar franja")
            dup_btn.clicked.connect(lambda checked, ref=s: self._duplicate_tslot(ref))
            row.addWidget(dup_btn)
            # Botón de eliminar franja
            del_btn = QPushButton("❌")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.setToolTip("Eliminar franja")
            del_btn.clicked.connect(lambda checked, ref=s: self._delete_tslot(ref))
            row.addWidget(del_btn)
            row.addStretch()
            self.tslot_layout.insertWidget(self.tslot_layout.count()-1, frame)

    def _update_stats(self):
        """Actualiza las estadísticas de la barra superior (profes, necesidades, horas)."""
        n_slots = sum(len(t.get("time_slots", [])) for t in self.teachers)
        n_need_s = len(self.needs)
        # Suma de minutos disponibles y mínimos necesarios
        avail_min = sum(duration_min(s) for t in self.teachers for s in t.get("time_slots", []))
        need_min = sum(n["min"] * duration_min(n) for n in self.needs)
        self.info_teachers.setText(f"👨‍🏫 {len(self.teachers)} profesores")
        self.info_needs.setText(f"📋 {len(self.needs)} necesidades")
        self.info_slots.setText(f"🗓 {n_slots} franjas profe")
        self.info_need_slots.setText(f"📅 {n_need_s} franjas neces.")
        self.info_hours.setText(f"⏱ {avail_min // 60}h disponibles")
        self.info_need_hours.setText(f"⏰ {need_min // 60}h necesarias (min)")
        self.gen_summary.setText(
            f"👨‍🏫 {len(self.teachers)} profes  ·  📋 {len(self.needs)} neces.  ·  🗓 {n_slots} franjas  ·  ⏱ {avail_min // 60}h disp.  ·  ⏰ {need_min // 60}h neces. min"
        )

    # ── Acciones: Profesores ─────────────────────────────────────────
    def _add_teacher(self):
        """Añade un nuevo profesor desde el formulario de la pestaña Profes."""
        name = self.t_name.text().strip()
        if not name:
            self.toast.show("Nombre obligatorio", "warning"); return
        try:
            mx = int(self.t_max.text())
            mxd = int(self.t_maxd.text())
        except ValueError:
            self.toast.show("Límites deben ser enteros", "warning"); return
        turno = self.t_turno.currentText()
        color = self._teacher_color_pick
        email = self.t_email.text().strip()
        # Crea el objeto profesor y lo añade a la lista global
        self.teachers.append({
            "name": name, "max_hours": mx, "max_hours_per_day": mxd,
            "time_slots": [], "turno": turno, "color": color, "email": email or None
        })
        _save_teachers(self.teachers)
        self._selected_teacher_idx = len(self.teachers) - 1
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()
        self._update_stats()
        self.t_name.clear()
        self.t_email.clear()
        self._teacher_color_pick = TEACHER_COLORS[len(self.teachers) % len(TEACHER_COLORS)]
        self.toast.show(f"Profe «{name}» añadido")

    def _pick_teacher_color(self):
        """Abre el diálogo de color para elegir el color del nuevo profesor."""
        color = QColorDialog.getColor(QColor(self._teacher_color_pick), self, "Color del profesor")
        if color.isValid():
            self._teacher_color_pick = color.name()
            self.t_color_btn.setStyleSheet(f"background: {self._teacher_color_pick}; border-radius: 4px;")

    def _duplicate_teacher(self, idx):
        """Duplica un profesor existente con nombre único (añade "(copia)" si es necesario)."""
        if idx >= len(self.teachers): return
        t = self.teachers[idx]
        new_name = f"{t['name']} (copia)"
        base = new_name
        counter = 1
        while any(p["name"] == new_name for p in self.teachers):
            counter += 1
            new_name = f"{base[:-8] if base.endswith(' (copia)') else base} (copia {counter})"
        dup = {k: (list(v) if isinstance(v, list) else v) for k, v in t.items()}
        dup["name"] = new_name
        self.teachers.insert(idx + 1, dup)
        _save_teachers(self.teachers)
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"Profe «{t['name']}» duplicado como «{new_name}»")

    def _edit_teacher_name(self, idx):
        """Abre un diálogo para renombrar un profesor existente."""
        if idx >= len(self.teachers): return
        t = self.teachers[idx]
        name, ok = QInputDialog.getText(self, "Editar nombre", "Nombre del profesor:",
                                        text=t["name"])
        if ok and name.strip() and name.strip() != t["name"]:
            self.teachers[idx]["name"] = name.strip()
            _save_teachers(self.teachers)
            self._rebuild_teacher_list()
            self._refresh_tslot_panel()
            self._update_stats()
            self.toast.show(f"Nombre actualizado a «{name.strip()}»")

    def _delete_teacher(self, idx):
        """Elimina un profesor de la lista y ajusta la selección si era el actual."""
        if idx >= len(self.teachers): return
        self.teachers.pop(idx)
        _save_teachers(self.teachers)
        # Ajusta el índice seleccionado si el eliminado era el actual o posterior
        if self._selected_teacher_idx is not None:
            if self._selected_teacher_idx >= len(self.teachers):
                self._selected_teacher_idx = len(self.teachers) - 1 if self.teachers else None
            elif self._selected_teacher_idx == idx:
                self._selected_teacher_idx = min(idx, len(self.teachers)-1) if self.teachers else None
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()
        self._update_stats()

    def _add_tslot_preset(self, start, end):
        """Añade una franja rápida predefinida (mañana, tarde, completo) al profesor seleccionado."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        qd = self.tslot_date.date()
        date = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        slot = {"date": date, "start": start, "end": end}
        self.teachers[self._selected_teacher_idx].setdefault("time_slots", []).append(slot)
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"✅ Franja {start}-{end} añadida", "success")

    def _add_tslot_custom_dialog(self):
        """Abre un diálogo para añadir una franja con horario personalizado."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        d = QDialog(self)
        d.setWindowTitle("➕ Franja personalizada")
        d.setMinimumWidth(320)
        fl = QFormLayout(d)
        start_ed = QLineEdit("09:00")
        start_ed.setPlaceholderText("HH:MM")
        start_ed.setToolTip("Hora de inicio de la franja (formato HH:MM)")
        end_ed = QLineEdit("10:00")
        end_ed.setPlaceholderText("HH:MM")
        end_ed.setToolTip("Hora de fin de la franja (formato HH:MM, posterior a inicio)")
        fl.addRow("🕐 De:", start_ed)
        fl.addRow("🕐 A:", end_ed)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        fl.addRow(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        qd = self.tslot_date.date()
        date = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        start = start_ed.text().strip()
        end = end_ed.text().strip()
        # Valida formato HH:MM y que inicio sea anterior a fin
        if not re.match(r"^\d{2}:\d{2}$", start) or not re.match(r"^\d{2}:\d{2}$", end):
            self.toast.show("Hora debe ser HH:MM", "warning"); return
        if start >= end:
            self.toast.show("Inicio debe ser anterior a fin", "warning"); return
        slot = {"date": date, "start": start, "end": end}
        self.teachers[self._selected_teacher_idx].setdefault("time_slots", []).append(slot)
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"✅ Franja {start}-{end} añadida", "success")

    def _edit_tslot(self, slot):
        """Abre un diálogo para modificar fecha, inicio o fin de una franja existente."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            return
        d = QDialog(self)
        d.setWindowTitle("Editar franja")
        d.setMinimumWidth(320)
        fl = QFormLayout(d)
        date_ed = QDateEdit()
        date_ed.setDisplayFormat("yyyy-MM-dd")
        date_ed.setDate(_str_to_qdate(slot["date"]))
        date_ed.setCalendarPopup(True)
        fl.addRow("📅 Fecha:", date_ed)
        start_ed = QLineEdit(slot["start"])
        fl.addRow("🕐 De:", start_ed)
        end_ed = QLineEdit(slot["end"])
        fl.addRow("🕐 A:", end_ed)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        fl.addRow(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        t = self.teachers[self._selected_teacher_idx]
        # Busca la franja original por identidad de objeto y la actualiza in situ
        for s in t["time_slots"]:
            if s is slot:
                qd = date_ed.date()
                s["date"] = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
                s["start"] = start_ed.text().strip()
                s["end"] = end_ed.text().strip()
                break
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show("Franja actualizada")

    def _weekly_grid_dialog(self):
        """Abre la rejilla semanal: el profesor marca días y turnos con checkboxes."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        t = self.teachers[self._selected_teacher_idx]
        d = QDialog(self)
        d.setWindowTitle(f"📅 Rejilla semanal — {t['name']}")
        d.setMinimumWidth(520)
        v = QVBoxLayout(d)
        v.setSpacing(8)
        info = QLabel("Marca los turnos en los que el profesor está disponible cada día:")
        info.setStyleSheet(f"color: {C_TEXT2};")
        v.addWidget(info)
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        base_date = QDate.currentDate()
        while base_date.dayOfWeek() != 1:
            base_date = base_date.addDays(-1)
        grid = QGridLayout()
        grid.setSpacing(4)
        periods = [("☕ Mañana", "09:00", "14:00"), ("🌤 Tarde", "15:00", "18:00"), ("🌞 Completo", "09:00", "18:00")]
        grid.addWidget(QLabel(""), 0, 0)
        for j, (plabel, ps, pe) in enumerate(periods):
            lbl = QLabel(plabel)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight:600;")
            grid.addWidget(lbl, 0, j + 1)
        checkboxes = {}
        for i, day_name in enumerate(days):
            dt = base_date.addDays(i)
            day_lbl = QLabel(f"{day_name}<br><span style='font-size:10px;color:#94a3b8;'>{dt.toString('dd/MM')}</span>")
            day_lbl.setTextFormat(Qt.TextFormat.RichText)
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(day_lbl, i + 1, 0)
            date_str = f"{dt.year():04d}-{dt.month():02d}-{dt.day():02d}"
            for j, (plabel, ps, pe) in enumerate(periods):
                cb = QCheckBox()
                has_slot = any(s["date"] == date_str and s["start"] == ps and s["end"] == pe for s in t.get("time_slots", []))
                cb.setChecked(has_slot)
                cb.setToolTip(f"{day_name} {plabel} ({ps}-{pe})")
                grid.addWidget(cb, i + 1, j + 1, alignment=Qt.AlignmentFlag.AlignCenter)
                checkboxes[(i, j)] = (cb, date_str, ps, pe)
        v.addLayout(grid)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        v.addWidget(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        new_slots = []
        existing_dates = {(s["date"], s["start"], s["end"]) for s in t.get("time_slots", [])}
        for (i, j), (cb, date_str, ps, pe) in checkboxes.items():
            if cb.isChecked():
                if (date_str, ps, pe) not in existing_dates:
                    new_slots.append({"date": date_str, "start": ps, "end": pe})
                existing_dates.discard((date_str, ps, pe))
        for (date_str, ps, pe) in existing_dates:
            t["time_slots"] = [s for s in t.get("time_slots", [])
                               if not (s["date"] == date_str and s["start"] == ps and s["end"] == pe)]
        t.setdefault("time_slots", []).extend(new_slots)
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        added = len(new_slots)
        if added:
            self.toast.show(f"✅ {added} franjas añadidas desde rejilla", "success")
        else:
            self.toast.show("Rejilla sin cambios")

    def _copy_schedule_dialog(self):
        """Abre un diálogo para copiar las franjas de otro profesor al seleccionado."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        target = self.teachers[self._selected_teacher_idx]
        others = [(i, t) for i, t in enumerate(self.teachers) if i != self._selected_teacher_idx and t.get("time_slots")]
        if not others:
            self.toast.show("No hay otros profes con franjas para copiar", "warning"); return
        d = QDialog(self)
        d.setWindowTitle(f"Copiar horario a {target['name']}")
        d.setMinimumWidth(400)
        v = QVBoxLayout(d)
        v.addWidget(QLabel("Selecciona el profesor del que copiar las franjas:"))
        list_w = QListWidget()
        for i, t in others:
            n_slots = len(t.get("time_slots", []))
            item = QListWidgetItem(f"👤 {t['name']}  ({n_slots} franjas)")
            item.setData(Qt.ItemDataRole.UserRole, i)
            list_w.addItem(item)
        v.addWidget(list_w)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        v.addWidget(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        sel = list_w.currentItem()
        if not sel:
            return
        src_idx = sel.data(Qt.ItemDataRole.UserRole)
        src = self.teachers[src_idx]
        target["time_slots"] = [dict(s) for s in src.get("time_slots", [])]
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"✅ Horario copiado de «{src['name']}» a «{target['name']}»", "success")

    def _duplicate_tslot(self, slot):
        """Duplica una franja insertándola justo después del original."""
        if self._selected_teacher_idx is not None and self._selected_teacher_idx < len(self.teachers):
            t = self.teachers[self._selected_teacher_idx]
            idx = t["time_slots"].index(slot) + 1
            t["time_slots"].insert(idx, dict(slot))
            _save_teachers(self.teachers)
            self._refresh_tslot_panel()
            self._rebuild_teacher_list()
            self._update_stats()
            self.toast.show("Franja duplicada")

    def _duplicate_slots_to_day(self):
        """Copia las franjas de un día a otro para el profesor seleccionado."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profesor primero", "warning")
            return
        t = self.teachers[self._selected_teacher_idx]
        slots = t.get("time_slots", [])
        dates = sorted({s["date"] for s in slots})
        if not dates:
            self.toast.show("Este profesor no tiene franjas", "warning")
            return
        src_date, ok = QInputDialog.getItem(self, "Origen", "Copiar franjas del día:", dates, 0, False)
        if not ok:
            return
        src_slots = [s for s in slots if s["date"] == src_date]
        if not src_slots:
            return
        d = QDialog(self)
        d.setWindowTitle(f"📋 Duplicar franjas — {len(src_slots)} franjas")
        d.setMinimumWidth(320)
        v = QVBoxLayout(d)
        v.addWidget(QLabel(f"Origen: {src_date} ({len(src_slots)} franjas)"))
        v.addWidget(QLabel("📅 Fecha destino:"))
        dst_date_ed = QDateEdit()
        dst_date_ed.setDisplayFormat("yyyy-MM-dd")
        dst_date_ed.setDate(_str_to_qdate(src_date))
        dst_date_ed.setCalendarPopup(True)
        v.addWidget(dst_date_ed)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        v.addWidget(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        qd = dst_date_ed.date()
        dst_date = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        if dst_date == src_date:
            self.toast.show("El destino debe ser distinto al origen", "warning")
            return
        for s in src_slots:
            dup = dict(s)
            dup["date"] = dst_date
            t["time_slots"].append(dup)
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"✅ {len(src_slots)} franjas copiadas de {src_date} a {dst_date} para {t['name']}")

    def _delete_tslot(self, slot):
        """Elimina una franja de disponibilidad del profesor seleccionado por identidad de objeto."""
        if self._selected_teacher_idx is not None and self._selected_teacher_idx < len(self.teachers):
            t = self.teachers[self._selected_teacher_idx]
            t["time_slots"] = [s for s in t["time_slots"] if s is not slot]
            _save_teachers(self.teachers)
            self._refresh_tslot_panel()
            self._rebuild_teacher_list()
            self._update_stats()

    def _duplicate_slots_all_teachers(self):
        """Copia las franjas de una fecha a otra para TODOS los profesores."""
        if not self.teachers:
            self.toast.show("No hay profesores", "warning")
            return
        dates = sorted({s["date"] for t in self.teachers for s in t.get("time_slots", [])})
        if not dates:
            self.toast.show("Ningún profesor tiene franjas", "warning")
            return
        src_date, ok = QInputDialog.getItem(self, "Origen", "Copiar franjas del día:", dates, 0, False)
        if not ok:
            return
        d = QDialog(self)
        d.setWindowTitle("📋 Duplicar franjas a todos los profes")
        d.setMinimumWidth(320)
        v = QVBoxLayout(d)
        v.addWidget(QLabel(f"Origen: {src_date}"))
        v.addWidget(QLabel("📅 Fecha destino:"))
        dst_date_ed = QDateEdit()
        dst_date_ed.setDisplayFormat("yyyy-MM-dd")
        dst_date_ed.setDate(_str_to_qdate(src_date))
        dst_date_ed.setCalendarPopup(True)
        v.addWidget(dst_date_ed)
        info = QLabel(f"💡 Se copiarán las franjas del {src_date} a la fecha\ndestino para TODOS los {len(self.teachers)} profesores.")
        info.setStyleSheet(f"color: {C_SLATE}; font-size: 11px;")
        v.addWidget(info)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        v.addWidget(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        qd = dst_date_ed.date()
        dst_date = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        if dst_date == src_date:
            self.toast.show("El destino debe ser distinto al origen", "warning")
            return
        total = 0
        # Recorre todos los profesores y copia las franjas del día origen al destino
        for t in self.teachers:
            src_slots = [s for s in t.get("time_slots", []) if s["date"] == src_date]
            for s in src_slots:
                dup = dict(s)
                dup["date"] = dst_date
                t["time_slots"].append(dup)
                total += 1
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"✅ {total} franjas copiadas de {src_date} a {dst_date} en {len(self.teachers)} profesores")

    def _save_tslot_template(self):
        """Guarda las franjas del profesor seleccionado como plantilla reutilizable."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        t = self.teachers[self._selected_teacher_idx]
        if not t.get("time_slots"):
            self.toast.show("El profe no tiene franjas", "warning"); return
        name, ok = QInputDialog.getText(self, "Guardar plantilla", "Nombre de la plantilla:")
        if not ok or not name.strip():
            return
        self._tslot_templates.append({"name": name.strip(), "slots": list(t["time_slots"])})
        self.toast.show(f"Plantilla «{name.strip()}» guardada")

    def _load_tslot_template(self):
        """Carga una plantilla guardada y reemplaza las franjas del profesor seleccionado."""
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        if not self._tslot_templates:
            self.toast.show("No hay plantillas guardadas", "warning"); return
        names = [tmpl["name"] for tmpl in self._tslot_templates]
        name, ok = QInputDialog.getItem(self, "Cargar plantilla", "Selecciona:", names, 0, False)
        if not ok or not name:
            return
        tmpl = next(t for t in self._tslot_templates if t["name"] == name)
        self.teachers[self._selected_teacher_idx]["time_slots"] = list(tmpl["slots"])
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"Plantilla «{name}» cargada")

    def _export_csv(self):
        """Exporta las asignaciones actuales a un archivo CSV con columnas Fecha, Tarea, Profesor, Horas."""
        if not self.needs:
            self.toast.show("No hay datos para exportar", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "cuadrante.csv", "CSV (*.csv)")
        if not path: return
        try:
            import csv
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Fecha", "Inicio", "Fin", "Tarea", "Min", "Max", "Profesor", "Horas"])
                if self.last_assignment:
                    # Agrupa asignaciones por necesidad (puede tener varios profes)
                    rows = {}
                    for a in self.last_assignment:
                        nd = a["need"]
                        key = (nd["date"], nd["start"], nd["end"], nd["name"])
                        rows.setdefault(key, {"need": nd, "teachers": []})
                        rows[key]["teachers"].append(a["teacher"]["name"])
                    for key, g in sorted(rows.items()):
                        nd = g["need"]
                        dur = duration_min(nd) / 60
                        profs = "; ".join(g["teachers"])
                        w.writerow([nd["date"], nd["start"], nd["end"], nd["name"],
                                    nd["min"], nd["max"], profs, f"{dur:.1f}"])
                else:
                    for n in self.needs:
                        w.writerow([n["date"], n["start"], n["end"], n["name"],
                                    n["min"], n["max"], "", ""])
            self.toast.show("CSV exportado")
        except Exception as e:
            self.toast.show(f"Error: {e}", "error")

    # ── Acciones: Necesidades ─────────────────────────────────────────
    def _add_need(self):
        """Añade una nueva necesidad desde el formulario de la pestaña Necesidades."""
        name = self.nd_name.text().strip()
        qd = self.nd_date.date()
        date = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        start = self.nd_start.text().strip()
        end = self.nd_end.text().strip()
        try:
            mn, mx = int(self.nd_min.text()), int(self.nd_max.text())
        except ValueError:
            self.toast.show("Min/Max deben ser enteros", "warning"); return
        if not name:
            self.toast.show("Nombre obligatorio", "warning"); return
        if not re.match(r"^\d{2}:\d{2}$", start) or not re.match(r"^\d{2}:\d{2}$", end):
            self.toast.show("Hora debe ser HH:MM", "warning"); return
        if start >= end:
            self.toast.show("Inicio debe ser anterior a fin", "warning"); return
        if mn < 1 or mx < mn:
            self.toast.show("Min/Max inválidos", "warning"); return
        tags = self.nd_tags.text().strip()
        self.needs.append({"name": name, "date": date, "start": start, "end": end, "min": mn, "max": mx, "tags": tags})
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()
        self.nd_name.clear()
        self.nd_tags.clear()
        self.toast.show(f"Necesidad «{name}» añadida")

    def _duplicate_need(self, n):
        """Duplica una necesidad con el sufijo '(copia)'."""
        dup = dict(n)
        dup["name"] = f"{n['name']} (copia)"
        idx = self.needs.index(n) + 1
        self.needs.insert(idx, dup)
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()
        self.toast.show(f"Necesidad «{n['name']}» duplicada")

    def _duplicate_needs_to_day(self):
        """Copia todas las necesidades de una fecha origen a una fecha destino."""
        if not self.needs:
            self.toast.show("No hay necesidades que duplicar", "warning")
            return
        dates = sorted({n["date"] for n in self.needs})
        src_date, ok = QInputDialog.getItem(self, "Origen", "Copiar necesidades del día:", dates, 0, False)
        if not ok:
            return
        src_needs = [n for n in self.needs if n["date"] == src_date]
        if not src_needs:
            self.toast.show(f"No hay necesidades en {src_date}", "warning")
            return
        d = QDialog(self)
        d.setWindowTitle(f"📋 Duplicar a otro día — {len(src_needs)} necesidades")
        d.setMinimumWidth(320)
        v = QVBoxLayout(d)
        v.addWidget(QLabel(f"Origen: {src_date} ({len(src_needs)} necesidades)"))
        v.addWidget(QLabel("📅 Fecha destino:"))
        dst_date_ed = QDateEdit()
        dst_date_ed.setDisplayFormat("yyyy-MM-dd")
        dst_date_ed.setDate(_str_to_qdate(src_date))
        dst_date_ed.setCalendarPopup(True)
        v.addWidget(dst_date_ed)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        v.addWidget(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        dst_qdate = dst_date_ed.date()
        dst_date = f"{dst_qdate.year():04d}-{dst_qdate.month():02d}-{dst_qdate.day():02d}"
        if dst_date == src_date:
            self.toast.show("El destino debe ser distinto al origen", "warning")
            return
        for n in src_needs:
            dup = dict(n)
            dup["date"] = dst_date
            self.needs.append(dup)
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()
        self.toast.show(f"✅ {len(src_needs)} necesidades copiadas de {src_date} a {dst_date}")

    def _duplicate_day_from_schedule(self):
        """Copia todas las necesidades y asignaciones de un día a otro y regenera la vista."""
        if not self.last_assignment:
            self.toast.show("No hay cuadrante generado", "warning")
            return
        dates = sorted({a["need"]["date"] for a in self.last_assignment})
        if not dates:
            self.toast.show("No hay fechas en el cuadrante", "warning")
            return
        src_date, ok = QInputDialog.getItem(self, "Origen", "Duplicar día:", dates, 0, False)
        if not ok:
            return
        src_need_idxs = [i for i, n in enumerate(self.needs) if n["date"] == src_date]
        if not src_need_idxs:
            self.toast.show(f"No hay necesidades en {src_date}", "warning")
            return
        d = QDialog(self)
        d.setWindowTitle(f"📋 Duplicar día — {len(src_need_idxs)} necesidades")
        d.setMinimumWidth(320)
        v = QVBoxLayout(d)
        v.addWidget(QLabel(f"Origen: {src_date} ({len(src_need_idxs)} necesidades)"))
        v.addWidget(QLabel("📅 Fecha destino:"))
        dst_date_ed = QDateEdit()
        dst_date_ed.setDisplayFormat("yyyy-MM-dd")
        dst_date_ed.setDate(_str_to_qdate(src_date))
        dst_date_ed.setCalendarPopup(True)
        v.addWidget(dst_date_ed)
        info = QLabel("💡 Las necesidades Y las asignaciones actuales se copiarán al día destino.\nLuego puedes retocar con clic derecho.")
        info.setStyleSheet(f"color: {C_SLATE}; font-size: 11px;")
        v.addWidget(info)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        v.addWidget(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        qd = dst_date_ed.date()
        dst_date = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        if dst_date == src_date:
            self.toast.show("El destino debe ser distinto al origen", "warning")
            return

        # Mapa: old need_idx → new need_idx (tras añadir las copias)
        old_to_new = {}
        for ni in src_need_idxs:
            n = self.needs[ni]
            dup = dict(n)
            dup["date"] = dst_date
            self.needs.append(dup)
            old_to_new[ni] = len(self.needs) - 1

        # Copiar asignaciones de last_assignment apuntando a las nuevas necesidades
        new_assignments = []
        for a in self.last_assignment:
            old_ni = a["need_idx"]
            if old_ni in old_to_new:
                new_ni = old_to_new[old_ni]
                new_n = self.needs[new_ni]
                new_assignments.append({
                    "need": new_n,
                    "teacher": dict(a["teacher"]),
                    "need_idx": new_ni
                })
        self.last_assignment.extend(new_assignments)

        # Actualizar la opción actual en generated_options
        if self.current_option_index < len(self.generated_options):
            op = self.generated_options[self.current_option_index]
            op["assignment"] = list(self.last_assignment)
            # Recalcular estadísticas
            op["n_assignments"] = len(self.last_assignment)
            op["n_covered"] = len({a["need_idx"] for a in self.last_assignment})
            op["total_needs"] = len(self.needs)
            op["total_minutes"] = sum(
                (int(a["need"]["end"].split(":")[0])*60 + int(a["need"]["end"].split(":")[1]) -
                 int(a["need"]["start"].split(":")[0])*60 - int(a["need"]["start"].split(":")[1])
                ) for a in self.last_assignment
            )
            teacher_mins = {}
            for a in self.last_assignment:
                tname = a["teacher"]["name"]
                mins = (int(a["need"]["end"].split(":")[0])*60 + int(a["need"]["end"].split(":")[1]) -
                        int(a["need"]["start"].split(":")[0])*60 - int(a["need"]["start"].split(":")[1]))
                teacher_mins[tname] = teacher_mins.get(tname, 0) + mins
            op["teacher_hours"] = teacher_mins

        self._save_generated_options(self.generated_options)
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()
        self._update_schedule_tab()
        self.toast.show(f"✅ Día {src_date} duplicado a {dst_date} con {len(new_assignments)} asignaciones")

    def _edit_need_from_schedule(self, need_idx):
        """Edita una necesidad desde el menú contextual del cuadrante y actualiza la vista."""
        if need_idx < 0 or need_idx >= len(self.needs):
            return
        self._edit_need(self.needs[need_idx])
        self._update_schedule_tab()

    def _edit_need(self, n):
        """Abre un diálogo para modificar todos los campos de una necesidad."""
        d = QDialog(self)
        d.setWindowTitle(f"Editar necesidad: {n['name']}")
        d.setMinimumWidth(400)
        fl = QFormLayout(d)
        name_ed = QLineEdit(n["name"])
        fl.addRow("📝 Nombre:", name_ed)
        date_ed = QDateEdit()
        date_ed.setDisplayFormat("yyyy-MM-dd")
        date_ed.setDate(_str_to_qdate(n["date"]))
        date_ed.setCalendarPopup(True)
        fl.addRow("📅 Fecha:", date_ed)
        start_ed = QLineEdit(n["start"])
        fl.addRow("🕐 Inicio:", start_ed)
        end_ed = QLineEdit(n["end"])
        fl.addRow("🕐 Fin:", end_ed)
        min_ed = QLineEdit(str(n["min"]))
        fl.addRow("👤 Min:", min_ed)
        max_ed = QLineEdit(str(n["max"]))
        fl.addRow("👤 Max:", max_ed)
        tags_ed = QLineEdit(n.get("tags", ""))
        fl.addRow("🏷️ Etiquetas:", tags_ed)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        fl.addRow(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        idx = self.needs.index(n)
        self.needs[idx] = {
            "name": name_ed.text().strip(),
            "date": f"{date_ed.date().year():04d}-{date_ed.date().month():02d}-{date_ed.date().day():02d}",
            "start": start_ed.text().strip(),
            "end": end_ed.text().strip(),
            "min": int(min_ed.text()),
            "max": int(max_ed.text()),
            "tags": tags_ed.text().strip(),
        }
        # Actualiza referencias obsoletas en last_assignment
        if self.last_assignment:
            for a in self.last_assignment:
                if a["need"] is n:
                    a["need"] = self.needs[idx]
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()
        self.toast.show(f"Necesidad «{name_ed.text().strip()}» actualizada")

    def _delete_need(self, n):
        """Elimina una necesidad por identidad de objeto de la lista."""
        self.needs = [x for x in self.needs if x is not n]
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()

    def _rebuild_need_list(self):
        """Reconstruye la lista visual de necesidades aplicando el filtro de búsqueda."""
        filtro = self.need_search.text().strip().lower()
        # Limpia los widgets existentes (deja el stretch final)
        while self.need_layout.count() > 1:
            item = self.need_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        shown = 0
        for n in self.needs:
            # Filtra por nombre, fecha o etiqueta
            if filtro and filtro not in n["name"].lower() and filtro not in n.get("date", "") and filtro not in n.get("tags", "").lower():
                continue
            shown += 1
            # Crea una fila visual para cada necesidad
            frame = QFrame()
            frame.setObjectName("need_row")
            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 4, 10, 4)
            tags_str = f"  🏷️ {n.get('tags','')}" if n.get("tags") else ""
            dsp = f"{_fmt_slot(n)}  |  👤 [{n['min']}-{n['max']}] profes{tags_str}"
            lbl = QLabel(f"📋 <b>{n['name']}</b>  —  {dsp}")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setToolTip("Doble clic para editar")
            lbl.mouseDoubleClickEvent = lambda e, ref=n: self._edit_need(ref)
            row.addWidget(lbl, 1)
            dup_btn = QPushButton("📋")
            dup_btn.setFixedSize(28, 28)
            dup_btn.setToolTip("Duplicar necesidad")
            dup_btn.clicked.connect(lambda checked, ref=n: self._duplicate_need(ref))
            row.addWidget(dup_btn)

            del_btn = QPushButton("❌")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.setToolTip("Eliminar necesidad")
            del_btn.clicked.connect(lambda checked, ref=n: self._delete_need(ref))
            row.addWidget(del_btn)
            self.need_layout.insertWidget(self.need_layout.count()-1, frame)

        self.need_count.setText(f"{shown} necesidades (de {len(self.needs)})" if filtro else f"{len(self.needs)} necesidades")

    # ── Acciones: Proyecto ───────────────────────────────────────────
    def _refresh_project_list(self):
        """Actualiza el combo de proyectos desde el disco, manteniendo la selección actual si es posible."""
        self.project_selector.blockSignals(True)
        cur = self.project_selector.currentText()
        self.project_selector.clear()
        names = _list_projects()
        if names:
            self.project_selector.addItems(names)
            idx = self.project_selector.findText(cur)
            if idx >= 0:
                self.project_selector.setCurrentIndex(idx)
            else:
                self.project_selector.setCurrentIndex(0)
                self._load_project_data(names[0])
        else:
            self.project_selector.addItem("(ninguno)")
        self.project_selector.blockSignals(False)

    def _on_project_selected(self, choice):
        """Carga el proyecto seleccionado en el combo, guardando antes el actual."""
        if choice in ("(ninguno)", ""): return
        self._save_current(silent=True)
        self._load_project_data(choice)

    def _new_project(self):
        """Crea un proyecto en blanco, limpiando necesidades, opciones y asignaciones."""
        self._save_current(silent=True)
        self.project_name_input.clear()
        self.needs = []
        self.generated_options = []
        self.generated_html_paths = []
        self.current_option_index = 0
        self.last_assignment = None
        self.last_html_path = None
        self._locked_assignments = {}
        self._dirty = False
        self._dirty_label.setText("")
        self._rebuild_need_list()
        self._update_stats()
        self._update_schedule_tab()
        self.project_name_input.setText("Nuevo proyecto")
        self._mark_dirty()
        self.toast.show("Nuevo proyecto creado")

    def _duplicate_project(self):
        """Crea una copia del proyecto actual añadiendo '(copia)' al nombre y lo guarda."""
        if not self.project_name_input.text().strip():
            self.toast.show("Guarda el proyecto antes de duplicar", "warning"); return
        base = self.project_name_input.text().strip()
        self.project_name_input.setText(f"{base} (copia)")
        self._mark_dirty()
        self._save_current(silent=False)

    def _save_current(self, silent=False):
        """Guarda el proyecto actual en disco. Si silent=True, no muestra notificación."""
        name = self.project_name_input.text().strip()
        if not name:
            self.toast.show("Escribe un nombre para guardar", "warning"); return
        _save_project(name, self.needs)
        self._dirty = False
        self._dirty_label.setText("")
        self._refresh_project_list()
        if not silent:
            self.toast.show(f"Proyecto «{name}» guardado")
            self._status(f"💾 Proyecto «{name}» guardado correctamente")

    def _delete_project(self):
        """Elimina el proyecto seleccionado (pide confirmación al usuario)."""
        name = self.project_selector.currentText()
        if name in ("(ninguno)", ""): return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar el proyecto «{name}»?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            _delete_project_file(name)
            self._refresh_project_list()
            self.toast.show("Proyecto eliminado")

    def _load_project_data(self, name):
        """Carga un proyecto desde su archivo JSON y restaura necesidades y opciones generadas."""
        try:
            data = _load_project(name)
            if not isinstance(data, dict):
                raise ValueError("El archivo no contiene un proyecto válido")
        except Exception as e:
            self.toast.show(f"Error al cargar: {e}", "error"); return
        self.project_name_input.setText(data.get("name", name))
        self.needs = [dict(n) for n in data.get("needs", [])]
        self._dirty = False
        self._dirty_label.setText("")
        self._rebuild_need_list()
        self._update_stats()

        # Intenta restaurar las opciones generadas guardadas asociadas al proyecto
        saved = self._load_generated_options()
        if saved:
            self.generated_options = saved
            self.generated_html_paths = []
            self.current_option_index = 0
            self.last_assignment = saved[0]["assignment"]
            self.last_html_path = None
            self._log(f"📂 Cargadas {len(saved)} opciones guardadas del proyecto")
            self._update_schedule_tab()
        else:
            self.generated_options = []
            self.generated_html_paths = []
            self.current_option_index = 0

    def _mark_dirty(self):
        """Marca el proyecto como modificado (activa el indicador visual de 'Sin guardar')."""
        if not self._dirty:
            self._dirty = True
            self._dirty_label.setText("⚠️ Sin guardar")
        self._update_stats()

    def _load_seed(self):
        """Carga los datos ficticios de demostración (15 profesores + 50 necesidades)."""
        self.teachers = get_seed_teachers()
        _save_teachers(self.teachers)
        ndata = get_seed_needs()
        self.project_name_input.setText("XarxaLlibres 2026 - Recogida y distribución")
        self.needs = [dict(n) for n in ndata]
        self.generated_options = []
        self.generated_html_paths = []
        self.current_option_index = 0
        self.last_assignment = None
        self.last_html_path = None
        self._locked_assignments = {}
        self._selected_teacher_idx = 0 if self.teachers else None
        self._rebuild_teacher_list()
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_schedule_tab()
        self.toast.show("✅ Datos XarxaLlibres: 15 profes con horarios + 50 necesidades (5 días)")

    # ── Importación / Exportación ────────────────────────────────────
    def _import_teachers(self):
        """Importa profesores desde un archivo JSON, evitando duplicados por nombre."""
        path, _ = QFileDialog.getOpenFileName(self, "Importar profesores", "", "JSON (*.json)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                self.toast.show("El archivo debe contener un array de profesores", "error"); return
            imported = 0
            for t in data:
                if not all(k in t for k in ("name", "max_hours", "max_hours_per_day", "time_slots")):
                    continue
                if not any(ex["name"] == t["name"] for ex in self.teachers):
                    self.teachers.append(t)
                    imported += 1
            _save_teachers(self.teachers)
            self._rebuild_teacher_list()
            self._refresh_tslot_panel()
            self._update_stats()
            self.toast.show(f"Importados {imported} profesores")
        except Exception as e:
            self.toast.show(f"Error al importar: {e}", "error")

    def _export_teachers(self):
        """Exporta la lista completa de profesores a un archivo JSON."""
        if not self.teachers:
            self.toast.show("No hay profesores para exportar", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar profesores", "profesores.json", "JSON (*.json)")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.teachers, f, ensure_ascii=False, indent=2)
            self.toast.show(f"Exportados {len(self.teachers)} profesores")
        except Exception as e:
            self.toast.show(f"Error al exportar: {e}", "error")

    def _import_needs(self):
        """Importa necesidades desde un archivo JSON y las añade a la lista actual."""
        path, _ = QFileDialog.getOpenFileName(self, "Importar necesidades", "", "JSON (*.json)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                self.toast.show("El archivo debe contener un array de necesidades", "error"); return
            for n in data:
                if all(k in n for k in ("name", "date", "start", "end", "min", "max")):
                    self.needs.append(n)
            self._rebuild_need_list()
            self._mark_dirty()
            self._update_stats()
            self.toast.show(f"Importadas {len(data)} necesidades")
        except Exception as e:
            self.toast.show(f"Error al importar: {e}", "error")

    def _export_needs(self):
        """Exporta las necesidades actuales a un archivo JSON."""
        if not self.needs:
            self.toast.show("No hay necesidades para exportar", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar necesidades", "necesidades.json", "JSON (*.json)")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.needs, f, ensure_ascii=False, indent=2)
            self.toast.show(f"Exportadas {len(self.needs)} necesidades")
        except Exception as e:
            self.toast.show(f"Error al exportar: {e}", "error")

    def _import_project(self):
        """Importa un proyecto completo (profesores + necesidades) desde un archivo JSON."""
        path, _ = QFileDialog.getOpenFileName(self, "Importar proyecto", "", "JSON (*.json)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Si es un array, indica que debe usar "Importar necesidades"
            if isinstance(data, list):
                self.toast.show("Usa 'Importar necesidades' para arrays directos", "warning"); return
            pname = data.get("project_name") or data.get("name", "")
            if not pname:
                self.toast.show("El archivo debe tener 'project_name' o 'name'", "error"); return
            # Reemplaza todos los profesores si el archivo incluye el campo teachers
            if "teachers" in data and isinstance(data["teachers"], list):
                self.teachers = []
                for t in data["teachers"]:
                    if all(k in t for k in ("name", "max_hours", "max_hours_per_day", "time_slots")):
                        self.teachers.append(t)
                _save_teachers(self.teachers)
                self._rebuild_teacher_list()
                self._refresh_tslot_panel()
            needs_data = data.get("needs", [])
            if isinstance(needs_data, list):
                self.project_name_input.setText(pname)
                self.needs = []
                for n in needs_data:
                    if all(k in n for k in ("name", "date", "start", "end", "min", "max")):
                        self.needs.append(n)
                self._rebuild_need_list()
            self._mark_dirty()
            self.generated_options = []
            self.generated_html_paths = []
            self.current_option_index = 0
            self.last_assignment = None
            self.last_html_path = None
            self._update_schedule_tab()
            self._update_stats()
            self.toast.show(f"Proyecto «{pname}» importado")
        except Exception as e:
            self.toast.show(f"Error al importar: {e}", "error")

    def _export_project(self):
        """Exporta el proyecto actual (nombre, profesores, necesidades) a un archivo JSON."""
        pname = self.project_name_input.text().strip()
        if not pname:
            self.toast.show("Escribe un nombre de proyecto", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar proyecto", f"{pname}.json", "JSON (*.json)")
        if not path: return
        try:
            data = {
                "project_name": pname,
                "teachers": self.teachers,
                "needs": self.needs,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.toast.show(f"Proyecto «{pname}» exportado")
        except Exception as e:
            self.toast.show(f"Error al exportar: {e}", "error")

    def _show_stats(self):
        """Genera un HTML con estadísticas detalladas y lo abre en el navegador."""
        if not self.last_assignment:
            self.toast.show("Genera un cuadrante primero", "warning"); return
        project_name = self.project_name_input.text().strip() or "Cuadrante"
        total_min = sum(duration_min(a["need"]) for a in self.last_assignment)
        unique = len({a["need_idx"] for a in self.last_assignment})
        teacher_mins = {}
        teacher_max = {t["name"]: t["max_hours"] * 60 for t in self.teachers}
        for a in self.last_assignment:
            name = a["teacher"]["name"]
            teacher_mins[name] = teacher_mins.get(name, 0) + duration_min(a["need"])
        avail_min = sum(duration_min(s) for t in self.teachers for s in t.get("time_slots", []))
        need_min = sum(n["min"] * duration_min(n) for n in self.needs)
        max_possible = sum((n["max"] or n["min"]) * duration_min(n) for n in self.needs)

        rows = ""
        for name in sorted(teacher_mins.keys()):
            m = teacher_mins[name]
            hh = m // 60
            mm = m % 60
            cap = teacher_max.get(name, 1)
            pct = min(m * 100 // cap, 100)
            rows += f"<tr><td>{name}</td><td>{hh}h {mm:02d}m / {cap//60}h</td><td><div class='bar'><div class='fill' style='width:{pct}%'></div></div>{pct}%</td></tr>\n"

        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>📊 Estadísticas - {project_name}</title>
<style>
  *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',-apple-system,sans-serif; background:#f1f5f9; color:#0f172a; padding:30px; }}
  .card {{ background:#fff; border-radius:14px; padding:28px 32px; margin-bottom:20px; box-shadow:0 1px 4px rgba(0,0,0,.06); }}
  h1 {{ font-size:1.6rem; margin-bottom:6px; }}
  .sub {{ color:#64748b; font-size:0.92rem; margin-bottom:20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:20px; }}
  .stat {{ background:#f8fafc; border-radius:10px; padding:16px; text-align:center; }}
  .stat .num {{ font-size:1.8rem; font-weight:700; color:#16a34a; }}
  .stat .lbl {{ font-size:0.82rem; color:#64748b; margin-top:4px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.92rem; }}
  th {{ text-align:left; padding:10px 8px; border-bottom:2px solid #e2e8f0; color:#64748b; font-weight:600; font-size:0.82rem; text-transform:uppercase; }}
  td {{ padding:8px; border-bottom:1px solid #f1f5f9; }}
  .bar {{ display:inline-block; width:80px; height:8px; background:#e2e8f0; border-radius:4px; vertical-align:middle; margin-right:8px; }}
  .fill {{ height:100%; background:#16a34a; border-radius:4px; }}
  .coverage {{ font-size:0.95rem; line-height:1.8; }}
  .coverage span {{ font-weight:600; color:#16a34a; }}
</style></head>
<body>
  <div class="card">
    <h1>📊 Estadísticas del cuadrante</h1>
    <p class="sub">{project_name}</p>
    <div class="grid">
      <div class="stat"><div class="num">{len(self.needs)}</div><div class="lbl">📋 Necesidades totales</div></div>
      <div class="stat"><div class="num">{unique}</div><div class="lbl">✅ Necesidades cubiertas</div></div>
      <div class="stat"><div class="num">{len(self.last_assignment)}</div><div class="lbl">📌 Asignaciones totales</div></div>
      <div class="stat"><div class="num">{total_min // 60}h {total_min % 60:02d}m</div><div class="lbl">⏱ Horas asignadas</div></div>
    </div>
    <h2 style="font-size:1rem;margin-bottom:12px;">👨‍🏫 Carga por profesor</h2>
    <table><thead><tr><th>Profesor</th><th>Horas</th><th>Proporción</th></tr></thead><tbody>{rows}</tbody></table>
  </div>
  <div class="card">
    <h2 style="font-size:1rem;margin-bottom:12px;">📊 Cobertura general</h2>
    <div class="coverage">
      👨‍🏫 Profesores: <span>{len(self.teachers)}</span><br>
      ⏰ Horas disponibles totales: <span>{avail_min // 60}h</span><br>
      📋 Horas mínimas necesarias: <span>{need_min // 60}h</span><br>
      🎯 Horas máximas posibles: <span>{max_possible // 60}h</span><br>
      📈 Cobertura real: <span>{total_min}/{avail_min}h ({total_min*100//max(avail_min,1)}%)</span>
    </div>
  </div>
</body></html>"""
        path = os.path.join("output", f"stats_{project_name.replace(' ','_')}.html")
        os.makedirs("output", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open(os.path.abspath(path))
        self.toast.show(f"📊 Estadísticas abiertas en el navegador")

    def _toggle_compact_view(self):
        """Alterna entre vista normal (columnas) y compacta (una columna por día)."""
        self._compact_view = not self._compact_view
        self._update_schedule_tab()
        self.toast.show(f"Vista {'compacta' if self._compact_view else 'normal'}")

    def _toggle_lock(self, need_idx, teacher_idx):
        """Bloquea o desbloquea una asignación para que el solver no la modifique al regenerar."""
        key = (need_idx, teacher_idx)
        if key in self._locked_assignments:
            del self._locked_assignments[key]
            self.toast.show("🔓 Bloqueo eliminado")
        else:
            self._locked_assignments[key] = True
            self.toast.show("🔒 Asignación bloqueada")
        self._update_schedule_tab()

    def _launch_solver(self, locked=None, n_options=5, generate_html=True):
        """Lanza el solver en un hilo separado para no bloquear la UI."""
        self._solver_generate_html = generate_html
        self._solver_loading = LoadingDialog(self)
        msg = "🧠 Resolviendo...\nPuede tardar varios minutos" if not locked \
            else f"🔒 Regenerando con {len(locked)} bloqueos...\nPuede tardar varios minutos"
        self._solver_loading.set_message(msg)
        self._solver_loading.show()

        self._solver_thread = QThread(self)
        self._solver_worker = SolverWorker(
            self.teachers, self.needs,
            locked=locked, n_options=n_options, time_limit=10
        )
        self._solver_worker.moveToThread(self._solver_thread)
        self._solver_worker.finished.connect(self._on_solver_finished)
        self._solver_worker.error.connect(self._on_solver_error)
        self._solver_worker.progress.connect(self._solver_loading.set_message)
        self._solver_thread.started.connect(self._solver_worker.run)
        self._solver_thread.finished.connect(self._solver_thread.deleteLater)
        self._solver_thread.start()

    def _on_solver_finished(self, opciones):
        """Procesa las opciones generadas por el solver en segundo plano."""
        self._solver_loading.close()
        self._solver_loading = None
        self._solver_thread.quit()
        self._solver_thread.wait()

        opciones = [op for op in opciones if op["n_assignments"] > 0]
        if not opciones:
            self._log("❌ Sin solución posible.")
            self.toast.show("Sin solución posible", "error"); return

        if self._solver_generate_html:
            # Flujo completo: guardar, exportar HTML, mostrar
            pname = self.project_name_input.text().strip() or "(sin nombre)"
            self._log(f"✅ Se generaron {len(opciones)} opciones distintas")
            for op in opciones:
                self._log(f"   Opción {op['id']}: {op['n_assignments']} asignaciones, "
                          f"{op['n_covered']}/{op['total_needs']} necesidades, "
                          f"{op['total_minutes'] // 60}h{op['total_minutes'] % 60:02d}m totales")
            self._log("→ Guardando todas las opciones...")
            out_dir = os.path.join(BASE_DIR, "output")
            os.makedirs(out_dir, exist_ok=True)
            safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", pname)
            html_paths = []
            for op in opciones:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{safe}_op{op['id']}_{ts}.html"
                path = os.path.join(out_dir, filename)
                export_html_file(pname, self.teachers, self.needs, op["assignment"], path)
                html_paths.append(path)
            self.generated_options = opciones
            self.generated_html_paths = html_paths
            self._save_generated_options(opciones)
            self.current_option_index = 0
            self.last_assignment = opciones[0]["assignment"]
            self.last_html_path = html_paths[0]
            self._log(f"\n✅ Opción {opciones[0]['id']} — {len(opciones[0]['assignment'])} asignaciones (navega con ◀ ▶)")
            self._log(f"   HTML: {html_paths[0]}")
            self.tabs.setCurrentIndex(4)
            self._update_schedule_tab()
            self._log(f"\n✅ {len(opciones)} opciones generadas")
            self._status(f"✅ {len(opciones)} opciones generadas — navega con ◀ ▶")
            self.toast.show(f"✅ {len(opciones)} opciones generadas. Usa ◀ ▶ para cambiar entre ellas")
        else:
            # Solo regenerar con bloqueos
            self.generated_options = opciones
            self.generated_html_paths = []
            self.current_option_index = 0
            self._save_generated_options(opciones)
            self.last_assignment = opciones[0]["assignment"]
            self.last_html_path = None
            self.tabs.setCurrentIndex(4)
            self._update_schedule_tab()
            self._log(f"✅ {len(opciones)} opciones regeneradas con bloqueos")
            self._status(f"🔒 Regenerado con {len(self._locked_assignments)} bloqueos")
            self.toast.show(f"✅ Regenerado con {len(self._locked_assignments)} bloqueos")

    def _on_solver_error(self, msg):
        """Maneja errores del solver lanzado en segundo plano."""
        self._solver_loading.close()
        self._solver_loading = None
        self._solver_thread.quit()
        self._solver_thread.wait()
        self._log(f"❌ Error del solver: {msg}")
        self.toast.show(f"Error: {msg}", "error")

    def _regenerate_with_locks(self):
        """Regenera el cuadrante en segundo plano manteniendo fijas las asignaciones bloqueadas."""
        if not self._locked_assignments:
            self.toast.show("No hay bloqueos activos. Bloquea haciendo clic en un profesor en el cuadrante.", "warning")
            return
        if not self.teachers or not self.needs:
            self.toast.show("Faltan profes o necesidades", "warning"); return
        self._log(f"\n{'='*60}")
        self._log(f"Regenerando con {len(self._locked_assignments)} bloqueos...")
        self._launch_solver(locked=self._locked_assignments, n_options=5, generate_html=False)

    def _export_md(self):
        """Exporta el cuadrante actual como Markdown con tablas por día."""
        if not self.last_assignment:
            self.toast.show("No hay cuadrante que exportar", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Markdown", "cuadrante.md", "Markdown (*.md)")
        if not path: return
        try:
            groups = {}
            for x in self.last_assignment:
                key = x["need_idx"]
                if key not in groups:
                    groups[key] = {"need": self.needs[key] if 0 <= key < len(self.needs) else x["need"], "teachers": []}
                groups[key]["teachers"].append(x["teacher"]["name"])
            dates = sorted({g["need"]["date"] for g in groups.values()})
            lines = [f"# Cuadrante — {self.project_name_input.text().strip() or 'Sin nombre'}", ""]
            for day in dates:
                day_items = sorted(
                    [(i, g) for i, g in groups.items() if g["need"]["date"] == day],
                    key=lambda x: x[1]["need"]["start"]
                )
                lines.append(f"## {day}")
                lines.append("| Hora | Tarea | Profesorado |")
                lines.append("|------|-------|-------------|")
                for ni, g in day_items:
                    n = g["need"]
                    teachers = ", ".join(sorted(g["teachers"])) if g["teachers"] else "_—_"
                    lines.append(f"| {n['start']}-{n['end']} | {n['name']} | {teachers} |")
                lines.append("")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self.toast.show("📝 Markdown guardado")
        except Exception as e:
            self.toast.show(f"Error: {e}", "error")

    def _export_ics(self):
        """Exporta las asignaciones a formato ICS (Google Calendar, Outlook). Genera un evento por asignación."""
        if not self.last_assignment:
            self.toast.show("No hay asignaciones que exportar", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar ICS", "cuadrante.ics", "ICS (*.ics)")
        if not path: return
        try:
            lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//GeneradorCuadrante//ES",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH",
                "X-WR-CALNAME:Cuadrante de Apoyo",
            ]
            for a in self.last_assignment:
                nd = a["need"]
                tname = a["teacher"]["name"]
                temail = a["teacher"].get("email") or ""
                ds = nd["date"].replace("-", "")
                start_dt = f"{ds}T{nd['start'].replace(':', '')}00"
                end_dt = f"{ds}T{nd['end'].replace(':', '')}00"
                summary = f"{nd['name']} - {tname}"
                event = [
                    "BEGIN:VEVENT",
                    f"DTSTART:{start_dt}",
                    f"DTEND:{end_dt}",
                    f"SUMMARY:{summary}",
                    f"DESCRIPTION:Tarea: {nd['name']}\\nProfesor: {tname}\\nProyecto: {self.project_name_input.text().strip() or 'Cuadrante'}",
                ]
                if temail:
                    event.append(f"ATTENDEE;CN={tname}:mailto:{temail}")
                event.append("END:VEVENT")
                lines.extend(event)
            lines.append("END:VCALENDAR")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\r\n".join(lines))
            self.toast.show(f"✅ ICS exportado: {len(self.last_assignment)} eventos", "success")
        except Exception as e:
            self.toast.show(f"Error: {e}", "error")

    def _export_docx(self):
        """Exporta el cuadrante como documento DOCX (HTML envuelto como .doc, compatible con Word)."""
        if not self.last_assignment:
            self.toast.show("No hay asignaciones que exportar", "warning"); return
        pname = self.project_name_input.text().strip() or "cuadrante"
        safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", pname)
        default_name = f"{safe}_op{self.current_option_index+1}_word.doc"
        path, _ = QFileDialog.getSaveFileName(self, "Exportar como DOC", default_name, "Word (*.doc)")
        if not path:
            return
        try:
            html = export_html_file(
                pname, self.teachers, self.needs, self.last_assignment, None, view="docx"
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            self.toast.show(f"✅ DOC exportado: {os.path.basename(path)}", "success")
        except Exception as e:
            self.toast.show(f"Error: {e}", "error")

    # ── Asignación manual ─────────────────────────────────────────────
    def _get_available_teachers(self, need, need_idx):
        """Calcula qué profesores están disponibles para una necesidad concreta (no asignados, no ocupados)."""
        # Profesores ya asignados a esta necesidad
        now_assigned = {a["teacher"]["name"] for a in self.last_assignment if a["need_idx"] == need_idx}
        # Profesores ocupados en otra necesidad con solapamiento horario el mismo día
        busy_teachers = set()
        for a in self.last_assignment:
            if a["need_idx"] == need_idx:
                continue
            an = a["need"]
            if an["date"] != need["date"]:
                continue
            # Comprueba solapamiento horario: inicio < fin ajeno y fin > inicio ajeno
            if an["start"] < need["end"] and an["end"] > need["start"]:
                busy_teachers.add(a["teacher"]["name"])

        available = []
        need_start_min = int(need["start"].split(":")[0]) * 60 + int(need["start"].split(":")[1])
        need_end_min = int(need["end"].split(":")[0]) * 60 + int(need["end"].split(":")[1])
        for ti, t in enumerate(self.teachers):
            if t["name"] in now_assigned or t["name"] in busy_teachers:
                continue
            # Verifica si alguna franja del profesor cubre completamente la necesidad
            for slot in t.get("time_slots", []):
                if slot["date"] != need["date"]:
                    continue
                slot_start = int(slot["start"].split(":")[0]) * 60 + int(slot["start"].split(":")[1])
                slot_end = int(slot["end"].split(":")[0]) * 60 + int(slot["end"].split(":")[1])
                if slot_start <= need_start_min and slot_end >= need_end_min:
                    available.append((ti, t["name"]))
                    break
        return available

    def _need_context_menu(self, need_idx, need, pos):
        """Muestra menú contextual sobre una necesidad: asignar profesor, editar o quitar."""
        menu = QMenu(self)
        available = self._get_available_teachers(need, need_idx)
        if available:
            assign_menu = menu.addMenu("➕ Asignar profesor")
            for ti, tname in sorted(available, key=lambda x: x[1]):
                act = assign_menu.addAction(tname)
                act.setData((need_idx, ti))
            assign_menu.triggered.connect(self._assign_teacher_manual)
        else:
            menu.addAction("➖ No hay profesores disponibles").setEnabled(False)
        menu.addSeparator()
        edit_act = menu.addAction("📝 Editar necesidad")
        edit_act.triggered.connect(lambda checked, ni=need_idx: self._edit_need_from_schedule(ni))
        menu.addSeparator()
        # Lista de profesores ya asignados que se pueden quitar
        assigned_list = [a for a in self.last_assignment if a["need_idx"] == need_idx]
        if assigned_list:
            remove_menu = menu.addMenu("❌ Quitar profesor")
            for a in assigned_list:
                tname = a["teacher"]["name"]
                ti = next((i for i, t in enumerate(self.teachers) if t["name"] == tname), -1)
                act = remove_menu.addAction(tname)
                act.setData((need_idx, ti))
            remove_menu.triggered.connect(self._remove_teacher_manual)
        menu.exec(pos)

    def _teacher_remove_menu(self, need_idx, teacher_idx, pos):
        """Menú contextual rápido para quitar un profesor concreto de una tarea."""
        menu = QMenu(self)
        tname = self.teachers[teacher_idx]["name"] if 0 <= teacher_idx < len(self.teachers) else "?"
        act = menu.addAction(f"❌ Quitar {tname}")
        act.setData((need_idx, teacher_idx))
        menu.triggered.connect(self._remove_teacher_manual)
        menu.exec(pos)

    def _assign_teacher_manual(self, act):
        """Asigna manualmente un profesor a una necesidad desde el menú contextual."""
        need_idx, teacher_idx = act.data()
        if need_idx < 0 or teacher_idx < 0:
            return
        t = self.teachers[teacher_idx]
        n = self.needs[need_idx]
        # Evita asignaciones duplicadas (mismo profesor a misma necesidad)
        if any(a["need_idx"] == need_idx and a["teacher"]["name"] == t["name"] for a in self.last_assignment):
            self.toast.show(f"{t['name']} ya asignado a esta tarea", "warning")
            return
        self.last_assignment.append({
            "need": n,
            "teacher": {"name": t["name"], "color": t.get("color", "")},
            "need_idx": need_idx
        })
        self._update_schedule_tab()
        self.toast.show(f"✅ {t['name']} asignado a «{n['name']}»")

    def _remove_teacher_manual(self, act):
        """Quita manualmente un profesor de una necesidad desde el menú contextual."""
        need_idx, teacher_idx = act.data()
        if teacher_idx < 0 or teacher_idx >= len(self.teachers):
            return
        tname = self.teachers[teacher_idx]["name"]
        self.last_assignment = [a for a in self.last_assignment
                                if not (a["need_idx"] == need_idx and a["teacher"]["name"] == tname)]
        self._update_schedule_tab()
        self.toast.show(f"❌ {tname} quitado")

    def _move_teacher_drop(self, src_need_idx, tgt_need_idx, teacher_idx):
        """Mueve un profesor de una necesidad a otra vía drag & drop."""
        if teacher_idx < 0 or teacher_idx >= len(self.teachers):
            return
        tname = self.teachers[teacher_idx]["name"]
        if tgt_need_idx < 0 or tgt_need_idx >= len(self.needs):
            return
        n = self.needs[tgt_need_idx]
        # Quitar de la tarea origen si es distinta
        if src_need_idx != tgt_need_idx:
            self.last_assignment = [a for a in self.last_assignment
                                    if not (a["need_idx"] == src_need_idx and a["teacher"]["name"] == tname)]
        # Comprobar si ya está en la destino
        if any(a["need_idx"] == tgt_need_idx and a["teacher"]["name"] == tname for a in self.last_assignment):
            self.toast.show(f"{tname} ya está en esta tarea", "warning")
            self._update_schedule_tab()
            return
        # Añadir a la destino
        self.last_assignment.append({
            "need": n,
            "teacher": {"name": tname, "color": self.teachers[teacher_idx].get("color", "")},
            "need_idx": tgt_need_idx
        })
        self._update_schedule_tab()
        self.toast.show(f"✅ {tname} movido a «{n['name']}»")

    # ── Generación del cuadrante ──────────────────────────────────────
    def _generate(self):
        """Genera múltiples opciones de cuadrante en segundo plano y deja elegir al usuario."""
        # ── Validaciones previas ─────────────────────────────────────
        if not self.teachers:
            self.toast.show("Añade al menos un profesor", "warning"); return
        if not self.needs:
            self.toast.show("Añade al menos una necesidad", "warning"); return
        total_avail = sum(len(t.get("time_slots", [])) for t in self.teachers)
        if total_avail == 0:
            self.toast.show("Los profes necesitan franjas disponibles", "warning"); return

        pname = self.project_name_input.text().strip() or "(sin nombre)"

        # ── Validación de cobertura previa ──────────────────────────
        warnings = self._validate_coverage()
        if warnings:
            msg = "Se detectaron los siguientes problemas:\n\n" + "\n".join(warnings)
            msg += "\n\n¿Deseas continuar de todas formas?"
            reply = QMessageBox.warning(self, "⚠️ Advertencias de cobertura", msg,
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                self._log("❌ Generación cancelada por advertencias")
                return
            for w in warnings:
                self._log(f"  {w}")

        # ── Log de cabecera del proceso ─────────────────────────────
        self._log(f"\n{'='*60}")
        self._log(f"Proyecto: {pname}")
        self._log(f"Profesores: {len(self.teachers)}")
        self._log(f"Necesidades: {len(self.needs)}  |  "
                  f"H. mín necesarias: {sum(n['min'] * duration_min(n) for n in self.needs) // 60}h")
        self._log(f"Franjas disponibilidad totales profes: {total_avail}")
        n_opts = self._n_options_spin.value()
        self._log(f"Generando {n_opts} opciones con distintas semillas...")

        # Lanza el solver en segundo plano con animación funcional
        self._launch_solver(
            locked=self._locked_assignments if self._locked_assignments else None,
            n_options=n_opts, generate_html=True
        )

    def _log(self, msg):
        """Añade un mensaje al panel de log y hace scroll automático al final."""
        self.status_text.append(msg)
        sb = self.status_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Persistencia de opciones generadas ─────────────────────────────
    def _save_generated_options(self, options):
        """Guarda las opciones generadas en un archivo *_generated.json asociado al proyecto."""
        name = self.project_name_input.text().strip()
        if not name:
            return
        try:
            with open(_generated_options_filename(name), "w", encoding="utf-8") as f:
                json.dump(options, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"⚠️ No se pudieron guardar las opciones: {e}")

    def _load_generated_options(self):
        """Carga las opciones generadas guardadas del proyecto actual."""
        name = self.project_name_input.text().strip()
        if not name:
            return []
        path = _generated_options_filename(name)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._log(f"⚠️ No se pudieron cargar opciones guardadas: {e}")
            return []

    # ── Navegación entre opciones ──────────────────────────────────────
    def _prev_option(self):
        """Navega a la opción anterior en el cuadrante (cíclico)."""
        if not self.generated_options:
            return
        self.current_option_index = (self.current_option_index - 1) % len(self.generated_options)
        self._show_option(self.current_option_index)

    def _next_option(self):
        """Navega a la opción siguiente en el cuadrante (cíclico)."""
        if not self.generated_options:
            return
        self.current_option_index = (self.current_option_index + 1) % len(self.generated_options)
        self._show_option(self.current_option_index)

    def _show_option(self, index):
        """Muestra una opción específica por índice: actualiza asignaciones y la vista del cuadrante."""
        if not self.generated_options or index < 0 or index >= len(self.generated_options):
            return
        op = self.generated_options[index]
        self.last_assignment = op["assignment"]
        if index < len(self.generated_html_paths):
            self.last_html_path = self.generated_html_paths[index]
        self.current_option_index = index
        self._update_schedule_tab()

    def _clear_solutions(self):
        """Elimina todas las opciones generadas y limpia el cuadrante."""
        if not self.generated_options:
            return
        reply = QMessageBox.question(self, "Borrar soluciones",
                                     "¿Eliminar todas las opciones generadas?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.generated_options = []
        self.generated_html_paths = []
        self.current_option_index = 0
        self.last_assignment = None
        self.last_html_path = None
        self._locked_assignments = {}
        name = self.project_name_input.text().strip()
        if name:
            path = _generated_options_filename(name)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        self._update_schedule_tab()
        self.toast.show("🗑️ Soluciones eliminadas", "info")

    # ── Actualización del cuadrante ────────────────────────────────────
    def _update_schedule_tab(self):
        """Reconstruye completamente la vista del cuadrante con las asignaciones actuales."""
        while self.cal_layout.count():
            item = self.cal_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not self.last_assignment:
            self.open_btn.setEnabled(False)
            self.open_folder_btn.setEnabled(False)
            self.stats_btn.setEnabled(False)
            self.compact_btn.setEnabled(False)
            self.lock_regenerate_btn.setEnabled(False)
            self.dup_day_btn.setEnabled(False)
            self.md_btn.setEnabled(False)
            self.ics_btn.setEnabled(False)

            self.docx_btn.setEnabled(False)
            self.view_combo.setEnabled(False)
            self.nav_prev_btn.setEnabled(False)
            self.nav_next_btn.setEnabled(False)
            self.clear_opts_btn.setEnabled(False)
            self.nav_label.setText("")
            self.cal_summary.setText("")
            return

        self.open_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)
        self.stats_btn.setEnabled(True)
        self.compact_btn.setEnabled(True)
        self.dup_day_btn.setEnabled(True)
        self.compact_btn.setText("📅 Cambiar a vista normal" if self._compact_view else "📅 Cambiar a vista compacta")
        self.lock_regenerate_btn.setEnabled(bool(self._locked_assignments))
        self.md_btn.setEnabled(True)
        self.ics_btn.setEnabled(True)
        self.docx_btn.setEnabled(True)
        self.view_combo.setEnabled(True)
        # Actualizar navegación
        n_opts = len(self.generated_options)
        has_opts = n_opts > 0
        self.clear_opts_btn.setEnabled(has_opts)
        self.nav_prev_btn.setEnabled(has_opts)
        self.nav_next_btn.setEnabled(has_opts)
        if has_opts:
            idx = self.current_option_index
            op = self.generated_options[idx]
            self.nav_label.setText(
                f"  Opción {op['id']}  de  {n_opts}  "
                f"({op['n_assignments']} asig.  ·  "
                f"{op['total_minutes'] // 60}h{op['total_minutes'] % 60:02d}m)  "
            )
        else:
            self.nav_label.setText("")

        # Agrupa asignaciones por necesidad (varios profes por tarea)
        a = self.last_assignment
        groups = {}
        for x in a:
            key = x["need_idx"]
            if key < 0 or key >= len(self.needs):
                continue
            if key not in groups:
                groups[key] = {"need": self.needs[key], "teachers": []}
            groups[key]["teachers"].append(x["teacher"]["name"])
        unique_needs = len({x["need_idx"] for x in a})
        self.cal_summary.setText(f"📋 {len(self.needs)} neces. · ✅ {unique_needs} cubiertas · "
                                 f"👨‍🏫 {len(self.teachers)} profes · 📌 {len(a)} asignaciones")

        dates = sorted({n["date"] for n in self.needs})
        if not dates:
            return

        cal_frame = QFrame()
        if self._compact_view:
            cal_lay = QVBoxLayout(cal_frame)
            cal_lay.setSpacing(12)
        else:
            cal_lay = QHBoxLayout(cal_frame)
            cal_lay.setSpacing(8)
        cal_lay.setContentsMargins(4, 4, 4, 4)

        for day in dates:
            try:
                d = datetime.strptime(day, "%Y-%m-%d")
                wd = d.weekday()
                day_header = f"{DAYS_ES[wd].capitalize()} {d.strftime('%d/%m')}"
                day_num = d.strftime("%d")
                day_name = DAYS_ES[wd]
                is_weekend = wd >= 5
            except:
                day_header = day; day_num = ""; day_name = day; is_weekend = False

            # Columna/día del cuadrante
            col = QFrame()
            col.setObjectName("card")
            col.setStyleSheet("")
            col.setMinimumWidth(190)
            col_v = QVBoxLayout(col)
            col_v.setContentsMargins(6, 6, 6, 6)
            col_v.setSpacing(4)

            # Cabecera del día con número y nombre del día de la semana
            hdr_frame = QFrame()
            hdr_color = C_PRI
            hdr_frame.setStyleSheet(f"background: {hdr_color}; border-radius: 6px;")
            hdr_frame.setFixedHeight(48)
            hdr_v = QVBoxLayout(hdr_frame)
            hdr_v.setContentsMargins(0, 4, 0, 2)
            hdr_v.setSpacing(0)
            num_lbl = QLabel(day_num)
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
            hdr_v.addWidget(num_lbl)
            name_lbl = QLabel(day_name[:3].upper())
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 9px; font-weight: bold;")
            hdr_v.addWidget(name_lbl)
            col_v.addWidget(hdr_frame)

            # Necesidades del día ordenadas por hora de inicio
            day_needs = sorted(
                [(i, g) for i, g in groups.items() if g["need"]["date"] == day],
                key=lambda x: x[1]["need"]["start"]
            )

            if not day_needs:
                empty = QLabel("—")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty.setStyleSheet(f"color: {C_SLATE}; padding: 12px;")
                col_v.addWidget(empty)
            else:
                for ni, g in day_needs:
                    n = g["need"]
                    assigned = sorted(g["teachers"]) if g["teachers"] else []

                    # Tarjeta de necesidad con soporte de drop
                    card = DropFrame(ni, self)
                    card.setObjectName("card")
                    card.setStyleSheet("")
                    card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                    card.customContextMenuRequested.connect(
                        lambda pos, ni2=ni, n2=n, c=card: self._need_context_menu(ni2, n2, c.mapToGlobal(pos))
                    )
                    card.setToolTip("Suelta aquí un profesor para asignarlo manualmente")
                    card.dropped.connect(self._move_teacher_drop)
                    card_v = QVBoxLayout(card)
                    card_v.setContentsMargins(6, 4, 6, 4)
                    card_v.setSpacing(2)

                    # Franja horaria de la necesidad
                    time_lbl = QLabel(f"{n['start']} - {n['end']}")
                    time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    time_lbl.setStyleSheet(f"background: {C_PRI}; color: white; border-radius: 4px; padding: 2px; font-weight: bold; font-size: 9px;")
                    card_v.addWidget(time_lbl)

                    # Nombre de la tarea
                    name_lbl = QLabel(n["name"])
                    name_lbl.setWordWrap(True)
                    name_lbl.setStyleSheet("font-weight: bold; font-size: 11px;")
                    card_v.addWidget(name_lbl)

                    # Requisitos mínimo/máximo de profesores
                    req_lbl = QLabel(f"min {n['min']} · max {n['max']}")
                    req_lbl.setStyleSheet(f"color: {C_SLATE}; font-size: 9px;")
                    card_v.addWidget(req_lbl)

                    if assigned:
                        for tname in assigned:
                            c = self._teacher_color(tname)
                            # Buscar teacher_idx para este nombre y need_idx
                            t_idx = next((ti for ti, t in enumerate(self.teachers) if t["name"] == tname), -1)
                            n_idx = ni
                            is_locked = (n_idx, t_idx) in self._locked_assignments
                            lock_char = "🔒" if is_locked else "🔓"
                            tlabel = ClickFrame(n_idx, t_idx, self)
                            tlabel.setObjectName("card")
                            tlabel.setCursor(Qt.CursorShape.PointingHandCursor)
                            tlabel.setToolTip("Clic para bloquear/desbloquear · Arrastra a otra tarea para reasignar")
                            tlabel_inner = QLabel(f"  {lock_char}  {tname}  ")
                            if is_locked:
                                tlabel_inner.setStyleSheet(
                                    f"color: {c}; background: {self._rgba(c, 0.35)}; "
                                    f"border: 2px solid {c}; border-radius: 4px; "
                                    f"padding: 1px 4px; font-weight: bold; font-size: 9px;"
                                )
                            else:
                                tlabel_inner.setStyleSheet(f"color: {c}; background: {self._rgba(c, 0.12)}; border-radius: 4px; padding: 1px 4px; font-weight: bold; font-size: 9px;")
                            tlabel_lyt = QVBoxLayout(tlabel)
                            tlabel_lyt.setContentsMargins(0, 0, 0, 0)
                            tlabel_lyt.addWidget(tlabel_inner)
                            tlabel.clicked.connect(self._toggle_lock)
                            tlabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                            tlabel.customContextMenuRequested.connect(
                                lambda pos, ni2=n_idx, ti2=t_idx, tl=tlabel: self._teacher_remove_menu(ni2, ti2, tl.mapToGlobal(pos))
                            )
                            card_v.addWidget(tlabel)

                    col_v.addWidget(card)

            cal_lay.addWidget(col)

        self.cal_layout.addWidget(cal_frame)

    # ── Apertura en navegador ─────────────────────────────────────────
    def _get_view_param(self):
        """Devuelve el parámetro de vista según el combo seleccionado (schedule/teacher/task/word/print)."""
        idx = self.view_combo.currentIndex()
        return ["schedule", "teacher", "task", "word", "print"][idx]

    def _open_html(self):
        """Genera el HTML del cuadrante según la vista elegida y lo abre en el navegador."""
        view = self._get_view_param()
        pname = self.project_name_input.text().strip() or "cuadrante"

        out_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(out_dir, exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", pname)
        view_suffix = ["cuadrante", "profesores", "tareas", "word", "imprimir"][self.view_combo.currentIndex()]
        filename = f"{safe}_op{self.current_option_index+1}_{view_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(out_dir, filename)
        export_html_file(pname, self.teachers, self.needs, self.last_assignment, path, view=view)
        self.last_html_path = path
        webbrowser.open(f"file://{os.path.abspath(path)}")

    def _open_folder(self):
        """Abre el explorador de archivos en la carpeta donde se guardan los HTML generados."""
        if self.last_html_path:
            os.startfile(os.path.dirname(os.path.abspath(self.last_html_path)))

    # ── Auto-guardado ──────────────────────────────────────────────────
    def _auto_save(self):
        """Guarda automáticamente cada 2 minutos si hay cambios sin guardar."""
        name = self.project_name_input.text().strip()
        if name and self._dirty:
            _save_project(name, self.needs)
            self._dirty = False
            self._dirty_label.setText("")

    # ── Validación previa ──────────────────────────────────────────────
    def _validate_coverage(self):
        """Valida que las necesidades puedan cubrirse con los profesores disponibles.
        Retorna una lista de advertencias (vacía si todo es correcto)."""
        warnings = []
        # Agrupa necesidades por fecha
        needs_by_date = {}
        for n in self.needs:
            needs_by_date.setdefault(n["date"], []).append(n)
        for day, day_needs in needs_by_date.items():
            # Profesores con alguna franja ese día
            avail_teachers = []
            for t in self.teachers:
                if any(s["date"] == day for s in t.get("time_slots", [])):
                    avail_teachers.append(t["name"])
            for n in day_needs:
                # Profesores cuya franja cubre completamente la necesidad
                can_cover = [t["name"] for t in self.teachers
                             if any(s["date"] == n["date"] and s["start"] <= n["start"] and s["end"] >= n["end"]
                                    for s in t.get("time_slots", []))]
                if len(can_cover) < n["min"]:
                    warnings.append(f"⚠️ «{n['name']}» necesita {n['min']} profes, solo {len(can_cover)} pueden cubrirla")
        # Compara horas disponibles totales vs mínimas necesarias
        avail_min = sum(duration_min(s) for t in self.teachers for s in t.get("time_slots", []))
        need_min = sum(n["min"] * duration_min(n) for n in self.needs)
        if need_min > avail_min:
            warnings.append(f"⏰ Horas necesarias ({need_min // 60}h) superan las disponibles ({avail_min // 60}h)")
        if not self._undo_active():
            self._save_undo()
        return warnings

    def _undo_active(self):
        """Comprueba si existe la pila de deshacer (inicialización segura)."""
        return hasattr(self, '_undo_stack')

    def _save_undo(self):
        """Guarda el estado actual de profesores y necesidades en la pila de deshacer (máx. 50)."""
        state = {"teachers": [dict(t) for t in self.teachers], "needs": [dict(n) for n in self.needs]}
        self._undo_stack.append(state)
        self._redo_stack.clear()
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _undo(self):
        """Deshace la última acción restaurando profesores y necesidades desde la pila."""
        if not self._undo_stack:
            self.toast.show("Nada que deshacer", "warning"); return
        state = {"teachers": [dict(t) for t in self.teachers], "needs": [dict(n) for n in self.needs]}
        self._redo_stack.append(state)
        prev = self._undo_stack.pop()
        self.teachers = prev["teachers"]
        self.needs = prev["needs"]
        _save_teachers(self.teachers)
        self._rebuild_teacher_list()
        self._rebuild_need_list()
        self._refresh_tslot_panel()
        self._update_stats()
        self._mark_dirty()
        self.toast.show("↩️ Deshecho")

    def _redo(self):
        """Rehace la última acción deshecha restaurando estado desde la pila de rehacer."""
        if not self._redo_stack:
            self.toast.show("Nada que rehacer", "warning"); return
        state = {"teachers": [dict(t) for t in self.teachers], "needs": [dict(n) for n in self.needs]}
        self._undo_stack.append(state)
        nxt = self._redo_stack.pop()
        self.teachers = nxt["teachers"]
        self.needs = nxt["needs"]
        _save_teachers(self.teachers)
        self._rebuild_teacher_list()
        self._rebuild_need_list()
        self._refresh_tslot_panel()
        self._update_stats()
        self._mark_dirty()
        self.toast.show("🔁 Rehecho")
