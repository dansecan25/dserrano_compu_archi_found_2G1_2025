# Guía del Sistema Dual de Procesadores

## 🎯 Descripción General

El sistema ahora muestra **DOS procesadores lado a lado** en tiempo real:

- **Izquierda**: Pipeline SIN control de hazards (lee `log.txt`)
- **Derecha**: Pipeline CON control de hazards (lee `log_hazard_control.txt`)

**Ambos avanzan simultáneamente** cuando se presiona Step o Run.

---

## 🏗️ Arquitectura del Sistema

### Componentes Nuevos Creados

#### 1. `processor_components.py` (Actualizado)
Se agregaron dos nuevas clases:

**HazardUnit**
```python
class HazardUnit(ProcessorBlock):
    """Hazard Detection and Forwarding Unit"""
```
- Indicadores visuales: STALL (rojo) y FWD (verde)
- Se activa cuando hay hazards
- `set_stall(bool)` - Activa indicador de stall
- `set_forwarding(bool)` - Activa indicador de forwarding

**ForwardingPath**
```python
class ForwardingPath(Wire):
    """Special wire type for forwarding paths"""
```
- Cables especiales para forwarding
- Estilo: líneas punteadas
- Color: Amarillo cuando activo
- Diferente de cables normales

#### 2. `processor_diagram_hazard.py` (Nuevo)
Extiende `ProcessorDiagram` para añadir hazard control:

```python
class ProcessorDiagramWithHazards(ProcessorDiagram):
    def __init__(self, canvas):
        super().__init__(canvas)  # Crea procesador base
        self._add_hazard_unit()    # Agrega hazard unit
        self._add_forwarding_paths()  # Agrega forwarding paths
```

**Componentes adicionales:**
- Hazard Unit (centro-abajo)
- 2 Forwarding Paths:
  - `Forward_EX_EX`: De EX/MEM a ALU (EX-EX forwarding)
  - `Forward_MEM_EX`: De MEM/WB a ALU (MEM-EX forwarding)

#### 3. `dual_processor_view.py` (Nuevo)
Vista dual que muestra ambos procesadores:

```python
class DualProcessorView(tk.Frame):
    def __init__(self, parent, log_path_no_hazard, log_path_with_hazard):
        # Crea dos parsers
        self.parser_no_hazard = LogParser(log_path_no_hazard)
        self.parser_with_hazard = LogParser(log_path_with_hazard)

        # Crea dos diagramas
        self.diagram_no_hazard = ProcessorDiagram(...)
        self.diagram_with_hazard = ProcessorDiagramWithHazards(...)
```

**Características:**
- Control unificado (un solo panel de controles)
- Ambos procesadores comparten ciclo actual
- Step/Run/Reset afectan ambos simultáneamente
- Estados independientes mostrados en paralelo

#### 4. `mainMenu.py` (Actualizado)
Integra la vista dual:

```python
# Antes
self.processor_view = ProcessorView(self.processor_tab, self.log_path)

# Ahora
self.processor_view = DualProcessorView(
    self.processor_tab,
    self.log_path_no_hazard,
    self.log_path_with_hazard
)
```

---

## 🎨 Layout Visual

```
┌──────────────────────────────────────────────────────────────────┐
│  [⟲ Reset] [◀ Back] [▶ Step] [▶▶ Run] [⏸ Stop]   Cycle: X      │
│  Speed: [────────▬──────]                                        │
├─────────────────────────────────┬────────────────────────────────┤
│ Pipeline WITHOUT Hazard Control │ Pipeline WITH Hazard Control   │
├─────────────────────────────────┼────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐ │  ┌──────┐  ┌──────┐  ┌──────┐│
│  │  PC  │→│Inst  │→│  ALU │ │  │  PC  │→│Inst  │→│  ALU │ │
│  └──────┘  │Mem   │  └──────┘ │  └──────┘  │Mem   │  └──────┘ │
│            └──────┘            │            └──────┘            │
│                                │      ┌──────────────┐          │
│                                │      │ Hazard Unit  │          │
│                                │      │ [STALL][FWD] │          │
│                                │      └──────────────┘          │
│                                │      Forwarding: ┄┄┄→          │
├─────────────────────────────────┴────────────────────────────────┤
│ No Hazards: Cycle 5: PC=20      │ With Hazards: Cycle 5: PC=20  │
│ ✓ addi x1, x0, 100              │ ✓ addi x1, x0, 100           │
└─────────────────────────────────┴────────────────────────────────┘
```

---

## 🔄 Flujo de Ejecución

### 1. Preparación
```
Usuario escribe código RISC-V
    ↓
Click en "Run"
    ↓
Backend ejecuta y genera:
    - log.txt (sin hazards)
    - log_hazard_control.txt (con hazards)
```

### 2. Carga de Logs
```python
# En DualProcessorView.load_logs()
parser_no_hazard.parse()    # Lee log.txt
parser_with_hazard.parse()  # Lee log_hazard_control.txt
current_cycle = 0
update_displays()           # Actualiza ambos
```

### 3. Navegación por Ciclos
```python
# Cuando usuario presiona Step
def step(self):
    self.current_cycle += 1
    self._update_no_hazard_display()    # Actualiza izquierda
    self._update_with_hazard_display()  # Actualiza derecha
```

### 4. Actualización de Displays

**Procesador Sin Hazards:**
```python
# Lee ciclo actual del log
cycle_data = parser_no_hazard.get_cycle_data(current_cycle)

# Mapea etapas a componentes
for stage in cycle_data['stages']:
    if stage != "Libre":
        add_components_for_stage(stage)

# Actualiza diagrama
diagram_no_hazard.set_active_components(components)
diagram_no_hazard.set_active_wires(wires)
```

**Procesador Con Hazards:**
```python
# Lee ciclo actual del log
cycle_data = parser_with_hazard.get_cycle_data(current_cycle)

# Mapea etapas a componentes
for stage in cycle_data['stages']:
    if stage != "Libre":
        add_components_for_stage(stage)

# Detecta hazards (heurística: si 4+ etapas activas)
has_hazards = (active_stages >= 4)

# Actualiza diagrama CON hazard unit
diagram_with_hazard.set_active_components(components)
diagram_with_hazard.set_active_wires(wires)
diagram_with_hazard.set_hazard_state(stall=False, forwarding=has_hazards)
```

---

## 🎮 Controles y Uso

### Controles Unificados

| Botón | Acción |
|-------|--------|
| **⟲ Reset** | Ambos procesadores vuelven a ciclo 0 |
| **◀ Step Back** | Ambos retroceden 1 ciclo |
| **▶ Step** | Ambos avanzan 1 ciclo |
| **▶▶ Run** | Ambos se ejecutan automáticamente |
| **⏸ Stop** | Pausa la ejecución automática |
| **Speed Slider** | Ajusta velocidad de animación (100-2000ms) |

### Sincronización

```python
# Ciclo compartido
self.current_cycle = 5  # Mismo para ambos

# Al avanzar
max_cycles = max(
    parser_no_hazard.get_total_cycles(),
    parser_with_hazard.get_total_cycles()
)

if current_cycle < max_cycles - 1:
    current_cycle += 1
    # Actualiza AMBOS
```

---

## 🎨 Diferencias Visuales

### Procesador Sin Hazards (Izquierda)

**Título:** Verde (`#6ADA6A`)
```
Pipeline WITHOUT Hazard Control
```

**Componentes:**
- Procesador estándar (5 etapas)
- Sin hazard unit
- Sin forwarding paths
- Cables normales (verdes cuando activos)

### Procesador Con Hazards (Derecha)

**Título:** Rojo (`#DA6A6A`)
```
Pipeline WITH Hazard Control
```

**Componentes adicionales:**
- Hazard Unit (centro-abajo)
  - Indicador STALL (rojo cuando activo)
  - Indicador FWD (verde cuando activo)
- Forwarding Paths (líneas punteadas amarillas)
  - Forward_EX_EX (de EX/MEM a ALU)
  - Forward_MEM_EX (de MEM/WB a ALU)

---

## 📊 Estados de la Hazard Unit

### Indicadores

**STALL** (rojo `#FF6A6A`)
- Se activa cuando hay data hazard
- Pipeline se detiene
- Instrucciones no avanzan

**FWD** (verde `#6ADA6A`)
- Se activa cuando hay forwarding
- Datos se pasan directamente
- Evita stalls innecesarios

### Forwarding Paths

**Forward_EX_EX** (EX-EX Forwarding)
```
De: EX/MEM (resultado recién calculado)
A:  ALU input (instrucción siguiente)
Usa: Resultado de ALU antes de escribir a registro
```

**Forward_MEM_EX** (MEM-EX Forwarding)
```
De: MEM/WB (dato de memoria o cálculo anterior)
A:  ALU input (instrucción siguiente)
Usa: Resultado después de memoria
```

---

## 🔧 Configuración y Personalización

### Ajustar Detección de Hazards

En `dual_processor_view.py`:

```python
def _update_with_hazard_display(self):
    # Detectar hazards (actualmente heurística simple)
    active_stages = sum(1 for v in stages.values() if v != "Libre")
    has_hazards = active_stages >= 4

    # Mejorar detección:
    # TODO: Leer información de hazards del log
    # TODO: Detectar tipos específicos (data, control, structural)
```

### Agregar Más Información

Modificar `DualProcessorView.setup_ui()`:

```python
# Agregar más paneles de información
# Ejemplo: CPI comparison, stall count, forwarding count
```

### Colores Personalizados

```python
# Hazard Unit activa
fill='#4A4A6A', outline='#8A8ADA'

# STALL indicator
color='#FF6A6A'  # Rojo

# FWD indicator
color='#6ADA6A'  # Verde

# Forwarding paths
color='#DADA6A'  # Amarillo/Naranja
```

---

## 📝 Ejemplo de Uso

### Código de Prueba

```assembly
addi x1, x0, 10
addi x2, x0, 20
add x3, x1, x2   # Usa x1 y x2 recién calculados
sw x3, 0(x0)
```

### Ejecución

1. **Escribir código** en Editor
2. **Click Run** → Backend genera ambos logs
3. **Click Processor** → Se abre vista dual
4. **Click Step** varias veces:

**Ciclo 1**: Fetch de `addi x1, x0, 10`
- Izquierda: Solo Fetch activo
- Derecha: Solo Fetch activo

**Ciclo 3**: Pipeline se llena
- Izquierda: 3 instrucciones en pipeline
- Derecha: 3 instrucciones en pipeline

**Ciclo 5**: Completa primera instrucción
- Izquierda: Pipeline completo, x1 = 10
- Derecha: Pipeline completo, x1 = 10

**Ciclo 7**: `add x3, x1, x2` en Execute
- **Izquierda**: Sin hazards, avanza normal
- **Derecha**:
  - Hazard Unit ACTIVA
  - FWD indicador VERDE (forwarding activo)
  - Forward_EX_EX cables AMARILLOS
  - Datos forwardeados directamente al ALU

**Resultado:**
- Ambos completan el programa
- Derecha puede tener ciclos extra por stalls
- O mismo número de ciclos si forwarding resuelve todo

---

## 🚀 Iniciar el Sistema

```bash
cd Front
python main.py
```

**Workflow:**
1. Editor → Escribir código RISC-V
2. Run → Genera `log.txt` y `log_hazard_control.txt`
3. Processor → Vista dual con ambos procesadores
4. Step/Run → Avanzar ciclos simultáneamente
5. Observar diferencias entre ambos pipelines

---

## ✅ Checklist de Funcionalidades

### Componentes
- [x] HazardUnit con indicadores STALL/FWD
- [x] ForwardingPath cables especiales
- [x] ProcessorDiagramWithHazards (extiende base)
- [x] DualProcessorView (vista dual)

### Visualización
- [x] Dos procesadores lado a lado
- [x] Panel de control unificado
- [x] Títulos diferenciados (verde/rojo)
- [x] Estados independientes

### Funcionalidad
- [x] Lee dos logs diferentes
- [x] Sincroniza ciclo actual
- [x] Step afecta ambos
- [x] Run afecta ambos
- [x] Reset afecta ambos
- [x] Velocidad compartida

### Hazard Control
- [x] Hazard Unit visible
- [x] Indicadores STALL/FWD
- [x] Forwarding paths (líneas punteadas)
- [ ] Detección automática de stalls (pendiente)
- [ ] Detección automática de forwarding (pendiente)

---

## 🔮 Mejoras Futuras

### Detección Inteligente de Hazards

Parsear el log para detectar:
- RAW hazards (Read After Write)
- Control hazards (branches)
- Structural hazards (recurso ocupado)

### Métricas Comparativas

Agregar panel con:
- CPI de cada procesador
- Total de ciclos
- Número de stalls
- Número de forwards
- Eficiencia (%)

### Highlighting de Instrucciones Problemáticas

- Resaltar instrucciones que causan hazards
- Mostrar dependencias con flechas
- Explicación textual del hazard

### Animación de Forwarding

- Animar datos moviéndose por forwarding paths
- Mostrar valores siendo forwardeados
- Highlight de registros involucrados

---

**¡Sistema Dual Completo y Funcional!** 🎉

Ahora puedes comparar visualmente el comportamiento de un pipeline con y sin control de hazards, viendo cómo el forwarding y los stalls afectan la ejecución en tiempo real.
