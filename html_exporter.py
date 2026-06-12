# Importaciones necesarias para manejo de fechas y cálculo de duración
from datetime import datetime
from scheduler import duration_min

# Colores corporativos principales (azul y dorado)
GVA_BLUE = "#16a34a"
GVA_GOLD = "#f59e0b"

# Pares de colores (texto/fondo) para distinguir profesores en el cuadrante
TEACHER_COLORS = [
    (GVA_BLUE, "#e0e7ff"),
    ("#ef4444", "#fee2e2"),
    ("#10b981", "#d1fae5"),
    ("#8b5cf6", "#ede9fe"),
    (GVA_GOLD, "#fef3c7"),
    ("#06b6d4", "#cffafe"),
    ("#ec4899", "#fce7f3"),
    ("#3b82f6", "#dbeafe"),
    ("#f97316", "#ffedd5"),
    ("#14b8a6", "#ccfbf1"),
]


def _color_for_teacher(name, names):
    """Devuelve el par (fg, bg) asignado a un profesor según su posición en la lista."""
    idx = names.index(name) % len(TEACHER_COLORS)
    return TEACHER_COLORS[idx]


# Nombres de días y meses en español para formateo de fechas
DAYS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _day_name(date_str):
    """Convierte una fecha YYYY-MM-DD a formato legible: 'Miércoles 12 de marzo de 2026'."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        wd = d.weekday()
        return f"{DAYS_ES[wd].capitalize()} {d.day} de {MONTHS_ES[d.month-1]} de {d.year}"
    except ValueError:
        return date_str


def _short_day(date_str):
    """Convierte una fecha a formato abreviado: 'Miércoles 12/03'."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        wd = d.weekday()
        return f"{DAYS_ES[wd].capitalize()} {d.day}/{d.month:02d}"
    except ValueError:
        return date_str


def _fmt_mins(m):
    """Formatea minutos como 'Xh YYm'; devuelve '0h' si es cero."""
    return f"{m // 60}h {m % 60:02d}m" if m else "0h"


def _build_data(teachers, needs, assignment):
    """Preprocesa los datos de entrada y devuelve estructuras auxiliares para generar el HTML."""
    # Lista ordenada de nombres de profesores
    teacher_names = sorted({t["name"] for t in teachers})
    # Mapa nombre -> colores
    tcolors = {n: _color_for_teacher(n, teacher_names) for n in teacher_names}

    # Agrupa asignaciones por índice de necesidad
    need_map = {}
    for a in assignment:
        key = a["need_idx"]
        if key not in need_map:
            need_map[key] = {"need": a["need"], "teachers": []}
        need_map[key]["teachers"].append(a["teacher"]["name"])

    # Índices de necesidades ordenados por fecha y hora de inicio
    sorted_need_idxs = sorted(need_map.keys(), key=lambda i: (needs[i]["date"], needs[i]["start"]))
    # Fechas únicas ordenadas
    dates = sorted({n["date"] for n in needs})

    # Acumula minutos totales y asignaciones por profesor
    work_sums = {}
    teacher_assignments = {}
    for a in assignment:
        tname = a["teacher"]["name"]
        work_sums[tname] = work_sums.get(tname, 0) + duration_min(a["need"])
        teacher_assignments.setdefault(tname, []).append(a)

    return teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments



def _view_schedule(project_name, teachers, needs, assignment, teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments):
    """Genera la vista de cuadrante agrupada por día con tabla de horarios y profesores asignados."""
    html = ""
    for day in dates:
        # Filtra necesidades del día actual
        day_needs = [i for i in sorted_need_idxs if needs[i]["date"] == day]
        day_label = _short_day(day)
        html += f'<div class="day-section">\n<div class="day-title">📅 {day_label}</div>\n'
        html += """<table>
<thead><tr><th>Hora</th><th>Necesidad</th><th>Profesores asignados</th></tr></thead>
<tbody>
"""
        for ni in day_needs:
            n = needs[ni]
            entry = need_map.get(ni)
            label = f"{n['start']} - {n['end']}"
            need_name = n["name"]
            req = f"(min {n['min']}, max {n['max']})"

            if entry and entry["teachers"]:
                # Genera etiqueta de color para cada profesor asignado
                tags = ""
                for tname in sorted(entry["teachers"]):
                    fg, bg = tcolors[tname]
                    tags += f'<span class="teacher-tag" style="background:{bg};color:{fg};border:1px solid {fg};">{tname}</span> '
                html += f"<tr><td>{label}</td><td>{need_name} <span style='color:#94a3b8;font-size:11px;'>{req}</span></td><td>{tags}</td></tr>\n"
            else:
                # Muestra guión si no hay profesores asignados
                html += f"<tr><td>{label}</td><td>{need_name} <span style='color:#94a3b8;font-size:11px;'>{req}</span></td><td><span class='empty-cell'>—</span></td></tr>\n"

        html += "</tbody>\n</table>\n</div>\n"
    return html


def _view_by_teacher(project_name, teachers, needs, assignment, teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments):
    """Genera la vista agrupada por profesor, mostrando sus tareas asignadas día a día."""
    html = ""
    for tname in teacher_names:
        assigns = teacher_assignments.get(tname, [])
        if not assigns:
            continue
        total_mins = work_sums.get(tname, 0)
        # Agrupa asignaciones del profesor por fecha
        assigns_by_day = {}
        for a in assigns:
            d = a["need"]["date"]
            assigns_by_day.setdefault(d, []).append(a)

        fg, bg = tcolors[tname]
        html += f'<div class="day-section">\n<div class="day-title" style="background:{fg};">👤 {tname}  ·  {_fmt_mins(total_mins)}</div>\n'
        html += """<table>
<thead><tr><th>Día</th><th>Hora</th><th>Tarea</th></tr></thead>
<tbody>
"""
        for d in sorted(assigns_by_day.keys()):
            dl = _short_day(d)
            for a in sorted(assigns_by_day[d], key=lambda x: x["need"]["start"]):
                n = a["need"]
                html += f"<tr><td>{dl}</td><td>{n['start']} - {n['end']}</td><td>{n['name']}</td></tr>\n"
        html += "</tbody>\n</table>\n</div>\n"
    return html


def _view_by_task(project_name, teachers, needs, assignment, teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments):
    """Genera la vista agrupada por tarea, listando los profesores asignados a cada necesidad."""
    html = ""
    for ni in sorted_need_idxs:
        n = needs[ni]
        entry = need_map.get(ni)
        day_label = _short_day(n["date"])
        label = f"{n['start']} - {n['end']}"
        req = f"(min {n['min']}, max {n['max']})"

        if entry and entry["teachers"]:
            # Construye etiquetas de color para los profesores asignados
            tags = ""
            for tname in sorted(entry["teachers"]):
                fg, bg = tcolors[tname]
                tags += f'<span class="teacher-tag" style="background:{bg};color:{fg};border:1px solid {fg};">{tname}</span> '
        else:
            tags = '<span class="empty-cell">—</span>'

        html += f'<div class="day-section">\n<div class="day-title" style="background:#475569;">📋 {n["name"]}</div>\n'
        html += f"""<table>
<thead><tr><th>Día</th><th>Hora</th><th>Requisito</th><th>Profesores asignados</th></tr></thead>
<tbody>
<tr><td>{day_label}</td><td>{label}</td><td>{req}</td><td>{tags}</td></tr>
</tbody>
</table>
</div>
"""
    return html


def _view_word(project_name, teachers, needs, assignment, teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments):
    """Genera la vista estilo Word con bordes negros y fuente Calibri para copiar directamente."""
    html = ""
    for day in dates:
        day_needs = [i for i in sorted_need_idxs if needs[i]["date"] == day]
        day_label = _short_day(day)
        html += f'<h3 style="font-family:Calibri,sans-serif;color:#1e293b;margin:16px 0 6px 0;font-size:14pt;">📅 {day_label}</h3>\n'
        html += """<table class="word-table">
<thead>
<tr><th style="width:100px;">Hora</th><th style="width:260px;">Tarea</th><th>Profesorado asignado</th></tr>
</thead>
<tbody>
"""
        for ni in day_needs:
            n = needs[ni]
            entry = need_map.get(ni)
            label = f"{n['start']} - {n['end']}"
            need_name = n["name"]

            if entry and entry["teachers"]:
                teachers_str = ", ".join(sorted(entry["teachers"]))
            else:
                teachers_str = "—"

            html += f"<tr><td style='white-space:nowrap;'>{label}</td><td>{need_name}</td><td>{teachers_str}</td></tr>\n"
        html += "</tbody>\n</table>\n"
    return html


def _view_print(project_name, teachers, needs, assignment, teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments):
    """Genera la vista limpia para impresión, con tabla resumen de carga al final."""
    html = ""
    for day in dates:
        day_needs = [i for i in sorted_need_idxs if needs[i]["date"] == day]
        day_label = _short_day(day)
        html += f'<div class="print-day">\n<h3>📅 {day_label}</h3>\n'
        html += """<table class="print-table">
<thead>
<tr><th>Hora</th><th>Tarea</th><th>Profesorado</th></tr>
</thead>
<tbody>
"""
        for ni in day_needs:
            n = needs[ni]
            entry = need_map.get(ni)
            label = f"{n['start']} - {n['end']}"

            if entry and entry["teachers"]:
                teachers_str = ", ".join(sorted(entry["teachers"]))
            else:
                teachers_str = "—"

            html += f"<tr><td>{label}</td><td>{n['name']}</td><td>{teachers_str}</td></tr>\n"
        html += "</tbody>\n</table>\n</div>\n"
    return html


def _view_docx(project_name, teachers, needs, assignment, teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments):
    """Genera la vista minimalista para exportar a DOCX: solo los cuadrantes, sin extras."""
    html = ""
    for day in dates:
        day_needs = [i for i in sorted_need_idxs if needs[i]["date"] == day]
        day_label = _short_day(day)
        html += f'<div class="docx-day">\n<h2>{day_label}</h2>\n'
        html += """<table class="docx-table">
<thead>
<tr><th>Hora</th><th>Tarea</th><th>Profesorado</th></tr>
</thead>
<tbody>
"""
        for ni in day_needs:
            n = needs[ni]
            entry = need_map.get(ni)
            label = f"{n['start']} - {n['end']}"

            if entry and entry["teachers"]:
                teachers_str = ", ".join(sorted(entry["teachers"]))
            else:
                teachers_str = "—"

            html += f"<tr><td>{label}</td><td>{n['name']}</td><td>{teachers_str}</td></tr>\n"
        html += "</tbody>\n</table>\n</div>\n"
    return html


def _workload_html(teacher_names, work_sums, max_work, tcolors):
    """Genera barras de carga horizontal que muestran el porcentaje de trabajo de cada profesor."""
    html = """<div class="workload no-print">
<h3>📊 Carga de trabajo por profesor</h3>
"""
    for name in teacher_names:
        mins = work_sums.get(name, 0)
        hours = _fmt_mins(mins)
        # Calcula el porcentaje respecto al máximo de trabajo
        pct = int(mins / max_work * 100) if max_work else 0
        fg, bg = tcolors[name]
        html += f"""<div class="workload-bar">
  <span style="width:130px;text-align:right;padding-right:8px;">{name}</span>
  <div style="flex:1;background:#e2e8f0;border-radius:4px;height:18px;">
    <div class="workload-fill" style="width:{pct}%;background:{fg};"></div>
  </div>
  <span style="width:70px;">{hours}</span>
</div>
"""
    html += "</div>\n"
    return html


def generate_html(project_name, teachers, needs, assignment, view="all"):
    """
    Genera un documento HTML completo con vistas en pestañas.
    view: "all" (pestañas), "schedule", "teacher", "task", "word", "print"
    """
    # Preprocesa los datos en estructuras auxiliares
    data = _build_data(teachers, needs, assignment)
    teacher_names, tcolors, need_map, sorted_need_idxs, dates, work_sums, teacher_assignments = data

    title = project_name.strip() or "Cuadrante de Apoyo"
    now_str = datetime.now().strftime('%d/%m/%Y a las %H:%M')

    # Genera el HTML de cada vista
    views_html = {}
    views_html["schedule"] = _view_schedule(project_name, teachers, needs, assignment, *data)
    views_html["teacher"] = _view_by_teacher(project_name, teachers, needs, assignment, *data)
    views_html["task"] = _view_by_task(project_name, teachers, needs, assignment, *data)
    views_html["word"] = _view_word(project_name, teachers, needs, assignment, *data)
    views_html["print"] = _view_print(project_name, teachers, needs, assignment, *data)
    views_html["docx"] = _view_docx(project_name, teachers, needs, assignment, *data)

    # Máximo de minutos para escalar las barras de carga
    max_work = max(work_sums.values()) if work_sums else 1

    # Define las pestañas disponibles
    tabs_def = [
        ("schedule", "📅 Cuadrante"),
        ("teacher", "👤 Por profesor"),
        ("task", "📋 Por tarea"),
        ("word", "📄 Estilo Word"),
        ("print", "🖨️ Para imprimir"),
    ]

    view_map = {"schedule": "📅 Cuadrante", "teacher": "👤 Por profesor", "task": "📋 Por tarea", "word": "📄 Estilo Word", "print": "🖨️ Para imprimir"}

    # Para exportación DOCX: HTML minimalista solo con los cuadrantes (antes de tocar tabs_def)
    if view == "docx":
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  @page {{ size: landscape; margin: 1cm; }}
  body {{ font-family: Calibri, 'Segoe UI', Arial, sans-serif; color: #000; background: #fff; padding: 20px; }}
  h1 {{ font-size: 20pt; color: {GVA_BLUE}; margin-bottom: 4px; }}
  .subtitle {{ font-size: 10pt; color: #555; margin-bottom: 14px; }}
  h2 {{ font-size: 14pt; color: #1e293b; margin: 16px 0 6px 0; }}
  .docx-table {{ border-collapse: collapse; width: 100%; font-size: 10pt; }}
  .docx-table th, .docx-table td {{ border: 1px solid #555; padding: 4px 8px; vertical-align: middle; }}
  .docx-table th {{ background: #e2e8f0; color: #000; font-weight: 700; text-align: center; }}
  .docx-table td:first-child {{ white-space: nowrap; font-weight: 400; background: #fff; }}
  .docx-table tr:nth-child(even) td {{ background: #f8fafc; }}
  .docx-day {{ margin-bottom: 18px; }}
</style>
</head>
<body>
<h1>📋 {title}</h1>
<p class="subtitle">Generado el {now_str} &middot; {len(needs)} necesidades &middot; {len(teacher_names)} profesores &middot; {len(assignment)} asignaciones</p>
{views_html["docx"]}
</body>
</html>"""

    if view != "all":
        tabs_def = [(view, view_map[view])]

    # Genera botones de pestañas con la primera activa por defecto
    tab_buttons = "  ".join(
        f'<button class="tab-btn {"active" if i == 0 else ""}" onclick="switchTab(\'{k}\', this)">{l}</button>'
        for i, (k, l) in enumerate(tabs_def)
    )

    # Genera contenedores de contenido, mostrando solo la primera pestaña
    tab_contents = "".join(
        f'<div class="tab-content" id="tab_{k}" style="display:{"block" if i == 0 else "none"};">{views_html[k]}</div>'
        for i, (k, l) in enumerate(tabs_def)
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @page {{ size: landscape; margin: 1cm; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif;
    color: #1e293b; background: #f8fafc; padding: 20px;
  }}
  h1 {{ font-size: 22px; font-weight: 700; color: {GVA_BLUE}; margin-bottom: 2px; }}
  .subtitle {{ font-size: 13px; color: #64748b; margin-bottom: 14px; }}
  .tab-bar {{ display: flex; gap: 4px; margin-bottom: 16px; flex-wrap: wrap; }}
  .tab-btn {{
    padding: 8px 18px; border: 1px solid {GVA_BLUE}; background: #fff;
    color: {GVA_BLUE}; border-radius: 6px 6px 0 0; cursor: pointer;
    font-size: 13px; font-weight: 600; transition: all .15s;
  }}
  .tab-btn:hover {{ background: #eef2ff; }}
  .tab-btn.active {{ background: {GVA_BLUE}; color: #fff; }}
  .tab-content {{ display: none; }}
  .day-section {{ margin-bottom: 20px; }}
  .day-title {{ font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 8px;
                padding: 7px 12px; background: {GVA_BLUE}; border-radius: 6px; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 4px; }}
  th, td {{ border: 1px solid #d0d5dd; padding: 6px 10px; text-align: center; vertical-align: middle; font-size: 12px; }}
  th {{ background: {GVA_BLUE}; color: #fff; font-weight: 600; font-size: 12px; padding: 8px 8px; }}
  td:first-child {{ font-weight: 600; background: #f1f5f9; color: #0f172a; white-space: nowrap; font-size: 11px; }}
  td:nth-child(2) {{ text-align: left; font-weight: 500; }}
  .teacher-tag {{
    display: inline-block; margin: 2px 3px; padding: 3px 10px;
    border-radius: 12px; font-size: 11px; font-weight: 600;
  }}
  .empty-cell {{ color: #94a3b8; font-style: italic; font-size: 11px; }}
  .workload {{ margin-top: 20px; }}
  .workload h3 {{ font-size: 15px; margin-bottom: 8px; color: {GVA_BLUE}; }}
  .workload-bar {{ display: flex; align-items: center; gap: 8px; margin: 3px 0; font-size: 12px; }}
  .workload-fill {{ height: 18px; border-radius: 4px; min-width: 4px; }}

  .email-section {{ margin-top: 30px; }}
  .email-section h3 {{ font-size: 17px; color: {GVA_BLUE}; margin-bottom: 12px;
                       border-bottom: 2px solid {GVA_BLUE}; padding-bottom: 5px; }}
  .email-card {{ background: #fff; border: 1px solid #d0d5dd; border-radius: 6px;
                 margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.05); }}
  .email-card-header {{ background: {GVA_BLUE}; color: #fff; padding: 9px 14px;
                        border-radius: 6px 6px 0 0; font-weight: 600; font-size: 13px;
                        display: flex; justify-content: space-between; align-items: center; }}
  .email-body {{ padding: 14px; font-size: 13px; line-height: 1.6; color: #1e293b;
                 font-family: 'Segoe UI', sans-serif; white-space: pre-wrap; }}
  .copy-btn {{
    background: #fff; color: {GVA_BLUE}; border: 1px solid {GVA_BLUE};
    padding: 3px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600;
  }}
  .copy-btn:hover {{ background: {GVA_BLUE}; color: #fff; }}
  .toast-msg {{
    position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
    background: {GVA_BLUE}; color: #fff; padding: 10px 24px; border-radius: 6px;
    font-size: 13px; font-weight: 600; display: none; z-index: 999;
  }}
  @media print {{
    body {{ background: #fff; padding: 0; }}
    .no-print, .tab-bar {{ display: none !important; }}
    .tab-content {{ display: block !important; }}
    th {{ background: {GVA_BLUE} !important; color: #fff !important;
         -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .teacher-tag {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    td:first-child {{ background: #f1f5f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .day-title {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .email-card {{ break-inside: avoid; }}
  }}
  .btn-print {{
    display: inline-block; padding: 8px 20px; background: {GVA_BLUE};
    color: #fff; border: none; border-radius: 6px; font-size: 13px;
    cursor: pointer; margin-bottom: 10px;
  }}
  .btn-print:hover {{ background: #4f46e5; }}

  /* Estilos específicos para la vista estilo Word (copy-paste directo) */
  .word-table {{
    border-collapse: collapse; width: 100%;
    font-family: Calibri, 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
  }}
  .word-table th, .word-table td {{
    border: 1px solid #000;
    padding: 5px 8px;
    vertical-align: middle;
  }}
  .word-table th {{
    background: #d9e2f3;
    color: #000;
    font-weight: 700;
    font-size: 11pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .word-table td:first-child {{ background: #fff; font-weight: 400; }}
  .word-table tr:nth-child(even) td {{ background: #f2f2f2; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}

  /* Estilos minimalistas para la vista de impresión */
  .print-day {{ margin-bottom: 18px; }}
  .print-day h3 {{ font-family: Calibri, 'Segoe UI', sans-serif; font-size: 13pt; color: #1e293b; margin: 12px 0 4px 0; }}
  .print-table {{
    border-collapse: collapse; width: 100%;
    font-family: Calibri, 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
  }}
  .print-table th, .print-table td {{
    border: 1px solid #555;
    padding: 4px 8px;
    vertical-align: middle;
  }}
  .print-table th {{
    background: #e2e8f0;
    color: #000;
    font-weight: 700;
    font-size: 10pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .print-table td:first-child {{ background: #fff; font-weight: 400; }}
  .print-table tr:nth-child(even) td {{ background: #f8fafc; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .print-summary {{ margin-top: 20px; }}
  .print-summary h3 {{ font-family: Calibri, 'Segoe UI', sans-serif; font-size: 13pt; color: #1e293b; margin-bottom: 6px; }}
  .print-summary table {{ width: auto; min-width: 280px; }}
</style>
</head>
<body>
<div class="toast-msg" id="toast">📋 ¡Copiado al portapapeles!</div>
<script>
function copyText(id) {{
  var txt = document.getElementById(id).textContent;
  navigator.clipboard.writeText(txt).then(function() {{
    var t = document.getElementById('toast');
    t.style.display = 'block';
    setTimeout(function(){{ t.style.display = 'none'; }}, 2000);
  }});
}}
function switchTab(name, btn) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.style.display = 'none'; }});
  document.querySelectorAll('.tab-btn').forEach(function(el) {{ el.classList.remove('active'); }});
  document.getElementById('tab_' + name).style.display = 'block';
  btn.classList.add('active');
}}
</script>
<div class="no-print" style="text-align:right;margin-bottom:6px;">
  <button class="btn-print" onclick="window.print()">🖨️ Imprimir / PDF</button>
  <button class="btn-print" onclick="var a=document.createElement('a');a.href='data:application/msword;base64,'+btoa(unescape(encodeURIComponent(document.documentElement.outerHTML)));a.download='cuadrante.doc';document.body.appendChild(a);a.click();document.body.removeChild(a)">📄 Word</button>
</div>
<h1>📋 {title}</h1>
<p class="subtitle">
  Generado el {now_str} &middot; {len(needs)} necesidades &middot; {len(teacher_names)} profesores &middot; {len(assignment)} asignaciones
</p>
"""
    if view == "all":
        html += f'<div class="tab-bar no-print">{tab_buttons}</div>\n'
    html += tab_contents

    # Añade las barras de carga de trabajo (con class no-print, no salen al imprimir)
    html += _workload_html(teacher_names, work_sums, max_work, tcolors)

    # Sección de correos electrónicos (general e individuales)
    html += f"""<div class="email-section no-print">
<h3>📧 Correos electrónicos</h3>
<p style="font-size:12px;color:#64748b;margin-bottom:12px;">
  📋 <b>General</b> — resumen para todo el equipo.  👤 <b>Individuales</b> — cada profe con sus tareas.
  Haz clic en "📋 Copiar" para llevar al portapapeles.
</p>
"""

    # Construye el correo general dirigido a todo el equipo
    gen_lines = []
    gen_lines.append(f"Hola a todo el equipo,")
    gen_lines.append("")
    gen_lines.append(f"Les comunico el cuadro de apoyo para el proyecto «{title}»:")
    gen_lines.append("")
    for d in dates:
        day_needs = [i for i in sorted_need_idxs if needs[i]["date"] == d]
        gen_lines.append(f"📅 {_short_day(d)}")
        for ni in day_needs:
            entry = need_map.get(ni)
            n = needs[ni]
            names_str = ", ".join(sorted(entry["teachers"])) if entry else "—"
            gen_lines.append(f"   {n['start']}-{n['end']}  {n['name']}  →  {names_str}")
        gen_lines.append("")
    gen_lines.append(f"Total: {len(assignment)} asignaciones, {len(teacher_names)} profesores")
    gen_lines.append("")
    gen_lines.append("¡Muchas gracias a todos por la colaboración!")
    gen_lines.append("")
    gen_lines.append("--")
    gen_lines.append("Departamento de Coordinación")
    gen_text = "\n".join(gen_lines)
    gen_subject = f"Cuadrante apoyo - {title}"
    gen_email = f"Asunto: {gen_subject}\n\n{gen_text}"

    html += f"""<div class="email-card">
  <div class="email-card-header" style="background:{GVA_BLUE};">
    <span>📋 Correo general — Todo el equipo</span>
    <button class="copy-btn" onclick="copyText('email_general')">📋 Copiar</button>
  </div>
  <div class="email-body" id="email_general">{gen_email}</div>
</div>
"""

    # Genera un correo individual para cada profesor con sus asignaciones
    for tname in teacher_names:
        assigns = teacher_assignments.get(tname, [])
        if not assigns:
            continue
        total_mins = work_sums.get(tname, 0)
        assigns_by_day = {}
        for a in assigns:
            d = a["need"]["date"]
            assigns_by_day.setdefault(d, []).append(a)

        email_lines = []
        email_lines.append(f"Hola {tname},")
        email_lines.append("")
        email_lines.append(f"Te comunico las tareas de apoyo que se te han asignado para el proyecto «{title}»:")
        email_lines.append("")
        for d in sorted(assigns_by_day.keys()):
            dl = _short_day(d)
            email_lines.append(f"📅 {dl}")
            for a in sorted(assigns_by_day[d], key=lambda x: x["need"]["start"]):
                n = a["need"]
                email_lines.append(f"   {n['start']} - {n['end']}  →  {n['name']}")
            email_lines.append("")
        email_lines.append(f"Total: {_fmt_mins(total_mins)}")
        email_lines.append("")
        email_lines.append("¡Muchas gracias por tu colaboración!")
        email_lines.append("")
        email_lines.append("--")
        email_lines.append("Departamento de Coordinación")
        email_text = "\n".join(email_lines)

        email_subject = f"Cuadrante apoyo - {title}"
        full_email = f"Asunto: {email_subject}\n\n{email_text}"

        email_id = f"email_{tname.replace(' ', '_')}"
        fg, _ = tcolors[tname]
        html += f"""<div class="email-card">
  <div class="email-card-header">
    <span>👤 {tname}  ·  {_fmt_mins(total_mins)}</span>
    <button class="copy-btn" onclick="copyText('{email_id}')">📋 Copiar</button>
  </div>
  <div class="email-body" id="{email_id}">{full_email}</div>
</div>
"""

    html += """</div>
<div class="footer" style="margin-top:12px;font-size:11px;color:#94a3b8;text-align:center;">Generador Cuadrante Tareas Profesorado &middot; IES Serra Perenxisa &middot; Optimización CP-SAT</div>
</body>
</html>"""
    return html


def export_html_file(project_name, teachers, needs, assignment, filepath, view="all"):
    """Genera el HTML completo y opcionalmente lo escribe en un archivo.
    Si filepath es None, devuelve el HTML como string sin escribir."""
    html = generate_html(project_name, teachers, needs, assignment, view=view)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return filepath
    return html
