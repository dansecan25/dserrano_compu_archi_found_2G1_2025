# CPU Pipeline con Predicción de Saltos

## Descripción

Este módulo implementa un CPU pipeline de 5 etapas con **predicción de saltos (branch prediction)** para reducir la penalización por branches.

## Características

### 1. Arquitectura Modular
- **No modifica** componentes existentes (Fetch, Decode, RegisterFile, Execute, Store)
- Mantiene compatibilidad con otros CPUs del proyecto
- Implementación completamente independiente

### 2. Branch Predictor
El CPU incluye un predictor de saltos con tres estrategias:

#### a) Always Taken
- Predice que todos los branches serán tomados
- Simple pero efectivo cuando mayoría de branches se toman
- Útil para bucles

#### b) Always Not Taken
- Predice que ningún branch será tomado
- Útil cuando hay muchos branches condicionales que fallan

#### c) Bimodal (2-bit predictor)
- Usa tabla de historia con estados de 2 bits por cada PC
- Estados: 
  - 0: Strongly Not Taken
  - 1: Weakly Not Taken
  - 2: Weakly Taken
  - 3: Strongly Taken
- Se adapta al patrón de cada branch individual
- Mejor para patrones mixtos

### 3. Ejecución Especulativa
- Cuando detecta un branch en Decode, hace predicción inmediata
- Si predice "tomado", cambia PC especulativamente al target
- Continúa ejecutando instrucciones del path predicho
- Si predicción fue correcta: **0 ciclos de penalización**
- Si predicción fue incorrecta: flush pipeline y corregir PC

### 4. Ventajas vs CPU Sin Predicción
- **Reducción de ciclos** cuando predicción es correcta
- **Sin penalización** en branches predichos correctamente
- **Estadísticas detalladas** de precisión

## Uso

### Ejemplo Básico

```python
from cpuPipelineConPredicciondeSaltos import CPUpipelineConPrediccionSaltos

# Crear CPU con estrategia de predicción
cpu = CPUpipelineConPrediccionSaltos(predictor_strategy='always_taken')

# Cargar código
codigo = [
    "addi x1, x0, 10",
    "addi x2, x0, 10",
    "beq x1, x2, igual",
    "addi x3, x0, 99",    # No se ejecuta
    "jal x0, fin",
    "igual:",
    "addi x3, x0, 100",   # Se ejecuta
    "fin:",
    "nop"
]

cpu.cargarCodigo(codigo)
cpu.ejecutar()

# Ver estadísticas
print(f"Ciclos: {cpu.ciclo_actual}")
print(f"Precisión: {cpu.branch_predictor.get_accuracy():.2f}%")
print(f"Flushes: {cpu.total_flushes}")
```

### Estrategias Disponibles

```python
# Always Taken (default)
cpu_at = CPUpipelineConPrediccionSaltos(predictor_strategy='always_taken')

# Always Not Taken
cpu_nt = CPUpipelineConPrediccionSaltos(predictor_strategy='always_not_taken')

# Bimodal (adaptativo)
cpu_bi = CPUpipelineConPrediccionSaltos(predictor_strategy='bimodal')
```

## Estadísticas Generadas

El CPU reporta:
- **Total branches**: Número de instrucciones branch ejecutadas
- **Predicciones**: Total de predicciones realizadas
- **Correctas**: Predicciones acertadas
- **Incorrectas**: Mispredictions
- **Precisión**: Porcentaje de acierto (%)
- **Total flushes**: Número de veces que se limpió el pipeline

## Comparación de Rendimiento

### Ejemplo: Programa con 3 branches

**Sin predicción:**
- Flush en cada branch
- Penalización de 4 ciclos por branch

**Con predicción Always Taken (si todos se toman):**
- 0 flushes
- 100% precisión
- Ahorro de ~12 ciclos

**Con predicción Bimodal:**
- Se adapta al patrón de cada branch
- Alta precisión tras "entrenamiento"

## Archivos Generados

- `log_prediccion.txt`: Log detallado de ejecución
- `memoria_salida_prediccion.txt`: Estado final de memoria

## Diferencias con cpuPipelineSinHazards

| Característica | Sin Hazards | Con Predicción |
|----------------|-------------|----------------|
| Branch Penalty | 4 ciclos (siempre) | 0 o 4 ciclos (depende) |
| Predicción | No | Sí (3 estrategias) |
| Ejecución Especulativa | No | Sí |
| Flush Pipeline | Siempre en branch | Solo en misprediction |
| Estadísticas | Básicas | Detalladas + precisión |

## Testing

Ejecutar tests:

```bash
# Test simple
python test_prediccion_simple.py

# Test comparativo completo
python test_prediccion_saltos.py
```

## Notas de Implementación

1. **Detección de Branch**: Se realiza en etapa Decode
2. **Predicción**: Inmediata al detectar branch
3. **Verificación**: En etapa Store cuando se conoce resultado real
4. **Corrección**: Si misprediction, flush y actualizar PC
5. **Actualización BHT**: Después de cada branch (para bimodal)

## Arquitectura del Predictor

```
Branch History Table (BHT)
┌─────────┬────────┐
│   PC    │ Estado │
├─────────┼────────┤
│   24    │   3    │ (Strongly Taken)
│   48    │   2    │ (Weakly Taken)
│   72    │   1    │ (Weakly Not Taken)
└─────────┴────────┘
```

## Extensiones Futuras

- Branch Target Buffer (BTB) para guardar targets
- Predictor gshare (global history)
- Predictor tournament (híbrido)
- Return Address Stack (RAS) para calls
