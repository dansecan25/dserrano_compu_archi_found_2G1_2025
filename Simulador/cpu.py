from componentes import ALU, BancoRegistros, Memoria, SignExtender, MUX
from control import UnidadControl
import os
from pathlib import Path

class CPU:
    def __init__(self):
        # Componentes
        self.mem_inst = Memoria(64)
        self.mem_data = Memoria(256)
        self.regs = BancoRegistros()
        self.alu = ALU()
        self.uc = UnidadControl()
        self.sign_ext = SignExtender()
        self.PC = 0

        # Log
        self.log_file = open("log.txt", "w", encoding="utf-8")
        self.log_file.write("=== LOG DE EJECUCIÓN DEL CPU ===\n")

    def log(self, mensaje):
        print(mensaje)
        self.log_file.write(mensaje + "\n")

    def cargar_programa_desde_archivo(self, ruta):
        # Resolver la ruta relativa al directorio de este archivo para evitar
        # problemas si el script se ejecuta desde otro working directory.
        base_dir = Path(__file__).resolve().parent
        ruta_path = Path(ruta)
        if not ruta_path.is_absolute():
            ruta_path = base_dir / ruta_path

        instrucciones = []
        try:
            with open(ruta_path, "r", encoding="utf-8") as f:
                instrucciones = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.log(f"Archivo no encontrado: {ruta_path}")
        except Exception as e:
            self.log(f"Error leyendo {ruta_path}: {e}")

        for i, instr in enumerate(instrucciones):
            self.mem_inst.escribir(i, instr)
        self.log(f"{len(instrucciones)} instrucciones cargadas desde {ruta_path}")

    def guardar_memoria_en_archivo(self, ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            for i, valor in enumerate(self.mem_data.data):
                f.write(f"[{i:03d}] -> {valor}\n")
        self.log(f"Estado de memoria escrito en {ruta}")

    def ejecutar_ciclo(self):
        instr = self.mem_inst.leer(self.PC)
        if not instr:
            self.log("Fin del programa")
            return False

        self.log(f"\n=== Ciclo {self.PC} ===")
        self.log(f"Instrucción: {instr}")

        partes = instr.replace(",", "").split()
        opcode = partes[0]
        señales = self.uc.decodificar(opcode)
        self.log(f"Señales: {señales}")

        if opcode in ["add", "sub"]:
            rd, rs1, rs2 = [int(p[1:]) for p in partes[1:4]]
            a, b = self.regs.leer(rs1), self.regs.leer(rs2)
            res = self.alu.operar(señales["ALUOp"], a, b)
            if señales["RegWrite"]:
                self.regs.escribir(rd, res)
            self.log(f"ALU: {a} {opcode} {b} = {res} → x{rd}")

        elif opcode == "addi":
            rd, rs1, imm = int(partes[1][1:]), int(partes[2][1:]), int(partes[3])
            a = self.regs.leer(rs1)
            b = self.sign_ext.extender(imm)
            res = self.alu.operar("add", a, b)
            if señales["RegWrite"]:
                self.regs.escribir(rd, res)
            self.log(f"ADDInmediato: x{rd} = {a} + {b} = {res}")

        elif opcode == "sw":
            rs2, offset_reg = partes[1], partes[2]
            rs2 = int(rs2[1:])
            offset, rs1 = offset_reg.split("(")
            offset = int(offset)
            rs1 = int(rs1[1:-1])
            addr = self.regs.leer(rs1) + offset
            val = self.regs.leer(rs2)
            self.mem_data.escribir(addr, val)
            self.log(f"Store: Mem[{addr}] = x{rs2} valor guardado->({val})")

        elif opcode == "lw":
            rd, offset_reg = partes[1], partes[2]
            rd = int(rd[1:])
            offset, rs1 = offset_reg.split("(")
            offset = int(offset)
            rs1 = int(rs1[1:-1])
            addr = self.regs.leer(rs1) + offset
            val = self.mem_data.leer(addr)
            self.regs.escribir(rd, val)
            self.log(f"Load: x{rd} = Mem[{addr}] = {val}")

        self.PC += 1
        self.log(f"PC → {self.PC}")
        return True

    def ejecutar_todo(self):
        while self.ejecutar_ciclo():
            pass
        self.log("\n--- EJECUCIÓN FINALIZADA ---")
        self.guardar_memoria_en_archivo("memoria_salida.txt")
        self.log_file.close()
