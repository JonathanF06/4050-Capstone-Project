import sqlite3
DB_NAME = "highpeak_rentals.db"
DATE_FMT = "%Y-%m-%d %H:%M"

#connecting to my database 
def get_connection():
    return sqlite3.connect(DB_NAME)

#creating database tables
def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS bicycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_number TEXT UNIQUE NOT NULL,
                    bike_class TEXT NOT NULL,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    frame_size TEXT NOT NULL,
                    frame_number TEXT NOT NULL,
                    date_of_purchase TEXT NOT NULL,
                    purchase_price REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Available',
                    selling_date TEXT,
                    selling_price REAL
                    
                );

                CREATE TABLE IF NOT EXISTS rental_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bike_class TEXT NOT NULL,
                    period TEXT NOT NULL,
                    rate REAL NOT NULL,
                    effective_from TEXT NOT NULL,
                    effective_to TEXT,
                    UNIQUE(bike_class, period, effective_from)
                );

                CREATE TABLE IF NOT EXISTS rentals (
                    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    telephone TEXT NOT NULL,
                    date_created TEXT NOT NULL,
                    time_out TEXT NOT NULL,
                    expected_time_back TEXT NOT NULL,
                    expected_period TEXT NOT NULL,
                    deposit_type TEXT NOT NULL,
                    total_prepaid_amount REAL NOT NULL,
                    total_deposit_amount REAL NOT NULL,
                    time_returned TEXT,
                    actual_charge REAL,
                    extra_charge REAL,
                    deposit_released INTEGER DEFAULT 0,
                    rental_status TEXT NOT NULL DEFAULT 'Open',
                    incident_notes TEXT
                );

                CREATE TABLE IF NOT EXISTS rental_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bicycle_class TEXT NOT NULL,
                    period TEXT NOT NULL,
                    rate REAL NOT NULL
                );
                """
    ) 
    connection.commit()
    connection.close()

# creating sample data and pushing into database
def seed_sample_data(): 
    bikes = [
        ("MB001", "MB", "Trek", "Marlin 7", "M", "FRM001", "2025-05-01", 800.0),
        ("MB002", "MB", "Giant", "Talon 2", "L", "FRM002", "2025-06-15", 760.0),
        ("MB003", "MB", "Scott", "Aspect 960", "M", "FRM003", "2024-08-20", 780.0),
        ("AT001", "AT", "Specialized", "Sirrus X", "M", "FRM004", "2025-03-10", 700.0),
        ("AT002", "AT", "Cannondale", "Quick CX", "S", "FRM005", "2024-09-05", 690.0)
    ]
    rates = [
        ("MB", "Day", 18.0, "2026-01-01", None),
        ("MB", "Half-Day", 10.0, "2026-01-01", None),
        ("MB", "Late Rental", 6.0, "2026-01-01", None),
        ("AT", "Day", 20.0, "2026-01-01", None),
        ("AT", "Half-Day", 12.0, "2026-01-01", None),
        ("AT", "Late Rental", 8.0, "2026-01-01", None)
    ]
    add_bicycles(bikes)
    add_rates(rates)

def add_rates(data):    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.executemany(
        """
        INSERT OR IGNORE INTO rental_rates (
            bike_class,period,rate,effective_from,effective_to
        ) VALUES (?, ?, ?, ?, ?)
        """,
        data
    )
    connection.commit()
    connection.close()


#inserting data into bicycle table.
def add_bicycles(data): 
    connection = get_connection()
    cursor = connection.cursor()
    cursor.executemany(
        """
        INSERT OR IGNORE INTO bicycles (
            registration_number, bike_class, make, model, frame_size,
            frame_number, date_of_purchase, purchase_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?,?)
        """,
        data
    )
    connection.commit()
    connection.close()

#pulls all availble bikes from the table     
def list_available_bikes():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT registration_number, bike_class, make, model, status
            FROM bicycles
            WHERE status = 'Available'
            ORDER BY bike_class, registration_number
            """)
    rows = cursor.fetchall() 
    connection.close()
    return rows

#pulls rates from our database 
def get_rate(bicycle_class, period):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT rate FROM rental_rates
    WHERE bike_class = ? AND period = ?
    ORDER BY id DESC LIMIT 1
    """, (bicycle_class, period))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0 

def add_rental(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO rentals (
        customer_name, telephone, date_created, time_out, expected_time_back, expected_period,
        deposit_type, total_prepaid_amount, total_deposit_amount
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
