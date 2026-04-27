import tkinter as tk
from tkinter import ttk
from database import list_all_bikes
from styles import setup_styles


class BicycleListForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        setup_styles(self)

        self.parent=parent
        self.title("Available Bicycles")
        self.geometry("800x400")

        ttk.Label(self, text="Available Bicycles", font=("Arial", 14, "bold")).pack(pady=10)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id","registration_number", "bicycle_class", "make", "model","status")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="Bike ID")
        self.tree.heading("registration_number", text="Reg #")
        self.tree.heading("bicycle_class", text="Class")
        self.tree.heading("make", text="Make")
        self.tree.heading("model", text="Model")
        self.tree.heading("status", text="Status")

        self.tree.column("status", width=140, anchor="center")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("registration_number", width=140, anchor="center")
        self.tree.column("bicycle_class", width=120, anchor="center")
        self.tree.column("make", width=140, anchor="center")
        self.tree.column("model", width=140, anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

        self.load_bicycles()

        ttk.Button(self, text="Back", command=self.open_main_window).pack(pady=10)
    
    def open_main_window(self):
        self.destroy()
        self.parent.deiconify()
        

    def load_bicycles(self):
        rows = list_all_bikes()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for bike in rows:
            self.tree.insert("", "end", values=bike)