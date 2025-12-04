from Simulador.cpuPipelinePrediccionSaltosHazardControl import *
from Simulador.cpuPipelineSinHazards import *
from Simulador.cpuPipelineHazardControl import *
from Simulador.cpuPipelineConPredicciondeSaltos import *
codigo_pruebas:int = 4
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
    "sw x1, 5",
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
elif codigo_pruebas==3:
    # ============================================================
    # PRUEBA: Predicción de saltos con bucle
    # ============================================================
    riscv_code = [
        "# ============================================================",
        "# PRUEBA 3: Predicción de saltos - Bucle con decisiones",
        "# ============================================================",
        "",
        "# --- Inicialización ---",
        "addi x1, x0, 0        # x1 = 0 (contador)",
        "addi x2, x0, 5        # x2 = 5 (límite del bucle)",
        "addi x3, x0, 0        # x3 = 0 (acumulador)",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Bucle: sumar números del 1 al 5 ---",
        "bucle:",
        "addi x1, x1, 1        # x1++ (incrementar contador)",
        "nop",
        "nop",
        "nop",
        "add x3, x3, x1        # x3 += x1 (acumular)",
        "nop",
        "nop",
        "nop",
        "nop",
        "beq x1, x2, fin_bucle # Si x1 == 5, salir del bucle",
        "jal x0, bucle         # Si no, repetir bucle",
        "",
        "fin_bucle:",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Decisión: verificar si suma es correcta ---",
        "addi x4, x0, 15       # x4 = 15 (valor esperado)",
        "nop",
        "nop",
        "nop",
        "beq x3, x4, correcto  # Si x3 == 15, ir a 'correcto'",
        "addi x5, x0, 99       # x5 = 99 (ERROR - no debería ejecutarse)",
        "jal x0, fin           # Saltar a fin",
        "",
        "correcto:",
        "addi x5, x0, 100      # x5 = 100 (CORRECTO)",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Operaciones finales ---",
        "mul x6, x3, x2        # x6 = x3 * x2 = 15 * 5 = 75",
        "nop",
        "nop",
        "nop",
        "nop",
        "",
        "fin:",
        "addi x7, x0, 77       # x7 = 77 (marca de fin)",
        "nop",
        "",
        "# Resultado esperado:",
        "#   x1  = 5  (contador final)",
        "#   x2  = 5  (límite)",
        "#   x3  = 15 (suma: 1+2+3+4+5)",
        "#   x4  = 15 (valor esperado)",
        "#   x5  = 100 (marca de correcto)",
        "#   x6  = 75 (15 * 5)",
        "#   x7  = 77 (marca de fin)",
    ]
elif codigo_pruebas==4:
    riscv_code=["# ============================================================",
        "# PRUEBA 4: Múltiples Store Words (sw)",
        "# Objetivo: Escribir varios valores en memoria",
        "# ============================================================",
        "",
        "# --- Inicializar valores en registros ---",
        "addi x1, x0, 10       # x1 = 10",
        "addi x2, x0, 20       # x2 = 20",
        "addi x3, x0, 30       # x3 = 30",
        "addi x4, x0, 40       # x4 = 40",
        "addi x5, x0, 50       # x5 = 50",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Dirección base ---",
        "addi x10, x0, 0       # x10 = 0 (dirección base)",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Store múltiples valores ---",
        "sw x1, 0(x10)         # Mem[0] = 10",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x2, 4(x10)         # Mem[4] = 20",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x3, 8(x10)         # Mem[8] = 30",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x4, 12(x10)        # Mem[12] = 40",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x5, 16(x10)        # Mem[16] = 50",
        "nop",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Calcular suma y guardar ---",
        "add x6, x1, x2        # x6 = 10 + 20 = 30",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x6, 20(x10)        # Mem[20] = 30",
        "nop",
        "nop",
        "nop",
        "nop",
        "",
        "add x7, x3, x4        # x7 = 30 + 40 = 70",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x7, 24(x10)        # Mem[24] = 70",
        "nop",
        "nop",
        "nop",
        "nop",
        "",
        "add x8, x5, x6        # x8 = 50 + 30 = 80",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x8, 28(x10)        # Mem[28] = 80",
        "nop",
        "nop",
        "nop",
        "nop",
        "",
        "# --- Store valor final ---",
        "addi x9, x0, 99       # x9 = 99 (marca de finalización)",
        "nop",
        "nop",
        "nop",
        "nop",
        "sw x9, 32(x10)        # Mem[32] = 99",
        "nop",
        "",]


def mock_menu():
    print("Ejecutando mock interface")
    print("Seleccione 2 procesadores para correr simultaneamente")

    option = None

    while option != 7:
        simuladores_seleccionados: list[int] = []

        while len(simuladores_seleccionados) < 2:
            sim_seleccionado = input(
                "Seleccione un simulador:\n"
                "1. Pipeline sin hazard control\n"
                "2. Pipeline con hazard control\n"
                "3. Pipeline con prediccion de saltos always taken\n"
                "4. Pipeline con prediccion de saltos always not taken\n"
                "5. Pipeline con prediccion de saltos always taken y hazard control\n"
                "6. Pipeline con prediccion de saltos always not taken y hazard control\n"
                "7. Salir\n"
                "Seleccione: "
            )

            try:
                sim_seleccionado_int = int(sim_seleccionado)

                # Opción de salir
                if sim_seleccionado_int == 7:
                    option = 7
                    print("Adios")
                    return

                # Validar rango
                if sim_seleccionado_int < 1 or sim_seleccionado_int > 7:
                    print("Opción fuera de rango")
                    continue

                # Evitar duplicados
                if sim_seleccionado_int in simuladores_seleccionados:
                    print("Ya seleccionó ese simulador, escoja otro.")
                    continue

                # Agregar simulador seleccionado
                simuladores_seleccionados.append(sim_seleccionado_int)
                print(f"Simulador {sim_seleccionado_int} agregado.")

            except ValueError:
                print("Ingrese un número válido.")

        clases_simulador:list[object]=[]
        for numero_simulador in simuladores_seleccionados:
            if(numero_simulador==1):
                clases_simulador.append(CPUpipelineNoHazard())
            elif(numero_simulador==2):
                clases_simulador.append(CPUPipelineHazardControl())
            elif(numero_simulador==3):
                clases_simulador.append(CPUpipelineConPrediccionSaltos(predictor_strategy='always_taken'))
            elif(numero_simulador==4):
                clases_simulador.append(CPUpipelineConPrediccionSaltos(predictor_strategy='always_not_taken'))
            elif(numero_simulador==5):
                clases_simulador.append(CPUPipelinePrediccionSaltosHazardControl(predictor_strategy='always_taken'))
            elif(numero_simulador==6):
                clases_simulador.append(CPUPipelinePrediccionSaltosHazardControl(predictor_strategy='always_not_taken'))
            
        print(f"Simuladores seleccionados: {clases_simulador}")
        print("Ejecutando simulación...\n")

        # Selección del método de ejecución
        metodoSeleccionado = None

        while metodoSeleccionado is None:
            metodo_selecc = input(
                "¿Cómo quiere correrlo?\n"
                "1. Paso a paso\n"
                "2. A una velocidad determinada\n"
                "3. Todo de un solo\n"
                "Seleccione: "
            )

            try:
                metodoSeleccionado_int = int(metodo_selecc)

                # Validar rango
                if metodoSeleccionado_int < 1 or metodoSeleccionado_int > 3:
                    print("Opción fuera de rango (solo 1, 2 o 3).")
                    continue

                # Si está dentro del rango, seleccionar
                metodoSeleccionado = metodoSeleccionado_int
                print(f"Método seleccionado: {metodoSeleccionado}")

            except ValueError:
                print("Ingrese un número válido.")

        # Aquí ya tienes un método válido y confirmado
        print(f"Ejecutando simulación con método {metodoSeleccionado}...\n")
        clases_simulador[0].cargarCodigo(riscv_code)
        clases_simulador[0].ejecutar()
        clases_simulador[1].cargarCodigo(riscv_code)
        clases_simulador[1].ejecutar()


mock_menu()
CPUPipelineHazardControl.cargarCodigo(riscv_code)
CPUPipelineHazardControl.ejecutar()