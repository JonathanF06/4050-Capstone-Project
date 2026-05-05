import tkinter as tk
from tkinter import ttk
from database import list_all_rentals
from styles import setup_styles
from gui.reciept import ReceiptForm
from database import get_rentaldata
from database import get_bikes_from_rental
from gui.returned_form import ReturnForm 
from database import get_rental_status
from gui.final_receipt import FinalReceipt

class RentalList(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        setup_styles(self)
        self.parent=parent
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.title("High Peak | View Rentals")
        self.geometry("800x400")

        ttk.Label(self, text="List of Rentals").pack(pady=10)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("rental_id","customer_name","telephone","date_created","rental_status")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("rental_id", text="Rental ID")
        self.tree.heading("customer_name", text="Customer Name")
        self.tree.heading("telephone", text="Phone Number")
        self.tree.heading("date_created", text="Date Rented")
        self.tree.heading("rental_status", text="Status")

        self.tree.column("rental_id", width=100, anchor="center")
        self.tree.column("customer_name", width=100, anchor="center")
        self.tree.column("telephone", width=140, anchor="center")
        self.tree.column("date_created", width=120, anchor="center")
        self.tree.column("rental_status", width=140, anchor="center")
        
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

    
        self.load_rentals()
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="View", width=20, command=self.get_copy).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Return", width=20, command=self.open_return_form).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Back", width=20, command=self.open_main_window, style="Exit.TButton").pack(side="left", padx=10)
        

    def open_main_window(self):
        self.destroy()
        self.parent.deiconify()

    def open_return_form(self):
        selected=self.tree.selection()
        if selected:
            row = self.tree.item(selected[0])
            values= row["values"]
            rental_id=values[0]
            if get_rental_status(rental_id) == "Closed":
                return   
            ReturnForm(self,self.parent,rental_id)        
            self.withdraw()
        

    def load_rentals(self):
        rows = list_all_rentals()

        for row in self.tree.get_children():
            self.tree.delete(row)
        for bike in rows:
            self.tree.insert("", "end", values=bike)
    
    def get_copy(self):
        selected=self.tree.selection()
        if selected:   
            row = self.tree.item(selected[0])
            values= row["values"]
            if values[4] == "Closed":
                FinalReceipt(values[0])
            else:
                ReceiptForm(get_rentaldata(values[0]),values[0],get_bikes_from_rental(values[0]),True)
            
    def on_close(self):
        self.destroy()
        self.parent.deiconify()


