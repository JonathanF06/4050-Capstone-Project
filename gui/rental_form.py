import tkinter as tk
from tkinter import ttk
from database import list_available_bikes
from tkinter import messagebox
from database import get_rate
from database import add_rental
from database import add_rental_item
from gui.reciept import ReceiptForm
from tkcalendar import DateEntry
from styles import setup_styles

class RentalForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        setup_styles(self)

        self.parent=parent
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("Create Rental")
        self.geometry("620x550")

        ttk.Label(self, text="Customer Name", style="Form.TLabel").grid(row=0, column=0, padx=50, sticky="w")
        self.name_entry = ttk.Entry(self, font=("Arial", 12))
        self.name_entry.grid(row=1, column=0, padx=50, pady=(0, 10), sticky="w")

        ttk.Label(self, text="Phone", style="Form.TLabel").grid(row=0, column=1, padx=50, sticky="w")
        self.phone_entry = ttk.Entry(self, font=("Arial", 12))
        self.phone_entry.grid(row=1, column=1, padx=50, pady=(0, 10), sticky="w")

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

        ttk.Label(self, text="Rental Date", style="Form.TLabel").grid(row=2, column=0, padx=50, sticky="w")
        self.date_entry = DateEntry(
            self,
            width=18,
            font=("Arial", 12),
            date_pattern="mm/dd/yyyy"
        )
        self.date_entry.grid(row=3, column=0, padx=50, pady=(0, 10), sticky="w")


        time_values=["8:00AM","8:30AM","9:00AM","9:30AM","10:00AM","10:30AM","11:00AM","11:30AM","12:00PM","12:30PM","1:00PM","1:30PM",
                "2:00PM","2:30PM","3:00PM","3:30PM","4:00PM","4:30PM","5:00PM"]

        ttk.Label(self, text="Time Out", style="Form.TLabel").grid(row=2, column=1, padx=50, sticky="w")
        self.time_out_entry = ttk.Combobox(self, values=time_values, state="readonly", font=("Arial", 12))
        self.time_out_entry.grid(row=3, column=1, padx=50, pady=(0, 10), sticky="w")

        ttk.Label(self, text="Expected Time Back", style="Form.TLabel").grid(row=4, column=0, padx=50, sticky="w")
        self.expected_back_entry = ttk.Combobox(self, values=time_values, state="readonly", font=("Arial", 12))
        self.expected_back_entry.grid(row=5, column=0, padx=50, pady=(0, 10), sticky="w")

        ttk.Label(self, text="Rental Period", style="Form.TLabel").grid(row=4, column=1, padx=50, sticky="w")
        self.period_combo = ttk.Combobox(self, values=["Day", "Half-Day", "Late Rental"], state="readonly", font=("Arial", 12))
        self.period_combo.grid(row=5, column=1, padx=50, pady=(0, 10), sticky="w")

        ttk.Label(self, text="Deposit Type", style="Form.TLabel").grid(row=6, column=0, padx=50, sticky="w")
        self.deposit_combo = ttk.Combobox(self, values=["Cash", "Credit Card"], state="readonly", font=("Arial", 12))
        self.deposit_combo.grid(row=7, column=0, padx=50, pady=(0, 10), sticky="w")

        #ttk.Label(self, text="Available Bicycles (max 4)").grid(row=8, column=0, padx=50, sticky="w")
        self.bicycle_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=50, height=10, font=("Arial", 12))
        self.bicycle_listbox.grid(row=8, column=0, columnspan=2, pady=20)

        self.available_bicycles = list_available_bikes()
        for bike in self.available_bicycles:
            self.bicycle_listbox.insert(tk.END, f"{bike[1]} | {bike[2]} | {bike[3]} | {bike[4]} [{bike[5]}]")
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Create Rental",
                command=self.create_rental).pack(side="left", padx=10)

        ttk.Button(button_frame, text="Back", style="Exit.TButton",
                command=self.main_menu).pack(side="left", padx=10)
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
            rental_data=(name,phone,date,out,time_back,period,deposit,0,total_deposit,total)
            rental_id=add_rental(rental_data)
            self.destroy()
            self.parent.deiconify()
            ReceiptForm(rental_data,rental_id,selected_bicycles,False)
            

    def calculate_price(self,bicycles,period):
        total=0
        
        for bike in bicycles:
            bikeclass=bike[2] 
            rate = get_rate(bikeclass,period)
            total= rate + total
    
        
        return total
    
    def main_menu(self):
        self.destroy()
        self.parent.deiconify()

    def on_close(self):
        self.destroy()
        self.parent.deiconify()

