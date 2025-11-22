class UnidadControl:
    def __init__(self):
        self.control = {
            "RegWrite": 0,
            "ALUSrc": 0,
            "MemRead": 0,
            "MemWrite": 0,
            "MemToReg": 0,
            "Branch": 0,
            "ALUOp": "add"
        }

    def decodificar(self, opcode):
        for key in self.control:
            self.control[key] = 0
        self.control["ALUOp"] = "add"

        if opcode in ["add", "sub", "and", "or", "xor", "slt"]:
            self.control.update({
                "RegWrite": 1,
                "ALUSrc": 0,
                "MemToReg": 0,
                "ALUOp": opcode
            })
        elif opcode == "addi":
            self.control.update({
                "RegWrite": 1,
                "ALUSrc": 1,
                "ALUOp": "add"
            })
        elif opcode == "lw":
            self.control.update({
                "RegWrite": 1,
                "ALUSrc": 1,
                "MemRead": 1,
                "MemToReg": 1
            })
        elif opcode == "sw":
            self.control.update({
                "ALUSrc": 1,
                "MemWrite": 1
            })
        elif opcode == "beq":
            self.control.update({
                "Branch": 1,
                "ALUSrc": 0,
                "ALUOp": "sub"
            })
        else:
            print(f"[UnidadControl] Opcode desconocido: {opcode}")
        return self.control
