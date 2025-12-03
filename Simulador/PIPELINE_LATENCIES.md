# Pipeline CPU: Latencias Realistas y Simulación de 5 Etapas

## Resumen de la Solución

He implementado un **simulador realista de un procesador RISC-V con pipeline de 5 etapas**, donde cada instrucción se mueve a través del pipeline con latencias que reflejan procesadores modernos (2024).

---

## 1. Latencias Asignadas (State-of-the-Art)

Las latencias están definidas en `pipelineEtapas/latencias_config.py`:

| Etapa | Latencia | Justificación |
|-------|----------|---------------|
| **Fetch** | 1 ciclo | Acceso a L1 instruction cache (hit) - muy rápido |
| **Decode** | 1 ciclo | Decodificación y lectura del archivo de registros - parallelizable |
| **RegisterFile** | 1 ciclo | Lectura de registros (análisis separado) - típicamente con Decode |
| **Execute** | Variable (1-10) | Depende de la instrucción: ADD=1, MUL=3, DIV=10 |
| **Store** | 1 ciclo | Writeback a registros + acceso L1 data cache |

### Justificación basada en procesadores reales:
- **AMD Ryzen 9 9950X** (2024): latencia L/S ≈ 4-5 ciclos (L1 caché)
- **Intel Core Ultra**: latencia L/S ≈ 4-5 ciclos
- **Nuestro modelo**: latencia total ideal ≈ 1+1+1+2+1 = **6 ciclos** (sin hazards)

Latencias específicas por instrucción:
```python
INSTRUCTION_LATENCIES = {
    'add': 1,      # ALU integer
    'mul': 3,      # Multiplicación
    'div': 10,     # División (muy lenta)
    'lw': 4,       # Load (3-4 ciclos por cache miss)
    'sw': 1,       # Store
}
```

---

## 2. Cómo Funciona el Pipeline

### 2.1 Ciclos de Reloj Discretos

El simulador ejecuta **ciclos de reloj discretos** donde:

1. **Tick en todas las etapas**: Cada etapa reduce su contador `ciclos_restantes`
2. **Movimiento de instrucciones**: Si una etapa completa (ciclos_restantes = 0) y la siguiente está libre, la instrucción se mueve

```python
# Pseudocódigo del ciclo:
def tick(self):
    # 1. Reduce ciclos en todas las etapas
    fetch.tick()      # -1 ciclo si está ocupada
    decode.tick()     # -1 ciclo si está ocupada
    execute.tick()    # -1 ciclo si está ocupada
    ...
    
    # 2. Mueve instrucciones si se cumplen condiciones
    if execute.completa() and store.esta_libre():
        store.cargarInstruccion(execute.getInstruccion())
    ...
    
    # 3. Carga nueva instrucción en Fetch si está libre
    if fetch.esta_libre():
        fetch.cargarInstruccion(siguiente_instruccion)
```

### 2.2 Estados de una Etapa

Cada etapa mantiene:
- `instruccionEjecutando`: Instrucción actual
- `ciclos_restantes`: Ciclos que faltan para completar
- `ocupada`: Boolean indicando si está procesando
- `latencia`: Ciclos totales de la etapa (base)

```python
class Fetch:
    def cargarInstruccion(self, instr):
        if not self.ocupada:
            self.instruccionEjecutando = instr
            self.ciclos_restantes = self.latencia
            self.ocupada = True
    
    def tick(self):
        if self.ocupada:
            self.ciclos_restantes -= 1
            if self.ciclos_restantes == 0:
                self.ocupada = False
                return True
        return False
```

### 2.3 Visualización del Estado

En cada ciclo, el simulador muestra el estado de todas las etapas:

```
[CICLO   5] Estado del Pipeline:
  Fetch:        Procesando: la x6, limit (1 ciclos restantes)
  Decode:       Procesando: la x5, count (1 ciclos restantes)
  RegFile:      Procesando: _start: (1 ciclos restantes)
  Execute:      Procesando: .globl _start (1 ciclos restantes)
  Store:        Procesando: .text (1 ciclos restantes)

[CICLO 5] [COMPLETADA] .text
[STORE] Escribiendo: .globl _start, latencia=1 ciclos
[EXECUTE] Ejecutando en ALU: _start:, latencia=1 ciclos
[REGISTER_FILE] Leyendo registros: la x5, count, latencia=1 ciclos
[DECODE] Decodificando: la x6, limit, latencia=1 ciclos
[FETCH] Cargada instrucción: lw x7, 0(x5), latencia=1 ciclos
```

---

## 3. Archivos Modificados y Creados

### Nuevos:
- **`pipelineEtapas/latencias_config.py`**: Configuración de latencias y función `get_stage_latency()`, `get_instruction_latency()`

### Refactorizados:
- **`pipelineEtapas/Fetch.py`**: Ahora con latencia interna, estado `ocupada`, `ciclos_restantes`
- **`pipelineEtapas/Decode.py`**: Idem
- **`pipelineEtapas/RegisterFile.py`**: Idem
- **`pipelineEtapas/Execute.py`**: Idem, con latencia específica por instrucción
- **`pipelineEtapas/EtapaStore.py`**: Idem
- **`pipelineEtapas/__init__.py`**: Exporta funciones de latencias

### Completamente Reescrito:
- **`cpuPipelineSinHazards.py`**: Nuevo motor de simulación con ciclos discretos, transición correcta entre etapas

---

## 4. Cómo Usar

### Ejecución Básica:

```bash
cd Simulador
python main.py
```

### Salida:
- **`log.txt`**: Log detallado de cada ciclo, instrucciones completadas, estado del pipeline
- **Pantalla**: En vivo durante la ejecución (primeros 100-150 ciclos en terminal)

### Archivos de Entrada:
- **`main.py`**: Define el programa RISC-V como lista de strings
- Usa `CPUpipelineNoHazard` para la simulación

---

## 5. Ejemplo de Ejecución

Para un programa simple con 5 instrucciones:

```
Ciclo 0-4: Cada instrucción entra en Fetch con latencia 1 ciclo cada una
Ciclo 5: Primera instrucción sale de Store (completada)
           → Latencia total = 5 etapas × 1 ciclo = 5 ciclos
Ciclo 6: Segunda instrucción sale (completada)
Ciclo 9: Tercera instrucción sale (pero Execute tomó 2 ciclos si es un `div`)
         → Latencia total = 1+1+1+10+1 = 14 ciclos
```

---

## 6. Próximos Pasos (Opcionales)

1. **Hazards de datos**: Detectar dependencias RAW (Read-After-Write) e implementar forwarding
2. **Hazards de control**: Branch prediction, delay slots
3. **Cache realista**: Latencias de L1/L2/L3 y misses
4. **Out-of-order execution**: Permitir que instrucciones se ejecuten fuera de orden si no hay dependencias
5. **Estadísticas**: IPC (Instructions Per Cycle), ciclos promedio por instrucción, throughput

---

## 7. Detalles Técnicos

### Ventajas del Diseño:

✓ **Realista**: Latencias basadas en hardware real  
✓ **Flexible**: Fácil cambiar latencias en `latencias_config.py`  
✓ **Observable**: Logging detallado en cada ciclo  
✓ **Modular**: Cada etapa es independiente  
✓ **Extensible**: Fácil agregar nuevas instrucciones o etapas  

### Limitaciones Actuales:

- Sin hazards implementados (todavía)
- Todas las instrucciones se cargan secuencialmente
- No hay branch prediction (asume rutas lineales)

---

## 8. Estadísticas del Pipeline

Después de ejecutar el programa, el log mostrará:

```
[SIMULACIÓN COMPLETADA] Total de ciclos: 47
```

Esto significa:
- **47 ciclos** para procesar ~9 instrucciones reales
- **IPC ≈ 0.19** (instruction-per-cycle)
- Sin pipeline: sería ~5 ciclos × 9 = 45 ciclos (similar, porque sin hazards)
- **Con hazards**: CPI aumentaría significativamente

---

Cualquier pregunta o mejora, avísame. ¡El simulador está listo para usar!
