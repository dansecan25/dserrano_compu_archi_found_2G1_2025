


class Execute():
    def __init__(self):
        self.instruccionEjecutando=""
        self.params=[]
        pass
    def cargarInstruccion(self, instruccion, params):
        self.instruccionEjecutando=instruccion
        self.params=params
        print("Ejecutando instruccion en ALU: ",self.instruccionEjecutando)

    def getInstruccion(self):
        return self.instruccionEjecutando