from datetime import datetime
from scheduler import duration_min

GVA_BLUE = "#6366f1"
GVA_GOLD = "#f59e0b"

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
    idx = names.index(name) % len(TEACHER_COLORS)
    return TEACHER_COLORS[idx]


DAYS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

def _day_name(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        wd = d.weekday()
        return f"{DAYS_ES[wd].capitalize()} {d.day} de {MONTHS_ES[d.month-1]} de {d.year}"
    except ValueError:
        return date_str

def _short_day(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        wd = d.weekday()
        return f"{DAYS_ES[wd].capitalize()} {d.day}/{d.month:02d}"
    except ValueError:
        return date_str


def _fmt_mins(m):
    return f"{m // 60}h {m % 60:02d}m" if m else "0h"


def generate_html(project_name, teachers, needs, assignment):
    teacher_names = sorted({t["name"] for t in teachers})
    tcolors = {n: _color_for_teacher(n, teacher_names) for n in teacher_names}

    need_map = {}
    for a in assignment:
        key = a["need_idx"]
        if key not in need_map:
            need_map[key] = {"need": a["need"], "teachers": []}
        need_map[key]["teachers"].append(a["teacher"]["name"])

    sorted_need_idxs = sorted(need_map.keys(), key=lambda i: (needs[i]["date"], needs[i]["start"]))
    dates = sorted({n["date"] for n in needs})

    work_sums = {}
    teacher_assignments = {}
    for a in assignment:
        tname = a["teacher"]["name"]
        work_sums[tname] = work_sums.get(tname, 0) + duration_min(a["need"])
        teacher_assignments.setdefault(tname, []).append(a)

    title = project_name.strip() or "Cuadrante de Apoyo"
    now_str = datetime.now().strftime('%d/%m/%Y a las %H:%M')

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @page {{ size: landscape; margin: 1.2cm; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif;
    color: #1e293b; background: #f8fafc; padding: 20px;
  }}
  h1 {{ font-size: 22px; font-weight: 700; color: {GVA_BLUE}; margin-bottom: 2px; }}
  .subtitle {{ font-size: 13px; color: #64748b; margin-bottom: 20px; }}
  .day-section {{ margin-bottom: 28px; }}
  .day-title {{ font-size: 17px; font-weight: 700; color: #fff; margin-bottom: 10px;
                padding: 8px 12px; background: {GVA_BLUE}; border-radius: 6px; }}
  table {{ border-collapse: collapse; width: 100%; box-shadow: 0 1px 3px rgba(0,0,0,.08);
           border-radius: 8px; overflow: hidden; margin-bottom: 6px; }}
  th, td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: center; vertical-align: middle; font-size: 12px; }}
  th {{ background: {GVA_BLUE}; color: #fff; font-weight: 600; font-size: 12px; padding: 10px 8px; }}
  th:first-child {{ width: 110px; }}
  th:nth-child(2) {{ width: 200px; }}
  td:first-child {{ font-weight: 600; background: #f1f5f9; color: #0f172a; white-space: nowrap; font-size: 11px; }}
  td:nth-child(2) {{ text-align: left; font-weight: 500; }}
  .teacher-tag {{
    display: inline-block; margin: 2px 3px; padding: 4px 10px;
    border-radius: 14px; font-size: 11px; font-weight: 600;
  }}
  .empty-cell {{ color: #94a3b8; font-style: italic; font-size: 11px; }}
  .footer {{ margin-top: 14px; font-size: 11px; color: #94a3b8; text-align: center; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 14px 0; justify-content: center; }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; font-size: 12px; }}
  .legend-swatch {{ width: 14px; height: 14px; border-radius: 50%; border: 1px solid #cbd5e1; }}
  .workload {{ margin-top: 24px; }}
  .workload h3 {{ font-size: 15px; margin-bottom: 8px; color: {GVA_BLUE}; }}
  .workload-bar {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 12px; }}
  .workload-fill {{ height: 20px; border-radius: 4px; min-width: 4px; }}

  .email-section {{ margin-top: 36px; }}
  .email-section h3 {{ font-size: 18px; color: {GVA_BLUE}; margin-bottom: 16px;
                       border-bottom: 2px solid {GVA_BLUE}; padding-bottom: 6px; }}
  .email-card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
                 margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  .email-card-header {{ background: {GVA_BLUE}; color: #fff; padding: 10px 16px;
                        border-radius: 8px 8px 0 0; font-weight: 600; font-size: 14px;
                        display: flex; justify-content: space-between; align-items: center; }}
  .email-body {{ padding: 16px; font-size: 13px; line-height: 1.6; color: #1e293b;
                 font-family: 'Segoe UI', sans-serif; white-space: pre-wrap; }}
  .copy-btn {{
    background: #fff; color: {GVA_BLUE}; border: 1px solid {GVA_BLUE};
    padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600;
  }}
  .copy-btn:hover {{ background: {GVA_BLUE}; color: #fff; }}
  .toast-msg {{
    position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
    background: {GVA_BLUE}; color: #fff; padding: 10px 24px; border-radius: 6px;
    font-size: 13px; font-weight: 600; display: none; z-index: 999;
  }}
  @media print {{
    body {{ background: #fff; padding: 0; }}
    .no-print {{ display: none !important; }}
    th {{ background: {GVA_BLUE} !important; color: #fff !important;
         -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .teacher-tag {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    td:first-child {{ background: #f1f5f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .day-title {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .email-card {{ break-inside: avoid; }}
  }}
  .btn-print {{
    display: inline-block; padding: 10px 24px; background: {GVA_BLUE};
    color: #fff; border: none; border-radius: 6px; font-size: 14px;
    cursor: pointer; margin-bottom: 14px;
  }}
  .btn-print:hover {{ background: #002573; }}
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
</script>
<div class="no-print" style="text-align:right;">
  <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Guardar PDF</button>
</div>
<h1>📋 {title}</h1>
<p class="subtitle">
  Generado el {now_str} &middot; {len(needs)} necesidades &middot; {len(teacher_names)} profesores
</p>
<div class="legend">
"""

    for name in teacher_names:
        fg, bg = tcolors[name]
        html += f'  <div class="legend-item"><span class="legend-swatch" style="background:{bg};border-color:{fg};"></span>{name}</div>\n'

    html += """</div>
"""

    for day in dates:
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
                tags = ""
                for tname in sorted(entry["teachers"]):
                    fg, bg = tcolors[tname]
                    tags += f'<span class="teacher-tag" style="background:{bg};color:{fg};border:1px solid {fg};">{tname}</span> '
                html += f"<tr><td>{label}</td><td>{need_name} <span style='color:#94a3b8;font-size:11px;'>{req}</span></td><td>{tags}</td></tr>\n"
            else:
                html += f"<tr><td>{label}</td><td>{need_name} <span style='color:#94a3b8;font-size:11px;'>{req}</span></td><td><span class='empty-cell'>—</span></td></tr>\n"

        html += "</tbody>\n</table>\n</div>\n"

    max_work = max(work_sums.values()) if work_sums else 1

    html += """<div class="workload no-print">
<h3>📊 Carga de trabajo por profesor</h3>
"""
    for name in teacher_names:
        mins = work_sums.get(name, 0)
        hours = _fmt_mins(mins)
        pct = int(mins / max_work * 100) if max_work else 0
        fg, bg = tcolors[name]
        html += f"""<div class="workload-bar">
  <span style="width:130px;text-align:right;padding-right:8px;">{name}</span>
  <div style="flex:1;background:#e2e8f0;border-radius:4px;height:20px;">
    <div class="workload-fill" style="width:{pct}%;background:{fg};"></div>
  </div>
  <span style="width:70px;">{hours}</span>
</div>
"""

    html += """</div>
"""

    # --- Email section ---
    html += f"""<div class="email-section">
<h3>📧 Correos electrónicos</h3>
<p style="font-size:12px;color:#64748b;margin-bottom:14px;">
  📋 <b>General</b> — resumen para todo el equipo.  👤 <b>Individuales</b> — cada profe con sus tareas.
  Haz clic en "📋 Copiar" para llevar al portapapeles.
</p>
"""

    # ── General email ──
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

    # ── Individual emails ──
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
<div class="footer">Generador Cuadrante Tareas Profesorado &middot; IES Serra Perenxisa &middot; Optimización CP-SAT</div>
</body>
</html>"""
    return html


def export_html_file(project_name, teachers, needs, assignment, filepath):
    html = generate_html(project_name, teachers, needs, assignment)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath
