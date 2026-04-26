import tkinter as tk
from tkinter import ttk
from database import list_available_bikes
from tkinter import messagebox
from database import get_rate
from database import add_rental
from database import add_rental_item
from gui.reciept import ReceiptForm
from tkcalendar import DateEntry

class RentalForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.title("Create Rental")
        self.geometry("650x500")
        

        ttk.Label(self, text="Customer Name").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Phone").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=1, column=1, padx=10, pady=5)

        def format_phone(event):
            text = self.phone_entry.get()
            digits = "".join(filter(str.isdigit, text))
            
            digits = digits[:10]

            formatted = ""

            if len(digits) >= 1:
                formatted = "(" + digits[:3]
            if len(digits) >= 4:
                formatted += ") " + digits[3:6]
            if len(digits) >= 7:
                formatted += "-" + digits[6:10]

            # avoid cursor jumping issue
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, formatted)

        self.phone_entry.bind("<KeyRelease>", format_phone)

        ttk.Label(self, text="Rental Date").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = DateEntry(
            self,
            width=18,
            date_pattern="mm/dd/yyyy"
        )
        self.date_entry.grid(row=2, column=1, padx=10, pady=5)


        time_values=["8:00AM","8:30AM","9:00AM","9:30AM","10:00AM","10:30AM","11:00AM","11:30AM","12:00PM","12:30PM","1:00PM","1:30PM",
                "2:00PM","2:30PM","3:00PM","3:30PM","4:00PM","4:30PM","5:00PM"]

        ttk.Label(self, text="Time Out").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.time_out_entry = ttk.Combobox(self, values=time_values, state="readonly")
        self.time_out_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Expected Time Back").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.expected_back_entry = ttk.Combobox(self, values=time_values, state="readonly")
        self.expected_back_entry.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self, text="Rental Period").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.period_combo = ttk.Combobox(self, values=["Day", "Half-Day", "Late Rental"], state="readonly")
        self.period_combo.grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self, text="Deposit Type").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.deposit_combo = ttk.Combobox(self, values=["Cash", "Credit Card"], state="readonly")
        self.deposit_combo.grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(self, text="Available Bicycles (max 4)").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.bicycle_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=50, height=10)
        self.bicycle_listbox.grid(row=7, column=1, padx=10, pady=5)

        self.available_bicycles = list_available_bikes()
        for bike in self.available_bicycles:
            self.bicycle_listbox.insert(tk.END, f"{bike[1]} | {bike[2]} | {bike[3]} | {bike[4]} [{bike[5]}]")
        ttk.Button(self, text="Create Rental", command=self.create_rental).grid(row=8, column=0, columnspan=2, pady=20)
    #
    def create_rental(self):
        name=self.name_entry.get()
        phone=self.phone_entry.get()
        date=self.date_entry.get()
        out=self.time_out_entry.get()
        time_back=self.expected_back_entry.get()
        period=self.period_combo.get()
        deposit=self.deposit_combo.get()
        selected_indices = self.bicycle_listbox.curselection()
        values = [name,phone,date,out,time_back,period,deposit] 
        names = ["Customer Name", "Phone", "Rental Date", "Time Out", "Expected Time Back" ,"Rental Period", "Desposit Type"]
        empty = [names[i] for i, v in enumerate(values) if not v.strip()]
        if empty:
            messagebox.showerror(
            "Missing Fields",
            "Please fill in:\n\n• " + "\n• ".join(empty)
            )
        elif not selected_indices:
            messagebox.showerror(
                "Missing Fields",
                "Please select at least one rental bike.")
        elif len(selected_indices) > 4:
             messagebox.showerror(
                "Missing Fields",
                "Please make sure only 4 were selected.")
             
        else: 
            selected_bicycles = [self.available_bicycles[i] for i in selected_indices]
            total=self.calculate_price(selected_bicycles,period) 
            total_deposit=len(selected_indices) * 20
            rental_data=(name,phone,date,out,time_back,period,deposit,0,total_deposit)
            rental_id=add_rental(rental_data)
            self.destroy()
            self.parent.deiconify()
            
            ReceiptForm(rental_data,rental_id,selected_bicycles)
    def calculate_price(self,bicycles,period):
        total=0
        
        for bike in bicycles:
            bikeclass=bike[2] 
            rate = get_rate(bikeclass,period)
            total= rate + total
    
        
        return total

