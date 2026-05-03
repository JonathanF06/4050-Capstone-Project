import tkinter as tk 
from tkinter import ttk
from database import get_bikes_from_rental
from database import get_late_fee
from database import get_bike_status
from database import get_rate
from database import get_period
from database import get_total_deposit
from database import get_prepaid_amount

class FinalReceipt(tk.Toplevel):
    def __init__(self,rental_id):
        super().__init__()
        
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
        ttk.Label(main, text="Receipt").grid(row=0, column=0,columnspan=2)
        for row, bike in enumerate(bikes,start=1):
            bikeid =bike[0]
            registration=bike[1]
            bikeclass=bike[2]
            rate=get_rate(bikeclass,get_period(rental_id))
            total=rate + total
            #LABEL REGISTRATION         rate  
            status=get_bike_status(bikeid)
            if status == "Late":
                late_fee += get_late_fee(bikeclass)
            elif status == "Lost":
                lost_fee += 20
            ttk.Label(main,text=f"Bike {row}: {registration}").grid(row=row, column=0)
            ttk.Label(main,text=f"${rate}").grid(row=row, column=1)
        total =lost_fee + late_fee +total
        count=len(bikes)
        ttk.Label(main,text="Deposit").grid(row=count+1, column=0) 
        ttk.Label(main,text=f"${deposit}").grid(row=count+1, column=1)

        ttk.Label(main,text="Prepaid").grid(row=count+2, column=0)
        ttk.Label(main,text=f"${prepaid}").grid(row=count+2, column=1)

        ttk.Label(main,text="Late Fee").grid(row=count+3, column=0)
        ttk.Label(main,text=f"${late_fee}").grid(row=count+3, column=1)

        ttk.Label(main,text="Lost Fee").grid(row=count+4, column=0)
        ttk.Label(main,text=f"${lost_fee}").grid(row=count+4, column=1)
        
        ttk.Separator(main, orient="horizontal").grid(row=count+5,column=0,columnspan=2,sticky="ew")

        ttk.Label(main,text="Lost Fee").grid(row=count+4, column=0)

        ttk.Label(main,text="Total").grid(row=count+5, column=0)
        ttk.Label(main,text=f"${total}").grid(row=count+5, column=1)

        ttk.Label(main,text="Credit").grid(row=count+6, column=0)
        ttk.Label(main,text=f"${credit}").grid(row=count+6, column=1)







