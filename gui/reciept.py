import tkinter as tk
from tkinter import ttk
from database import get_rate
from database import add_rental
from database import add_rental_item
from tkinter import messagebox
class ReceiptForm(tk.Toplevel):
    def __init__(self,data,rentals_id,selected):
        super().__init__()
        self.data=data
        self.selected=selected
        self.rentals_id=rentals_id

        def only_numbers(P):
            return P.isdigit() or P == ""
        vcmd = (self.register(only_numbers), "%P")

        self.title("Receipt")
        self.geometry("820x500")

        main = tk.Frame(self, padx=10, pady=10)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        # Left top
        company = tk.LabelFrame(main, text="High Peak Bicycles", font=("bold"), padx=12, pady=12)
        company.grid(row=0, column=0, sticky="nw", padx=(0, 10), pady=(0, 15))

        tk.Label(company, text="Telephone #: ", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(company, text="+1 (305) 460-6081").grid(row=0, column=1, sticky="w")

        # Left bottom
        customer = tk.LabelFrame(main, text="Customer Details", font=("bold"), padx=12, pady=12, width=330, height=210)
        customer.grid(row=1, column=0, sticky="nw", padx=(0, 10))
        customer.grid_propagate(False)

        tk.Label(customer, text="Name:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(customer, text=data[0]).grid(row=0, column=1, sticky="w")

        tk.Label(customer, text="Tel No:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w")
        tk.Label(customer, text=data[1]).grid(row=1, column=1, sticky="w")

        # Right side
        details = tk.LabelFrame(main, text="Rental Details", font=("bold"), padx=12, pady=12, width=450, height=277)
        details.grid(row=0, column=1, rowspan=2, sticky="nsew")
        details.grid_propagate(False)
        rows = [
            ("Date:", data[2]),
            ("Time Out:", data[3]),
            ("Expected Time Back:",data[4]),
            ("Expected Period:", data[5]),
            ("Total Deposit:", f"${data[8]}"),
        ]

        for r, (label, value) in enumerate(rows):
            tk.Label(details, text=label, font=("Arial", 9, "bold")).grid(
                row=r, column=0, sticky="w", pady=4
            )
            tk.Label(details, text=value).grid(
                row=r, column=1, sticky="w", padx=(80, 0), pady=4
            )

        table_frame = tk.Frame(main, bd=1, relief="solid")
        table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=15)
        for i in range(6):
            table_frame.columnconfigure(i, weight=1)

        headers_top = ["Rental Information", "", "", "", "Payment:",""]
        col_spans = [4, 0, 0, 0, 2,0]

        col = 0
        for text, span in zip(headers_top, col_spans):
            if span == 0:
                continue
            lbl = tk.Label(table_frame, text=text, font=("Arial", 10, "bold"),
                        borderwidth=1, relief="solid", anchor="w", padx=5, pady=5)
            lbl.grid(row=0, column=col, columnspan=span, sticky="nsew")
            col += span
        
        headers=["Reg Number","Class","Make","Model","Price","Prepaid"]
        for column,text in enumerate(headers): 
            tk.Label(table_frame,text=text,borderwidth=1,relief="solid",padx=5,pady=5).grid(row=1,column=column, sticky="nsew")
        
        bike_data = []
        self.list_prices = []

        for id,reg_number,bike_class,make,model,status in selected:
            price = int(get_rate(bike_class,data[5]))
            self.list_prices.append(price)
            price_formatted=f"${price}"

            bike_data.append([reg_number,bike_class,make,model,price_formatted,"prepay"])
        
        self.prepaid_entries = []
        for row, row_data in enumerate(bike_data,start=2):

            for column, value in enumerate(row_data):
                if value == "prepay":
                    entry = tk.Entry(table_frame,borderwidth=1,relief="solid",validate="key",validatecommand=vcmd)
                    entry.grid(row=row, column=column,padx=5, pady=5)

                    self.prepaid_entries.append(entry)
                else:
                    tk.Label(table_frame,text=value,borderwidth=1, relief="solid",padx=5,pady=5).grid(row=row,column=column, sticky="nsew")


        bottom = tk.Frame(main)
        bottom.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))    
        
        done_btn = tk.Button(bottom, text="Print", width=12, command=self.save_print)
        done_btn.pack(anchor="e", padx=10, pady=5) 
    
    def save_print(self):
        
        prepaid_amount=[]
        
        for i, entry in enumerate(self.prepaid_entries):
            if entry.get() != '':
                if self.list_prices[i] < int(entry.get()):
                    messagebox.showerror(
                        "Error",
                        "Please make sure prepaid prices are correct."
                    )
                else:
                    prepaid_amount.append(entry.get())
         
        if len(prepaid_amount) != len(self.selected):
            messagebox.showerror(
                "Missing Fields",
                "Please fill out a Prepaid amount.") 
        
        for i, bike in enumerate(self.selected):
            bike_id=bike[0]
            #add_rental_item(prepaid_amount[i],self.rentals_id,bike_id) 
        