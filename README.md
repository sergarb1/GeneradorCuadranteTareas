# 📋 Generador Cuadrante Tareas Profesorado

**Generador inteligente de cuadrantes de apoyo al profesorado con optimización CP-SAT.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-CP--SAT-EA4335?logo=google&logoColor=white)](https://developers.google.com/optimization)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Licencia](https://img.shields.io/badge/Licencia-GPLv3-blue)](LICENSE)

---

## 📸 Captura

> _Aplicación de escritorio para asignar profesores a tareas de apoyo (XarxaLlibres, refuerzo, clasificación, etc.) usando optimización combinatoria._

---

## ✨ Características

| Característica | Descripción |
|---|---|
| 👨‍🏫 **Profesores globales** | Los profesores y su disponibilidad se guardan en `teachers.json` y se comparten entre todos los proyectos |
| 📋 **Necesidades por proyecto** | Cada proyecto define sus propias tareas con fecha, hora y rango de profesores necesarios |
| 🧠 **Optimización CP-SAT** | Google OR-Tools genera la mejor asignación posible maximizando el número total de asignaciones |
| 🎯 **10 opciones navegables** | El solver genera **10 variantes** y cambias entre ellas con ◀ ▶ sin perder ninguna |
| ⏳ **Loading animado** | Spinner visual mientras el solver piensa — evita clicks múltiples |
| 🔒 **Bloquear asignaciones** | Fija un profesor a una tarea (clic en el cuadrante) y regenera el resto |
| 🚫 **Sin solapamientos** | Un profesor no puede estar en dos sitios a la vez |
| ⏱ **Límites personalizados** | Horas máximas totales y por día para cada profesor |
| 🎨 **Colores y turnos** | Color HEX personalizado + turno (mañana/tarde/cualquiera) por profesor |
| 📧 **Correos integrados** | Genera correo **general** para el equipo y **correos individuales** para cada profesor |
| 📅 **Vista calendario** | Visualización por días con tarjetas de tareas — modo compacto y normal |
| 🖼️ **Exportar PNG** | Captura el cuadrante como imagen PNG |
| 🌓 **Tema claro/oscuro** | Conmutación instantánea con un solo clic |
| ↩️🔁 **Deshacer/Rehacer** | Botones con texto, hasta 50 estados de deshacer en edición |
| 🔍 **Búsqueda y filtros** | Filtra profesores y necesidades por texto |
| 📥📤 **Importar / Exportar JSON** | Profesores, necesidades o proyectos completos desde cualquier pestaña |
| 📊 **Exportar CSV** | Exporta asignaciones a CSV |
| 📈 **Panel de estadísticas** | Carga por profesor, cobertura, horas totales |
| ✅ **Validación previa** | Antes de generar, avisa si hay necesidades sin cobertura |
| 💾 **Auto-guardado** | Cada 2 minutos si hay cambios sin guardar |
| 🗃️ **Plantillas de horarios** | Guarda/carga patrones de disponibilidad de un profesor |
| 🖨️ **Exportación HTML** | Vista optimizada para impresión como PDF desde el navegador |
| 💾 **Persistencia local** | Las opciones generadas se guardan al proyecto y persisten al recargar |
| 🖥️ **Layout compacto** | Optimizado para 1280×720, columnas estrechas, scrollbars finos, toolbar en 2 filas |

---

## 🚀 Instalación

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/GeneradorCuadranteTareasProfesorado.git
cd GeneradorCuadranteTareasProfesorado

# Instala dependencias
pip install -r requirements.txt

# Ejecuta
python main.py
```

O haz doble clic en `lanzar.bat` (Windows).

### Dependencias

- **PyQt6** — Interfaz gráfica moderna con estilo Fusion
- **ortools** — Google OR-Tools (CP-SAT solver)

---

## 📖 Guía de uso

### Flujo de trabajo

```
1. 👨‍🏫 Profes     →  Añade profesores con disponibilidad, turno y color (o importa JSON)
2. 🏠 Proyecto     →  Crea o selecciona un proyecto (o importa proyecto completo)
3. 📋 Necesidades  →  Añade tareas con fecha, hora y mínimo/máximo (o importa JSON)
4. ⚙️ Generar      →  El solver genera 10 opciones (con loading animado y validación previa)
5. 🔒 Cuadrante    →  Bloquea profes a tareas (clic) y regenera si es necesario
6. 📅 Navega       →  Cambia entre opciones con ◀ ▶, exporta HTML/PNG/CSV
```

### Datos de ejemplo

El proyecto incluye datos ficticios del proceso **XarxaLlibres** (recogida y distribución de libros de texto):

- **15 profesores** con distinta disponibilidad (mañana, tarde, mixto, jornada partida, reducida)
- **50 tareas** a lo largo de 5 días (22–26 de junio de 2026) con solapamientos densos
- Límites individuales de 10h–25h total y 4h–8h por día
- Cada profesor con turno preferente y color HEX personalizado

Para cargarlos: pulsa **"📦 Cargar datos ficticios"** en la pestaña Proyecto.

---

## 🧠 Modelo CP-SAT

### Variables
```
x[necesidad, profesor] ∈ {0, 1}
  → 1 si el profesor se asigna a esa necesidad
```

### Restricciones

| Restricción | Descripción |
|---|---|
| **Capacidad** | `min ≤ Σ x[n, p] ≤ max` por necesidad |
| **Disponibilidad** | El profesor debe tener una franja que cubra la tarea |
| **Sin solapamientos** | `x[ni, p] + x[nj, p] ≤ 1` para tareas que coincidan en tiempo |
| **Carga total** | Σ duración · x ≤ `max_hours` del profesor |
| **Carga diaria** | Σ duración · x ≤ `max_hours_per_day` por día y profesor |

### Objetivo
```
Maximizar Σ x[n, p]
  → Tantos profesores asignados como sea posible
  → Cada tarea tiende hacia su máximo, no solo al mínimo
```

---

## 📁 Estructura del proyecto

```
GeneradorCuadranteTareasProfesorado/
├── gui.py              # 🖥️ Interfaz gráfica PyQt6 (~2050 líneas)
├── scheduler.py        # 🧠 Modelo CP-SAT con OR-Tools
├── html_exporter.py    # 📄 Generación HTML (cuadrante + correos)
├── seed_data.py        # 🌱 Datos de ejemplo XarxaLlibres (15 profes, 50 tareas)
├── main.py             # 🚀 Punto de entrada
├── teachers.json       # 👨‍🏫 Profesores (se crea al usar)
├── AGENTS.md           # 🤖 Guía para IA y esquemas de datos
├── projects/           # 📂 Proyectos guardados + opciones generadas
├── output/             # 📁 HTML generados
├── lanzar.bat          # 🏃 Lanzador Windows
├── index.html          # 🌐 Página del proyecto
├── requirements.txt    # 📦 Dependencias Python
└── README.md           # 📖 Este archivo
```

---

## 🎨 Personalización

- **Colores**: edita las constantes `C_PRI`, `C_ACCENT`, `C_BG`, etc. en `gui.py`
- **Tema**: botón ☀️/🌙 en la cabecera
- **Idioma**: toda la interfaz en español, días de la semana en español

---

## 🛠️ Tecnologías

| Tecnología | Propósito |
|---|---|
| **Python 3.11+** | Lenguaje principal |
| **PyQt6** | GUI moderna con QSS styling y Fusion theme |
| **OR-Tools CP-SAT** | Optimización combinatoria de Google |
| **HTML + CSS** | Exportación del cuadrante con diseño responsivo |

---

## 📄 Licencia

GNU General Public License v3.0 — Ver archivo [LICENSE](LICENSE).

---

**Desarrollado para centros educativos** · IES Serra Perenxisa · Proyecto XarxaLlibres
