import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Front.processor_window import ProcessorWindow
from Simulador.cpuPipelineSinHazards import CPUpipelineNoHazard
from Simulador.cpuPipelineHazardControl import CPUPipelineHazardControl
from Simulador.cpuPipelineConPredicciondeSaltos import CPUpipelineConPrediccionSaltos
from Simulador.cpuPipelinePrediccionSaltosHazardControl import CPUPipelinePrediccionSaltosHazardControl

from processor_view import ProcessorView

back = "#1A1A1A"


def button_hover(button, on_hover, on_leave):
    button.bind("<Enter>", func=lambda e: button.config(background=on_hover))

    button.bind("<Leave>", func=lambda e: button.config(background=on_leave))


class MainMenu:

    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Ripes")
        self.master.resizable(False, False)
        self.master.config(bg=back)
        self.lftPos = (self.master.winfo_screenwidth() - 1500) / 2
        self.topPos = (self.master.winfo_screenheight() - 900) / 2
        self.master.geometry("%dx%d+%d+%d" % (1500, 900, self.lftPos, self.topPos))

        self.var = tk.StringVar()
        self.list = []
        self.filtered_list = []
        self.first = True

        # Botones de la GUI

        self.editor_button = tk.Button(self.master, text="Editor", font=("Terminal", 20), width=10, height=2,
                                       pady=25, command=lambda: self.editor_window(), state=tk.DISABLED,
                                       bg="#3A3A3A", activebackground=back)
        self.process_button = tk.Button(self.master, text="Processor", font=("Terminal", 20), width=10, height=2,
                                        pady=25, command=lambda: self.processor_window(), activebackground=back)
        self.memory_button = tk.Button(self.master, text="Memory", font=("Terminal", 20), width=10, height=2, pady=25,
                                       command=lambda: self.memory_window(), activebackground=back)

        self.editor_button.grid(column=0, row=0)
        self.process_button.grid(column=0, row=1)
        self.memory_button.grid(column=0, row=2)

        button_hover(self.process_button, "#3A3A3A", "SystemButtonFace")
        button_hover(self.memory_button, "#3A3A3A", "SystemButtonFace")

        self.change_button = ttk.Combobox(self.master, font=("Terminal", 20), state="readonly", width=14, height=4)

        self.change_button["values"] = ('CPU_NH/CPU_HC', 'CPU_PS/CPU_SHC')
        self.change_button.current(0)
        #self.change_button.bind('<<ComboboxSelected>>', self.selected)
        self.compile_button = tk.Button(self.master, text="Compile", font=("Terminal", 20),
                                        command=lambda: self.get_txt())

        self.change_button.grid(column=2, row=0)
        self.compile_button.grid(column=3, row=0)


        # Editor
        self.editor_tab = tk.Frame(self.master, bg=back, width=645, height=525)
        self.editor_tab.grid_propagate(False)
        self.editor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)

        self.code_entry = tk.Text(self.editor_tab, height=30, width=80)

        self.code_entry.grid(column=1, row=3, columnspan=5)
        self.editor_button.grid(column=0, row=0)

        # Processor
        self.processor_tab = tk.Frame(self.master, bg="#1A1A1A", width=1280, height=900)
        self.processor_tab.grid_propagate(False)

        # Path to log file
        self.log_path = os.path.join(os.path.dirname(__file__), "..", "log.txt")

        # Create processor view widget
        self.processor_view = ProcessorView(self.processor_tab, self.log_path)
        self.processor_view.pack(fill='both', expand=True)

        # Memory
        self.memory_tab = tk.Frame(self.master, bg=back, width=645, height=525)
        self.memory_tab.grid_propagate(False)
        self.memory_text = tk.Text(self.memory_tab, height=31, width=40)

        self.memory_text.grid(column=1, row=3, columnspan=3)


    def get_txt(self):
        self.list.clear()
        self.filtered_list.clear()
        txt = self.code_entry.get(1.0, "end").rstrip("\n")

        self.list = txt.split("\n")
        for i in range(len(self.list)):
            linea = self.list[i].split("#")[0].strip()
            self.filtered_list.append(linea)

        self.filtered_list = [item for item in self.filtered_list if item.strip()]

        if len(self.filtered_list) != 0:
            new_cpu_pipeline = CPUpipelineNoHazard()
            new_cpu_pipeline.cargarCodigo(self.filtered_list)   
            new_cpu_pipeline.ejecutar()

            # After execution, reload the log in processor view
            if self.processor_view:
                success = self.processor_view.load_log()
                if success:
                    messagebox.showinfo("Success", "Simulation completed! Switch to Processor tab to view pipeline execution.")
                else:
                    messagebox.showerror("Error", "Failed to load simulation log.")


    def editor_window(self):
        self.processor_tab.grid_forget()
        self.memory_tab.grid_forget()
        self.editor_button.unbind("<Enter>")
        self.editor_button.unbind("<Leave>")
        self.editor_button.config(state=tk.DISABLED)
        button_hover(self.process_button, "#3A3A3A", "SystemButtonFace")
        button_hover(self.memory_button, "#3A3A3A", "SystemButtonFace")
        self.process_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.memory_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.editor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)
        self.editor_tab.grid_propagate(False)

    def processor_window(self):
        self.editor_tab.grid_forget()
        self.memory_tab.grid_forget()
        self.process_button.unbind("<Enter>")
        self.process_button.unbind("<Leave>")
        self.process_button.config(state=tk.DISABLED)
        button_hover(self.editor_button, "#3A3A3A", "SystemButtonFace")
        button_hover(self.memory_button, "#3A3A3A", "SystemButtonFace")
        self.editor_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.memory_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.master.focus_set()
        self.processor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)
        self.processor_tab.grid_propagate(False)

        # Try to load log if it exists
        if self.processor_view and os.path.exists(self.log_path):
            self.processor_view.load_log()

        ProcessorWindow(self.master,back,"Processor 1")
        ProcessorWindow(self.master, back, "Processor 2")

    def memory_window(self):
        self.editor_tab.grid_forget()
        self.processor_tab.grid_forget()
        self.memory_button.unbind("<Enter>")
        self.memory_button.unbind("<Leave>")
        self.memory_button.config(state=tk.DISABLED)
        button_hover(self.editor_button, "#3A3A3A", "SystemButtonFace")
        button_hover(self.process_button, "#3A3A3A", "SystemButtonFace")
        self.editor_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.process_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.master.focus_set()
        self.memory_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)
        self.memory_tab.grid_propagate(False)

        # Get Memory File

        if not self.first:
            file_paths = ["memoria_salida.txt", "memoria_salida_hazard_control.txt", "memoria_salida_prediccion.txt",
                          "memoria_salida_prediccion_hazard_control.txt"]
            self.memory_text.config(state=tk.NORMAL)
            with open(file_paths[self.change_button.current()], "r") as file:
                content = file.read()
                self.memory_text.delete(1.0, tk.END)
                self.memory_text.insert(tk.END, content)
            self.memory_text.config(state=tk.DISABLED)



    def start(self):
        self.master.mainloop()


