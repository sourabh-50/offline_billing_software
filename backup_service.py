import os
import zipfile
import datetime
import sqlite3
import pandas as pd
import database

def create_backup():
    # Full traditional binary backup
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    backup_filename = f"backup_full_{timestamp}.zip"
    backup_path = os.path.join("backups", backup_filename)

    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists("database.db"):
            zipf.write("database.db", arcname="database.db")
        if os.path.exists("invoices"):
            for root, _, files in os.walk("invoices"):
                for file in files:
                    full_path = os.path.join(root, file)
                    arc_name = os.path.join("invoices", file)
                    zipf.write(full_path, arcname=arc_name)
    return backup_path

def export_timeline_backup(timeline: str, save_path: str):
    """
    Exports a professional Excel (.xlsx) timeline report.
    """
    conn = sqlite3.connect(database.DB_NAME)
    
    now = datetime.datetime.now()
    
    query = "SELECT i.invoice_number, c.name as Customer_Name, c.mobile, i.date, i.total_amount, ii.product_name, ii.imei FROM Invoices i LEFT JOIN Customers c ON i.customer_id = c.customer_id LEFT JOIN Invoice_Items ii ON i.invoice_id = ii.invoice_id"
    
    if timeline == "Today":
        date_cond = now.strftime("%Y-%m-%d")
        query += " WHERE substr(i.date, 1, 10) = ?"
        df = pd.read_sql_query(query, conn, params=(date_cond,))
    elif timeline == "This Week":
        start = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        query += " WHERE substr(i.date, 1, 10) >= ?"
        df = pd.read_sql_query(query, conn, params=(start,))
    elif timeline == "This Month":
        start = now.strftime("%Y-%m-01")
        query += " WHERE substr(i.date, 1, 10) >= ?"
        df = pd.read_sql_query(query, conn, params=(start,))
    elif timeline == "This Year":
        start = now.strftime("%Y-01-01")
        query += " WHERE substr(i.date, 1, 10) >= ?"
        df = pd.read_sql_query(query, conn, params=(start,))
    else: # All Time
        df = pd.read_sql_query(query, conn)

    conn.close()

    if df.empty:
        raise ValueError(f"No records found for the timeline: {timeline}")

    # Ensure extension is .xlsx
    if not save_path.endswith(".xlsx"):
        save_path = os.path.splitext(save_path)[0] + ".xlsx"

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    df.to_excel(save_path, index=False)
        
    return save_path

if __name__ == "__main__":
    pass
