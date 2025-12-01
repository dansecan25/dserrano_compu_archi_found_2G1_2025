from pipelineEtapas import EtapaStore, Fetch, RegisterFile, Execute, Decode
from componentes import Memoria
from control import UnidadControl
import os
from pathlib import Path

class CPUpipelineNoHazard:
    def __init__(self):
        # Componentes del Pipeline
        self.mem_inst = Memoria(64)
        self.mem_data = Memoria(256)
        # Banco de registros simple para la simulación pipelined
        self.regs = [0] * 32
        self.etapa_fetch = Fetch()
        self.etapa_decode = Decode()
        self.etapa_registerFile = RegisterFile()
        self.etapa_execute = Execute()
        self.etapa_store = EtapaStore()
        self.PC = 0
        self.labels = {}
        self.data_pointer = 0
        self.codigo = []
        self.instrucciones_cola = []  # Cola de instrucciones a cargar en Fetch
        self.indice_instruccion = 0  # Índice de siguiente instrucción a cargar
        self.ciclo_actual = 0  # Contador de ciclos de reloj
        
        # Log
        self.log_file = open("log.txt", "w", encoding="utf-8")
        self.log_file.write("=== LOG DE EJECUCIÓN DEL CPU PIPELINE ===\n")
        self.log_file.write("Latencias: Fetch=1, Decode=1, RegisterFile=1, Execute=2(var), Store=1\n")
        self.log_file.write("=" * 80 + "\n\n")

    def log(self, mensaje):
        print(mensaje)
        self.log_file.write(mensaje + "\n")

    def cargarCodigo(self, codigo):
        """Carga el código (lista de instrucciones) en la cola."""
        # Filtrar comentarios y líneas vacías
        self.codigo = []
        for linea in codigo:
            linea = linea.split("#")[0].strip()
            if linea:
                self.codigo.append(linea)
        self.instrucciones_cola = self.codigo.copy()
        # Escribir también en la memoria de instrucciones para compatibilidad
        # con el comportamiento anterior de `CPU.cargar_programa_desde_archivo`.
        for i, instr in enumerate(self.instrucciones_cola):
            try:
                self.mem_inst.escribir(i, instr)
            except Exception:
                # ignorar errores de escritura fuera de rango
                pass
        # Registrar en el log cuántas instrucciones se cargaron y listarlas
        try:
            self.log(f"{len(self.instrucciones_cola)} instrucciones cargadas desde lista `riscv_code`")
            for idx, ins in enumerate(self.instrucciones_cola):
                self.log(f"  [{idx:03d}] {ins}")
        except Exception:
            # si el log no está disponible por alguna razón, no interrumpir
            pass

    def mostrar_estado_pipeline(self):
        """Imprime el estado actual de todas las etapas."""
        estado = f"\n[CICLO {self.ciclo_actual:3d}] Estado del Pipeline:\n"
        estado += f"  Fetch:        {self.etapa_fetch.get_estado()}\n"
        estado += f"  Decode:       {self.etapa_decode.get_estado()}\n"
        estado += f"  RegFile:      {self.etapa_registerFile.get_estado()}\n"
        estado += f"  Execute:      {self.etapa_execute.get_estado()}\n"
        estado += f"  Store:        {self.etapa_store.get_estado()}\n"
        return estado

    def tick(self):
        """
        Simula un ciclo de reloj discreto del pipeline.
        - Primero, las etapas reducen sus ciclos internos (tick)
        - Luego, movemos instrucciones entre etapas si ambas condiciones se cumplen:
          1. Etapa actual completó (ciclos_restantes == 0 después de tick)
          2. Etapa siguiente está libre
        """
        # 1. Tick en todas las etapas (reduce ciclos restantes)
        self.etapa_fetch.tick()
        self.etapa_decode.tick()
        self.etapa_registerFile.tick()
        self.etapa_execute.tick()
        self.etapa_store.tick()

        # 2. Mover instrucciones entre etapas (de Store hacia Fetch en ese orden)
        #    Esto simula que al final de cada ciclo, si una etapa termina, 
        #    pasa su instrucción a la siguiente (si está libre)

        # Store → Writeback (si completa, ejecutar efecto: mem/reg write)
        if self.etapa_store.getInstruccion() != "":
            instr_store = self.etapa_store.get_instruccion_actual()
            self.log(f"[CICLO {self.ciclo_actual}] [COMPLETADA] {instr_store}")
            # Ejecutar efectos pasados en params (si existen)
            try:
                params = getattr(self.etapa_store, 'params', []) or []
                if params:
                    accion = params[0]
                    if accion == 'reg_write':
                        rd, val = params[1], params[2]
                        if 0 <= rd < len(self.regs):
                            self.regs[rd] = val
                            self.log(f"[STORE] Registro x{rd} <- {val}")
                    elif accion == 'mem_write':
                        addr, val = params[1], params[2]
                        # escribir en memoria de datos
                        try:
                            self.mem_data.escribir(addr, val)
                            self.log(f"[STORE] Mem[{addr}] <- {val}")
                        except Exception:
                            self.log(f"[STORE] Error escribiendo Mem[{addr}]")
                    elif accion == 'mem_read_and_reg_write':
                        rd, addr = params[1], params[2]
                        val = self.mem_data.leer(addr)
                        if 0 <= rd < len(self.regs):
                            self.regs[rd] = val
                            self.log(f"[STORE] Load: x{rd} <- Mem[{addr}] = {val}")
            except Exception:
                pass
            # Limpiar la etapa Store después de completar
            self.etapa_store.instruccionEjecutando = ""
            self.etapa_store.ocupada = False

        # Execute → Store (si Execute completa y Store está libre)
        if self.etapa_execute.getInstruccion() != "" and self.etapa_store.esta_libre():
            instr = self.etapa_execute.getInstruccion()
            # Preparar params según el tipo de instrucción
            params = []
            try:
                partes = instr.replace(',', '').split()
                opcode = partes[0] if partes else ''
                if opcode in ['add', 'sub', 'mul', 'div']:
                    rd = int(partes[1][1:]); rs1 = int(partes[2][1:]); rs2 = int(partes[3][1:])
                    a = self.regs[rs1]; b = self.regs[rs2]
                    if opcode == 'add': val = a + b
                    elif opcode == 'sub': val = a - b
                    elif opcode == 'mul': val = a * b
                    else: 
                        val = a // b if b != 0 else 0
                    params = ['reg_write', rd, val]
                elif opcode == 'addi':
                    rd = int(partes[1][1:]); rs1 = int(partes[2][1:]); imm = int(partes[3])
                    val = self.regs[rs1] + imm
                    params = ['reg_write', rd, val]
                elif opcode == 'sw':
                    rs2 = int(partes[1][1:])
                    offset_reg = partes[2]
                    offset, rs1 = offset_reg.split('(')
                    offset = int(offset); rs1 = int(rs1[1:-1])
                    addr = self.regs[rs1] + offset
                    val = self.regs[rs2]
                    params = ['mem_write', addr, val]
                elif opcode == 'lw':
                    rd = int(partes[1][1:])
                    offset_reg = partes[2]
                    offset, rs1 = offset_reg.split('(')
                    offset = int(offset); rs1 = int(rs1[1:-1])
                    addr = self.regs[rs1] + offset
                    params = ['mem_read_and_reg_write', rd, addr]
                else:
                    params = []
            except Exception:
                params = []

            self.etapa_store.cargarInstruccion(instr, params)
            # Limpiar Execute
            self.etapa_execute.instruccionEjecutando = ""
            self.etapa_execute.ocupada = False

        # RegisterFile → Execute (si RegFile completa y Execute está libre)
        if self.etapa_registerFile.getInstruccion() != "" and self.etapa_execute.esta_libre():
            instr = self.etapa_registerFile.getInstruccion()
            self.etapa_execute.cargarInstruccion(instr, [])
            # Limpiar RegisterFile
            self.etapa_registerFile.instruccionEjecutando = ""
            self.etapa_registerFile.ocupada = False

        # Decode → RegisterFile (si Decode completa y RegFile está libre)
        if self.etapa_decode.getInstruccion() != "" and self.etapa_registerFile.esta_libre():
            instr = self.etapa_decode.getInstruccion()
            self.etapa_registerFile.cargarInstruccion(instr, [])
            # Limpiar Decode
            self.etapa_decode.instruccionEjecutando = ""
            self.etapa_decode.ocupada = False

        # Fetch → Decode (si Fetch completa y Decode está libre)
        if self.etapa_fetch.getInstruccion() != "" and self.etapa_decode.esta_libre():
            instr = self.etapa_fetch.getInstruccion()
            self.etapa_decode.cargarInstruccion(instr, [])
            # Limpiar Fetch
            self.etapa_fetch.instruccionEjecutando = ""
            self.etapa_fetch.ocupada = False

        # 3. Cargar siguiente instrucción en Fetch (si hay y Fetch está libre)
        if self.indice_instruccion < len(self.instrucciones_cola) and self.etapa_fetch.esta_libre():
            instr = self.instrucciones_cola[self.indice_instruccion]
            self.etapa_fetch.cargarInstruccion(instr, [])
            self.indice_instruccion += 1

        self.ciclo_actual += 1

    def ejecutar(self):
        """Ejecuta el programa completo en ciclos de reloj discretos."""
        self.log("\n=== INICIANDO SIMULACIÓN DEL PIPELINE ===\n")
        
        # Simulación de ciclos de reloj
        ciclos_max = 1000  # Prevención de bucle infinito
        
        while self.ciclo_actual < ciclos_max:
            # Mostrar estado antes del tick
            self.log(self.mostrar_estado_pipeline())
            
            # Ejecutar un ciclo
            self.tick()
            
            # Condición de salida: no hay más instrucciones y pipeline está vacío
            if (self.indice_instruccion >= len(self.instrucciones_cola) and
                self.etapa_fetch.get_instruccion_actual() == "" and
                self.etapa_decode.get_instruccion_actual() == "" and
                self.etapa_registerFile.get_instruccion_actual() == "" and
                self.etapa_execute.get_instruccion_actual() == "" and
                self.etapa_store.get_instruccion_actual() == ""):
                break
        
        self.log("\n" + "=" * 80)
        self.log(f"[SIMULACIÓN COMPLETADA] Total de ciclos: {self.ciclo_actual}")
        self.log("=" * 80 + "\n")
        # Guardar memoria de datos en archivo (mismo comportamiento que CPU)
        try:
            self.guardar_memoria_en_archivo("memoria_salida.txt")
        except Exception:
            pass
        self.log_file.close()

    def guardar_memoria_en_archivo(self, ruta):
        """Guarda el contenido de la memoria de datos en un archivo."""
        with open(ruta, "w", encoding="utf-8") as f:
            for i, valor in enumerate(self.mem_data.data):
                f.write(f"[{i:03d}] -> {valor}\n")
        self.log(f"Estado de memoria escrito en {ruta}")
