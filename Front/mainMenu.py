import tkinter as tk
from tkinter.font import Font

back = "#1D1A1A"


class MainMenu:

    def __init__(self, first):
        self.master = tk.Tk()
        self.master.title("Ripes")
        self.master.resizable(False, False)
        self.master.config(bg=back)
        self.lftPos = (self.master.winfo_screenwidth() - 1000) / 2
        self.topPos = (self.master.winfo_screenheight() - 700) / 2
        self.master.geometry("%dx%d+%d+%d" % (1000, 700, self.lftPos, self.topPos))

        self.manual_font = Font(family="Terminal", size=20)

        self.var = tk.StringVar()
        self.list = []

        
        self.code_entry = tk.Text(self.master, height=30, width=self.master.winfo_screenwidth() - 1000)
        self.code_entry.pack()
        self.nextButton = tk.Button(self.master, text="Save", font=("Terminal", 20),
                                 command=lambda: self.get_txt())
        self.nextButton.pack()

    def get_txt(self):
        self.list.clear()
        txt = self.code_entry.get(1.0, "end").rstrip("\n")

        self.list = txt.split("\n")

        print(self.list)


    def start(self):
        self.master.mainloop()
