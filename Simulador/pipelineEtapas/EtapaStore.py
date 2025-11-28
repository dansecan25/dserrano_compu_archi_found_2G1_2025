


class EtapaStore():
    def __init__(self):
        self.instruccionEjecutando=""
        self.params=[]
        pass
    def cargarInstruccion(self, instruccion, params):
        self.instruccionEjecutando=instruccion
        self.params=params
        print("Almacenando instruccion: ",self.instruccionEjecutando)
    def getInstruccion(self):
        return self.instruccionEjecutando