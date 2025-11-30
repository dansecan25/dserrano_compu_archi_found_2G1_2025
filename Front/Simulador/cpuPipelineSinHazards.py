from Simulador.pipelineEtapas import EtapaStore,Fetch, RegisterFile, Execute, Decode
from Simulador.componentes import Memoria
from Simulador.control import UnidadControl
import os
from pathlib import Path

class CPUpipelineNoHazard:
    def __init__(self):
        # Componentes
        self.mem_inst = Memoria(64)
        self.mem_data = Memoria(256)
        self.etapa_fetch=Fetch();
        self.etapa_decode=Decode();
        self.etapa_registerFile=RegisterFile();
        self.etapa_execute=Execute();
        self.etapa_store=EtapaStore();
        self.PC = 0
        self.labels = {}
        self.data_pointer = 0  # apunta dentro de memoria de datos
        self.codigo:list[str]=[]

        # Log
        self.log_file = open("log.txt", "w", encoding="utf-8")
        self.log_file.write("=== LOG DE EJECUCIÓN DEL CPU ===\n")

    def cargarCodigo(self, codigo):
        self.codigo=codigo


    def ejecutar(self, code):
        #loop, leer linea por linea
        for linea in code:
            cargaFetch,cargaDecode,cargaRF,cargaExecute,cargaStore = False,False,False,False,False


            # Split robusto: divide por cualquier cantidad de espacios/tabs
            partes = linea.replace("\t", " ").split(" ")

            # Filtrar vacíos
            lineaCodigo = [p for p in partes if p != ""]

            # Si está vacía → saltar
            if not lineaCodigo:
                continue

            print("Linea de codigo es:", lineaCodigo)
            #mueve la instruccion en cada iteracion por las 5 etapas
            self.etapa_store.cargarInstruccion(self.etapa_execute.getInstruccion(),[])
            self.etapa_execute.cargarInstruccion(self.etapa_registerFile.getInstruccion(),[])
            self.etapa_registerFile.cargarInstruccion(self.etapa_decode.getInstruccion(),[])
            self.etapa_decode.cargarInstruccion(self.etapa_fetch.getInstruccion(),[])
            self.etapa_fetch.cargarInstruccion(lineaCodigo[0],[])
            print("------------------------------------------------------------------------")
            
            
            #siguiente ciclo, si hay instrucción en fetch, decode, register file, execute o store, moverla a la siguiente etapa

            #cargar en fetch la siguiente instruccion
        #si sale del for, pero aun hay instrucciones en los registros, termine
        while self.etapa_fetch.getInstruccion()!="" or self.etapa_decode.getInstruccion()!="" or self.etapa_registerFile.getInstruccion()!="" or self.etapa_decode.getInstruccion()!="" or self.etapa_store.getInstruccion()!="":
            self.etapa_store.cargarInstruccion(self.etapa_execute.getInstruccion(),[])
            self.etapa_execute.cargarInstruccion(self.etapa_registerFile.getInstruccion(),[])
            self.etapa_registerFile.cargarInstruccion(self.etapa_decode.getInstruccion(),[])
            self.etapa_decode.cargarInstruccion(self.etapa_fetch.getInstruccion(),[])
            self.etapa_fetch.cargarInstruccion("",[])