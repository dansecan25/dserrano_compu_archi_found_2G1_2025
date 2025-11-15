from componentes import *



# Inicializar componentes
alu = ALU()
regs = BancoRegistros()
mem = Memoria(16)
mux = MUX()
signext = SignExtender()
pipe = RegistroPipeline()

# Pruebas básicas
regs.escribir(1, 5)
regs.escribir(2, 10)
res = alu.operar("add", regs.leer(1), regs.leer(2))
print("Resultado ALU:", res)

mux_out = MUX.seleccionar(10, 99, 1)
print("MUX salida:", mux_out)

sign = SignExtender.extender(0b111111111111, 12)
print("Signo extendido:", sign)

pipe.escribir("PC", 4)
pipe.escribir("Instr", "add x1, x2, x3")
pipe.mostrar()
