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
    "        #-------------------------------------------------",
    "        # Inicialización",
    "        #-------------------------------------------------",
    "        la x5, count         # x5 = dirección del contador",
    "        la x6, limit         # x6 = dirección del límite",
    "        lw x7, 0(x5)         # x7 = count = 0",
    "        lw x8, 0(x6)         # x8 = limit = 500",
    "",
    "loop:",
    "        #-------------------------------------------------",
    "        # Cuerpo del bucle: cada iteración implica un salto",
    "        #-------------------------------------------------",
    "        addi x7, x7, 1       # count++",
    "        sw x7, 0(x5)         # Guardar en memoria (1 acceso write)",
    "",
    "        # Condicional: si count < limit → saltar a loop",
    "        blt x7, x8, loop     # Branch condicional (salto)",
    "        addi x0, x0, 0       # NOP para evitar hazard de control (si no hay hardware)",
    "",
    "        # Si no se cumple, continúa aquí",
    "end:",
    "        # Salto incondicional final",
    "        jal x0, done         # Jump sin retorno (salto absoluto)",
    "        addi x0, x0, 0       # NOP (evita usar PC incorrecto si no hay branch forwarding)",
    "",
    "done:",
    "        # Fin del programa",
    "        nop                  # No operation (última instrucción)"
]
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
            "add x3, x1, x2        # x3 = 15",
            "sw x3, 0(x0)          # Mem[0] = 15",
            "",
            "addi x4, x3, 2        # x4 = 17",
            "sw x4, 4(x0)          # Mem[4] = 17",
            "",
            "sub x5, x4, x1        # x5 = 12",
            "sw x5, 8(x0)          # Mem[8] = 12",
            "",
            "add x6, x5, x5        # x6 = 24",
            "sw x6, 12(x0)         # Mem[12] = 24",
            "",
            "lw x7, 0(x0)          # x7 = 15",
            "lw x8, 4(x0)          # x8 = 17",
            "lw x9, 8(x0)          # x9 = 12",
            "lw x10, 12(x0)        # x10 = 24",
            "add x11, x7, x8       # x11 = 32",
            "add x12, x9, x10      # x12 = 36",
            "sw x11, 16(x0)        # Mem[16] = 32",
            "sw x12, 20(x0)        # Mem[20] = 36",
            "",
            "lw x13, 16(x0)        # x13 = 32",
            "lw x14, 20(x0)        # x14 = 36",
            "add x15, x13, x14     # x15 = 68",
            "sw x15, 24(x0)        # Mem[24] = 68"
    "done:",
    "        # Fin del programa",
    "        nop                  # No operation (última instrucción)"
]




cpu = CPU()
cpuPipeline=CPUpipelineNoHazard()
cpuPipeline.cargarCodigo(riscv_code)
cpuPipeline.ejecutar()

# cpu.ejecutar(riscv_code)
# cpu.ejecutar_todo()




print("\nEjecución completada. Revisa 'log.txt' y 'memoria_salida.txt'.")



