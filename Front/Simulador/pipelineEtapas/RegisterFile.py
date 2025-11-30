


class RegisterFile():
    def __init__(self):
        self.instruccionEjecutando=""
        self.params=[]
        pass
    def cargarInstruccion(self, instruccion, params):
        self.instruccionEjecutando=instruccion
        self.params=params
        print("Register file, no se que hace: ",self.instruccionEjecutando)
    def getInstruccion(self):
        return self.instruccionEjecutando