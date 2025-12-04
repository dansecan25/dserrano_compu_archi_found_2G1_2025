# Sistema Completo de Visualización Pipeline RISC-V

## 🎯 Resumen del Sistema

El sistema completo funciona en **3 fases** que se ejecutan automáticamente:

### Fase 1: Ejecución del Backend
```
Usuario escribe código → Click en "Run" → Backend genera log.txt
```

### Fase 2: Lectura y Parseo del Log
```
log.txt → LogParser extrae ciclos → Estados por ciclo
```

### Fase 3: Visualización Dinámica
```
Ciclo actual → Mapeo de etapas → Activación de componentes → Diagrama actualizado
```

---

## 📊 Flujo Completo del Sistema

```
┌─────────────────────┐
│   Editor (Front)    │
│  Código RISC-V      │
└──────────┬──────────┘
           │ [Run Button]
           ▼
┌─────────────────────┐
│  Backend Pipeline   │
│ CPUpipelineNoHazard │
└──────────┬──────────┘
           │ Genera
           ▼
┌─────────────────────┐
│  Simulador/log.txt  │
│  ┌───────────────┐  │
│  │[CICLO X] ...  │  │
│  │  Fetch: ...   │  │
│  │  Decode: ...  │  │
│  │  RegFile: ... │  │
│  │  Execute: ... │  │
│  │  Store: ...   │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │ Lee
           ▼
┌─────────────────────┐
│    LogParser        │
│  Extrae por ciclo:  │
│  - PC               │
│  - Estados etapas   │
│  - Instrucciones    │
│  - Registros        │
└──────────┬──────────┘
           │ Envía estados
           ▼
┌─────────────────────┐
│  ProcessorView      │
│  update_display()   │
└──────────┬──────────┘
           │ Mapea etapas
           ▼
┌─────────────────────┐
│ _add_stage_comp...  │
│ Fetch → IF          │
│ Decode → ID         │
│ RegFile → EX        │
│ Execute → MEM       │
│ Store → WB          │
└──────────┬──────────┘
           │ Activa
           ▼
┌─────────────────────────────────┐
│    ProcessorDiagram             │
│  set_active_components([...])   │
│  set_active_wires([...])        │
└──────────┬──────────────────────┘
           │ Actualiza visual
           ▼
┌─────────────────────────────────┐
│      Visualización              │
│  ┌───────────────────────────┐  │
│  │ Pipeline Stages (arriba)  │  │
│  │ [Fetch][Decode][RegFile]  │  │
│  │ [Execute][Store]          │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ Processor Diagram (centro)│  │
│  │  Componentes + Cables     │  │
│  │  activos en VERDE         │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ Register File (derecha)   │  │
│  │  x0: 0   x16: 0          │  │
│  │  x1: 100 x17: 0          │  │
│  │  x2: 24  ...             │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## 🔄 Mapeo Correcto de Etapas

### Según el Formato del Log

El archivo `Simulador/log.txt` tiene este formato:

```
[CICLO   X] [PC=  Y] Estado del Pipeline:
  Fetch:        Procesando: addi x1, x0, 100 (1 ciclos restantes) / Libre
  Decode:       Procesando: nop (1 ciclos restantes) / Libre
  RegFile:      Procesando: addi x1, x0, 100 (1 ciclos restantes) / Libre
  Execute:      Procesando: addi x1, x0, 100 (1 ciclos restantes) / Libre
  Store:        Procesando: addi x1, x0, 100 (1 ciclos restantes) / Libre
```

### Mapeo a Etapas del Pipeline

| Nombre en Log | Etapa Pipeline | Componentes Principales |
|---------------|----------------|-------------------------|
| **Fetch** | IF (Instruction Fetch) | PC, Instruction Memory |
| **Decode** | ID (Instruction Decode) | Control Unit, Register File, Sign Extend |
| **RegFile** | EX (Execute) | ALU, ALU Control, Muxes |
| **Execute** | MEM (Memory Access) | Data Memory |
| **Store** | WB (Write Back) | Write Back Mux |

---

## 🎮 Uso del Sistema con Steps

### Controles Disponibles

```
⟲ Reset        → Volver a ciclo 0
◀ Step Back    → Ciclo anterior
▶ Step         → Siguiente ciclo
▶▶ Run         → Reproducción automática
⏸ Stop         → Pausar reproducción
[Speed Slider] → Ajustar velocidad (100-2000ms)
```

### Ejemplo de Navegación

**Ciclo 1**: Fetch activo
```
[CICLO 1] [PC= 4] Estado del Pipeline:
  Fetch:        Procesando: addi x1, x0, 100 (1 ciclos restantes)
  Decode:       Libre
  RegFile:      Libre
  Execute:      Libre
  Store:        Libre
```

**Componentes activos:**
- PC (verde)
- Instruction Memory (verde)
- IF/ID (verde)

**Cables activos:**
- PC_to_IMem (verde)
- IMem_to_IFID (verde)

---

**Ciclo 2**: Fetch + Decode activos
```
[CICLO 2] [PC= 8] Estado del Pipeline:
  Fetch:        Procesando: nop (1 ciclos restantes)
  Decode:       Procesando: addi x1, x0, 100 (1 ciclos restantes)
  RegFile:      Libre
  Execute:      Libre
  Store:        Libre
```

**Componentes activos:**
- PC, Instruction Memory, IF/ID (Fetch)
- Control Unit, Register File, Sign Extend, ID/EX (Decode)

---

**Ciclo 5**: Pipeline completo
```
[CICLO 5] [PC= 20] Estado del Pipeline:
  Fetch:        Procesando: nop (1 ciclos restantes)
  Decode:       Procesando: nop (1 ciclos restantes)
  RegFile:      Procesando: nop (1 ciclos restantes)
  Execute:      Procesando: nop (1 ciclos restantes)
  Store:        Procesando: addi x1, x0, 100 (1 ciclos restantes)
```

**Componentes activos:** TODOS
- IF: PC, Inst_Mem, IF/ID
- ID: Control, RegFile, SignExt, ID/EX
- EX: ALU, ALU_Control, Muxes, EX/MEM
- MEM: Data_Mem, MEM/WB
- WB: Mux_WB

**Al finalizar ciclo 5:**
```
[CICLO 5] [COMPLETADA] addi x1, x0, 100
[STORE] Registro x1 <- 100
```

**Register File se actualiza:**
- x1: 0 → x1: 100 (verde, resaltado)

---

## 💻 Código: Cómo Funciona Internamente

### 1. LogParser lee el log
```python
# En processor_view.py
self.parser = LogParser(log_path)
success = self.parser.parse()

# LogParser extrae:
cycle_data = {
    'cycle': 5,
    'pc': 20,
    'stages': {
        'Fetch': 'Procesando: nop (1 ciclos restantes)',
        'Decode': 'Procesando: nop (1 ciclos restantes)',
        'RegFile': 'Procesando: nop (1 ciclos restantes)',
        'Execute': 'Procesando: nop (1 ciclos restantes)',
        'Store': 'Procesando: addi x1, x0, 100 (1 ciclos restantes)'
    },
    'completed': 'addi x1, x0, 100',
    'reg_updates': [('x1', 100)]
}
```

### 2. update_display() procesa el ciclo
```python
def update_display(self):
    cycle_data = self.parser.get_cycle_data(self.current_cycle)

    # Actualizar etapas superiores
    for stage_name, stage_widget in self.stages.items():
        stage_value = stages.get(stage_name, 'Libre')
        stage_widget.update_stage(stage_value)

        # Si activa, agregar componentes
        if stage_value != "Libre":
            self._add_stage_components(stage_name, active_components, active_wires)

    # Actualizar diagrama
    self.processor_diagram.set_active_components(active_components)
    self.processor_diagram.set_active_wires(active_wires)
```

### 3. _add_stage_components mapea etapas
```python
def _add_stage_components(self, stage_name, components, wires):
    stage_mapping = {
        'Fetch': {
            'components': ['PC', 'PC_Adder', 'Inst_Mem', 'IF/ID'],
            'wires': ['PC_to_IMem', 'PC_to_Adder', 'Adder_to_IFID', 'IMem_to_IFID']
        },
        'Decode': {
            'components': ['Control', 'RegFile', 'SignExt', 'ID/EX'],
            'wires': ['IFID_to_Control', 'IFID_to_RegFile', 'RegFile_to_IDEX', 'SignExt_to_IDEX']
        },
        'RegFile': {  # = Execute (EX)
            'components': ['ALU_Control', 'ALU', 'Mux_ALU_A', 'Mux_ALU_B', 'EX/MEM'],
            'wires': ['IDEX_to_ALU', 'MuxA_to_ALU', 'MuxB_to_ALU', 'ALU_to_EXMEM']
        },
        'Execute': {  # = Memory (MEM)
            'components': ['Data_Mem', 'Mux_PC', 'MEM/WB'],
            'wires': ['EXMEM_to_DMem', 'DMem_to_MEMWB']
        },
        'Store': {  # = WriteBack (WB)
            'components': ['Mux_WB'],
            'wires': ['MEMWB_to_Mux', 'WB_to_RegFile']
        }
    }

    # Agregar componentes y cables de la etapa activa
    components.extend(stage_mapping[stage_name]['components'])
    wires.extend(stage_mapping[stage_name]['wires'])
```

### 4. ProcessorDiagram actualiza visualmente
```python
def set_active_components(self, component_names):
    # Desactivar todos
    for comp in self.components.values():
        comp.set_active(False)

    # Activar los especificados
    for name in component_names:
        if name in self.components:
            self.components[name].set_active(True)  # Se pone VERDE

def set_active_wires(self, wire_names):
    # Similar para cables
    for name in wire_names:
        if name in self.wires:
            self.wires[name].set_active(True)  # Se pone VERDE
```

---

## 🎬 Sistema de Animación (Steps)

### Avanzar un Ciclo
```python
def step(self):
    if self.current_cycle < self.parser.get_total_cycles() - 1:
        self.current_cycle += 1
        self.update_display()  # Actualiza TODO
```

### Reproducción Automática
```python
def run(self):
    self.is_running = True
    self._run_cycle()

def _run_cycle(self):
    if self.is_running and self.current_cycle < total_cycles - 1:
        self.current_cycle += 1
        self.update_display()
        # Esperar animation_speed ms y continuar
        self.after(self.animation_speed, self._run_cycle)
```

### Reset
```python
def reset(self):
    self.current_cycle = 0
    # Limpiar registros
    for reg_name, label in self.reg_labels.items():
        label.config(text=f'{reg_name}: 0')
    # Limpiar diagrama
    self.processor_diagram.reset_all()
    self.update_display()
```

---

## 📝 Formato de Entrada Alternativo (JSON)

Aunque actualmente el sistema lee `log.txt`, también está preparado para recibir estados en formato JSON:

```json
{
  "cycle": 5,
  "pc": 20,
  "description": "Full pipeline with store",
  "components": ["PC", "Inst_Mem", "Control", "RegFile", "ALU", "Data_Mem", "Mux_WB"],
  "wires": ["PC_to_IMem", "IFID_to_Control", "ALU_to_EXMEM", "WB_to_RegFile"]
}
```

Uso:
```python
# En ProcessorDiagram
diagram.set_state_from_json(state_data)
```

---

## ✅ Checklist de Funcionamiento

### Sistema Completo
- [x] Backend genera log.txt con formato correcto
- [x] LogParser extrae ciclos, PC, etapas, registros
- [x] ProcessorView integra pipeline stages + diagram
- [x] Mapeo correcto: Fetch→IF, Decode→ID, RegFile→EX, Execute→MEM, Store→WB
- [x] Componentes se activan según etapas
- [x] Cables se activan según etapas
- [x] Registros se actualizan al completar instrucciones
- [x] Step forward/backward funciona
- [x] Run/Stop funcionan
- [x] Reset funciona
- [x] Velocidad ajustable

### Visualización
- [x] Pipeline stages muestran instrucciones
- [x] Processor diagram con todos los componentes
- [x] Color coding: Verde=activo, Gris=inactivo
- [x] Register file con 32 registros
- [x] Info panel con estado del ciclo
- [x] Scrollbars para diagrama grande

---

## 🚀 Ejecución

```bash
# Terminal
cd Front
python main.py

# 1. Escribir código RISC-V en Editor
# 2. Click en "Run"
# 3. Click en "Processor"
# 4. Usar Step/Run para navegar ciclos
# 5. Ver componentes activarse en tiempo real
```

---

## 🎯 Resultado Final

**El usuario puede:**
1. ✅ Escribir código RISC-V
2. ✅ Ejecutar simulación (genera log.txt)
3. ✅ Ver pipeline stages actualizándose
4. ✅ Ver diagrama del procesador con componentes activos
5. ✅ Navegar ciclo por ciclo (Step)
6. ✅ Reproducir automáticamente (Run)
7. ✅ Ver registros actualizándose
8. ✅ Entender el flujo de datos visualmente

**Como fotos formando un video:**
- Cada ciclo = 1 foto
- Step/Run = pasar fotos
- Componentes verdes = flujo de datos
- Animación fluida del procesamiento

---

**¡Sistema completamente funcional!** 🎉

El procesador se visualiza dinámicamente, leyendo el log.txt del backend y mostrando los componentes activos en cada ciclo usando el sistema de steps para crear una animación del procesamiento.
