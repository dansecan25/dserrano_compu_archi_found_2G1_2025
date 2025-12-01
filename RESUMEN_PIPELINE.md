# RESUMEN DE CAMBIOS: Pipeline con Latencias Realistas

## ¿Qué se hizo?

Implementaste un **simulador realista de un procesador RISC-V con pipeline de 5 etapas** donde:

1. **Cada etapa tiene una latencia configurable** (Fetch, Decode, RegisterFile, Execute, Store)
2. **Las instrucciones avanzan ciclo a ciclo**, solo si la etapa actual termina Y la siguiente está libre
3. **Las latencias son state-of-the-art**: basadas en procesadores reales (AMD Ryzen, Intel Core, etc.)

---

## Estructura del Pipeline

```
┌─────────┐      ┌─────────┐      ┌──────────┐      ┌─────────┐      ┌───────┐
│ FETCH   │ ---> │ DECODE  │ ---> │ REG FILE │ ---> │EXECUTE  │ ---> │ STORE │
│ (1 ciclo)       │(1 ciclo)       │(1 ciclo)       │(variable)      │(1ciclo)
└─────────┘      └─────────┘      └──────────┘      └─────────┘      └───────┘
                                                            ↑
                                        Latencia por instrucción:
                                        add/sub: 1 ciclo
                                        mul: 3 ciclos
                                        div: 10 ciclos
                                        lw: 4 ciclos
```

---

## Ejemplo de Ejecución (5 instrucciones)

```python
addi x1, x0, 5          # Ciclo 0-4: Pasa por todas las etapas (1 ciclo cada una)
addi x2, x0, 10         # Ciclo 1-5: Pasa detrás de x1
add x3, x1, x2          # Ciclo 2-6: Pasa detrás de x2  (execute: 1 ciclo)
mul x4, x3, x2          # Ciclo 3-9: Pasa detrás de x3  (execute: 3 ciclos ← MÁS LENTO)
div x5, x4, x1          # Ciclo 4-19: Pasa detrás de x4 (execute: 10 ciclos ← MUY LENTO)
```

**Total: ~19 ciclos** en lugar de sin pipeline que sería 5×5 = 25 ciclos.

---

## Archivos Creados/Modificados

### ✅ Nuevos

1. **`pipelineEtapas/latencias_config.py`**
   - Configuración centralizada de latencias
   - Diccionarios: `LATENCIES_CONFIG` (por etapa) y `INSTRUCTION_LATENCIES` (por instrucción)
   - Funciones: `get_stage_latency()` y `get_instruction_latency()`

2. **`PIPELINE_LATENCIES.md`**
   - Documentación completa con justificación state-of-the-art

3. **`ejemplo_pipeline_simple.py`**
   - Ejemplo ejecutable mostrando cómo usar el simulador

### 🔄 Refactorizados

- **`Fetch.py`**, **`Decode.py`**, **`RegisterFile.py`**, **`Execute.py`**, **`EtapaStore.py`**
  - Cada etapa ahora tiene:
    - `ciclos_restantes`: Contador de ciclos que faltan
    - `ocupada`: Boolean para saber si está procesando
    - `latencia`: Latencia base de la etapa
    - Métodos: `tick()`, `esta_libre()`, `get_estado()`

### 🆕 Completamente Reescrito

- **`cpuPipelineSinHazards.py`**
  - Motor de simulación con ciclos discretos
  - Transición correcta entre etapas (solo si ambas condiciones se cumplen)
  - Logging detallado en cada ciclo

---

## Cómo Cambiar Latencias

Para experimentar con latencias diferentes, edita `pipelineEtapas/latencias_config.py`:

```python
LATENCIES_CONFIG = {
    'Fetch': 2,          # Cambiar a 2 ciclos (simular caché miss)
    'Decode': 1,
    'RegisterFile': 1,
    'Execute': 2,
    'Store': 1,
}

INSTRUCTION_LATENCIES = {
    'add': 1,
    'mul': 5,            # Cambiar a 5 ciclos (hardware más rápido)
    'div': 20,           # Cambiar a 20 ciclos (hardware más lento)
    'lw': 5,             # L1 caché miss simulado
}
```

Luego ejecuta `python main.py` o `python ejemplo_pipeline_simple.py` y verás cómo cambia el número de ciclos.

---

## Salida del Simulador

### En Pantalla (en vivo):

```
[CICLO   5] Estado del Pipeline:
  Fetch:        Procesando: div x5, x4, x1 (1 ciclos restantes)
  Decode:       Procesando: mul x4, x3, x2 (1 ciclos restantes)
  RegFile:      Procesando: add x3, x1, x2 (1 ciclos restantes)
  Execute:      Procesando: addi x2, x0, 10 (1 ciclos restantes)
  Store:        Procesando: addi x1, x0, 5 (1 ciclos restantes)

[CICLO 5] [COMPLETADA] addi x1, x0, 5
```

### En `log.txt`:

Log completo de toda la ejecución (ciclos, instrucciones completadas, estados).

---

## Próximos Pasos (Sugerencias)

1. **Detectar Hazards de Datos**: Si una instrucción depende de otra, añadir stalls
2. **Branch Prediction**: Manejar saltos condicionales e incondicionales
3. **Forwarding**: Pasar datos entre etapas sin esperar writeback
4. **Cache Realista**: Diferentes latencias para cache hit/miss
5. **Out-of-Order**: Permitir que instrucciones sin dependencias se ejecuten en paralelo

---

## Resumen Ejecutivo

| Aspecto | Descripción |
|---------|-------------|
| **Pipeline** | 5 etapas (Fetch, Decode, RegFile, Execute, Store) |
| **Latencias** | State-of-the-art (Fetch=1, Decode=1, Execute=var, Store=1) |
| **Precisión** | Ciclos de reloj discretos, transiciones correctas |
| **Flexibility** | Fácil cambiar latencias en archivo config |
| **Logging** | Detallado, mostrando estado en cada ciclo |
| **Ejemplo** | `ejemplo_pipeline_simple.py` ejecutable |

¡El simulador está listo para usar y extender!
