# Simulador de CPU Pipeline RISC-V

## ¿Qué es esto?

Un **simulador educativo de un procesador RISC-V con pipeline de 5 etapas** que permite visualizar y experimentar con:
- **Latencias por etapa** (Fetch, Decode, RegisterFile, Execute, Store)
- **Latencias por instrucción** (add, mul, div, lw, sw)
- **Ciclos de reloj discretos** donde instrucciones fluyen como en hardware real
- **State-of-the-art**: basado en procesadores reales (AMD Ryzen 2024, Intel Core)

---

## Ejecución Rápida

```bash
# En PowerShell/Terminal, dentro de la carpeta Simulador:

cd Simulador

# Opción 1: Ejecutar ejemplo simple (recomendado para entender)
python ejemplo_pipeline_simple.py

# Opción 2: Ejecutar programa completo
python main.py
```

---

## Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| **`cpuPipelineSinHazards.py`** | Motor de simulación (ciclos discretos, transiciones) |
| **`pipelineEtapas/Fetch.py`** | Etapa Fetch con latencia configurable |
| **`pipelineEtapas/Decode.py`** | Etapa Decode con latencia |
| **`pipelineEtapas/RegisterFile.py`** | Etapa RegisterFile |
| **`pipelineEtapas/Execute.py`** | Etapa Execute (latencia variable por instrucción) |
| **`pipelineEtapas/EtapaStore.py`** | Etapa Store/Writeback |
| **`pipelineEtapas/latencias_config.py`** | **CONFIGURACIÓN CENTRAL DE LATENCIAS** |
| **`ejemplo_pipeline_simple.py`** | Ejemplo ejecutable (5 instrucciones) |
| **`main.py`** | Programa principal con RISC-V complejo |
| **`log.txt`** | Salida detallada (se genera al ejecutar) |

---

## Cómo Cambiar Latencias

**Archivo**: `pipelineEtapas/latencias_config.py`

```python
# Cambiar latencias de etapas
LATENCIES_CONFIG = {
    'Fetch': 1,          # Ciclos
    'Decode': 1,
    'RegisterFile': 1,
    'Execute': 2,        # ← Cambiar aquí para ALU más rápida/lenta
    'Store': 1,
}

# Cambiar latencias por instrucción
INSTRUCTION_LATENCIES = {
    'add': 1,
    'mul': 3,            # ← Cambiar aquí (3 ciclos por multiplicación)
    'div': 10,           # ← Cambiar aquí (10 ciclos por división)
    'lw': 4,             # Load desde caché
    'sw': 1,
}
```

Luego ejecuta de nuevo: `python ejemplo_pipeline_simple.py`

---

## Ejemplo de Salida

```
[CICLO   0] Estado del Pipeline:
  Fetch:        Libre
  Decode:       Libre
  RegFile:      Libre
  Execute:      Libre
  Store:        Libre

[FETCH] Cargada instrucción: addi x1, x0, 5, latencia=1 ciclos

[CICLO   1] Estado del Pipeline:
  Fetch:        Procesando: addi x1, x0, 5 (1 ciclos restantes)
  Decode:       Libre
  RegFile:      Libre
  Execute:      Libre
  Store:        Libre

[DECODE] Decodificando: addi x1, x0, 5, latencia=1 ciclos
[FETCH] Cargada instrucción: addi x2, x0, 10, latencia=1 ciclos

...

[CICLO 9] [COMPLETADA] mul x4, x3, x2
[STORE] Escribiendo: mul x4, x3, x2, latencia=1 ciclos
[EXECUTE] Ejecutando en ALU: div x5, x4, x1, latencia=10 ciclos
  ↑ Nota: "div" toma 10 ciclos, no 1 como "mul"

[CICLO  10] Estado del Pipeline:
  Fetch:        Libre
  Decode:       Procesando: div x5, x4, x1 (1 ciclos restantes)
  RegFile:      Procesando: div x5, x4, x1 (1 ciclos restantes)
  Execute:      Procesando: div x5, x4, x1 (10 ciclos restantes)  ← BLOQUEADO
  Store:        Procesando: mul x4, x3, x2 (1 ciclos restantes)

[SIMULACIÓN COMPLETADA] Total de ciclos: 19
```

---

## Conceptos Clave

### Pipeline de 5 Etapas

```
Instr 1:  [F] [D] [R] [E] [S] → Completada
Instr 2:      [F] [D] [R] [E] [S]
Instr 3:          [F] [D] [R] [E] [S]
Instr 4:              [F] [D] [R] [E] [S]
Instr 5:                  [F] [D] [R] [E] [S]

Tiempo:   1   2   3   4   5   6   7   8   9
```

### Latencia de Execute (Variable)

Si `execute` toma 3 ciclos (mul):

```
Ciclo 7:  [EXECUTE] mul ... latencia=3 ciclos  ← Entra
Ciclo 8:  [EXECUTE] mul ... (3 ciclos restantes)
Ciclo 9:  [EXECUTE] mul ... (2 ciclos restantes)
Ciclo 10: [EXECUTE] mul ... (1 ciclo restante)
Ciclo 11: [EXECUTE] mul ... completa → pasa a Store
```

---

## Documentación Adicional

- **`PIPELINE_LATENCIES.md`**: Explicación detallada del pipeline y justificación de latencias
- **`GUIA_EXPERIMENTAR.md`**: Cómo cambiar latencias y experimentar
- **`RESUMEN_PIPELINE.md`**: Resumen ejecutivo de la implementación

---

## Indicadores de Rendimiento

### CPI (Cycles Per Instruction)

```
CPI = Total de ciclos / Número de instrucciones

Ejemplo:
- 19 ciclos / 5 instrucciones = 3.8 CPI (con mul y div)
- Objetivo: CPI ≤ 1.5 para buen rendimiento
```

### Ocupación del Pipeline

Porcentaje de ciclos donde todas las etapas están activas:

```
Ciclos llenos / Total de ciclos = Occupancy

Ejemplo:
- 10 ciclos llenos / 19 totales = 52% occupancy
- Objetivo: > 80% para buen paralelismo
```

---

## Próximas Mejoras (Futuro)

- [ ] Detectar y manejar hazards de datos
- [ ] Branch prediction y manejo de saltos
- [ ] Forwarding (data bypassing)
- [ ] Cache realista (L1, L2, L3)
- [ ] Out-of-order execution
- [ ] Estadísticas y análisis de rendimiento

---

## Archivos Generados

Al ejecutar, se crean:

- **`log.txt`**: Log detallado de la ejecución (ciclo a ciclo)
- **`memoria_salida.txt`**: Estado de la memoria de datos (si aplica)

---

## Requisitos

- Python 3.10+
- No requiere dependencias externas

---

## Instrucciones RISC-V Soportadas

- `add`, `sub` (ALU: 1 ciclo)
- `addi` (ALU immediate: 1 ciclo)
- `mul` (Multiplicación: 3 ciclos)
- `div` (División: 10 ciclos)
- `lw` (Load: 4 ciclos)
- `sw` (Store: 1 ciclo)
- `blt`, `beq` (Branch: 1 ciclo)
- `jal` (Jump: 1 ciclo)

---

## Ejemplo Completo

### main.py

```python
from cpuPipelineSinHazards import CPUpipelineNoHazard

programa = [
    "addi x1, x0, 5",
    "addi x2, x0, 10",
    "add x3, x1, x2",
    "mul x4, x3, x2",   # 3 ciclos en Execute
    "div x5, x4, x1",   # 10 ciclos en Execute
]

cpu = CPUpipelineNoHazard()
cpu.cargarCodigo(programa)
cpu.ejecutar()
```

**Resultado esperado**: ~19 ciclos total

---

## Modificar Latencias Fácilmente

```python
# pipelineEtapas/latencias_config.py

# CPU Rápida (1 ciclo todo)
LATENCIES_CONFIG = {'Execute': 1}
INSTRUCTION_LATENCIES = {'mul': 1, 'div': 1}
# Resultado: ~9 ciclos

# CPU Lenta (alta latencia)
LATENCIES_CONFIG = {'Execute': 3}
INSTRUCTION_LATENCIES = {'mul': 5, 'div': 15}
# Resultado: >40 ciclos
```

---

¡Disfruta experimentando con el simulador!

**Preguntas o sugerencias:**
- Edita `latencias_config.py` para experimentar
- Revisa `log.txt` para ver detalles de cada ciclo
- Lee la documentación complementaria (`.md`)
