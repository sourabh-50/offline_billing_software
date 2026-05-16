import os
import sys
import datetime
import config
import sqlite3
import hashlib

# Get the base directory of the application
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "database.db")

def init_db():
    # Create required directories
    os.makedirs("invoices", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("backups", exist_ok=True)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Firms Table
    # NOTE FOR ENGINEER: Firms are not editable in the UI. 
    # This allows you to charge for maintenance when clients want to change shop details.
    # Manually insert into this table before delivery.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Firms (
            firm_id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            gst_number TEXT NOT NULL,
            address TEXT,
            contact TEXT,
            invoice_prefix TEXT NOT NULL
        )
    ''')

    # Create Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT,
            address TEXT
        )
    ''')

    # Create Invoices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            firm_id INTEGER,
            customer_id INTEGER,
            date TEXT NOT NULL,
            subtotal REAL,
            cgst REAL,
            sgst REAL,
            total_amount REAL,
            pdf_path TEXT,
            device_power TEXT,
            screen_condition TEXT,
            camera_test TEXT,
            speaker_test TEXT,
            battery_health TEXT,
            network_status TEXT,
            back_panel TEXT,
            body_condition TEXT,
            accessories TEXT,
            FOREIGN KEY(firm_id) REFERENCES Firms(firm_id),
            FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
        )
    ''')

    # Create Invoice Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Invoice_Items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            product_name TEXT,
            imei TEXT,
            hsn TEXT,
            quantity INTEGER,
            price REAL,
            discount REAL,
            final_rate REAL
        )
    ''')

    # Safe Schema Migrations for Multiple Items upgrade
    try:
        cursor.execute("ALTER TABLE Invoice_Items ADD COLUMN battery_num TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE Invoice_Items ADD COLUMN charger_num TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE Invoice_Items ADD COLUMN warranty TEXT")
    except sqlite3.OperationalError:
        pass

    # Create Config Table for Offline Security
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AppConfig (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Create Stock Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Stock (
            stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            imei TEXT,
            quantity INTEGER DEFAULT 1,
            price REAL
        )
    ''')

    # Ensure default firm is present
    cursor.execute("SELECT COUNT(*) FROM Firms")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO Firms (firm_name, gst_number, address, contact, invoice_prefix)
            VALUES (?, ?, ?, ?, ?)
        ''', (config.SHOP_NAME, "27GEFPS4065Q1ZM", "Chh. Shivaji Maharaj Chowk, G. Sinagi Peth, S.T. Stand Road, Kurul, Taluka Mohol, Solapur", "9804117777", "INV-"))

    conn.commit()
    conn.close()
def hash_password(password):
    # Added salt for improved security against rainbow tables
    salt = "scalead_secure_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def is_auth_setup():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM AppConfig WHERE key='master_password'")
    row = cursor.fetchone()
    conn.close()
    return row is not None

def setup_auth(password):
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO AppConfig (key, value) VALUES ('master_password', ?)", (hashed,))
    conn.commit()
    conn.close()

def verify_auth(password):
    if not is_auth_setup():
        return True
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM AppConfig WHERE key='master_password'")
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hashed:
        return True
    return False

def remove_auth():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AppConfig WHERE key='master_password'")
    conn.commit()
    conn.close()

# Config Settings
def get_setting(key):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM AppConfig WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO AppConfig (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# CRUD Endpoints

def add_firm(firm_name, gst_number, address, contact, invoice_prefix):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Firms (firm_name, gst_number, address, contact, invoice_prefix)
        VALUES (?, ?, ?, ?, ?)
    ''', (firm_name, gst_number, address, contact, invoice_prefix))
    conn.commit()
    conn.close()

def get_firms():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Firms")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_or_create_customer(name, mobile, address):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM Customers WHERE mobile=?", (mobile,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]
    cursor.execute("INSERT INTO Customers (name, mobile, address) VALUES (?, ?, ?)", (name, mobile, address))
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def create_invoice(invoice_number, firm_id, customer_id, date, subtotal, cgst, sgst, total_amount, pdf_path, cert_data, items):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Insert Invoice
    cursor.execute('''
        INSERT INTO Invoices (
            invoice_number, firm_id, customer_id, date, subtotal, cgst, sgst, total_amount, pdf_path,
            device_power, screen_condition, camera_test, speaker_test, battery_health,
            network_status, back_panel, body_condition, accessories
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        invoice_number, firm_id, customer_id, date, subtotal, cgst, sgst, total_amount, pdf_path,
        cert_data.get('device_power', ''), cert_data.get('screen_condition', ''),
        cert_data.get('camera_test', ''), cert_data.get('speaker_test', ''),
        cert_data.get('battery_health', ''), cert_data.get('network_status', ''),
        cert_data.get('back_panel', ''), cert_data.get('body_condition', ''),
        cert_data.get('accessories', '')
    ))
    invoice_id = cursor.lastrowid

    # Insert Items and Decrement Stock (ACID compliant transaction)
    for item in items:
        # Insert Item
        cursor.execute('''
            INSERT INTO Invoice_Items (
                invoice_id, product_name, imei, hsn, quantity, price, discount, final_rate,
                battery_num, charger_num, warranty
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_id, item.get('product_name', ''), item.get('imei', ''), item.get('hsn', ''),
            item.get('quantity', 1), item.get('price', 0.0), item.get('discount', 0.0), item.get('final_rate', 0.0),
            item.get('battery_num', ''), item.get('charger_num', ''), item.get('warranty', '')
        ))
        
        # Decrement Stock
        cursor.execute('''
            UPDATE Stock 
            SET quantity = quantity - 1 
            WHERE stock_id = (
                SELECT stock_id FROM Stock 
                WHERE UPPER(model_name)=UPPER(?) AND quantity > 0 LIMIT 1
            )
        ''', (item.get('product_name', ''),))
        
    conn.commit()
    conn.close()
    return invoice_id

def search_invoices(query=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.invoice_number, c.name, i.date, i.total_amount, i.pdf_path 
        FROM Invoices i
        JOIN Customers c ON i.customer_id = c.customer_id
        WHERE c.name LIKE ? OR c.mobile LIKE ? OR i.invoice_number LIKE ?
    ''', ('%'+query+'%', '%'+query+'%', '%'+query+'%'))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_next_invoice_number(firm_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT invoice_prefix FROM Firms WHERE firm_id=?", (firm_id,))
    prefix_row = cursor.fetchone()
    if not prefix_row:
        return "INV-0001"
    prefix = prefix_row[0]

    # Find the maximum numeric part of existing invoice numbers with this prefix
    cursor.execute("SELECT invoice_number FROM Invoices WHERE firm_id=?", (firm_id,))
    rows = cursor.fetchall()
    
    max_num = 0
    for row in rows:
        inv_str = row[0]
        if inv_str.startswith(prefix):
            try:
                num_part = int(inv_str[len(prefix):])
                if num_part > max_num:
                    max_num = num_part
            except (ValueError, TypeError):
                continue
    
    next_num = max_num + 1
    conn.close()
    return f"{prefix}{next_num:04d}"

def get_all_customer_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM Customers")
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_customer_mobiles():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT mobile FROM Customers")
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_product_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT product_name FROM Invoice_Items")
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows

# Stock Management Functions
def add_stock(model_name, imei, quantity, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Stock (model_name, imei, quantity, price)
        VALUES (?, ?, ?, ?)
    ''', (model_name, imei, quantity, price))
    conn.commit()
    conn.close()

def get_all_stock():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Stock ORDER BY model_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_stock_item(stock_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Stock WHERE stock_id=?", (stock_id,))
    conn.commit()
    conn.close()

def update_stock_item(stock_id, model_name, imei, quantity, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Stock 
        SET model_name=?, imei=?, quantity=?, price=?
        WHERE stock_id=?
    ''', (model_name, imei, quantity, price, stock_id))
    conn.commit()
    conn.close()

def decrement_stock(model_name, imei=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Find one matching item in stock that has quantity > 0 and decrement it
    cursor.execute('''
        UPDATE Stock 
        SET quantity = quantity - 1 
        WHERE stock_id = (
            SELECT stock_id FROM Stock 
            WHERE UPPER(model_name)=UPPER(?) AND quantity > 0 LIMIT 1
        )
    ''', (model_name,))
    conn.commit()
    conn.close()

def clear_records_by_date(start_date_str, end_date_str=None):
    """
    Deletes invoices and their items between start_date and end_date.
    Format: YYYY-MM-DD
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT invoice_id, pdf_path FROM Invoices WHERE substr(date, 1, 10) >= ?"
    params = [start_date_str]
    
    if end_date_str:
        query += " AND substr(date, 1, 10) <= ?"
        params.append(end_date_str)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        return 0
    
    invoice_ids = [r[0] for r in rows]
    pdf_paths = [r[1] for r in rows]
    
    # 1. Delete Items
    cursor.execute(f"DELETE FROM Invoice_Items WHERE invoice_id IN ({','.join(['?']*len(invoice_ids))})", invoice_ids)
    
    # 2. Delete Invoices
    cursor.execute(f"DELETE FROM Invoices WHERE invoice_id IN ({','.join(['?']*len(invoice_ids))})", invoice_ids)
    
    # 3. Delete PDF files
    for path in pdf_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
                
    conn.commit()
    conn.close()
    return len(invoice_ids)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
