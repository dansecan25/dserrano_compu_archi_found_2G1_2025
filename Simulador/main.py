from cpu import CPU
from cpuPipelineSinHazards import CPUpipelineNoHazard

"""
riscv_code = [
    "#=========================================================",
    "# PROGRAMA: Conteo de saltos (branch y jump)",
    "# OBJETIVO: Realizar miles de saltos condicionales e",
    "#           incondicionales y documentar cuántos ocurren.",
    "# COMPATIBLE CON: Ripes (RISC-V RV32I)",
    "#=========================================================",
    "",
    "        .data",
    "count:  .word 0             # Contador de iteraciones",
    "limit:  .word 500          # Límite (miles de saltos)",
    "msg:    .string \"Fin del programa\\n\"",
    "",
    "        .text",
    "        .globl _start",
    "",
    "_start:",
            "addi x1, x0, 5        # x1 = 5",
            "addi x2, x0, 10       # x2 = 10",
            "add x3, x1, x2        # x3 = x1 + x2 (x3 = 15)",
            "add x4, x3, x1        # RAW: x4 depende de x3 recién escrito",
            "add x5, x3, x2        # RAW: x5 depende de x3 recién escrito",
            "add x6, x4, x5        # RAW: x6 depende de x4 y x5 recién escritos"
    "done:",
    "        # Fin del programa",
    "        nop                  # No operation (última instrucción)"
]

"""

riscv_code = [
    "# ============================================================",
    "# DEMOSTRACIÓN: Branch (beq) - Salto condicional",
    "# ============================================================",
    "",
    "addi x1, x0, 5         # x1 = 5",
    "addi x2, x0, 5         # x2 = 5",
    "nop",
    "nop",
    "nop",
    "nop",
    "beq x1, x2, igual      # Si x1 == x2, saltar a 'igual'",
    "addi x3, x0, 99        # x3 = 99 (NO se ejecuta si branch tomado)",
    "addi x4, x0, 88        # x4 = 88 (NO se ejecuta si branch tomado)",
    "igual:",
    "addi x5, x0, 10        # x5 = 10 (se ejecuta si branch tomado)",
    "nop",
    "nop",
    "nop",
    "nop",
    "addi x6, x5, 5         # x6 = 10 + 5 = 15",
    "",
    "# Resultado esperado (con branch tomado):",
    "#   x1 = 5",
    "#   x2 = 5",
    "#   x3 = 0 (instrucción saltada)",
    "#   x4 = 0 (instrucción saltada)",
    "#   x5 = 10",
    "#   x6 = 15",
]

cpu = CPU()
cpuPipeline=CPUpipelineNoHazard()
cpuPipeline.cargarCodigo(riscv_code)
cpuPipeline.ejecutar()

# cpu.ejecutar(riscv_code)
# cpu.ejecutar_todo()

print("\n" + "=" * 80)
print("ANÁLISIS DE HAZARDS")
print("=" * 80)

print(f"\nValores finales en registros:")
print(f"  x1 = {cpuPipeline.regs[1]} (esperado: 100)")
print(f"  x2 = {cpuPipeline.regs[2]} (esperado: 150)")
print(f"  x3 = {cpuPipeline.regs[3]} (esperado: 175)")

print("\n" + "=" * 80)
print("VERIFICACIÓN DE BRANCH (beq)")
print("=" * 80)

print(f"\nRegistros:")
print(f"  x1 = {cpuPipeline.regs[1]} (esperado: 5)")
print(f"  x2 = {cpuPipeline.regs[2]} (esperado: 5)")
print(f"  x3 = {cpuPipeline.regs[3]} (esperado: 0 - instrucción saltada)")
print(f"  x4 = {cpuPipeline.regs[4]} (esperado: 0 - instrucción saltada)")
print(f"  x5 = {cpuPipeline.regs[5]} (esperado: 10)")
print(f"  x6 = {cpuPipeline.regs[6]} (esperado: 15)")

print("\n" + "=" * 80)
print("VERIFICACIÓN")
print("=" * 80)

errores = 0

if cpuPipeline.regs[1] == 5:
    print(f"[OK] x1 = 5")
else:
    print(f"[ERROR] x1 = {cpuPipeline.regs[1]} (esperado 5)")
    errores += 1

if cpuPipeline.regs[2] == 5:
    print(f"[OK] x2 = 5")
else:
    print(f"[ERROR] x2 = {cpuPipeline.regs[2]} (esperado 5)")
    errores += 1

if cpuPipeline.regs[3] == 0:
    print(f"[OK] x3 = 0 (instrucción saltada por branch)")
else:
    print(f"[ERROR] x3 = {cpuPipeline.regs[3]} (esperado 0, branch no funciono)")
    errores += 1

if cpuPipeline.regs[4] == 0:
    print(f"[OK] x4 = 0 (instrucción saltada por branch)")
else:
    print(f"[ERROR] x4 = {cpuPipeline.regs[4]} (esperado 0, branch no funciono)")
    errores += 1

if cpuPipeline.regs[5] == 10:
    print(f"[OK] x5 = 10")
else:
    print(f"[ERROR] x5 = {cpuPipeline.regs[5]} (esperado 10)")
    errores += 1

if cpuPipeline.regs[6] == 15:
    print(f"[OK] x6 = 15")
else:
    print(f"[ERROR] x6 = {cpuPipeline.regs[6]} (esperado 15)")
    errores += 1

print("\n" + "=" * 80)
if errores == 0:
    print("[EXITO] Branch (beq) funciona correctamente")
    print("  - Condición evaluada: x1 == x2 (5 == 5) -> TOMADO")
    print("  - Instrucciones saltadas: 2 (x3, x4)")
    print("  - Pipeline flushed correctamente")
else:
    print(f"[ERROR] Se encontraron {errores} errores")

print("=" * 80)



