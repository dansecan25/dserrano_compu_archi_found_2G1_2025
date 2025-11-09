



class ProcessorSimulator:
    def __init__(self):
        self.codigo;






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
    "limit:  .word 5000          # Límite (miles de saltos)",
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
    "        lw x8, 0(x6)         # x8 = limit = 5000",
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




