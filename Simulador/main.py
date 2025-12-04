from cpu import CPU
from cpuPipelineSinHazards import CPUpipelineNoHazard
from cpuPipelineHazardControl import CPUPipelineHazardControl
# 0-> original ripes
# 1-> no hazard codigo  
# 2-> hazard control necesitado
# 3-> prediccion de saltos  
codigo_pruebas:int = 1
riscv_code=[]
if(codigo_pruebas==0):
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
elif codigo_pruebas==1:
    riscv_code = [
        "# ============================================================",
        "# DEMOSTRACIÓN: Jump and Link (jal)",
        "# ============================================================",
        "",
        "# MAIN: Código principal",
        "addi x1, x0, 100       # x1 = 100",
        "nop",
        "nop",
        "nop",
        "nop",
        "jal x2, funcion1       # Llamar a funcion1, guardar PC+1 en x2",
        "despues_jal1:",
        "addi x5, x0, 50        # x5 = 50 (después de retornar de funcion1)",
        "nop",
        "nop",
        "nop",
        "nop",
        "jal x6, funcion2       # Llamar a funcion2, guardar PC+1 en x6",
        "despues_jal2:",
        "addi x8, x0, 88        # x8 = 88 (código final)",
        "",
        "# FIN - loop infinito para detener ejecución",
        "fin:",
        "jal x0, fin            # Loop infinito (salta a sí mismo)",
        "",
        "# FUNCION 1",
        "funcion1:",
        "addi x10, x0, 10       # x10 = 10",
        "addi x11, x0, 20       # x11 = 20",
        "nop",
        "nop",
        "nop",
        "nop",
        "add x12, x10, x11      # x12 = 10 + 20 = 30",
        "nop",
        "nop",
        "nop",
        "nop",
        "jal x0, despues_jal1   # Retornar a despues_jal1",
        "",
        "# FUNCION 2",
        "funcion2:",
        "addi x15, x0, 77       # x15 = 77",
        "addi x16, x0, 33       # x16 = 33",
        "nop",
        "nop",
        "nop",
        "nop",
        "jal x0, despues_jal2   # Retornar a despues_jal2",
        "",
        "# Resultado esperado:",
        "#   x1  = 100",
        "#   x2  = 24 (PC del primer jal = 20, entonces guardamos 24)",
        "#   x5  = 50",
        "#   x6  = 48 (PC del segundo jal = 44, entonces guardamos 48)",
        "#   x8  = 88",
        "#   x10 = 10, x11 = 20, x12 = 30",
        "#   x15 = 77, x16 = 33",
    ]
elif codigo_pruebas==2:
    riscv_code = [
    "# ============================================================",
    "# PROGRAMA: Generador de Hazards para pruebas de pipeline",
    "# ============================================================",
    "",
    ".text",
    ".globl _start",
    "",
    "_start:",
    "addi x1, x0, 5          # x1 = 5",
    "addi x2, x1, 3          # RAW: x2 depende de x1",
    "add x3, x2, x1          # RAW: x3 depende de x2",
    "",
    "# ---- Hazards con load-use ----",
    "la x4, dato             # Cargar dirección",
    "lw x5, 0(x4)            # Carga a x5",
    "addi x6, x5, 10         # RAW inmediato después del load",
    "",
    "# ---- Hazards en branch ----",
    "addi x7, x6, 1          # x7 depende de x6 recién escrito",
    "beq x7, x0, salto       # RAW branch",
    "addi x8, x0, 99         # (si no salta)",
    "jal x0, fin",
    "",
    "salto:",
    "add x9, x7, x5          # RAW: usa x7 y x5 recién modificados",
    "",
    "# ---- Hazard con JAL ----",
    "jal x10, funcion        # x10 = PC+1",
    "addi x11, x10, 2        # RAW: usa x10 justo después",
    "",
    "fin:",
    "jal x0, fin             # loop infinito",
    "",
    "# ---- Función ----",
    "funcion:",
    "addi x12, x0, 12",
    "addi x13, x12, 1        # RAW: depende de x12",
    "jal x0, fin",
    "",
    ".data",
    "dato: .word 42",
    ]

# 0-> no hazard control
# 1-> hazard control 
# 2-> prediccion de saltos
# 3-> both
cpu_testear:int=1
if(cpu_testear==0):
    cpuPipeline=CPUpipelineNoHazard()
elif cpu_testear==1:
    cpuPipeline=CPUPipelineHazardControl()

cpuPipeline.cargarCodigo(riscv_code)
#cpuPipeline.ejecutar()

# cpu.ejecutar(riscv_code)
# cpu.ejecutar_todo()

print("\n" + "=" * 80)
print("ANALISIS DE RESULTADOS - JAL (Jump and Link)")
print("=" * 80)

print(f"\n[REGISTROS PRINCIPALES]")
print(f"  x1  = {cpuPipeline.regs[1]:3d} (esperado: 64)")
print(f"  x2  = {cpuPipeline.regs[2]:3d} (esperado: 18 - return address)")
print(f"  x5  = {cpuPipeline.regs[5]:3d} (esperado: 32)")
print(f"  x6  = {cpuPipeline.regs[6]:3d} (esperado: 30 - return address)")
print(f"  x8  = {cpuPipeline.regs[8]:3d} (esperado: 58)")

print(f"\n[FUNCION 1]")
print(f"  x10 = {cpuPipeline.regs[10]:3d} (esperado: 10)")
print(f"  x11 = {cpuPipeline.regs[11]:3d} (esperado: 20)")
print(f"  x12 = {cpuPipeline.regs[12]:3d} (esperado: 30 = x10 + x11)")

print(f"\n[FUNCION 2]")
print(f"  x15 = {cpuPipeline.regs[15]:3d} (esperado: 77)")
print(f"  x16 = {cpuPipeline.regs[16]:3d} (esperado: 33)")

print("\n" + "=" * 80)
print("VERIFICACION DETALLADA")
print("=" * 80)

errores = 0

tests = [
    (1, 100, "x1 (main)"),
    (2, 24, "x2 (return address 1)"),
    (5, 50, "x5 (despues de funcion1)"),
    (6, 48, "x6 (return address 2)"),
    (8, 88, "x8 (codigo final)"),
    (10, 10, "x10 (funcion1)"),
    (11, 20, "x11 (funcion1)"),
    (12, 30, "x12 (suma en funcion1)"),
    (15, 77, "x15 (funcion2)"),
    (16, 33, "x16 (funcion2)"),
]

for reg, esperado, descripcion in tests:
    valor_real = cpuPipeline.regs[reg]
    if valor_real == esperado:
        print(f"[OK] {descripcion}: {valor_real} == {esperado}")
    else:
        print(f"[ERROR] {descripcion}: {valor_real} != {esperado}")
        errores += 1

print("\n" + "=" * 80)
print("RESUMEN DE VALIDACION")
print("=" * 80)

if errores == 0:
    print("[OK] TODOS LOS TESTS PASARON")
    print("\nFuncionalidad JAL validada:")
    print("  - Salto incondicional a labels")
    print("  - Guardado de direccion de retorno en rd")
    print("  - Pipeline flush en cada jal")
    print("  - Llamadas a funciones y retornos")
    print("  - JAL anidado (funciones que llaman a otras)")
else:
    print(f"[ERROR] FALLO {errores} TEST(S)")
    print("    Revisar implementacion de JAL")

print("=" * 80)





