import tkinter as tk
import os
from Front.processor_view import ProcessorView


class ProcessorWindow:


    def __init__(self, root, back, title):
        self.root = root
        self.back = back
        self.process_win = tk.Toplevel(self.root)
        self.process_win.title(title)
        self.process_win.resizable(False, False)
        self.process_win.config(bg=back)
        self.lftPos = (self.process_win.winfo_screenwidth() - 1000) / 2
        self.topPos = (self.process_win.winfo_screenheight() - 700) / 2
        self.process_win.geometry("%dx%d+%d+%d" % (1000, 700, self.lftPos, self.topPos))

        self.processor_tab = tk.Frame(self.root, bg="#1A1A1A", width=1280, height=900)
        self.processor_tab.grid_propagate(False)

        # Path to log file
        self.log_path = os.path.join(os.path.dirname(__file__), "..", "log.txt")

        # Create processor view widget
        self.processor_view = ProcessorView(self.root, self.log_path)
        self.processor_view.grid(column=1, row=0, sticky="nsew", rowspan=30)

        self.processor_tab.grid(column=1, row=0, sticky="nsew", rowspan=30)
