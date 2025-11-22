from cpu import CPU

cpu = CPU()

cpu.cargar_programa_desde_archivo("programa.txt")
cpu.ejecutar_todo()


print("\nEjecución completada. Revisa 'log.txt' y 'memoria_salida.txt'.")
