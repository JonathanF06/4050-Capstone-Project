import tkinter as tk
from tkinter import ttk
from gui.bicycle_list import BicycleListForm
from gui.rental_form import RentalForm

class BicycleRentalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jonathan's Bicycle Store")
        self.geometry("1000x700")

        ttk.Label(self, text="Jonathan's Bicycle Store", font=("Arial", 16, "bold")).pack(pady=20)

        ttk.Button(self, text="List Available Bicycles",command=self.get_available_bikes).pack(pady=10)
        ttk.Button(self, text="Create Rental",command = self.create_rental_form).pack(pady=10)
        ttk.Button(self, text="Exit", command=self.destroy).pack(pady=20)

    def get_available_bikes(self):
        BicycleListForm(self)
    
    def create_rental_form(self):
        RentalForm(self)