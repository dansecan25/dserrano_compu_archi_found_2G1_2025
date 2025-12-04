# Guía del Diagrama del Procesador - Arquitectura Modular

## Resumen

El sistema de visualización del procesador se ha implementado en **3 fases** para crear una representación visual completa del procesador pipeline RISC-V de 5 etapas.

## Arquitectura del Sistema

```
processor_components.py  →  Fase 1: Componentes modulares (bloques y cables)
        ↓
processor_diagram.py     →  Fase 2: Ensamblaje del procesador completo
        ↓
processor_view.py        →  Fase 3: Animación y sincronización con logs
```

---

## Fase 1: Componentes Modulares

**Archivo**: `processor_components.py`

### Componentes Implementados

#### 1. Wire (Cable)
Representa conexiones entre componentes.

```python
Wire(canvas, points, width=2, color='#4A4A4A', active_color='#6ADA6A', name="")
```

**Características**:
- Soporta múltiples puntos (rutas con ángulos rectos)
- Estados: Activo (verde) / Inactivo (gris)
- Etiquetas opcionales
- Grosor variable

**Métodos**:
- `set_active(bool)`: Activar/desactivar
- `add_label(text, position, offset)`: Agregar etiqueta

#### 2. ProcessorBlock
Clase base para todos los componentes del procesador.

```python
ProcessorBlock(canvas, x, y, width, height, label, color, active_color)
```

**Métodos comunes**:
- `set_active(bool)`: Activar/desactivar
- `get_center()`: Obtener punto central
- `get_port(side)`: Obtener puerto de conexión

#### 3. Componentes Especializados

##### ALU (Unidad Aritmético-Lógica)
- Forma: Trapecio
- Puertos: `top_left`, `top_right`, `bottom`, `left`, `right`
- Color activo: Verde

##### Multiplexer (Mux)
- Forma: Trapecio (angosto a la izquierda)
- Puertos múltiples de entrada
- Métodos:
  - `get_input_port(index)`: Puerto de entrada
  - `get_output_port()`: Puerto de salida
  - `get_control_port()`: Puerto de control

##### RegisterFile (Archivo de Registros)
- Puertos etiquetados: RR1, RR2, WR, RD1, RD2, WD, WE
- Visualización de 32 registros RISC-V

##### Memory (Memoria)
- Tipos: "Instruction" o "Data"
- Puertos según tipo:
  - Instruction: `Addr`, `RD`
  - Data: `Addr`, `WD`, `RD`, `WE`

##### Adder (Sumador)
- Forma: Círculo con símbolo "+"
- Usado para PC+4 y cálculo de branches

##### Register (Registro de Pipeline)
- Registros IF/ID, ID/EX, EX/MEM, MEM/WB
- Forma: Barra vertical
- Incluye símbolo de reloj

##### ControlUnit (Unidad de Control)
- Múltiples salidas de control
- 7 puertos de salida
- Método: `get_output_port(index)`

##### SignExtend (Extensor de Signo)
- Extensión de inmediatos
- Conexión entre ID y EX

##### PCRegister (Registro PC)
- Contador de Programa
- Método: `update_value(int)`

##### Junction (Unión)
- Puntos de bifurcación de cables
- Forma: Círculo pequeño
- Estados activo/inactivo

### Funciones Helper

```python
# Crear rutas con ángulos rectos
create_path(start, end, style='horizontal_first')

# Crear rutas multi-segmento
create_multi_segment_path(points)
```

---

## Fase 2: Ensamblaje del Procesador

**Archivo**: `processor_diagram.py`

### Clase ProcessorDiagram

Ensambla todos los componentes en un procesador pipeline completo de 5 etapas.

#### Constructor
```python
ProcessorDiagram(canvas)
```

#### Componentes Creados

**Etapa IF (Instruction Fetch)**:
- PC Register
- PC+4 Adder
- Instruction Memory
- IF/ID Pipeline Register

**Etapa ID (Instruction Decode)**:
- Control Unit
- Register File
- Sign Extend
- ID/EX Pipeline Register

**Etapa EX (Execute)**:
- ALU Control
- ALU
- Mux ALU A
- Mux ALU B
- Branch Adder
- EX/MEM Pipeline Register

**Etapa MEM (Memory Access)**:
- Data Memory
- PC Source Mux
- MEM/WB Pipeline Register

**Etapa WB (Write Back)**:
- Write Back Mux

#### Métodos Principales

##### set_active_components(list)
Activar componentes específicos.

```python
diagram.set_active_components(['PC', 'Inst_Mem', 'ALU'])
```

##### set_active_wires(list)
Activar cables específicos.

```python
diagram.set_active_wires(['PC_to_IMem', 'ALU_to_EXMEM'])
```

##### set_state_from_json(dict)
Configurar estado desde diccionario/JSON.

```python
state = {
    'components': ['PC', 'ALU'],
    'wires': ['PC_to_IMem']
}
diagram.set_state_from_json(state)
```

##### highlight_stage(stage)
Resaltar etapa completa del pipeline.

```python
diagram.highlight_stage('IF')  # IF, ID, EX, MEM, WB
```

##### reset_all()
Desactivar todos los componentes y cables.

##### get_all_component_names()
Obtener lista de todos los componentes disponibles.

##### get_all_wire_names()
Obtener lista de todos los cables disponibles.

---

## Fase 3: Animación y Sincronización

**Archivo**: `processor_view.py`

### Integración con Logs

El `ProcessorView` ahora incluye:

1. **Pipeline Stages** (Bloques superiores)
   - Visualización de 5 etapas
   - Estado de cada etapa por ciclo

2. **Processor Diagram** (Sección inferior)
   - Diagrama arquitectónico completo
   - Sincronizado con pipeline stages

3. **Register File** (Panel lateral)
   - 32 registros RISC-V
   - Actualizaciones en tiempo real

### Mapeo de Etapas

```python
stage_mapping = {
    'Fetch': {
        'components': ['PC', 'PC_Adder', 'Inst_Mem', 'IF/ID'],
        'wires': ['PC_to_IMem', 'PC_to_Adder', 'Adder_to_IFID', 'IMem_to_IFID']
    },
    'Decode': {
        'components': ['Control', 'RegFile', 'SignExt', 'ID/EX'],
        'wires': ['IFID_to_Control', 'IFID_to_RegFile', 'RegFile_to_IDEX', 'SignExt_to_IDEX']
    },
    # ... etc
}
```

### Flujo de Actualización

1. Usuario avanza un ciclo (Step/Run)
2. `update_display()` lee datos del ciclo
3. Actualiza pipeline stages (bloques superiores)
4. Determina componentes activos según etapas
5. Actualiza diagrama del procesador
6. Actualiza registros modificados

---

## Uso del Sistema

### 1. Aplicación Principal

```bash
cd Front
python main.py
```

1. Escribir código RISC-V en Editor
2. Hacer clic en "Run"
3. Cambiar a pestaña "Processor"
4. Ver visualización completa del pipeline

### 2. Demo Independiente

```bash
cd Front
python test_processor_diagram.py
```

Permite probar el diagrama sin ejecutar simulaciones:
- Botones para cada etapa (IF, ID, EX, MEM, WB)
- Navegación entre etapas
- Reset para limpiar visualización

---

## Personalización

### Colores

Modificar en `processor_components.py`:

```python
# Colores por defecto
color='#3A3A3A'         # Componente inactivo
active_color='#4A6A4A'  # Componente activo
wire_color='#4A4A4A'    # Cable inactivo
active_wire='#6ADA6A'   # Cable activo
```

### Posicionamiento

Modificar en `processor_diagram.py` → `_build_processor()`:

```python
# Ajustar espaciado
stage_width = 200  # Ancho por etapa
margin_x = 50      # Margen izquierdo
margin_y = 20      # Margen superior
```

### Nuevos Componentes

1. Crear clase en `processor_components.py`:
```python
class NewComponent(ProcessorBlock):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, width, height, "Label")

    def _draw(self):
        # Custom drawing logic
        pass
```

2. Agregar a `processor_diagram.py`:
```python
self.components['New_Comp'] = NewComponent(self.canvas, x, y)
```

3. Conectar con cables:
```python
self.wires['New_Wire'] = Wire(
    self.canvas,
    [start_point, end_point],
    name='New_Wire'
)
```

---

## Características Implementadas

### ✅ Fase 1: Completada
- [x] Componentes modulares (ALU, Mux, Memory, etc.)
- [x] Sistema de cables con múltiples puntos
- [x] Estados activo/inactivo
- [x] Puertos de conexión configurables

### ✅ Fase 2: Completada
- [x] Ensamblaje completo del procesador
- [x] 5 etapas del pipeline
- [x] Todos los componentes interconectados
- [x] Sistema de activación por estado
- [x] Soporte para JSON/dict de configuración

### ✅ Fase 3: Completada
- [x] Integración con ProcessorView
- [x] Sincronización con logs del backend
- [x] Animación ciclo por ciclo
- [x] Mapeo automático de etapas a componentes
- [x] Actualización en tiempo real

---

## Mejoras Futuras

### Funcionalidades Planificadas

1. **Valores en Cables**
   - Mostrar valores de datos en tránsito
   - Direcciones de memoria
   - Valores de inmediatos

2. **Hazards Visualization**
   - Detección de data hazards
   - Control hazards
   - Structural hazards
   - Forwarding paths

3. **Control Signals**
   - Visualización de señales de control
   - Estados de muxes
   - Señales de habilitación

4. **Interactive Mode**
   - Click en componentes para ver detalles
   - Tooltips con información
   - Zoom in/out

5. **Performance Metrics**
   - CPI (Cycles Per Instruction)
   - Pipeline efficiency
   - Stall cycles
   - Branch prediction accuracy

6. **Export Functionality**
   - Guardar diagrama como imagen
   - Exportar trace de ejecución
   - Generar reportes PDF

---

## Estructura de Archivos

```
Front/
├── processor_components.py      # Fase 1: Componentes modulares
├── processor_diagram.py         # Fase 2: Ensamblaje
├── processor_view.py            # Fase 3: Vista principal (actualizada)
├── test_processor_diagram.py   # Demo/Testing
├── mainMenu.py                  # Menú principal
└── main.py                      # Entry point
```

---

## Troubleshooting

### El diagrama no se muestra
- Verificar imports en `processor_view.py`
- Asegurarse de que `processor_diagram` esté inicializado
- Revisar consola para errores

### Componentes no se activan
- Verificar nombres en `stage_mapping`
- Confirmar que los nombres coincidan con `processor_diagram.py`
- Usar `get_all_component_names()` para listar disponibles

### Cables no se ven
- Ajustar colores (pueden estar muy oscuros)
- Verificar que los puntos estén dentro del canvas
- Usar `diagram_canvas.bbox('all')` para ver región

### Performance lento
- Reducir velocidad de animación
- Considerar menos componentes visibles
- Optimizar redibujado

---

## Referencias

- **RIPES**: https://github.com/mortbopet/Ripes
- **RISC-V Spec**: https://riscv.org/specifications/
- **Tkinter Canvas**: https://docs.python.org/3/library/tkinter.html

---

**Versión**: 2.0
**Última actualización**: Diciembre 2025
**Autor**: Sistema de Visualización Pipeline RISC-V
