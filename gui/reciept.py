import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from database import get_rate
from database import add_rental
from database import add_rental_item
from tkinter import messagebox
from database import get_rental_prepaid
from database import get_rental_total 
from database import update_prepaid
from database import delete_rental
from styles import setup_styles


class ReceiptForm(tk.Toplevel):
    def __init__(self,data,rentals_id,selected,final):
        super().__init__()

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=12)

        bold_font = tkfont.nametofont("TkTextFont")
        bold_font.configure(size=12)
        self.data=data
        self.final = final
        self.selected=selected
        self.rentals_id=rentals_id
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        def only_numbers(P):
            return P.isdigit() or P == ""
        vcmd = (self.register(only_numbers), "%P")

        self.title("Receipt")
        self.geometry("900x600")

        main = tk.Frame(self, padx=10, pady=10)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        # top left UI
        company = tk.LabelFrame(
            main,
            text="Jonathan's Bicycles",
            font=("Arial", 20, "bold"),
            padx=10,
            pady=8
        )
        company.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

        tk.Label(company, text="Telephone:", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(company, text="+1 (305) 460-6081", font=("Arial", 14)).grid(row=0, column=1, sticky="w", padx=5)

        # bottom left UI
        customer = tk.LabelFrame(
            main,
            text="Customer Details",
            font=("Arial", 20, "bold"),
            padx=10,
            pady=8
        )
        customer.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        customer.columnconfigure(1, weight=1)

        tk.Label(customer, text="Name:", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", pady=3)
        tk.Label(customer, text=data[0], font=("Arial", 14)).grid(row=0, column=1, sticky="w")

        tk.Label(customer, text="Tel No:", font=("Arial", 16, "bold")).grid(row=1, column=0, sticky="w", pady=3)
        tk.Label(customer, text=data[1], font=("Arial", 14)).grid(row=1, column=1, sticky="w")

        # right UI
        details = tk.LabelFrame(
            main,
            text="Rental Details",
            font=("Arial", 20, "bold"),
            padx=15,
            pady=10
        )
        details.grid(row=0, column=1, rowspan=2, sticky="nsew")

        details.columnconfigure(0, weight=1)
        details.columnconfigure(1, weight=1)

        rows = [
            ("Date:", data[2]),
            ("Time Out:", data[3]),
            ("Expected Time Back:", data[4]),
            ("Expected Period:", data[5]),
            ("Total Deposit:", f"${int(data[8])}"),
        ]

        for r, (label, value) in enumerate(rows):
            tk.Label(details, text=label, font=("Arial", 16, "bold")).grid(
                row=r, column=0, sticky="w", pady=5
            )
            tk.Label(details, text=value, font=("Arial", 14)).grid(
                row=r, column=1, sticky="w", pady=5
            )


        # Table
        table_frame = tk.Frame(main, bd=1, relief="solid")
        table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=15)
        for i in range(6):
            table_frame.columnconfigure(i, weight=1)

        headers_top = ["Rental Information", "", "", "", "Payment",""]
        col_spans = [4, 0, 0, 0, 2,0]

        col = 0
        for text, span in zip(headers_top, col_spans):
            if span == 0:
                continue
            lbl = tk.Label(table_frame, text=text, font=("Arial", 14, "bold"),
                        borderwidth=1, relief="solid", anchor="w", padx=5, pady=5)
            lbl.grid(row=0, column=col, columnspan=span, sticky="nsew")
            col += span
        
        headers=["Reg Number","Class","Make","Model","Price","Prepaid"]
        for column,text in enumerate(headers): 
            tk.Label(table_frame,text=text,borderwidth=1,relief="solid",padx=5,pady=5, font=("Arial", 14)).grid(row=1,column=column, sticky="nsew")
        
        bike_data = []
        self.list_prices = []
        prepaid=[]

        for id,reg_number,bike_class,make,model,status in selected:
            price = int(get_rate(bike_class,data[5]))
            self.list_prices.append(price)
            price_formatted=f"${price}"

            bike_data.append([reg_number,bike_class,make,model,price_formatted,"prepay"])
            if final: 
                prepaid.append (get_rental_prepaid(rentals_id,id))
        
        self.prepaid_entries = []
        last_row = 0
        for row, row_data in enumerate(bike_data,start=2):

            for column, value in enumerate(row_data):
                if value == "prepay":
                    if not final:
                        entry = tk.Entry(table_frame,borderwidth=2,relief="solid",highlightthickness =0,validate="key",validatecommand=vcmd, font=("Arial", 14))
                        entry.grid(row=row, column=column,padx=5, pady=5)
                
                        self.prepaid_entries.append(entry)
                    else :
                        prepaid_formatted = f"${int(prepaid[row-2])}"
                        tk.Label(table_frame,text=prepaid_formatted,borderwidth=1,highlightthickness=0,relief="solid",padx=5,pady=5, font=("Arial", 14)).grid(row=row,column=column, sticky="nsew")


                else:
                    tk.Label(table_frame,text=value,borderwidth=1, relief="solid",padx=5,pady=5, font=("Arial", 14)).grid(row=row,column=column, sticky="nsew")
            
            last_row = row

        
        bottom = tk.Frame(main)
        bottom.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
       
        if not final:
            print_button = tk.Button(bottom, text="Print", width=12, command=self.save_print)
            print_button.pack(anchor="e", padx=10, pady=5)
        else: 
            total_prepaid=sum(prepaid)
            total_cost= get_rental_total(rentals_id)

            #tk.Label(table_frame,text="",borderwidth=1, relief="solid",padx=5,pady=5, font=("Arial", 14)).grid(row=last_row+1,column=0, columnspan=6, rowspan=2, sticky="nsew")
            paid_text_label=tk.Label(table_frame, text=f"Total Paid: ${total_prepaid}", font=("Arial", 16, "bold"))
            paid_text_label.grid(row=last_row+1, column=0, columnspan=6, sticky="e")

            cost_text_label=tk.Label(table_frame, text=f"Total Cost: ${total_cost}", font=("Arial", 16, "bold"))
            cost_text_label.grid(row=last_row+2, column=0, columnspan=6, sticky="e")
            

    def on_close(self):
        if not self.final:
            if messagebox.askyesno("Confirm","Do you want to cancel the rental?"):
                self.destroy()
                delete_rental(self.rentals_id)
        else:
            self.destroy()

    def save_print(self):
        prepaid_amount=[]
        hasError = False
        
        for i, entry in enumerate(self.prepaid_entries):
            if entry.get() != '':
                if self.list_prices[i] < int(entry.get()):
                    messagebox.showerror(
                        "Error",
                        "Please make sure prepaid prices are correct."
                    )
                    hasError = True
                    return
                else:
                    prepaid_amount.append(int(entry.get()))
        
        if len(prepaid_amount) != len(self.selected):
            if not hasError:
                messagebox.showerror(
                    "Missing Fields",
                    "Please fill out a Prepaid amount.") 
        else:
            update_prepaid(self.rentals_id,sum(prepaid_amount)) 
            for i, bike in enumerate(self.selected):
                bike_id=bike[0]
                add_rental_item(prepaid_amount[i],self.rentals_id,bike_id)
                self.destroy()
            ReceiptForm(self.data,self.rentals_id,self.selected,True)
     