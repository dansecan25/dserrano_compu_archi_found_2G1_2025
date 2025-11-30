


class Fetch():
    def __init__(self):
        self.instruccionEjecutando=""
        self.params=[]
        pass
    def cargarInstruccion(self, instruccion, params):
        self.instruccionEjecutando=instruccion
        self.params=params
        print("Instruccion en fetch: ",self.instruccionEjecutando)
    def getInstruccion(self):
        return self.instruccionEjecutando