# Guía: Cómo Experimentar con Latencias

## Modifica latencias fácilmente

Edita `pipelineEtapas/latencias_config.py` para cambiar comportamiento del simulador.

---

## Escenario 1: CPU Muy Rápida

```python
# pipelineEtapas/latencias_config.py

LATENCIES_CONFIG = {
    'Fetch': 1,          # Super-pipelined (1 ciclo)
    'Decode': 1,
    'RegisterFile': 1,
    'Execute': 1,        # ALU rápida (1 ciclo)
    'Store': 1,
}

INSTRUCTION_LATENCIES = {
    'add': 1,
    'mul': 2,            # Multiplicación rápida
    'div': 5,            # División rápida
    'lw': 2,             # Cache muy rápido
    'sw': 1,
}
```

**Resultado**: ~10-12 ciclos para 5 instrucciones (muy eficiente)

---

## Escenario 2: CPU Realista (Actual)

```python
# pipelineEtapas/latencias_config.py

LATENCIES_CONFIG = {
    'Fetch': 1,
    'Decode': 1,
    'RegisterFile': 1,
    'Execute': 2,        # ALU normal
    'Store': 1,
}

INSTRUCTION_LATENCIES = {
    'add': 1,
    'mul': 3,
    'div': 10,
    'lw': 4,             # L1 caché hit
    'sw': 1,
}
```

**Resultado**: ~15-19 ciclos para 5 instrucciones (realista)

---

## Escenario 3: CPU Lenta con Cache Miss

```python
# pipelineEtapas/latencias_config.py

LATENCIES_CONFIG = {
    'Fetch': 2,          # L1 instruction caché miss
    'Decode': 2,         # Decodificador complejo
    'RegisterFile': 2,   # Pocos puertos
    'Execute': 3,        # ALU lenta
    'Store': 2,          # Writeback lento
}

INSTRUCTION_LATENCIES = {
    'add': 2,
    'mul': 5,
    'div': 15,           # Division muy lenta
    'lw': 20,            # L3 caché miss (200 ciclos en real, pero acortamos)
    'sw': 2,
}
```

**Resultado**: ~30-40 ciclos para 5 instrucciones (lento)

---

## Escenario 4: Procesador Con Hazards (Simulación Manual)

Si quieres simular hazards, aumenta latencias de escritura:

```python
INSTRUCTION_LATENCIES = {
    'add': 3,            # Resultado disponible en ciclo 3
    'mul': 5,            # Resultado disponible en ciclo 5
    'div': 15,           # Resultado disponible en ciclo 15
    'lw': 10,            # Datos no listos hasta ciclo 10
    'sw': 1,
}
```

Esto simula que el siguiente instrucción debe esperar.

---

## Ejemplo: Cambiar y Ejecutar

### 1. Modifica el archivo:

```bash
# Windows
notepad pipelineEtapas\latencias_config.py

# Linux/Mac
nano pipelineEtapas/latencias_config.py
```

### 2. Cambia los valores. Ejemplo:

```python
LATENCIES_CONFIG = {
    'Fetch': 1,
    'Decode': 1,
    'RegisterFile': 1,
    'Execute': 1,        # Cambié de 2 a 1
    'Store': 1,
}

INSTRUCTION_LATENCIES = {
    'add': 1,
    'mul': 1,            # Cambié de 3 a 1
    'div': 1,            # Cambié de 10 a 1
    'lw': 1,             # Cambié de 4 a 1
    'sw': 1,
}
```

### 3. Ejecuta de nuevo:

```bash
python ejemplo_pipeline_simple.py
```

### 4. Compara los ciclos totales:

- **Antes**: ~19 ciclos
- **Después**: ~9 ciclos (casi todos en paralelo)

---

## Interpretación de Resultados

### Estado del Pipeline (cada ciclo):

```
[CICLO   9] Estado del Pipeline:
  Fetch:        Procesando: div x5, x4, x1 (1 ciclos restantes)
  Decode:       Procesando: mul x4, x3, x2 (1 ciclos restantes)
  RegFile:      Procesando: add x3, x1, x2 (1 ciclos restantes)
  Execute:      Procesando: addi x2, x0, 10 (1 ciclos restantes)
  Store:        Procesando: addi x1, x0, 5 (1 ciclos restantes)
```

**Análisis**: Todas las etapas ocupadas = buen paralelismo

```
[CICLO  15] Estado del Pipeline:
  Fetch:        Libre
  Decode:       Procesando: div x5, x4, x1 (1 ciclos restantes)
  RegFile:      Procesando: div x5, x4, x1 (1 ciclos restantes)
  Execute:      Procesando: div x5, x4, x1 (6 ciclos restantes)
  Store:        Libre
```

**Análisis**: Execute bloqueada por `div` lenta, Fetch/Store vacías = stall

---

## Indicadores Clave

### IPC (Instructions Per Cycle):

```
Total de ciclos / Número de instrucciones = CPI

CPI bajo = buen rendimiento
CPI alto = mal rendimiento

Ejemplo:
- 19 ciclos / 5 instrucciones = CPI 3.8 (con mul y div)
- 9 ciclos / 5 instrucciones = CPI 1.8 (sin hazards)
```

### Ocupación del Pipeline:

Contar ciclos donde todas las etapas están ocupadas:

```
Ciclos llenos / Total de ciclos = Occupancy

Occupancy alta = buen uso del pipeline
Occupancy baja = stalls frecuentes
```

---

## Ejercicios Sugeridos

1. **¿Cuál es el CPI mínimo teórico?**
   - Respuesta: 1.0 (una instrucción completada por ciclo)
   - Solo posible sin hazards y con todas las etapas en paralelo

2. **¿Qué latencia de Execute maximiza throughput?**
   - Experimenta: 1, 2, 3, 5 ciclos
   - Mide CPI para cada valor

3. **¿Cómo afecta latencia de Load?**
   - Cambia `lw` de 4 a 10, 20, 50 ciclos
   - Observa cómo se ralentiza todo

4. **¿Cuándo es mejor un CPU con 3 etapas vs 5?**
   - Menos etapas = menos latencia por salto de etapa
   - Más etapas = mejor paralelismo (en ideal)

---

## Debugging: ¿Por qué está lento?

Si el simulador toma muchos ciclos:

1. **Busca etapas con ciclos_restantes > 1**
   ```
   Execute:      Procesando: div (10 ciclos restantes)  ← BOTTLENECK!
   ```

2. **Mira qué instrucción causa el problema**
   ```
   [EXECUTE] Ejecutando en ALU: div x5, x4, x1, latencia=10 ciclos
   ```

3. **Considera:**
   - ¿Es realista esa latencia?
   - ¿Hay hazards de datos?
   - ¿El operando está disponible?

---

## Salida Esperada

```bash
$ python ejemplo_pipeline_simple.py
...
[SIMULACIÓN COMPLETADA] Total de ciclos: 19
```

- **19 ciclos**: Típico con mul (3) y div (10)
- **~9 ciclos**: Si todo es ALU simple
- **>30 ciclos**: Si hay latencias muy altas o hazards

---

¡Diviértete experimentando!
