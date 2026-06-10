# Generador Cuadrante Tareas Profesorado — Guía para IA

## Resumen del proyecto

Aplicación de escritorio (Python + PyQt6) que asigna profesores a tareas de apoyo usando optimización combinatoria con Google OR-Tools CP-SAT. Genera hasta 50 opciones de cuadrante horario navegables (configurable 1-50), con persistencia local, importación/exportación JSON, y validación previa.

Características recientes de UX pulida:
- **Tooltips** en todos los botones, inputs y labels
- **Barra de estado** inferior con mensajes contextuales y atajos
- **Atajos de teclado**: Ctrl+S, Ctrl+Z, Ctrl+Y, Ctrl+N, Ctrl+D, F1
- **Diálogo de bienvenida** interactivo en primer inicio
- **Botón 📖 Ayuda** en la cabecera que abre el manual
- **Toolbar agrupada**: 3 grupos con supertítulo (Generar HTML, Acciones, Exportar)
- **Botones CTA** con fondo beige claro (#ece5da): Generar HTML, Regenerar Bloqueos, Duplicar día, DOCX
- **Exportar DOCX** con plantilla dedicada (solo cuadrantes, sin extras)
- **Exportar ICS** como "Calendario ICS"

## Esquemas de datos

### Profesor (`teachers.json` y seed_data.py)

```python
{
    "name": str,                    # Nombre completo (único)
    "max_hours": int,               # Límite total semanal en horas
    "max_hours_per_day": int,       # Límite máximo por día en horas
    "turno": str,                   # "Cualquiera" | "Mañana" | "Tarde"
    "color": str,                   # Color HEX (ej: "#6366f1") — opcional
    "email": str,                   # Correo electrónico (opcional, se usa en ICS como ATTENDEE)
    "preferred_tasks": [str],       # Nombres de tareas preferidas — opcional
    "time_slots": [                  # Lista de franjas de disponibilidad
        {
            "date": str,            # "YYYY-MM-DD"
            "start": str,           # "HH:MM" (24h)
            "end": str              # "HH:MM" (debe ser > start)
        }
    ]
}
```

Reglas para `time_slots`:
- Cada franja debe tener `start < end`
- La franja debe **contener completamente** cualquier necesidad que se le asigne (start <= need.start AND end >= need.end)
- Una necesidad que va de 09:00 a 11:00 puede cubrirse con una franja 09:00-14:00, pero NO con 09:30-11:00
- Los slots pueden solaparse entre sí para un mismo profesor (se usan como "disponibilidad total" ese día)
- Si no hay slot para un día concreto, el profesor no está disponible ese día

### Necesidad (tarea)

```python
{
    "name": str,           # Nombre descriptivo de la tarea
    "date": str,           # "YYYY-MM-DD"
    "start": str,          # "HH:MM"
    "end": str,            # "HH:MM"
    "min": int,            # Mínimo de profesores requeridos (>= 1)
    "max": int             # Máximo de profesores que pueden asignarse (>= min)
}
```

Reglas para necesidades:
- `min >= 1`, `max >= min`
- `start < end`
- La duración se calcula automáticamente como `end - start` en minutos
- Una necesidad puede requerir varios profesores simultáneamente (min 2, max 4)

### Proyecto (archivo en `projects/`)

```json
{
    "name": "Nombre del proyecto",
    "needs": [ ... ]  // Lista de necesidades
}
```

### Opciones generadas (archivo `*_generated.json`)

Contiene una lista de opciones, cada una con:
- `id`: int — número de opción
- `assignment`: list — asignaciones (need + teacher)
- `n_assignments`: int — total de asignaciones
- `n_covered`: int — necesidades distintas cubiertas
- `total_needs`: int — total de necesidades
- `total_minutes`: int — minutos totales asignados
- `teacher_hours`: dict — {nombre_profesor: minutos}

## Formatos para importación / exportación

### Importar solo profesores → pestaña Profes

Archivo JSON con un array de objetos profesor:

```json
[
    {
        "name": "Ana Alumnez",
        "max_hours": 20,
        "max_hours_per_day": 6,
        "turno": "Cualquiera",
        "color": "#6366f1",
        "preferred_tasks": [],
        "time_slots": [
            {"date": "2026-06-22", "start": "09:00", "end": "14:00"},
            {"date": "2026-06-22", "start": "15:30", "end": "18:30"}
        ]
    }
]
```

### Importar solo necesidades → pestaña Necesidades

Archivo JSON con un array de objetos necesidad:

```json
[
    {
        "name": "Recogida libros 1º ESO A",
        "date": "2026-06-22",
        "start": "09:00",
        "end": "11:00",
        "min": 2,
        "max": 4
    }
]
```

### Importar/Exportar proyecto completo → pestaña Proyecto

```json
{
    "project_name": "Nombre del proyecto",
    "needs": [ ... ],
    "teachers": [ ... ]  // Opcional — si se incluye, reemplaza todos los profesores
}
```

## Reglas para generar datos válidos

1. **Nombres inventados**: Usa apellidos claramente ficticios (Alumnez, Profesorez, Inventadez, Ficticiez, etc.). No uses nombres reales de docentes.

2. **Disponibilidad vs necesidades**: Para que el solver encuentre solución, la disponibilidad de los profesores debe **cubrir** las necesidades. Si una necesidad es de 09:00 a 11:00, al menos un profesor debe tener una franja que empiece ≤ 09:00 y termine ≥ 11:00.

3. **Horas mínimas**: La suma de (min × duración) de todas las necesidades debe ser ≤ la suma de horas disponibles de todos los profesores.

4. **Solapamiento de necesidades**: Si dos necesidades ocurren el mismo día y sus horarios se cruzan, un mismo profesor no puede estar en ambas. El solver lo maneja automáticamente.

5. **Distribución realista**: Los datos semilla incluyen 15 profesores con distintos perfiles (mañanas, tardes, mixto, jornada partida, reducida) y ~50 necesidades distribuidas en 5 días con solapamientos densos. Es un buen punto de partida para estresar el solver.

6. **Límite de tiempo**: El solver tiene 10 segundos por opción. Con 15 profesores y 50 necesidades, puede tardar hasta 2 minutos en generar las 10 opciones. La interfaz muestra un loading animado mientras resuelve.

7. **Perfiles variados**: Los profesores deberían tener distintos `turno` y `max_hours` para que el solver tenga combinaciones interesantes. Mezcla perfiles de mañana, tarde, y mixtos.

8. **Colores**: Se recomienda usar colores HEX distintos para cada profesor. Si no se especifica `color`, se asigna automáticamente.

## Funcionalidades actuales

| Funcionalidad | Dónde |
|---|---|---|
| 🎨 **Colores personalizados** | Al crear profesor, botón 🎨 para elegir color |
| 👤 **Turno preferente** | Combo "Cualquiera/Mañana/Tarde" al crear profesor |
| 🔍 **Búsqueda y filtros** | Campos de texto en listas de profesores y necesidades |
| 📋 **Duplicar profesor** | Botón 📋 junto al nombre del profesor en lista |
| 📋 **Duplicar necesidad** | Botón 📋 junto a la necesidad en lista |
| 📋 **Duplicar franja** | Botón 📋 junto a la franja de disponibilidad |
| 📋 **Duplicar necesidades a otro día** | Botón "📋 Duplicar necesidades a otro día" en barra de búsqueda de Necesidades |
| 📋 **Duplicar franjas a otro día** | Botón "📋 Duplicar franjas a otro día" en toolbar de franjas de disponibilidad |
| 📋 **Duplicar día desde cuadrante** | Botón "📋 Duplicar día" en toolbar del cuadrante (copia necesidades de una fecha a otra) |
| 📥 **Importar JSON** | Cada pestaña tiene su botón de importación |
| 📤 **Exportar JSON** | Profesores, necesidades o proyecto completo |
| 📊 **Exportar CSV** | Botón en pestaña Proyecto |
| 📈 **Estadísticas** | Botón 📊 Stats — genera HTML y abre en navegador |
| 📅 **Vista compacta/normal** | Botón "Cambiar a vista compacta/normal" en pestaña Cuadrante |
| ↩️ **Deshacer/Rehacer** | Botones "↩️ Deshacer / 🔁 Rehacer" en pestaña Proyecto (hasta 50 estados) |
| 💾 **Auto-guardado** | Cada 2 minutos si hay cambios sin guardar |
| 🔁 **Opciones navegables (1-50)** | ◀ ▶ en pestaña Cuadrante |
| 🗃️ **Plantillas de horarios** | Guardar/cargar franjas de un profesor como plantilla |
| ✅ **Validación previa** | Antes de generar, avisa si hay necesidades sin cobertura |
| ⚠️ **Advertencias de cobertura** | Muestra qué necesidades no pueden cubrirse y horas insuficientes |
| 📝 **Exportar Markdown** | Exporta el cuadrante como Markdown (tablas por día) |
| 🕐 **Icono en franjas** | Las franjas de disponibilidad muestran 🕐 |
| 🔒 **Bloquear asignaciones** | Clic en profesor en cuadrante → 🔒, botón "🔒 Regenerar Bloqueos" |
| 🖱️ **Asignación manual** | Menú contextual (clic derecho) en tareas del cuadrante para asignar/quitar profesores manualmente |
| 🔄 **Arrastrar profesor** | Arrastra el nombre de un profe de una tarea a otra para reasignarlo al instante |
| 📝 **Editar necesidad desde cuadrante** | Menú contextual → "📝 Editar necesidad" abre el diálogo de edición |
| 🌓 **Tema claro/oscuro/alto contraste** | Botón en cabecera (3 modos: claro → oscuro → ♿ alto contraste) |
| 🔒 **Lock highlight** | Asignaciones bloqueadas con 0.35 opacity + borde 2px del color del profesor |
| ⏳ **Loading al generar** | Spinner animado mientras el solver piensa (evita dobles clics) |
| 💬 **Tooltips descriptivos** | Todos los botones e inputs tienen tooltips al pasar el ratón |
| ⌨️ **Atajos de teclado** | Ctrl+S/Z/Y/N/D, F1 ayuda, Esc limpiar estado |
| ℹ️ **Barra de estado** | Barra inferior con mensajes contextuales y atajos recordados |
| 🎉 **Diálogo de bienvenida** | Guía interactiva en primer inicio |
| 📖 **Ayuda en cabecera** | Botón 📖 que abre el manual completo |
| 🌐 **HTML multi-vista** | 5 vistas: Cuadrante, Profesores, Tareas, Estilo Word, Para imprimir |
| 📄 **Estilo Word** | Tabla con bordes negros y Calibri para copiar a Word directamente |
| 📄 **Exportar DOCX** | Botón "📄 DOCX" en grupo Exportar (plantilla dedicada solo cuadrantes) |
| 📝 **Exportar Markdown** | Botón "📝 MD" en grupo Exportar |
| 📅 **Exportar ICS** | Botón "📅 Calendario ICS" en grupo Exportar |

## Archivos del proyecto

| Archivo | Propósito |
|---|---|
| `main.py` | Punto de entrada |
| `gui.py` | Interfaz PyQt6 (~3448 líneas) |
| `scheduler.py` | Modelo CP-SAT (variables, restricciones, solver) |
| `seed_data.py` | Datos ficticios de demostración |
| `html_exporter.py` | Exportación a HTML (5 vistas + correos) |
| `teachers.json` | Persistencia global de profesores |
| `projects/*.json` | Proyectos guardados |
| `projects/*_generated.json` | Opciones generadas guardadas |
| `output/*.html` | Cuadrantes generados |
| `output/*.ics` | Calendarios ICS exportados |
| `lanzar.bat` | Lanzador Windows |
| `lanzar.sh` | Lanzador Linux/macOS |
| `AGENTS.md` | Esta guía |
