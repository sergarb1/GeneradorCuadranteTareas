import json, os, re, webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTabWidget, QScrollArea, QFrame, QTextEdit, QSizePolicy,
    QMessageBox, QDateEdit, QDialog, QFormLayout, QDialogButtonBox,
    QButtonGroup, QRadioButton, QFileDialog  # Para el selector de opciones múltiples
)
from PyQt6.QtCore import Qt, QTimer, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QColor
from PyQt6.QtWidgets import QColorDialog, QInputDialog

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
QPushButton#danger {{ background: transparent; color: {C_RED}; border: none; padding: 4px 8px; border-radius: 4px; font-size: 14px; }}
QPushButton#danger:hover {{ background: #fee2e2; }}
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
QPushButton#danger {{ background: transparent; color: {C_RED}; border: none; padding: 4px 8px; border-radius: 4px; font-size: 14px; }}
QPushButton#danger:hover {{ background: #450a0a; }}
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
    gp = _generated_options_filename(name)
    if os.path.exists(gp): os.remove(gp)

def _generated_options_filename(name):
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip() or "sin_titulo")
    return os.path.join(PROJECTS_DIR, f"{safe}_generated.json")

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
    clicked = pyqtSignal(int, int)
    def __init__(self, a=0, b=0, parent=None):
        super().__init__(parent)
        self.a = a
        self.b = b
    def mousePressEvent(self, e):
        self.clicked.emit(self.a, self.b)
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
        cancelar.setObjectName("secondary")
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
        self.setMinimumSize(1200, 720)
        self.resize(1400, 800)

        self.teachers = _load_teachers()
        self.needs = []
        self.project_name = ""
        self.last_assignment = None
        self.last_html_path = None
        self.generated_options = []
        self.generated_html_paths = []
        self.current_option_index = 0
        self._dirty = False
        self._selected_teacher_idx = None
        self._dark_mode = False
        self._undo_stack = []
        self._redo_stack = []
        self._compact_view = False
        self._locked_assignments = {}       # {(need_idx, teacher_idx): bool}
        self._teacher_filter = ""
        self._need_filter = ""
        self._tslot_templates = []

        self._build_ui()
        self._apply_theme()
        self._refresh_project_list()
        self._rebuild_teacher_list()
        self._update_stats()

        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(120000)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start()

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
        btn("🗑️ Eliminar", None, self._delete_project, "secondary")
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
        btn_imp_proj = QPushButton("📥 Importar proyecto...")
        btn_imp_proj.setObjectName("secondary")
        btn_imp_proj.clicked.connect(self._import_project)
        bf.addWidget(btn_imp_proj)
        btn_exp_proj = QPushButton("📤 Exportar proyecto")
        btn_exp_proj.setObjectName("secondary")
        btn_exp_proj.clicked.connect(self._export_project)
        bf.addWidget(btn_exp_proj)
        btn_csv = QPushButton("📊 Exportar CSV")
        btn_csv.setObjectName("secondary")
        btn_csv.clicked.connect(self._export_csv)
        bf.addWidget(btn_csv)
        btn_undo = QPushButton("↩️")
        btn_undo.setFixedWidth(36)
        btn_undo.setObjectName("secondary")
        btn_undo.setToolTip("Deshacer")
        btn_undo.clicked.connect(self._undo)
        bf.addWidget(btn_undo)
        btn_redo = QPushButton("🔁")
        btn_redo.setFixedWidth(36)
        btn_redo.setObjectName("secondary")
        btn_redo.setToolTip("Rehacer")
        btn_redo.clicked.connect(self._redo)
        bf.addWidget(btn_redo)
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
            "4. ⚙️ Genera el cuadrante — el solver CP-SAT genera 10 opciones y tú eliges la mejor\n"
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

        ie_teachers = QHBoxLayout()
        btn_imp_t = QPushButton("📥 Importar profesores...")
        btn_imp_t.setObjectName("secondary")
        btn_imp_t.clicked.connect(self._import_teachers)
        ie_teachers.addWidget(btn_imp_t)
        btn_exp_t = QPushButton("📤 Exportar profesores")
        btn_exp_t.setObjectName("secondary")
        btn_exp_t.clicked.connect(self._export_teachers)
        ie_teachers.addWidget(btn_exp_t)
        ie_teachers.addStretch()
        v.addLayout(ie_teachers)

        # Add teacher form
        f = QHBoxLayout()
        f.addWidget(QLabel("👤 Nombre:"))
        self.t_name = QLineEdit(); self.t_name.setPlaceholderText("Nombre del profe")
        f.addWidget(self.t_name)
        f.addSpacing(4)
        f.addWidget(QLabel("⏱ Max tot:"))
        self.t_max = QLineEdit("20"); self.t_max.setFixedWidth(40)
        f.addWidget(self.t_max)
        f.addSpacing(4)
        f.addWidget(QLabel("Max/día:"))
        self.t_maxd = QLineEdit("6"); self.t_maxd.setFixedWidth(36)
        f.addWidget(self.t_maxd)
        f.addSpacing(4)
        f.addWidget(QLabel("Turno:"))
        self.t_turno = QComboBox()
        self.t_turno.addItems(["Cualquiera", "Mañana", "Tarde"])
        self.t_turno.setFixedWidth(100)
        f.addWidget(self.t_turno)
        f.addSpacing(4)
        self.t_color_btn = QPushButton("🎨")
        self.t_color_btn.setFixedWidth(32)
        self.t_color_btn.setToolTip("Color personalizado")
        self.t_color_btn.clicked.connect(self._pick_teacher_color)
        f.addWidget(self.t_color_btn)
        self._teacher_color_pick = C_PRI
        f.addSpacing(4)
        btn = QPushButton("➕ Añadir profe")
        btn.clicked.connect(self._add_teacher)
        f.addWidget(btn)
        f.addStretch()
        v.addLayout(f)

        search_teach = QHBoxLayout()
        self.teacher_count = QLabel("0 profesores")
        self.teacher_count.setStyleSheet("font-weight: bold;")
        search_teach.addWidget(self.teacher_count)
        search_teach.addStretch()
        self.teacher_search = QLineEdit()
        self.teacher_search.setPlaceholderText("🔍 Filtrar profes...")
        self.teacher_search.setFixedWidth(200)
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
        presets.addSpacing(8)
        btn_save_t = QPushButton("💾 Guardar plantilla")
        btn_save_t.setObjectName("secondary")
        btn_save_t.clicked.connect(self._save_tslot_template)
        presets.addWidget(btn_save_t)
        btn_load_t = QPushButton("📂 Cargar plantilla")
        btn_load_t.setObjectName("secondary")
        btn_load_t.clicked.connect(self._load_tslot_template)
        presets.addWidget(btn_load_t)
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

        ie_needs = QHBoxLayout()
        btn_imp_n = QPushButton("📥 Importar necesidades...")
        btn_imp_n.setObjectName("secondary")
        btn_imp_n.clicked.connect(self._import_needs)
        ie_needs.addWidget(btn_imp_n)
        btn_exp_n = QPushButton("📤 Exportar necesidades")
        btn_exp_n.setObjectName("secondary")
        btn_exp_n.clicked.connect(self._export_needs)
        ie_needs.addWidget(btn_exp_n)
        ie_needs.addStretch()
        v.addLayout(ie_needs)

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

        search_needs = QHBoxLayout()
        self.need_count = QLabel("📋 0 necesidades")
        self.need_count.setStyleSheet("font-weight: bold;")
        search_needs.addWidget(self.need_count)
        search_needs.addStretch()
        self.need_search = QLineEdit()
        self.need_search.setPlaceholderText("🔍 Filtrar necesidades...")
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

    # ── Generate Tab ───────────────────────────────────────────────────
    def _build_generate_tab(self):
        sa, tab = self._tab_widget(True)
        self.tabs.addTab(sa, "⚙️ Generar")
        v = QVBoxLayout(tab)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        v.addWidget(QLabel("⚙️ Generar cuadrante de apoyo"))

        info_multi = QLabel(
            "🧠 El solver genera 10 opciones distintas (variando la semilla de búsqueda).\n"
            "Una vez generadas, cambia entre ellas libremente desde la pestaña 📅 Cuadrante."
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
        self.status_text.append("🔁 El solver probará 10 semillas distintas y podrás cambiar entre opciones.\n")
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

        self.stats_btn = QPushButton("📊 Stats")
        self.stats_btn.setObjectName("secondary")
        self.stats_btn.clicked.connect(self._show_stats)
        self.stats_btn.setEnabled(False)
        bf.addWidget(self.stats_btn)

        self.compact_btn = QPushButton("📅 Vista compacta")
        self.compact_btn.setObjectName("secondary")
        self.compact_btn.clicked.connect(self._toggle_compact_view)
        self.compact_btn.setEnabled(False)
        bf.addWidget(self.compact_btn)

        self.lock_regenerate_btn = QPushButton("🔒 Regenerar con bloqueos")
        self.lock_regenerate_btn.setObjectName("secondary")
        self.lock_regenerate_btn.clicked.connect(self._regenerate_with_locks)
        self.lock_regenerate_btn.setEnabled(False)
        bf.addWidget(self.lock_regenerate_btn)

        self.png_btn = QPushButton("🖼️ PNG")
        self.png_btn.setObjectName("secondary")
        self.png_btn.clicked.connect(self._export_png)
        self.png_btn.setEnabled(False)
        bf.addWidget(self.png_btn)

        bf.addSpacing(24)

        # Navegación entre opciones
        self.nav_prev_btn = QPushButton("◀")
        self.nav_prev_btn.setFixedWidth(36)
        self.nav_prev_btn.setObjectName("secondary")
        self.nav_prev_btn.clicked.connect(self._prev_option)
        self.nav_prev_btn.setEnabled(False)
        bf.addWidget(self.nav_prev_btn)

        self.nav_label = QLabel("")
        self.nav_label.setStyleSheet(f"font-weight: bold; color: {C_PRI}; font-size: 13px;")
        bf.addWidget(self.nav_label)

        self.nav_next_btn = QPushButton("▶")
        self.nav_next_btn.setFixedWidth(36)
        self.nav_next_btn.setObjectName("secondary")
        self.nav_next_btn.clicked.connect(self._next_option)
        self.nav_next_btn.setEnabled(False)
        bf.addWidget(self.nav_next_btn)

        bf.addStretch()

        self.cal_summary = QLabel("")
        self.cal_summary.setStyleSheet(f"color: {C_SLATE};")
        bf.addWidget(self.cal_summary)
        v.addLayout(bf)

        self.cal_scroll = QScrollArea()
        self.cal_scroll.setWidgetResizable(True)
        self.cal_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cal_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
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
        for t in self.teachers:
            if t["name"] == name and t.get("color"):
                return t["color"]
        idx = next((i for i, t in enumerate(self.teachers) if t["name"] == name), 0) % len(TEACHER_COLORS)
        return TEACHER_COLORS[idx]

    @staticmethod
    def _rgba(hexc, alpha=0.13):
        h = hexc.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    def _rebuild_teacher_list(self):
        filtro = self.teacher_search.text().strip().lower()
        while self.teacher_list_layout.count() > 1:
            item = self.teacher_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        shown = 0
        for i, t in enumerate(self.teachers):
            if filtro and filtro not in t["name"].lower():
                continue
            shown += 1
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
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 18px;")
            row.addWidget(dot)
            pref = t.get("preferred_tasks", [])
            pref_str = f"  ⭐ {len(pref)} pref." if pref else ""
            txt = QLabel(f"👤 {t['name']:16s}  ⏱ {t['max_hours']}h  📅 {t['max_hours_per_day']}h/d  🗓 {n_slots} franjas  {turno_icon.get(turno, '⏰')} {turno}{pref_str}")
            row.addWidget(txt, 1)
            del_btn = QPushButton("❌")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.setToolTip("Eliminar profesor")
            del_btn.clicked.connect(lambda checked, idx=i: self._delete_teacher(idx))
            row.addWidget(del_btn)

            self.teacher_list_layout.insertWidget(self.teacher_list_layout.count()-1, frame)

        self.teacher_count.setText(f"{shown} profesores (de {len(self.teachers)})" if filtro else f"{len(self.teachers)} profesores")

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
            del_btn = QPushButton("❌")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.setToolTip("Eliminar franja")
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
        turno = self.t_turno.currentText()
        color = self._teacher_color_pick
        self.teachers.append({
            "name": name, "max_hours": mx, "max_hours_per_day": mxd,
            "time_slots": [], "turno": turno, "color": color
        })
        _save_teachers(self.teachers)
        self._selected_teacher_idx = len(self.teachers) - 1
        self._rebuild_teacher_list()
        self._refresh_tslot_panel()
        self._update_stats()
        self.t_name.clear()
        self._teacher_color_pick = TEACHER_COLORS[len(self.teachers) % len(TEACHER_COLORS)]
        self.toast.show(f"Profe «{name}» añadido")

    def _pick_teacher_color(self):
        color = QColorDialog.getColor(QColor(self._teacher_color_pick), self, "Color del profesor")
        if color.isValid():
            self._teacher_color_pick = color.name()
            self.t_color_btn.setStyleSheet(f"background: {self._teacher_color_pick}; border-radius: 4px;")

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

    def _save_tslot_template(self):
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
        filtro = self.need_search.text().strip().lower()
        while self.need_layout.count() > 1:
            item = self.need_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        shown = 0
        for n in self.needs:
            if filtro and filtro not in n["name"].lower() and filtro not in n.get("date", ""):
                continue
            shown += 1
            frame = QFrame()
            frame.setObjectName("need_row")
            row = QHBoxLayout(frame)
            row.setContentsMargins(10, 4, 10, 4)
            dsp = f"{_fmt_slot(n)}  |  👤 [{n['min']}-{n['max']}] profes"
            lbl = QLabel(f"📋 <b>{n['name']}</b>  —  {dsp}")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            row.addWidget(lbl, 1)
            del_btn = QPushButton("❌")
            del_btn.setFixedSize(28, 28)
            del_btn.setObjectName("danger")
            del_btn.setToolTip("Eliminar necesidad")
            del_btn.clicked.connect(lambda checked, ref=n: self._delete_need(ref))
            row.addWidget(del_btn)
            self.need_layout.insertWidget(self.need_layout.count()-1, frame)

        self.need_count.setText(f"{shown} necesidades (de {len(self.needs)})" if filtro else f"{len(self.needs)} necesidades")

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

        # Cargar opciones generadas guardadas
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
        self.toast.show("Datos XarxaLlibres cargados (8 profesores, 25 tareas)")

    # ── Import / Export ─────────────────────────────────────────────────
    def _import_teachers(self):
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
        path, _ = QFileDialog.getOpenFileName(self, "Importar proyecto", "", "JSON (*.json)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.toast.show("Usa 'Importar necesidades' para arrays directos", "warning"); return
            pname = data.get("project_name") or data.get("name", "")
            if not pname:
                self.toast.show("El archivo debe tener 'project_name' o 'name'", "error"); return
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
        if not self.last_assignment:
            self.toast.show("Genera un cuadrante primero", "warning"); return
        d = QDialog(self)
        d.setWindowTitle("📊 Estadísticas")
        d.setMinimumSize(500, 400)
        v = QVBoxLayout(d)
        v.setSpacing(10)
        v.setContentsMargins(20, 16, 20, 16)
        total_min = sum(duration_min(a["need"]) for a in self.last_assignment)
        unique = len({a["need_idx"] for a in self.last_assignment})
        teacher_mins = {}
        for a in self.last_assignment:
            name = a["teacher"]["name"]
            teacher_mins[name] = teacher_mins.get(name, 0) + duration_min(a["need"])
        stats_text = f"""📊 <b>Estadísticas del cuadrante</b><br><br>
📋 Total necesidades: {len(self.needs)}<br>
✅ Necesidades cubiertas: {unique}<br>
📌 Asignaciones totales: {len(self.last_assignment)}<br>
⏱ Horas totales asignadas: {total_min // 60}h {total_min % 60:02d}m<br><br>
<b>Carga por profesor:</b><br>"""
        for name in sorted(teacher_mins.keys()):
            m = teacher_mins[name]
            hh = m // 60
            mm = m % 60
            stats_text += f"  {name}: {hh}h {mm:02d}m<br>"
        lbl = QLabel(stats_text)
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lbl.setWordWrap(True)
        v.addWidget(lbl)
        avail_min = sum(duration_min(s) for t in self.teachers for s in t.get("time_slots", []))
        need_min = sum(n["min"] * duration_min(n) for n in self.needs)
        cov_text = f"""<br><b>Cobertura:</b><br>
👨‍🏫 Total profes: {len(self.teachers)}<br>
⏰ Horas disponibles: {avail_min // 60}h<br>
📋 Horas mínimas necesarias: {need_min // 60}h<br>
📊 Cobertura: {total_min}/{avail_min}h ({total_min*100//max(avail_min,1)}%)"""
        lbl2 = QLabel(cov_text)
        lbl2.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(lbl2)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        bb.accepted.connect(d.accept)
        v.addWidget(bb)
        d.exec()

    def _toggle_compact_view(self):
        self._compact_view = not self._compact_view
        self._update_schedule_tab()
        self.toast.show(f"Vista {'compacta' if self._compact_view else 'normal'}")

    def _toggle_lock(self, need_idx, teacher_idx):
        key = (need_idx, teacher_idx)
        if key in self._locked_assignments:
            del self._locked_assignments[key]
            self.toast.show("🔓 Bloqueo eliminado")
        else:
            self._locked_assignments[key] = True
            self.toast.show("🔒 Asignación bloqueada")
        self._update_schedule_tab()

    def _regenerate_with_locks(self):
        if not self._locked_assignments:
            self.toast.show("No hay bloqueos activos. Bloquea haciendo clic en un profesor en el cuadrante.", "warning")
            return
        if not self.teachers or not self.needs:
            self.toast.show("Faltan profes o necesidades", "warning"); return
        self._log(f"\n{'='*60}")
        self._log("Regenerando con {len(self._locked_assignments)} bloqueos...")
        scheduler = TeacherScheduler(self.teachers, self.needs)
        scheduler.build_model(locked=self._locked_assignments)
        opciones = scheduler.solve_multiple(n_options=5, time_limit=10)
        opciones = [op for op in opciones if op["n_assignments"] > 0]
        if not opciones:
            self._log("❌ Sin solución posible con los bloqueos actuales.")
            self.toast.show("Sin solución con esos bloqueos", "error"); return
        self.generated_options = opciones
        self.generated_html_paths = []
        self.current_option_index = 0
        self._save_generated_options(opciones)
        self.last_assignment = opciones[0]["assignment"]
        self.last_html_path = None
        self.tabs.setCurrentIndex(4)
        self._update_schedule_tab()
        self._log(f"✅ {len(opciones)} opciones regeneradas con bloqueos")
        self.toast.show(f"✅ Regenerado con {len(self._locked_assignments)} bloqueos")

    def _export_png(self):
        if not self.last_assignment:
            self.toast.show("No hay cuadrante que exportar", "warning"); return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar PNG", "cuadrante.png", "PNG (*.png)")
        if not path: return
        try:
            pixmap = self.cal_container.grab()
            pixmap.save(path, "PNG")
            self.toast.show("PNG guardado")
        except Exception as e:
            self.toast.show(f"Error: {e}", "error")

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
        # Validación previa
        # ---------------------------------------------------------------
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
        scheduler.build_model(locked=self._locked_assignments if self._locked_assignments else None)

        # ---------------------------------------------------------------
        # Generación de múltiples opciones
        # ---------------------------------------------------------------
        self._log("Generando opciones (10 variantes con distintas semillas)...")
        self.status_text.repaint()

        num_opciones = 10
        opciones = scheduler.solve_multiple(n_options=num_opciones, time_limit=10)

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
        # Guardar todas las opciones (sin diálogo modal)
        # ---------------------------------------------------------------
        self._log("→ Guardando todas las opciones...")

        # Exportar HTML para cada opción
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
        self.current_option_index = 0

        # Guardar persistencia
        self._save_generated_options(opciones)

        # Mostrar la primera opción
        primera = opciones[0]
        self.last_assignment = primera["assignment"]
        self.last_html_path = html_paths[0]

        self._log(f"\n✅ Opción {primera['id']} — {len(primera['assignment'])} asignaciones (mostrando primera opción)")
        self._log("Carga por profesor:")
        for name in sorted(primera['teacher_hours'].keys()):
            mins = primera['teacher_hours'][name]
            h = mins // 60; m = mins % 60
            self._log(f"  {name}: {h}h {m:02d}m")

        self._log("Asignaciones detalladas:")
        for a in sorted(primera["assignment"], key=lambda x: (x["need"]["date"], x["need"]["start"], x["teacher"]["name"])):
            self._log(f"  {a['need']['date']} {a['need']['start']}-{a['need']['end']}  |  "
                      f"{a['need']['name'][:30]:30s}  |  {a['teacher']['name']}")

        self._log(f"\n✅ HTML: {html_paths[0]}")
        self.toast.show(f"✅ {len(opciones)} opciones generadas. Cambia entre ellas en 📅 Cuadrante")

        self.tabs.setCurrentIndex(4)
        self._update_schedule_tab()

    def _log(self, msg):
        self.status_text.append(msg)
        sb = self.status_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Persistencia de opciones generadas ─────────────────────────────
    def _save_generated_options(self, options):
        name = self.project_name_input.text().strip()
        if not name:
            return
        try:
            with open(_generated_options_filename(name), "w", encoding="utf-8") as f:
                json.dump(options, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"⚠️ No se pudieron guardar las opciones: {e}")

    def _load_generated_options(self):
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
        if not self.generated_options:
            return
        self.current_option_index = (self.current_option_index - 1) % len(self.generated_options)
        self._show_option(self.current_option_index)

    def _next_option(self):
        if not self.generated_options:
            return
        self.current_option_index = (self.current_option_index + 1) % len(self.generated_options)
        self._show_option(self.current_option_index)

    def _show_option(self, index):
        if not self.generated_options or index < 0 or index >= len(self.generated_options):
            return
        op = self.generated_options[index]
        self.last_assignment = op["assignment"]
        if index < len(self.generated_html_paths):
            self.last_html_path = self.generated_html_paths[index]
        self.current_option_index = index
        self._update_schedule_tab()

    # ── Schedule ───────────────────────────────────────────────────────
    def _update_schedule_tab(self):
        while self.cal_layout.count():
            item = self.cal_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not self.last_assignment:
            return

        self.open_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)
        self.stats_btn.setEnabled(True)
        self.compact_btn.setEnabled(True)
        self.compact_btn.setText("📅 Vista normal" if self._compact_view else "📅 Vista compacta")
        self.lock_regenerate_btn.setEnabled(bool(self._locked_assignments))
        self.png_btn.setEnabled(True)

        # Actualizar navegación
        n_opts = len(self.generated_options)
        has_opts = n_opts > 0
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
                            # Buscar teacher_idx para este nombre y need_idx
                            t_idx = next((ti for ti, t in enumerate(self.teachers) if t["name"] == tname), -1)
                            n_idx = ni
                            is_locked = (n_idx, t_idx) in self._locked_assignments
                            lock_char = "🔒" if is_locked else "🔓"
                            tlabel = ClickFrame(n_idx, t_idx, self)
                            tlabel.setObjectName("card")
                            tlabel.setCursor(Qt.CursorShape.PointingHandCursor)
                            tlabel.setToolTip("Clic para bloquear/desbloquear esta asignación")
                            tlabel_inner = QLabel(f"  {lock_char}  {tname}  ")
                            tlabel_inner.setStyleSheet(f"color: {c}; background: {self._rgba(c, 0.12)}; border-radius: 4px; padding: 1px 6px; font-weight: bold; font-size: 10px;")
                            tlabel_lyt = QVBoxLayout(tlabel)
                            tlabel_lyt.setContentsMargins(0, 0, 0, 0)
                            tlabel_lyt.addWidget(tlabel_inner)
                            tlabel.clicked.connect(self._toggle_lock)
                            card_v.addWidget(tlabel)

                    col_v.addWidget(card)

            cal_lay.addWidget(col)

        self.cal_layout.addWidget(cal_frame)

    # ── Open ───────────────────────────────────────────────────────────
    def _open_html(self):
        if self.last_html_path and os.path.exists(self.last_html_path):
            webbrowser.open(f"file://{os.path.abspath(self.last_html_path)}")
        elif self.last_assignment:
            pname = self.project_name_input.text().strip() or "cuadrante"
            out_dir = os.path.join(BASE_DIR, "output")
            os.makedirs(out_dir, exist_ok=True)
            safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", pname)
            filename = f"{safe}_op{self.current_option_index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            path = os.path.join(out_dir, filename)
            export_html_file(pname, self.teachers, self.needs, self.last_assignment, path)
            self.last_html_path = path
            webbrowser.open(f"file://{os.path.abspath(path)}")

    def _open_folder(self):
        if self.last_html_path:
            os.startfile(os.path.dirname(os.path.abspath(self.last_html_path)))

    # ── Auto-guardado ──────────────────────────────────────────────────
    def _auto_save(self):
        name = self.project_name_input.text().strip()
        if name and self._dirty:
            _save_project(name, self.needs)
            self._dirty = False
            self._dirty_label.setText("")

    # ── Validación previa ──────────────────────────────────────────────
    def _validate_coverage(self):
        warnings = []
        needs_by_date = {}
        for n in self.needs:
            needs_by_date.setdefault(n["date"], []).append(n)
        for day, day_needs in needs_by_date.items():
            avail_teachers = []
            for t in self.teachers:
                if any(s["date"] == day for s in t.get("time_slots", [])):
                    avail_teachers.append(t["name"])
            for n in day_needs:
                can_cover = [t["name"] for t in self.teachers
                             if any(s["date"] == n["date"] and s["start"] <= n["start"] and s["end"] >= n["end"]
                                    for s in t.get("time_slots", []))]
                if len(can_cover) < n["min"]:
                    warnings.append(f"⚠️ «{n['name']}» necesita {n['min']} profes, solo {len(can_cover)} pueden cubrirla")
        avail_min = sum(duration_min(s) for t in self.teachers for s in t.get("time_slots", []))
        need_min = sum(n["min"] * duration_min(n) for n in self.needs)
        if need_min > avail_min:
            warnings.append(f"⏰ Horas necesarias ({need_min // 60}h) superan las disponibles ({avail_min // 60}h)")
        if not self._undo_active():
            self._save_undo()
        return warnings

    def _undo_active(self):
        return hasattr(self, '_undo_stack')

    def _save_undo(self):
        state = {"teachers": [dict(t) for t in self.teachers], "needs": [dict(n) for n in self.needs]}
        self._undo_stack.append(state)
        self._redo_stack.clear()
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _undo(self):
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
