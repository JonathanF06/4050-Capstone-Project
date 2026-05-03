import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox
from database import get_bikes_from_rental 
from gui.final_receipt import FinalReceipt
from tkinter import messagebox
from database import update_rental_status



class ReturnForm(tk.Toplevel):
    def __init__(self,rental_id):
        super().__init__()
        self.rental_id=rental_id
        self.title("Receipt")
        self.geometry("900x550")

        bikes = get_bikes_from_rental(rental_id)

        self.status_bikes={}
        frame = tk.Frame(self, bd=2, relief="groove")
        frame.pack(padx=10, pady=10)
        for row, bike in enumerate(bikes):
            bikeid =bike[0]
            registration=bike[1]
            bikeclass=bike[2]
            make=bike[3]
            model=bike[4]
            status=bike[5]
            
            var=tk.StringVar(value="Returned")
            self.status_bikes[bikeid]=var

            ttk.Label(frame,text=registration,width=40).grid(row=row,column=0,sticky="w")
            ttk.Radiobutton(frame,text="Returned",variable=var,value="Returned").grid(row=row,column=1)
            ttk.Radiobutton(frame,text="Late",variable=var,value="Late").grid(row=row,column=2)
            ttk.Radiobutton(frame,text="Lost",variable=var,value="Lost").grid(row=row,column=3)
        current_rows = len(bikes)
         
        time_values=["8:00AM","8:30AM","9:00AM","9:30AM","10:00AM","10:30AM","11:00AM","11:30AM","12:00PM","12:30PM","1:00PM","1:30PM",
            "2:00PM","2:30PM","3:00PM","3:30PM","4:00PM","4:30PM","5:00PM"]

        ttk.Label(frame, text="Time Back", style="Form.TLabel").grid(row=current_rows, column=0, padx=50, sticky="w")
        self.expected_back_entry = ttk.Combobox(frame, values=time_values, state="readonly", font=("Arial", 12))
        self.expected_back_entry.grid(row=current_rows, column=1, padx=50, pady=(0, 10), sticky="w")
        

        ttk.Button(self, text="Print",
            command=self.final_print).pack(side="left", padx=10)

    def final_print(self): 
        time_back=self.expected_back_entry.get()
        if time_back is not '':
            for bike_id,status in self.status_bikes.items():
                status=status.get()  
                update_rental_status(bike_id,status)
            
            FinalReceipt(self.rental_id)
            self.destroy()
        else: 
            messagebox.showerror(
            "Missing Fields",
            "Return time is missing "
            )

    

    