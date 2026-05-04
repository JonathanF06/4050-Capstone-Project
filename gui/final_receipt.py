import tkinter as tk 
from tkinter import ttk
from database import get_bikes_from_rental
from database import get_late_fee
from database import get_bike_status
from database import get_rate
from database import get_period
from database import get_total_deposit
from database import get_prepaid_amount
from database import update_bike_status
from database import update_late_fee
from database import update_lost_fee
from database import get_rental_late_fee
from database import get_rental_lost_fee

class FinalReceipt(tk.Toplevel):
    def __init__(self,rental_id):
        super().__init__()

        self.title("Receipt")
        self.geometry("450x580")
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 24, "bold"))
        style.configure("TLabel", font=("Arial", 16, "bold"))

        bikes = get_bikes_from_rental(rental_id)
        late_fee=0
        lost_fee=0
        deposit=get_total_deposit(rental_id)
        prepaid=get_prepaid_amount(rental_id)
        total=0 
        credit= deposit + prepaid
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0,weight=1)
        main.columnconfigure(1,weight=1)

        ttk.Label(main, text=f"Receipt #{rental_id}", style="Title.TLabel").grid(row=0, column=0,columnspan=2)
        ttk.Label(
            main,
            text="---------------------------------------------------------",
            font=("Courier New", 14),
            padding=10
        ).grid(row=1, column=0, columnspan=2, sticky="ew")

        for row, bike in enumerate(bikes,start=1):
            bikeid =bike[0]
            registration=bike[1]
            bikeclass=bike[2]
            rate=get_rate(bikeclass,get_period(rental_id))
            total=rate + total
            status=get_bike_status(bikeid)
            if status == "Late":
                late_fee += get_late_fee(bikeclass)
                update_late_fee(rental_id, late_fee)
                update_bike_status(bikeid, "Available")
            elif status == "Lost":
                lost_fee += 20
                update_lost_fee(rental_id, lost_fee)
            ttk.Label(main,text=f"Bike {row}: {registration}").grid(row=row+1, column=0, sticky="w")
            ttk.Label(main,text=self.money(rate)).grid(row=row+1, column=1, sticky="e")

        if lost_fee == 0:
            lost_fee = get_rental_lost_fee(rental_id)
        
        if late_fee == 0:
            late_fee = get_rental_late_fee(rental_id)

        total =lost_fee + late_fee +total
        count=len(bikes)+2

        ttk.Label(main,text="Deposit").grid(row=count+1, column=0, sticky="w") 
        ttk.Label(main,text=f"-{self.money(deposit)}").grid(row=count+1, column=1, sticky="e")

        ttk.Label(main,text="Prepaid").grid(row=count+2, column=0, sticky="w")
        ttk.Label(main,text=f"-{self.money(prepaid)}").grid(row=count+2, column=1, sticky="e")

        ttk.Label(main,text="Late Fee").grid(row=count+3, column=0, sticky="w")
        ttk.Label(main,text=self.money(late_fee)).grid(row=count+3, column=1, sticky="e")

        ttk.Label(main,text="Lost Fee").grid(row=count+4, column=0, sticky="w")
        ttk.Label(main,text=self.money(lost_fee)).grid(row=count+4, column=1, sticky="e")
        
        ttk.Label(
            main,
            text="---------------------------------------------------------",
            font=("Courier New", 14),
            padding = 10
        ).grid(row=count+5, column=0, columnspan=2, sticky="ew")

        ttk.Label(main,text="Total").grid(row=count+6, column=0, sticky="w")
        ttk.Label(main,text=self.money(total)).grid(row=count+6, column=1, sticky="e")

        ttk.Label(main,text="Credit").grid(row=count+7, column=0, sticky="w")
        ttk.Label(main,text=f"-{self.money(credit)}").grid(row=count+7, column=1, sticky="e")

        ttk.Label(
            main,
            text="---------------------------------------------------------",
            font=("Courier New", 14),
            padding=10
        ).grid(row=count+8, column=0, columnspan=2, sticky="ew")

        ttk.Label(main, text="THANK YOU!", style="Title.TLabel").grid(row=count+9, column=0,columnspan=2)


    def money(self, value):
        return f"${float(value):.2f}"





