import json, os, re, webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTabWidget, QScrollArea, QFrame, QTextEdit, QSizePolicy,
    QMessageBox, QDateEdit, QDialog, QFormLayout, QDialogButtonBox,
    QButtonGroup, QRadioButton  # Para el selector de opciones múltiples
)
from PyQt6.QtCore import Qt, QTimer, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QAction

from ortools.sat.python import cp_model
from scheduler import TeacherScheduler, duration_min
from html_exporter import export_html_file
from seed_data import get_seed_teachers, get_seed_needs

# ── Colores ──────────────────────────────────────────────────────────────
C_PRI    = "#6366f1"
C_PRI_D  = "#4f46e5"
C_PRI_L  = "#a5b4fc"
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
QTabBar::tab {{ background: {C_BORDER}; color: {C_TEXT2}; padding: 8px 18px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 13px; }}
QTabBar::tab:selected {{ background: {C_CARD}; color: {C_PRI}; font-weight: bold; }}
QPushButton {{ background: {C_PRI}; color: #fff; border: none; padding: 6px 14px; border-radius: 5px; font-size: 12px; }}
QPushButton:hover {{ background: {C_PRI_D}; }}
QPushButton#danger {{ background: {C_RED}; }}
QPushButton#danger:hover {{ background: #b91c1c; }}
QPushButton#secondary {{ background: {C_BORDER}; color: {C_TEXT}; }}
QPushButton#secondary:hover {{ background: #cbd5e1; }}
QLineEdit {{ background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT}; }}
QComboBox {{ background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT}; }}
QLabel {{ color: {C_TEXT}; }}
QTextEdit {{ background: #f1f5f9; border: 1px solid {C_BORDER}; border-radius: 6px; color: {C_TEXT}; font-family: Consolas; }}
QScrollBar:vertical {{ background: {C_BG}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: #cbd5e1; border-radius: 4px; min-height: 20px; }}
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
QTabBar::tab {{ background: {C_BORDER_D}; color: {C_TEXT2_D}; padding: 8px 18px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 13px; }}
QTabBar::tab:selected {{ background: {C_CARD_D}; color: {C_PRI_L}; font-weight: bold; }}
QPushButton {{ background: {C_PRI}; color: #fff; border: none; padding: 6px 14px; border-radius: 5px; font-size: 12px; }}
QPushButton:hover {{ background: {C_PRI_D}; }}
QPushButton#danger {{ background: {C_RED}; }}
QPushButton#danger:hover {{ background: #b91c1c; }}
QPushButton#secondary {{ background: {C_BORDER_D}; color: {C_TEXT_D}; }}
QPushButton#secondary:hover {{ background: #475569; }}
QLineEdit {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT_D}; }}
QComboBox {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 4px; padding: 4px 7px; color: {C_TEXT_D}; }}
QLabel {{ color: {C_TEXT_D}; }}
QTextEdit {{ background: {C_BG_D}; border: 1px solid {C_BORDER_D}; border-radius: 6px; color: #e2e8f0; font-family: Consolas; }}
QScrollBar:vertical {{ background: {C_BG_D}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: #475569; border-radius: 4px; min-height: 20px; }}
QFrame#card {{ background: {C_CARD_D}; border: 1px solid {C_BORDER_D}; border-radius: 8px; }}
QFrame#sep {{ background: {C_BORDER_D}; max-height: 1px; }}
QFrame#row {{ background: {C_CARD_D}; border: 1px solid {C_BORDER_D}; border-radius: 5px; }}
QFrame#row:hover {{ background: #1a2332; }}
QFrame#row_selected {{ background: #1a3a5c; border: 1px solid {C_PRI_L}; border-radius: 5px; }}
QFrame#slot_row {{ background: #0a3d2a; border: 1px solid #166534; border-radius: 4px; }}
QFrame#need_row {{ background: #422006; border: 1px solid #713f12; border-radius: 4px; }}
"""

# ── Helpers (UI independent) ────────────────────────────────────────────
def _ensure_dirs():
    os.makedirs(PROJECTS_DIR, exist_ok=True)

def _load_teachers():
    if os.path.exists(TEACHERS_FILE):
        try:
            with open(TEACHERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_teachers(teachers):
    _ensure_dirs()
    with open(TEACHERS_FILE, "w", encoding="utf-8") as f:
        json.dump(teachers, f, ensure_ascii=False, indent=2)

def _list_projects():
    _ensure_dirs()
    names = []
    for f in sorted(os.listdir(PROJECTS_DIR)):
        if not f.endswith(".json"): continue
        try:
            with open(os.path.join(PROJECTS_DIR, f), "r", encoding="utf-8") as fh:
                names.append(json.load(fh).get("name", f.replace(".json", "")))
        except Exception:
            names.append(f.replace(".json", ""))
    return names

def _project_filename(name):
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip() or "sin_titulo")
    return os.path.join(PROJECTS_DIR, f"{safe}.json")

def _save_project(name, needs):
    _ensure_dirs()
    with open(_project_filename(name), "w", encoding="utf-8") as f:
        json.dump({"name": name.strip() or "Sin título", "needs": needs}, f, ensure_ascii=False, indent=2)

def _load_project(name):
    with open(_project_filename(name), "r", encoding="utf-8") as f:
        return json.load(f)

def _delete_project_file(name):
    p = _project_filename(name)
    if os.path.exists(p): os.remove(p)

def _fmt_slot(s):
    try:
        d = datetime.strptime(s["date"], "%Y-%m-%d")
        df = d.strftime("%d/%m/%Y")
    except Exception:
        df = s.get("date", "?")
    return f"{df}  {s.get('start', '?')} - {s.get('end', '?')}"

# ── Toast ────────────────────────────────────────────────────────────────
class Toast(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setStyleSheet("background: #059669; border-radius: 8px;")
        self.label = QLabel(self)
        self.label.setStyleSheet("color: white; font-size: 13px; padding: 10px 24px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()

    def show(self, message, type="success"):
        colors = {"success": "#059669", "warning": "#d97706", "error": "#dc2626"}
        self.setStyleSheet(f"background: {colors.get(type, '#059669')}; border-radius: 8px;")
        self.label.setText(message)
        w = self.parent().width()
        self.setFixedWidth(min(400, w - 40))
        self.adjustSize()
        self.move((w - self.width()) // 2, 16)
        self.raise_()
        super().show()
        QTimer.singleShot(3500, self.hide)

# ── Clickable Frame ──────────────────────────────────────────────────────
class ClickFrame(QFrame):
    clicked = pyqtSignal(int)
    def __init__(self, idx, parent=None):
        super().__init__(parent)
        self.idx = idx
    def mousePressEvent(self, e):
        self.clicked.emit(self.idx)
        super().mousePressEvent(e)

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
        cancelar.setObjectName("danger")
        cancelar.clicked.connect(self.reject)
        btn_lay.addWidget(cancelar)
        aceptar = QPushButton("✅ Aceptar opción seleccionada")
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


# ── Main App ─────────────────────────────────────────────────────────────
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📋 Generador Cuadrante Tareas Profesorado")
        self.setMinimumSize(1100, 650)  # 16:9 friendly minimum
        self.resize(1366, 768)          # 16:9 estándar

        self.teachers = _load_teachers()
        self.needs = []
        self.project_name = ""
        self.last_assignment = None
        self.last_html_path = None
        self._dirty = False
        self._selected_teacher_idx = None
        self._dark_mode = False

        self._build_ui()
        self._apply_theme()
        self._refresh_project_list()
        self._rebuild_teacher_list()
        self._update_stats()

    # ── Theme ──────────────────────────────────────────────────────────
    def _apply_theme(self):
        qss = DARK_QSS if self._dark_mode else LIGHT_QSS
        QApplication.instance().setStyleSheet(qss)
        mode = "dark" if self._dark_mode else "light"
        self.theme_btn.setText("☀️ Claro" if self._dark_mode else "🌙 Oscuro")
        # header always green
        self.header_bar.setStyleSheet(f"background: {C_PRI}; border-radius: 0;")

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    # ── Build UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)

        # Header bar
        self.header_bar = QFrame()
        self.header_bar.setFixedHeight(48)
        hdr_lay = QHBoxLayout(self.header_bar)
        hdr_lay.setContentsMargins(20, 0, 20, 0)

        title = QLabel("📋  Generador Cuadrante Tareas Profesorado")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        hdr_lay.addWidget(title)

        hdr_lay.addStretch()

        self.theme_btn = QPushButton("☀️ Claro")
        self.theme_btn.setFixedSize(100, 30)
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

        # Toast overlay
        self.toast = Toast(self)

    def _tab_widget(self, scroll=True):
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

    # ── Project Tab ────────────────────────────────────────────────────
    def _build_project_tab(self):
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "🏠 Proyecto")
        v = QVBoxLayout(tab)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        # Heading
        v.addWidget(QLabel("🏠 Seleccionar proyecto"))
        # Selector row
        sel = QHBoxLayout()
        self.project_selector = QComboBox()
        self.project_selector.setMinimumWidth(300)
        self.project_selector.currentTextChanged.connect(self._on_project_selected)
        sel.addWidget(self.project_selector)

        def btn(text, obj, cmd, color=None):
            b = QPushButton(text)
            b.clicked.connect(cmd)
            if color: b.setObjectName(color)
            sel.addWidget(b)
            return b
        btn("➕ Nuevo", None, self._new_project, "secondary")
        btn("📋 Duplicar", None, self._duplicate_project, "secondary")
        btn("💾 Guardar", None, self._save_current)
        btn("🗑️ Eliminar", None, self._delete_project, "danger")
        v.addLayout(sel)

        v.addWidget(QLabel("📛 Nombre del proyecto:"))
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Nombre del proyecto...")
        self.project_name_input.textChanged.connect(lambda: self._mark_dirty())
        v.addWidget(self.project_name_input)

        # Stats
        stats = QHBoxLayout()
        self.info_teachers = QLabel("👨‍🏫 0 profesores")
        self.info_teachers.setStyleSheet(f"font-weight: bold; color: {C_PRI};")
        self.info_needs = QLabel("📋 0 necesidades")
        self.info_slots = QLabel("🗓 0 franjas profe")
        self.info_need_slots = QLabel("📅 0 franjas neces.")
        self.info_hours = QLabel("⏱ 0h disponibles")
        self.info_need_hours = QLabel("⏰ 0h necesarias (min)")
        for lbl in [self.info_teachers, self.info_needs, self.info_slots, self.info_need_slots, self.info_hours, self.info_need_hours]:
            stats.addWidget(lbl)
            stats.addSpacing(18)
        stats.addStretch()
        v.addLayout(stats)

        bf = QHBoxLayout()
        btn("📦 Cargar datos ficticios", None, self._load_seed, "secondary")
        self._dirty_label = QLabel("")
        self._dirty_label.setStyleSheet(f"color: {C_ACCENT};")
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
            "4. ⚙️ Genera el cuadrante — el solver CP-SAT genera 5 opciones y tú eliges la mejor\n"
            "5. 📅 Abre el HTML, copia los correos e imprime como PDF"
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {C_TEXT2}; padding: 8px;")
        v.addWidget(info)
        v.addStretch()

    # ── Teachers Tab ───────────────────────────────────────────────────
    def _build_teachers_tab(self):
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "👨‍🏫 Profes")
        v = QVBoxLayout(tab)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        hint = QLabel("Los profesores se guardan automáticamente y se comparten entre proyectos")
        hint.setStyleSheet(f"color: {C_SLATE};")
        v.addWidget(hint)

        # Add teacher form
        f = QHBoxLayout()
        f.addWidget(QLabel("👤 Nombre:"))
        self.t_name = QLineEdit(); self.t_name.setPlaceholderText("Nombre del profe")
        f.addWidget(self.t_name)
        f.addSpacing(8)
        f.addWidget(QLabel("⏱ Max total (h):"))
        self.t_max = QLineEdit("20"); self.t_max.setFixedWidth(50)
        f.addWidget(self.t_max)
        f.addSpacing(8)
        f.addWidget(QLabel("📅 Max/día (h):"))
        self.t_maxd = QLineEdit("6"); self.t_maxd.setFixedWidth(50)
        f.addWidget(self.t_maxd)
        f.addSpacing(8)
        btn = QPushButton("➕ Añadir profe")
        btn.clicked.connect(self._add_teacher)
        f.addWidget(btn)
        f.addStretch()
        v.addLayout(f)

        self.teacher_count = QLabel("0 profesores")
        self.teacher_count.setStyleSheet("font-weight: bold;")
        v.addWidget(self.teacher_count)

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

        self.tslot_date = QDateEdit()
        self.tslot_date.setCalendarPopup(True)
        self.tslot_date.setDisplayFormat("yyyy-MM-dd")
        self.tslot_date.setDate(datetime.strptime("2026-06-22", "%Y-%m-%d").date())
        slot_top.addWidget(self.tslot_date)
        v.addLayout(slot_top)

        # ── Add buttons ──
        presets = QHBoxLayout()
        presets.setSpacing(6)
        add_custom = QPushButton("➕ Personalitzada")
        add_custom.clicked.connect(self._add_tslot_custom_dialog)
        presets.addWidget(add_custom)
        presets.addSpacing(12)
        for lbl, s, e in [("☕ Mañana  09-14h", "09:00", "14:00"),
                          ("🌤 Tarde 15-18h", "15:00", "18:00"),
                          ("🌞 Completo 09-18h", "09:00", "18:00")]:
            b = QPushButton(lbl)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda checked, ss=s, ee=e: self._add_tslot_preset(ss, ee))
            presets.addWidget(b)
        presets.addStretch()
        v.addLayout(presets)

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

    # ── Needs Tab ──────────────────────────────────────────────────────
    def _build_needs_tab(self):
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "📋 Necesidades")
        v = QVBoxLayout(tab)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        f = QHBoxLayout()
        f.addWidget(QLabel("📝 Nombre:"))
        self.nd_name = QLineEdit(); self.nd_name.setPlaceholderText("Nombre tarea"); self.nd_name.setFixedWidth(180)
        f.addWidget(self.nd_name)
        f.addSpacing(4)
        f.addWidget(QLabel("📅 Fecha:"))
        self.nd_date = QLineEdit("2026-06-22"); self.nd_date.setFixedWidth(90)
        f.addWidget(self.nd_date)
        f.addSpacing(4)
        f.addWidget(QLabel("🕐 Inicio:"))
        self.nd_start = QLineEdit("09:00"); self.nd_start.setFixedWidth(50)
        f.addWidget(self.nd_start)
        f.addSpacing(4)
        f.addWidget(QLabel("🕐 Fin:"))
        self.nd_end = QLineEdit("11:00"); self.nd_end.setFixedWidth(50)
        f.addWidget(self.nd_end)
        f.addSpacing(4)
        f.addWidget(QLabel("👤 Min:"))
        self.nd_min = QLineEdit("2"); self.nd_min.setFixedWidth(36)
        f.addWidget(self.nd_min)
        f.addSpacing(4)
        f.addWidget(QLabel("👤 Max:"))
        self.nd_max = QLineEdit("4"); self.nd_max.setFixedWidth(36)
        f.addWidget(self.nd_max)
        f.addSpacing(6)
        b = QPushButton("➕➕ Añadir necesidad")
        b.clicked.connect(self._add_need)
        f.addWidget(b)
        f.addStretch()
        v.addLayout(f)

        self.need_count = QLabel("📋 0 necesidades")
        self.need_count.setStyleSheet("font-weight: bold;")
        v.addWidget(self.need_count)

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

    # ── Generate Tab ───────────────────────────────────────────────────
    def _build_generate_tab(self):
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "⚙️ Generar")
        v = QVBoxLayout(tab)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        v.addWidget(QLabel("⚙️ Generar cuadrante de apoyo"))

        info_multi = QLabel(
            "🧠 El solver genera 5 opciones distintas (variando la semilla de búsqueda)\n"
            "y te permite elegir la que más te guste antes de mostrar el resultado final."
        )
        info_multi.setWordWrap(True)
        info_multi.setStyleSheet(f"color: {C_TEXT2}; background: #eef2ff; border: 1px solid {C_PRI_L}; border-radius: 6px; padding: 8px 12px;")
        v.addWidget(info_multi)

        self.gen_summary = QLabel("")
        self.gen_summary.setStyleSheet(f"color: {C_SLATE};")
        v.addWidget(self.gen_summary)

        gen_btn = QPushButton("🚀 Generar Cuadrante")
        gen_btn.setMinimumHeight(50)
        gen_btn.setStyleSheet(f"font-size: 18px; font-weight: bold; background: {C_PRI}; color: white; border-radius: 8px;")
        gen_btn.clicked.connect(self._generate)
        v.addWidget(gen_btn)

        v.addWidget(QLabel("📜 Log:"), alignment=Qt.AlignmentFlag.AlignBottom)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(200)
        self.status_text.append("💡 Define profesores y necesidades, luego pulsa Generar.\n")
        self.status_text.append("🔁 El solver probará 5 semillas distintas y abrirá un selector.\n")
        v.addWidget(self.status_text, 1)

    # ── Schedule Tab ───────────────────────────────────────────────────
    def _build_schedule_tab(self):
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "📅 Cuadrante")
        v = QVBoxLayout(tab)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        bf = QHBoxLayout()
        self.open_btn = QPushButton("🌐 Abrir en navegador")
        self.open_btn.setObjectName("secondary")
        self.open_btn.clicked.connect(self._open_html)
        self.open_btn.setEnabled(False)
        bf.addWidget(self.open_btn)

        self.open_folder_btn = QPushButton("📂 Abrir carpeta")
        self.open_folder_btn.setObjectName("secondary")
        self.open_folder_btn.clicked.connect(self._open_folder)
        self.open_folder_btn.setEnabled(False)
        bf.addWidget(self.open_folder_btn)

        self.cal_summary = QLabel("")
        self.cal_summary.setStyleSheet(f"color: {C_SLATE};")
        bf.addStretch()
        bf.addWidget(self.cal_summary)
        v.addLayout(bf)

        self.cal_scroll = QScrollArea()
        self.cal_scroll.setWidgetResizable(True)
        self.cal_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cal_container = QWidget()
        self.cal_layout = QVBoxLayout(self.cal_container)
        self.cal_layout.setContentsMargins(0, 0, 0, 0)
        self.cal_scroll.setWidget(self.cal_container)
        v.addWidget(self.cal_scroll, 1)

        empty = QLabel("📭 Aún no hay cuadrante.\nVe a ⚙️ Generar y pulsa el botón.")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setStyleSheet(f"color: {C_SLATE}; font-size: 15px;")
        self.cal_layout.addWidget(empty)

    # ── Helpers ────────────────────────────────────────────────────────
    def _sep(self):
        s = QFrame()
        s.setObjectName("sep")
        s.setFixedHeight(1)
        return s

    def _teacher_color(self, name):
        idx = next((i for i, t in enumerate(self.teachers) if t["name"] == name), 0) % len(TEACHER_COLORS)
        return TEACHER_COLORS[idx]

    @staticmethod
    def _rgba(hexc, alpha=0.13):
        h = hexc.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    def _rebuild_teacher_list(self):
        while self.teacher_list_layout.count() > 1:
            item = self.teacher_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for i, t in enumerate(self.teachers):
            frame = ClickFrame(i)
            if i == self._selected_teacher_idx:
                frame.setObjectName("row_selected")
            else:
                frame.setObjectName("row")
            frame.setStyleSheet("")  # let QSS handle it
            frame.setCursor(Qt.CursorShape.PointingHandCursor)
            frame.clicked.connect(self._select_teacher)

            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 6, 10, 6)
            color = self._teacher_color(t["name"])
            n_slots = len(t.get("time_slots", []))
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 18px;")
            row.addWidget(dot)
            txt = QLabel(f"👤 {t['name']:16s}  ⏱ {t['max_hours']}h  📅 {t['max_hours_per_day']}h/d  🗓 {n_slots} franjas")
            row.addWidget(txt, 1)
            del_btn = QPushButton("✕")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.clicked.connect(lambda checked, idx=i: self._delete_teacher(idx))
            row.addWidget(del_btn)

            self.teacher_list_layout.insertWidget(self.teacher_list_layout.count()-1, frame)

        self.teacher_count.setText(f"{len(self.teachers)} profesores")

    def _select_teacher(self, idx):
        if idx >= len(self.teachers): return
        self._selected_teacher_idx = idx
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()

    def _refresh_tslot_panel(self):
        while self.tslot_layout.count() > 1:
            item = self.tslot_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.tslot_header.setText("Franjas disponibles: (ningún profe seleccionado)")
            empty = QLabel("Selecciona un profe de la lista para gestionar sus franjas.")
            empty.setStyleSheet(f"color: {C_SLATE};")
            self.tslot_layout.insertWidget(0, empty)
            return

        t = self.teachers[self._selected_teacher_idx]
        self.tslot_header.setText(f"Franjas de: {t['name']}  ({len(t.get('time_slots', []))} franjas)")

        for s in t.get("time_slots", []):
            frame = QFrame()
            frame.setObjectName("slot_row")
            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 4, 10, 4)
            row.addWidget(QLabel(_fmt_slot(s)))
            del_btn = QPushButton("✕")
            del_btn.setFixedSize(24, 24)
            del_btn.setObjectName("danger")
            del_btn.clicked.connect(lambda checked, ref=s: self._delete_tslot(ref))
            row.addWidget(del_btn, alignment=Qt.AlignmentFlag.AlignRight)
            row.addStretch()
            self.tslot_layout.insertWidget(self.tslot_layout.count()-1, frame)

    def _update_stats(self):
        n_slots = sum(len(t.get("time_slots", [])) for t in self.teachers)
        n_need_s = len(self.needs)
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

    # ── Teacher actions ────────────────────────────────────────────────
    def _add_teacher(self):
        name = self.t_name.text().strip()
        if not name:
            self.toast.show("Nombre obligatorio", "warning"); return
        try:
            mx = int(self.t_max.text())
            mxd = int(self.t_maxd.text())
        except ValueError:
            self.toast.show("Límites deben ser enteros", "warning"); return
        self.teachers.append({"name": name, "max_hours": mx, "max_hours_per_day": mxd, "time_slots": []})
        _save_teachers(self.teachers)
        self._selected_teacher_idx = len(self.teachers) - 1
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()
        self._update_stats()
        self.t_name.clear()
        self.toast.show(f"Profe «{name}» añadido")

    def _delete_teacher(self, idx):
        if idx >= len(self.teachers): return
        self.teachers.pop(idx)
        _save_teachers(self.teachers)
        if self._selected_teacher_idx is not None:
            if self._selected_teacher_idx >= len(self.teachers):
                self._selected_teacher_idx = len(self.teachers) - 1 if self.teachers else None
            elif self._selected_teacher_idx == idx:
                self._selected_teacher_idx = min(idx, len(self.teachers)-1) if self.teachers else None
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()
        self._update_stats()

    def _add_tslot_preset(self, start, end):
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        date = self.tslot_date.date().toString("yyyy-MM-dd")
        slot = {"date": date, "start": start, "end": end}
        self.teachers[self._selected_teacher_idx].setdefault("time_slots", []).append(slot)
        _save_teachers(self.teachers)
        self._refresh_tslot_panel()
        self._rebuild_teacher_list()
        self._update_stats()
        self.toast.show(f"✅ Franja {start}-{end} añadida", "success")

    def _add_tslot_custom_dialog(self):
        if self._selected_teacher_idx is None or self._selected_teacher_idx >= len(self.teachers):
            self.toast.show("Selecciona un profe primero", "warning"); return
        d = QDialog(self)
        d.setWindowTitle("➕ Franja personalizada")
        d.setMinimumWidth(320)
        fl = QFormLayout(d)
        start_ed = QLineEdit("09:00")
        end_ed = QLineEdit("10:00")
        fl.addRow("🕐 De:", start_ed)
        fl.addRow("🕐 A:", end_ed)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        fl.addRow(bb)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        date = self.tslot_date.date().toString("yyyy-MM-dd")
        start = start_ed.text().strip()
        end = end_ed.text().strip()
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

    def _delete_tslot(self, slot):
        if self._selected_teacher_idx is not None and self._selected_teacher_idx < len(self.teachers):
            t = self.teachers[self._selected_teacher_idx]
            t["time_slots"] = [s for s in t["time_slots"] if s is not slot]
            _save_teachers(self.teachers)
            self._refresh_tslot_panel()
            self._rebuild_teacher_list()
            self._update_stats()

    # ── Need actions ───────────────────────────────────────────────────
    def _add_need(self):
        name = self.nd_name.text().strip()
        date = self.nd_date.text().strip()
        start = self.nd_start.text().strip()
        end = self.nd_end.text().strip()
        try:
            mn, mx = int(self.nd_min.text()), int(self.nd_max.text())
        except ValueError:
            self.toast.show("Min/Max deben ser enteros", "warning"); return
        if not name:
            self.toast.show("Nombre obligatorio", "warning"); return
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            self.toast.show("Fecha debe ser YYYY-MM-DD", "warning"); return
        if not re.match(r"^\d{2}:\d{2}$", start) or not re.match(r"^\d{2}:\d{2}$", end):
            self.toast.show("Hora debe ser HH:MM", "warning"); return
        if start >= end:
            self.toast.show("Inicio debe ser anterior a fin", "warning"); return
        if mn < 1 or mx < mn:
            self.toast.show("Min/Max inválidos", "warning"); return
        self.needs.append({"name": name, "date": date, "start": start, "end": end, "min": mn, "max": mx})
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()
        self.nd_name.clear()
        self.toast.show(f"Necesidad «{name}» añadida")

    def _delete_need(self, n):
        self.needs = [x for x in self.needs if x is not n]
        self._rebuild_need_list()
        self._mark_dirty()
        self._update_stats()

    def _rebuild_need_list(self):
        while self.need_layout.count() > 1:
            item = self.need_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for n in self.needs:
            frame = QFrame()
            frame.setObjectName("need_row")
            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 4, 10, 4)
            dsp = f"{_fmt_slot(n)}  |  👤 [{n['min']}-{n['max']}] profes"
            lbl = QLabel(f"📋 <b>{n['name']}</b>  —  {dsp}")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            row.addWidget(lbl, 1)
            del_btn = QPushButton("✕")
            del_btn.setFixedSize(24, 24)
            del_btn.setObjectName("danger")
            del_btn.clicked.connect(lambda checked, ref=n: self._delete_need(ref))
            row.addWidget(del_btn)
            self.need_layout.insertWidget(self.need_layout.count()-1, frame)

        self.need_count.setText(f"{len(self.needs)} necesidades")

    # ── Project actions ────────────────────────────────────────────────
    def _refresh_project_list(self):
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
        if choice in ("(ninguno)", ""): return
        self._save_current(silent=True)
        self._load_project_data(choice)

    def _new_project(self):
        self._save_current(silent=True)
        self.project_name_input.clear()
        self.needs = []
        self._dirty = False
        self._dirty_label.setText("")
        self._rebuild_need_list()
        self._update_stats()
        self.project_name_input.setText("Nuevo proyecto")
        self._mark_dirty()
        self.toast.show("Nuevo proyecto creado")

    def _duplicate_project(self):
        if not self.project_name_input.text().strip():
            self.toast.show("Guarda el proyecto antes de duplicar", "warning"); return
        base = self.project_name_input.text().strip()
        self.project_name_input.setText(f"{base} (copia)")
        self._mark_dirty()
        self._save_current(silent=False)

    def _save_current(self, silent=False):
        name = self.project_name_input.text().strip()
        if not name:
            self.toast.show("Escribe un nombre para guardar", "warning"); return
        _save_project(name, self.needs)
        self._dirty = False
        self._dirty_label.setText("")
        self._refresh_project_list()
        if not silent:
            self.toast.show(f"Proyecto «{name}» guardado")

    def _delete_project(self):
        name = self.project_selector.currentText()
        if name in ("(ninguno)", ""): return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar el proyecto «{name}»?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            _delete_project_file(name)
            self._refresh_project_list()
            self.toast.show("Proyecto eliminado")

    def _load_project_data(self, name):
        try:
            data = _load_project(name)
        except Exception as e:
            self.toast.show(f"Error al cargar: {e}", "error"); return
        self.project_name_input.setText(data.get("name", name))
        self.needs = [dict(n) for n in data.get("needs", [])]
        self._dirty = False
        self._dirty_label.setText("")
        self._rebuild_need_list()
        self._update_stats()

    def _mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self._dirty_label.setText("⚠️ Sin guardar")
        self._update_stats()

    def _load_seed(self):
        self.teachers = get_seed_teachers()
        _save_teachers(self.teachers)
        ndata = get_seed_needs()
        self.project_name_input.setText("XarxaLlibres 2026 - Recogida y distribución")
        self.needs = [dict(n) for n in ndata]
        self._selected_teacher_idx = 0 if self.teachers else None
        self._rebuild_teacher_list()
        self._rebuild_need_list()
        self._mark_dirty()
        self.toast.show("Datos XarxaLlibres cargados (8 profesores, 25 tareas)")

    # ── Generate ───────────────────────────────────────────────────────
    def _generate(self):
        """Genera múltiples opciones de cuadrante y deja elegir al usuario.

        Flujo:
        1. Validaciones básicas (profesores, necesidades, franjas)
        2. Construye el modelo CP-SAT una sola vez
        3. Llama a solve_multiple() que ejecuta el solver con varias semillas
        4. Muestra las opciones en MultiOptionDialog
        5. El usuario elige una opción
        6. Genera el HTML y muestra el cuadrante con la opción seleccionada
        """
        # ---------------------------------------------------------------
        # Validaciones previas
        # ---------------------------------------------------------------
        if not self.teachers:
            self.toast.show("Añade al menos un profesor", "warning"); return
        if not self.needs:
            self.toast.show("Añade al menos una necesidad", "warning"); return
        total_avail = sum(len(t.get("time_slots", [])) for t in self.teachers)
        if total_avail == 0:
            self.toast.show("Los profes necesitan franjas disponibles", "warning"); return

        pname = self.project_name_input.text().strip() or "(sin nombre)"

        # ---------------------------------------------------------------
        # Log de cabecera
        # ---------------------------------------------------------------
        self._log(f"\n{'='*60}")
        self._log(f"Proyecto: {pname}")
        self._log(f"Profesores: {len(self.teachers)}")
        self._log(f"Necesidades: {len(self.needs)}  |  "
                  f"H. mín necesarias: {sum(n['min'] * duration_min(n) for n in self.needs) // 60}h")
        self._log(f"Franjas disponibilidad totales profes: {total_avail}")

        # ---------------------------------------------------------------
        # Construcción del modelo (solo una vez)
        # ---------------------------------------------------------------
        self._log("Construyendo modelo CP-SAT...")
        scheduler = TeacherScheduler(self.teachers, self.needs)
        scheduler.build_model()

        # ---------------------------------------------------------------
        # Generación de múltiples opciones
        # ---------------------------------------------------------------
        self._log("Generando opciones (5 variantes con distintas semillas)...")
        self.status_text.repaint()  # Forzar actualización visual

        # Número de opciones a generar
        num_opciones = 5
        opciones = scheduler.solve_multiple(n_options=num_opciones, time_limit=10)

        # Filtra opciones válidas (con asignaciones)
        opciones = [op for op in opciones if op["n_assignments"] > 0]

        if not opciones:
            self._log("❌ Sin solución en ninguna variante. Añade más profes o franjas, o relaja límites.")
            self.toast.show("Sin solución posible", "error"); return

        self._log(f"✅ Se generaron {len(opciones)} opciones distintas")
        for op in opciones:
            self._log(f"   Opción {op['id']}: {op['n_assignments']} asignaciones, "
                      f"{op['n_covered']}/{op['total_needs']} necesidades, "
                      f"{op['total_minutes'] // 60}h{op['total_minutes'] % 60:02d}m totales")

        # ---------------------------------------------------------------
        # Diálogo de selección (si hay más de una opción)
        # ---------------------------------------------------------------
        if len(opciones) == 1:
            # Una sola opción: la usamos directamente
            opcion_elegida = opciones[0]
            self._log("→ Solo hay una opción disponible, se usará automáticamente")
        else:
            # Múltiples opciones: mostramos el diálogo para que elija
            self._log("→ Mostrando selector de opciones...")
            dialog = MultiOptionDialog(opciones, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                self._log("❌ Selección cancelada por el usuario")
                self.toast.show("Generación cancelada", "warning")
                return
            opcion_elegida = dialog.selected_option
            if opcion_elegida is None:
                return
            self._log(f"→ Opción {opcion_elegida['id']} seleccionada")

        # ---------------------------------------------------------------
        # Procesar la opción elegida
        # ---------------------------------------------------------------
        assignment = opcion_elegida["assignment"]
        self.last_assignment = assignment

        # Log detallado de la opción elegida
        self._log(f"\n✅ Opción {opcion_elegida['id']} — {len(assignment)} asignaciones")
        self._log("Carga por profesor:")
        for name in sorted(opcion_elegida['teacher_hours'].keys()):
            mins = opcion_elegida['teacher_hours'][name]
            h = mins // 60; m = mins % 60
            self._log(f"  {name}: {h}h {m:02d}m")

        self._log("Asignaciones detalladas:")
        for a in sorted(assignment, key=lambda x: (x["need"]["date"], x["need"]["start"], x["teacher"]["name"])):
            self._log(f"  {a['need']['date']} {a['need']['start']}-{a['need']['end']}  |  "
                      f"{a['need']['name'][:30]:30s}  |  {a['teacher']['name']}")

        # ---------------------------------------------------------------
        # Exportar HTML con la opción elegida
        # ---------------------------------------------------------------
        out_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(out_dir, exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", pname)
        filename = f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(out_dir, filename)
        export_html_file(pname, self.teachers, self.needs, assignment, path)
        self.last_html_path = path
        self._log(f"\n✅ HTML: {path}")
        self.toast.show("Cuadrante generado con éxito")

        # Cambia a la pestaña de cuadrante
        self.tabs.setCurrentIndex(4)
        self._update_schedule_tab()

    def _log(self, msg):
        self.status_text.append(msg)
        # scroll to bottom
        sb = self.status_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Schedule ───────────────────────────────────────────────────────
    def _update_schedule_tab(self):
        while self.cal_layout.count():
            item = self.cal_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not self.last_assignment:
            return

        self.open_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)

        a = self.last_assignment
        groups = {}
        for x in sorted(a, key=lambda x: (x["need"]["date"], x["need"]["start"])):
            key = x["need_idx"]
            if key not in groups:
                groups[key] = {"need": x["need"], "teachers": []}
            groups[key]["teachers"].append(x["teacher"]["name"])
        unique_needs = len({x["need_idx"] for x in a})
        self.cal_summary.setText(f"📋 {len(self.needs)} neces. · ✅ {unique_needs} cubiertas · "
                                 f"👨‍🏫 {len(self.teachers)} profes · 📌 {len(a)} asignaciones")

        dates = sorted({n["date"] for n in self.needs})
        if not dates:
            return

        cal_frame = QFrame()
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

            col = QFrame()
            col.setObjectName("card")
            col.setStyleSheet("")
            col.setMinimumWidth(260)
            col_v = QVBoxLayout(col)
            col_v.setContentsMargins(8, 8, 8, 8)
            col_v.setSpacing(6)

            # Day header
            hdr_frame = QFrame()
            hdr_color = C_PRI
            hdr_frame.setStyleSheet(f"background: {hdr_color}; border-radius: 6px;")
            hdr_frame.setFixedHeight(64)
            hdr_v = QVBoxLayout(hdr_frame)
            hdr_v.setContentsMargins(0, 6, 0, 4)
            hdr_v.setSpacing(0)
            num_lbl = QLabel(day_num)
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num_lbl.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
            hdr_v.addWidget(num_lbl)
            name_lbl = QLabel(day_name[:3].upper())
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 10px; font-weight: bold;")
            hdr_v.addWidget(name_lbl)
            col_v.addWidget(hdr_frame)

            day_needs = sorted(
                [(i, g) for i, g in groups.items() if g["need"]["date"] == day],
                key=lambda x: x[1]["need"]["start"]
            )

            if not day_needs:
                empty = QLabel("—")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty.setStyleSheet(f"color: {C_SLATE}; padding: 20px;")
                col_v.addWidget(empty)
            else:
                for ni, g in day_needs:
                    n = g["need"]
                    assigned = sorted(g["teachers"]) if g["teachers"] else []

                    card = QFrame()
                    card.setObjectName("card")
                    card.setStyleSheet("")
                    card_v = QVBoxLayout(card)
                    card_v.setContentsMargins(8, 6, 8, 6)
                    card_v.setSpacing(2)

                    # Time badge
                    time_lbl = QLabel(f"{n['start']} - {n['end']}")
                    time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    time_lbl.setStyleSheet(f"background: {C_PRI}; color: white; border-radius: 4px; padding: 2px; font-weight: bold; font-size: 10px;")
                    card_v.addWidget(time_lbl)

                    name_lbl = QLabel(n["name"])
                    name_lbl.setWordWrap(True)
                    name_lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
                    card_v.addWidget(name_lbl)

                    req_lbl = QLabel(f"min {n['min']} · max {n['max']}")
                    req_lbl.setStyleSheet(f"color: {C_SLATE}; font-size: 10px;")
                    card_v.addWidget(req_lbl)

                    if assigned:
                        for tname in assigned:
                            c = self._teacher_color(tname)
                            tlabel = QLabel(f"  {tname}  ")
                            tlabel.setStyleSheet(f"color: {c}; background: {self._rgba(c, 0.12)}; border-radius: 4px; padding: 1px 6px; font-weight: bold; font-size: 10px;")
                            card_v.addWidget(tlabel)

                    col_v.addWidget(card)

            cal_lay.addWidget(col)

        self.cal_layout.addWidget(cal_frame)

    # ── Open ───────────────────────────────────────────────────────────
    def _open_html(self):
        if self.last_html_path and os.path.exists(self.last_html_path):
            webbrowser.open(f"file://{os.path.abspath(self.last_html_path)}")

    def _open_folder(self):
        if self.last_html_path:
            os.startfile(os.path.dirname(os.path.abspath(self.last_html_path)))
