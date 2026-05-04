import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox
from database import get_bikes_from_rental 
from gui.final_receipt import FinalReceipt
from tkinter import messagebox
from database import update_bike_status
from styles import setup_styles
from database import update_rental_status
from database import update_rental_return


class ReturnForm(tk.Toplevel):
    def __init__(self,parent,main,rental_id):
        super().__init__()
        setup_styles(self)
        self.parent = parent
        self.main = main
        self.rental_id=rental_id
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("Receipt")
        self.geometry("500x350")


        bikes = get_bikes_from_rental(rental_id)

        self.status_bikes={}
        frame = ttk.Frame(self, borderwidth=2, padding=10, relief="groove")
        frame.pack(padx=10, pady=10)
        for row, bike in enumerate(bikes):
            bikeid =bike[0]
            registration=bike[1]
            bikeclass=bike[2]
            make=bike[3]
            model=bike[4]
            status=bike[5]
            
            var=tk.StringVar(value="Available")
            self.status_bikes[bikeid]=var

            ttk.Label(frame,text=registration, style="Form.TLabel").grid(row=row,column=0,sticky="ew")

            status_frame = ttk.Frame(frame)
            status_frame.grid(row=row, column=1, sticky="ew")

            status_frame.columnconfigure(0, weight=1)
            status_frame.columnconfigure(1, weight=1)
            status_frame.columnconfigure(2, weight=1)

            ttk.Radiobutton(status_frame, text="Returned", variable=var, value="Available").grid(row=0, column=0)
            ttk.Radiobutton(status_frame, text="Late", variable=var, value="Late").grid(row=0, column=1)
            ttk.Radiobutton(status_frame, text="Lost", variable=var, value="Lost").grid(row=0, column=2)
        current_rows = len(bikes)
         
        time_values=["8:00AM","8:30AM","9:00AM","9:30AM","10:00AM","10:30AM","11:00AM","11:30AM","12:00PM","12:30PM","1:00PM","1:30PM",
            "2:00PM","2:30PM","3:00PM","3:30PM","4:00PM","4:30PM","5:00PM"]

        ttk.Label(frame, text="Time Back", style="Form.TLabel").grid(row=current_rows, column=0, sticky="w")
        self.expected_back_entry = ttk.Combobox(frame, values=time_values, state="readonly", font=("Arial", 12))
        self.expected_back_entry.grid(row=current_rows, column=1, padx=50, pady=(0, 10), sticky="w")
        

        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", pady=20)

        ttk.Button(button_frame, text="Print",
            command=self.final_print).pack(side="left", padx=10)

        ttk.Button(button_frame, text="Back",
            command=self.back_rental_list, style="Exit.TButton").pack(side="left", padx=10)

    def final_print(self): 
        time_back=self.expected_back_entry.get()
        if time_back != '':
            for bike_id,status in self.status_bikes.items():
                status=status.get()  
                update_bike_status(bike_id,status)

            update_rental_return(self.rental_id, time_back)
            update_rental_status(self.rental_id, "Closed")
            FinalReceipt(self.rental_id)
            self.main.deiconify()
            self.destroy()
        else: 
            messagebox.showerror(
            "Missing Fields",
            "Return time is missing "
            )

    def back_rental_list(self):
        self.parent.deiconify()
        self.destroy()
    

    def on_close(self):
        self.parent.deiconify()
        self.destroy()