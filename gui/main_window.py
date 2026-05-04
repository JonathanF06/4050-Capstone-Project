import tkinter as tk
from tkinter import ttk
from styles import setup_styles
from gui.bicycle_list import BicycleListForm
from gui.rental_form import RentalForm
from gui.rental_list import RentalList
class BicycleRentalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        setup_styles(self)

        self.title("Jonathan's Bicycle Store")
        self.geometry("600x350")

        ttk.Label(self, text="Jonathan's Bicycle Store").pack(pady=10)
        ttk.Button(self, text="List Bicycles", width=50, command = self.get_available_bikes).pack(pady=10)
        ttk.Button(self, text="Create Rental", width=50, command = self.create_rental_form).pack(pady=10)
        ttk.Button(self, text="View Rentals", width=50, command = self.view_rentals).pack(pady=10)
        ttk.Button(self, text="Exit", style="Exit.TButton", width=50, command=self.destroy).pack(pady=10)

    def get_available_bikes(self):
        self.withdraw()
        BicycleListForm(self)
    
    def create_rental_form(self):
        self.withdraw()
        RentalForm(self)
    
    def view_rentals(self):
        self.withdraw()
        RentalList(self)

