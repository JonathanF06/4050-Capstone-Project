from tkinter import ttk

def setup_styles(window):
    style = ttk.Style()
    window.configure(bg="#f0f0f0")
    style.theme_use("clam")

    style.configure("TFrame", background="#f0f0f0")

    #Title Labels
    style.configure(
        "TLabel",
        font=("Arial", 25, "bold"),
        background="#f0f0f0"
    )

    #Regular Buttons
    style.configure(
        "TButton",
        font=("Arial", 11, "bold"),
        padding=10,
        foreground="white",
        background="#3c59e8"
    )
    style.map(
        "TButton",
        background=[("active", "#546ce3")],
        foreground=[("active", "white")]
    )

    #Exit/Back Buttons
    style.configure(
        "Exit.TButton",
        font=("Arial", 11, "bold"),
        padding=10,
        foreground="white",
        background="#ab0232"
    )
    style.map(
        "Exit.TButton",
        background=[("active", "#eb3467")],
        foreground=[("active", "white")]
    )

    # List available bikes Treeview (table body) 
    style.configure(
        "Treeview",
        background="#ffffff",
        foreground="#333333",
        rowheight=20,
        fieldbackground="#ffffff",
        bordercolor="#dddddd",
        borderwidth=1,
        font=("Arial", 10)
    )

    # List available bikes header 
    style.configure(
        "Treeview.Heading",
        background="#f5f5f5",
        foreground="#222222",
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=6
    )

    # List available bikes header hover effect
    style.map(
        "Treeview.Heading",
        background=[("active", "#e8e8e8")]
    )

    # List available bikes selected 
    style.map(
        "Treeview",
        background=[("selected", "#3c59e8")],
        foreground=[("selected", "white")]
    )

    style.configure(
        "TEntry",
        padding=6,
        font=("Arial", 20),
        relief="flat",
        borderwidth=1,
        foreground="#333333",
        fieldbackground="#ffffff",
        insertcolor="#333333",  # cursor color
    )