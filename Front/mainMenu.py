import tkinter as tk
from tkinter import messagebox
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Simulador.cpuPipelineSinHazards import CPUpipelineNoHazard
from dual_processor_view import DualProcessorView

back = "#1A1A1A"


def button_hover(button, on_hover, on_leave):
    button.bind("<Enter>", func=lambda e: button.config(background=on_hover))

    button.bind("<Leave>", func=lambda e: button.config(background=on_leave))


class MainMenu:

    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Ripes - RISC-V Pipeline Simulator")
        self.master.config(bg=back)

        # Hacer ventana resizable
        self.master.resizable(True, True)

        # Usar 95% del tamaño de la pantalla para mejor visualización
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.90)

        self.lftPos = (screen_width - window_width) / 2
        self.topPos = (screen_height - window_height) / 2
        self.master.geometry("%dx%d+%d+%d" % (window_width, window_height, self.lftPos, self.topPos))

        # Establecer tamaño mínimo
        self.master.minsize(1600, 900)

        self.var = tk.StringVar()
        self.list = []
        self.filtered_list = []

        # Botones de la GUI

        self.edit_button = tk.Button(self.master, text="Editor", font=("Terminal", 20), width=10, height=2,
                                     pady=25,command=lambda: self.editor_window(), state=tk.DISABLED,
                                     bg="#3A3A3A", activebackground=back)
        self.process_button = tk.Button(self.master, text="Processor", font=("Terminal", 20), width=10, height=2,
                                        pady=25, command=lambda: self.processor_window(), activebackground=back)
        self.cache_button = tk.Button(self.master, text="Cache", font=("Terminal", 20), width=10, height=2,
                                      pady=25, command=lambda: self.cache_window(), activebackground=back)

        self.edit_button.grid(column=0, row=0)
        self.process_button.grid(column=0, row=1)
        self.cache_button.grid(column=0, row=2)

        button_hover(self.process_button, "#3A3A3A", "SystemButtonFace")
        button_hover(self.cache_button, "#3A3A3A", "SystemButtonFace")

        # Editor
        self.editor_tab = tk.Frame(self.master, bg=back, width=645, height=525)
        self.editor_tab.grid_propagate(False)
        self.editor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)

        self.code_entry = tk.Text(self.editor_tab, height=30, width=80)
        self.reset_button = tk.Button(self.editor_tab, text="Reset", font=("Terminal", 20))
        self.step_back_button = tk.Button(self.editor_tab, text="<", font=("Terminal", 20))
        self.step_button = tk.Button(self.editor_tab, text=">", font=("Terminal", 20))
        self.run_button = tk.Button(self.editor_tab, text="Run", font=("Terminal", 20),
                                     command=lambda: self.get_txt())
        self.fast_button = tk.Button(self.editor_tab, text=">>", font=("Terminal", 20))


        self.reset_button.grid(column=1, row=0)
        self.step_back_button.grid(column=2, row=0)
        self.step_button.grid(column=3, row=0)
        self.run_button.grid(column=4, row=0)
        self.fast_button.grid(column=5, row=0)
        self.code_entry.grid(column=1, row=3, columnspan=5)
        self.edit_button.grid(column=0, row=0)

        # Processor
        self.processor_tab = tk.Frame(self.master, bg="#1A1A1A")
        # No restringir tamaño, dejar que se expanda con la ventana

        # Paths to both log files
        self.log_path_no_hazard = os.path.join(os.path.dirname(__file__), "..", "log.txt")
        self.log_path_with_hazard = os.path.join(os.path.dirname(__file__), "..", "log_hazard_control.txt")

        # Create dual processor view widget (shows both processors)
        self.processor_view = DualProcessorView(
            self.processor_tab,
            self.log_path_no_hazard,
            self.log_path_with_hazard
        )
        self.processor_view.pack(fill='both', expand=True)

        # Cache
        self.cache_tab = tk.Frame(self.master, bg="#1A1A1A")

        # Cache placeholder content
        cache_label = tk.Label(self.cache_tab, text="Cache Visualization",
                              bg="#1A1A1A", fg="white", font=("Arial", 24, "bold"))
        cache_label.pack(pady=50)

        cache_info = tk.Label(self.cache_tab, text="Cache visualization coming soon...\n\nThis tab will display:\n• Cache memory structure\n• Cache hits and misses\n• Cache replacement policies\n• Memory access patterns",
                             bg="#1A1A1A", fg="#AAAAAA", font=("Arial", 14), justify="center")
        cache_info.pack(pady=20)

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

            # After execution, reload both logs in dual processor view
            if self.processor_view:
                success = self.processor_view.load_logs()
                if success:
                    messagebox.showinfo("Success", "Simulation completed! Switch to Processor tab to view both pipeline executions.")
                else:
                    messagebox.showerror("Error", "Failed to load simulation logs.")


    def editor_window(self):
        self.processor_tab.grid_forget()
        self.edit_button.unbind("<Enter>")
        self.edit_button.unbind("<Leave>")
        self.edit_button.config(state=tk.DISABLED)
        button_hover(self.process_button, "#3A3A3A", "SystemButtonFace")
        self.process_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.editor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)
        self.editor_tab.grid_propagate(False)

    def processor_window(self):
        self.editor_tab.grid_forget()
        self.process_button.unbind("<Enter>")
        self.process_button.unbind("<Leave>")
        self.process_button.config(state=tk.DISABLED)
        button_hover(self.edit_button, "#3A3A3A", "SystemButtonFace")
        self.edit_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.master.focus_set()
        self.processor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)

        # Configurar expansión de la grid
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Try to load logs if they exist
        if self.processor_view:
            if os.path.exists(self.log_path_no_hazard) or os.path.exists(self.log_path_with_hazard):
                self.processor_view.load_logs()

    def cache_window(self):
        """Switch to cache tab"""
        self.editor_tab.grid_forget()
        self.processor_tab.grid_forget()

        # Disable cache button and enable others
        self.cache_button.unbind("<Enter>")
        self.cache_button.unbind("<Leave>")
        self.cache_button.config(state=tk.DISABLED)

        button_hover(self.edit_button, "#3A3A3A", "SystemButtonFace")
        button_hover(self.process_button, "#3A3A3A", "SystemButtonFace")
        self.edit_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        self.process_button.config(state=tk.NORMAL, bg="SystemButtonFace")

        self.master.focus_set()
        self.cache_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)

        # Configurar expansión de la grid
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def start(self):
        self.master.mainloop()


