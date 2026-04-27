import tkinter as tk
from tkinter import ttk
from database import list_all_rentals
from styles import setup_styles


class BicycleListForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        setup_styles(self)

        self.parent=parent
        self.title("Open Rentals")
        self.geometry("800x400")

        ttk.Label(self, text="Open Rentals").pack(pady=10)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ()

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.load_bicycles()

        ttk.Button(self, text="Back", command=self.open_main_window).pack(pady=10)