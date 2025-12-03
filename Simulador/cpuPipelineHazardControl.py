from pipelineEtapas import EtapaStore, Fetch, RegisterFile, Execute, Decode
from componentes import Memoria
from control import UnidadControl
import os
from pathlib import Path

class CPUPipelineHazardControl:
    """
    Pipeline de 5 etapas con:
     - Filtrado de directivas (.data, .text, .word, .string, .globl, labels)
     - Mapeo de labels a PC en bytes (offset = index*4)
     - Detección RAW simple y load-use
     - Inserción de NOPs (stall) como manejo de hazards (no forwarding)
    """

    def __init__(self):
        # Componentes del Pipeline
        self.mem_inst = Memoria(64)
        self.mem_data = Memoria(256)
        # Banco de registros simple para la simulación pipelined
        self.regs = [0] * 32
        self.etapa_fetch = Fetch()
        self.etapa_decode = Decode()
        self.etapa_registerFile = RegisterFile(regs=self.regs)
        self.etapa_execute = Execute(mem_data=self.mem_data)
        self.etapa_store = EtapaStore()
        self.PC = 0
        self.labels = {}
        self.data_pointer = 0
        self.codigo = []
        self.instrucciones_cola = []  # Cola de instrucciones a cargar en Fetch (solo instrucciones)
        self.indice_instruccion = 0  # Índice (en bytes) de siguiente instrucción a cargar
        self.ciclo_actual = 0  # Contador de ciclos de reloj

        # Log
        self.log_file = open("log_hazard_control.txt", "w", encoding="utf-8")
        self.log_file.write("=== LOG DE EJECUCIÓN DEL CPU PIPELINE (Hazard Control) ===\n")
        self.log_file.write("Latencias: Fetch=1, Decode=1, RegisterFile=1, Execute=2(var), Store=1\n")
        self.log_file.write("=" * 80 + "\n\n")

    def log(self, mensaje):
        print(mensaje)
        try:
            self.log_file.write(mensaje + "\n")
        except Exception:
            pass

    # ---------------------------
    # PARSER / CARGA DE CÓDIGO
    # ---------------------------

    def _es_directiva(self, linea):
        """Devuelve True si la línea es una directiva que NO debe entrar al pipeline."""
        l = linea.strip()
        if not l:
            return True
        if l.startswith("#"):
            return True
        if l.startswith("."):
            return True
        # definiciones de datos: .word, .string, etiquetas con colon no son instrucciones
        # También ignoramos pseudo-instrucciones que no queremos simular aquí
        return False

    def cargarCodigo(self, codigo):
        """
        Filtra directivas y labels. Llena:
        - self.instrucciones_cola: lista de instrucciones (strings) que entran al pipeline
        - self.labels: mapea label -> PC_en_bytes (index*4 en la lista instrucciones_cola)
        Nota: si un label está asociado a una directiva (ej: "count: .word 0"), NO se mapeará como label de código.
        """
        self.codigo = [line.rstrip() for line in codigo]  # copia cruda
        self.instrucciones_cola = []
        self.labels = {}

        # Primera pasada: tokenizar líneas manteniendo si son label/directiva/instr
        temp = []  # lista de tuples (texto, tipo) donde tipo ∈ {"instr","label","directiva","label_data"}
        for line in codigo:
            # eliminar comentarios
            linea = line.split("#")[0].strip()
            if linea == "":
                continue

            # Directivas solas (ej: .data, .text)
            if linea.startswith("."):
                temp.append((linea, "directiva"))
                continue

            # Detectar label con posible resto
            if ":" in linea:
                parts = linea.split(":", 1)
                label = parts[0].strip()
                resto = parts[1].strip()
                # Si el resto está vacío -> etiqueta sola
                if resto == "":
                    temp.append((f"{label}:", "label"))
                    continue
                # Si el resto comienza con '.' -> label ligado a data (ej: count: .word 0)
                if resto.startswith("."):
                    temp.append((f"{label}:", "label_data"))
                    temp.append((resto, "directiva"))
                    continue
                # Si el resto es una instrucción válida en la misma línea
                temp.append((f"{label}:", "label"))
                temp.append((resto, "instr"))
                continue

            # Línea sin label ni directiva -> posible instrucción
            # Si comienza con '.', considerarla directiva (seguro)
            if linea.startswith("."):
                temp.append((linea, "directiva"))
            else:
                temp.append((linea, "instr"))

        # Segunda pasada: construir instrucciones reales y mapear labels de código
        instr_index = 0
        for entry, kind in temp:
            if kind == "instr":
                instr_text = entry.strip()
                if instr_text == "":
                    continue
                self.instrucciones_cola.append(instr_text)
                instr_index += 1
            elif kind == "label":
                label_name = entry.rstrip(":")
                # Mapear label al PC (en bytes) de la próxima instrucción válida
                self.labels[label_name] = instr_index * 4
            elif kind == "label_data":
                # label que referencia datos: NO lo mapear como label de código
                # (si quieres guardar etiquetas de datos, podríamos almacenarlas aparte)
                continue
            else:
                # directiva -> ignorar
                continue

        # Escribir en memoria de instrucciones (opcional)
        for i, instr in enumerate(self.instrucciones_cola):
            try:
                self.mem_inst.escribir(i, instr)
            except Exception:
                pass

        # Resetear índice y log
        self.indice_instruccion = 0
        self.log(f"{len(self.instrucciones_cola)} instrucciones cargadas (directivas filtradas)")
        for idx, ins in enumerate(self.instrucciones_cola):
            self.log(f"  [{idx:03d}] {ins}")

    # ---------------------------
    # UTIL PARSING DE REGISTROS
    # ---------------------------

    def parse_regs(self, instr):
        """
        Extrae rd, rs1, rs2, y si la instrucción es load (lw) o store (sw).
        Retorna: (rd, rs1, rs2, is_load, is_store)
        Valores None si no aplican.
        """
        try:
            s = instr.replace(",", " ").replace("(", " ").replace(")", " ")
            parts = s.split()
            op = parts[0]

            rd = rs1 = rs2 = None
            is_load = is_store = False

            if op in ["add", "sub", "and", "or", "slt", "mul", "div", "rem"]:
                rd = int(parts[1].replace("x", ""))
                rs1 = int(parts[2].replace("x", ""))
                rs2 = int(parts[3].replace("x", ""))
                return rd, rs1, rs2, False, False

            if op in ["addi", "andi", "ori", "slti", "li"]:
                rd = int(parts[1].replace("x", ""))
                rs1 = int(parts[2].replace("x", ""))
                return rd, rs1, None, False, False

            if op == "lw":
                # lw rd, offset(rs1) -> after replace: ["lw","rd","offset","rs1"]
                rd = int(parts[1].replace("x", ""))
                rs1 = int(parts[3].replace("x", ""))
                is_load = True
                return rd, rs1, None, True, False

            if op == "sw":
                # sw rs2, offset(rs1)
                rs2 = int(parts[1].replace("x", ""))
                rs1 = int(parts[3].replace("x", ""))
                is_store = True
                return None, rs1, rs2, False, True

            if op in ["beq", "bne", "blt", "bge"]:
                rs1 = int(parts[1].replace("x", ""))
                rs2 = int(parts[2].replace("x", ""))
                return None, rs1, rs2, False, False

            if op == "jal":
                # jal rd, label_or_imm
                rd = int(parts[1].replace("x", ""))
                return rd, None, None, False, False

            if op == "nop":
                return None, None, None, False, False

            # Por defecto, no detectable
            return None, None, None, False, False
        except Exception:
            return None, None, None, False, False

    # ---------------------------
    # HAZARD DETECTION E INSERCIÓN NOP
    # ---------------------------

    def hazard_detected(self):
        """
        Detecta RAW entre Decode(operando) vs Execute/RegFile results.
        También detecta load-use (cuando Execute es load y Decode necesita su rd).
        Devuelve True si hay hazard que requiere insertar un NOP.
        """
        instr_decode = self.etapa_decode.getInstruccion()
        if not instr_decode:
            return False

        # Obtener regs que necesita Decode (rs1, rs2)
        _, rs1_d, rs2_d, _, _ = self.parse_regs(instr_decode)

        # Revisar Execute (destino pendiente)
        instr_exe = self.etapa_execute.getInstruccion()
        if instr_exe:
            rd_exe, _, _, is_load_exe, _ = self.parse_regs(instr_exe)
            if rd_exe and rd_exe != 0:
                if rs1_d == rd_exe or rs2_d == rd_exe:
                    # Si EXE está ejecutando un LW -> load-use: se necesita NOP
                    if is_load_exe:
                        return True
                    # Si EXE no es load pero el valor todavía no está disponible (sin forwarding) -> stall
                    return True

        # Revisar RegisterFile (instrucción que está en etapa RegFile y escribirá pronto)
        instr_rf = self.etapa_registerFile.getInstruccion()
        if instr_rf:
            rd_rf, _, _, _, _ = self.parse_regs(instr_rf)
            if rd_rf and rd_rf != 0:
                if rs1_d == rd_rf or rs2_d == rd_rf:
                    return True

        return False

    # ---------------------------
    # ESTADO / TICK / EJECUCIÓN
    # ---------------------------

    def mostrar_estado_pipeline(self):
        estado = f"\n[CICLO {self.ciclo_actual:3d}] [PC_instr_index={self.indice_instruccion//4:3d}] Estado del Pipeline:\n"
        estado += f"  Fetch:        {self.etapa_fetch.get_estado()}\n"
        estado += f"  Decode:       {self.etapa_decode.get_estado()}\n"
        estado += f"  RegFile:      {self.etapa_registerFile.get_estado()}\n"
        estado += f"  Execute:      {self.etapa_execute.get_estado()}\n"
        estado += f"  Store:        {self.etapa_store.get_estado()}\n"
        return estado

    def tick(self):
        """
        Simula un ciclo de reloj discreto del pipeline.
        Orden:
          - detectar hazards antes de fetch: si hay hazard en Decode, insertar NOP
          - tick en todas las etapas
          - mover instrucciones entre etapas (si etapa actual completó y la siguiente está libre)
          - cargar siguiente instrucción en Fetch (si existe y Fetch está libre)
        """

        # 1) HAZARD DETECTION: si detectamos un hazard RAW, insertamos un NOP en Fetch (burbuja)
        if self.hazard_detected():
            self.log(f"[CICLO {self.ciclo_actual}] *** HAZARD DETECTADO → Insertando NOP (stall) ***")
            # Insertar NOP en Fetch si está libre; si está ocupada, forzamos su instruccionEjecutando a "nop"
            if self.etapa_fetch.esta_libre():
                self.etapa_fetch.cargarInstruccion("nop", [])
            else:
                # Forzamos una NOP en fetch (si la etapa está ocupada, la transformamos en NOP)
                self.etapa_fetch.instruccionEjecutando = "nop"
                self.etapa_fetch.ocupada = True

        # 2) Tick en todas las etapas (reduce ciclos_restantes)
        self.etapa_fetch.tick()
        self.etapa_decode.tick()
        self.etapa_registerFile.tick()
        self.etapa_execute.tick()
        self.etapa_store.tick()

        # 3) Movimiento entre etapas (Store -> Writeback effects; Execute -> Store; RegFile -> Execute; Decode -> RegFile; Fetch -> Decode)
        # STORE -> writeback / efectos
        if self.etapa_store.getInstruccion() != "":
            instr_store = self.etapa_store.get_instruccion_actual()
            self.log(f"[CICLO {self.ciclo_actual}] [COMPLETADA] {instr_store}")
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
                    elif accion == 'branch_result':
                        branch_taken, label_or_offset = params[1], params[2]
                        if branch_taken:
                            if label_or_offset in self.labels:
                                nuevo_pc = self.labels[label_or_offset]
                            else:
                                try:
                                    nuevo_pc = self.indice_instruccion + int(label_or_offset) * 4
                                except:
                                    nuevo_pc = self.indice_instruccion
                            self.log(f"[STORE] Branch TOMADO: PC = {self.indice_instruccion} -> {nuevo_pc}")
                            self.indice_instruccion = nuevo_pc
                            # flush pipeline (Fetch/Decode/RegFile/Execute)
                            self.etapa_fetch.instruccionEjecutando = ""
                            self.etapa_fetch.ocupada = False
                            self.etapa_decode.instruccionEjecutando = ""
                            self.etapa_decode.ocupada = False
                            self.etapa_registerFile.instruccionEjecutando = ""
                            self.etapa_registerFile.ocupada = False
                            self.etapa_execute.instruccionEjecutando = ""
                            self.etapa_execute.ocupada = False
                            self.log(f"[STORE] Pipeline flushed (Fetch/Decode/RegFile/Execute)")
                        else:
                            self.log(f"[STORE] Branch NO tomado")
                    elif accion == 'jump_result':
                        rd, label = params[1], params[2]
                        instr_actual = self.etapa_store.get_instruccion_actual()
                        pc_jal = -1
                        for i, instr in enumerate(self.instrucciones_cola):
                            if instr == instr_actual:
                                pc_jal = i * 4
                                break
                        if 0 < rd < len(self.regs) and pc_jal >= 0:
                            return_addr = pc_jal + 4
                            self.regs[rd] = return_addr
                            self.log(f"[STORE] JAL: x{rd} <- {return_addr} (return address)")
                        if label in self.labels:
                            nuevo_pc = self.labels[label]
                        else:
                            try:
                                nuevo_pc = pc_jal + int(label) * 4
                            except:
                                nuevo_pc = pc_jal + 4
                        self.log(f"[STORE] JAL: PC = {pc_jal} -> {nuevo_pc}")
                        self.indice_instruccion = nuevo_pc
                        # flush pipeline
                        self.etapa_fetch.instruccionEjecutando = ""
                        self.etapa_fetch.ocupada = False
                        self.etapa_decode.instruccionEjecutando = ""
                        self.etapa_decode.ocupada = False
                        self.etapa_registerFile.instruccionEjecutando = ""
                        self.etapa_registerFile.ocupada = False
                        self.etapa_execute.instruccionEjecutando = ""
                        self.etapa_execute.ocupada = False
                        self.log(f"[STORE] Pipeline flushed (Fetch/Decode/RegFile/Execute)")
            except Exception:
                pass

            # limpiar Store
            self.etapa_store.instruccionEjecutando = ""
            self.etapa_store.ocupada = False

        # EXECUTE -> STORE
        if self.etapa_execute.getInstruccion() != "" and self.etapa_store.esta_libre():
            instr = self.etapa_execute.getInstruccion()
            params = getattr(self.etapa_execute, 'params', []) or []
            self.etapa_store.cargarInstruccion(instr, params)
            self.etapa_execute.instruccionEjecutando = ""
            self.etapa_execute.ocupada = False

        # REGFILE -> EXECUTE
        if self.etapa_registerFile.getInstruccion() != "" and self.etapa_execute.esta_libre():
            instr = self.etapa_registerFile.getInstruccion()
            params = getattr(self.etapa_registerFile, 'params', []) or []
            self.etapa_execute.cargarInstruccion(instr, params)
            self.etapa_registerFile.instruccionEjecutando = ""
            self.etapa_registerFile.ocupada = False

        # DECODE -> REGFILE
        if self.etapa_decode.getInstruccion() != "" and self.etapa_registerFile.esta_libre():
            instr = self.etapa_decode.getInstruccion()
            self.etapa_registerFile.cargarInstruccion(instr)
            self.etapa_decode.instruccionEjecutando = ""
            self.etapa_decode.ocupada = False

        # FETCH -> DECODE
        if self.etapa_fetch.getInstruccion() != "" and self.etapa_decode.esta_libre():
            instr = self.etapa_fetch.getInstruccion()
            self.etapa_decode.cargarInstruccion(instr, [])
            self.etapa_fetch.instruccionEjecutando = ""
            self.etapa_fetch.ocupada = False

        # 4) CARGAR siguiente instrucción en Fetch si existe y Fetch está libre
        if self.indice_instruccion < len(self.instrucciones_cola) * 4 and self.etapa_fetch.esta_libre():
            instr = self.instrucciones_cola[self.indice_instruccion // 4]
            self.etapa_fetch.cargarInstruccion(instr, [])
            self.indice_instruccion += 4

        # fin de ciclo
        self.ciclo_actual += 1

    def ejecutar(self):
        """Ejecuta el programa completo en ciclos de reloj discretos."""
        self.log("\n=== INICIANDO SIMULACIÓN DEL PIPELINE (HAZARD CONTROL) ===\n")

        ciclos_max = 1000  # Prevención de bucle infinito

        while self.ciclo_actual < ciclos_max:
            # Mostrar estado antes del tick
            self.log(self.mostrar_estado_pipeline())

            # Ejecutar un ciclo
            self.tick()

            # Condición de salida: no hay más instrucciones y pipeline está vacío
            if (self.indice_instruccion >= len(self.instrucciones_cola) * 4 and
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
            self.guardar_memoria_en_archivo("memoria_salida_hazard_control.txt")
        except Exception:
            pass
        try:
            self.log_file.close()
        except Exception:
            pass

    def guardar_memoria_en_archivo(self, ruta):
        """Guarda el contenido de la memoria de datos en un archivo."""
        with open(ruta, "w", encoding="utf-8") as f:
            for i, valor in enumerate(self.mem_data.data):
                f.write(f"[{i:03d}] -> {valor}\n")
        self.log(f"Estado de memoria escrito en {ruta}")
