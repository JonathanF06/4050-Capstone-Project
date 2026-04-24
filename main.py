from database import *
from gui.main_window import BicycleRentalApp

def main():
    initialize_database()
    seed_sample_data()
    app = BicycleRentalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
