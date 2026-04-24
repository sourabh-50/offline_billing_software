import os
import zipfile
import datetime
import sqlite3
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
    Exports a professional Excel (.xlsx) timeline report using openpyxl.
    """
    from openpyxl import Workbook
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.datetime.now()
    
    query = "SELECT i.invoice_number, c.name as Customer_Name, c.mobile, i.date, i.total_amount, ii.product_name, ii.imei FROM Invoices i LEFT JOIN Customers c ON i.customer_id = c.customer_id LEFT JOIN Invoice_Items ii ON i.invoice_id = ii.invoice_id"
    
    params = ()
    if timeline == "Today":
        date_cond = now.strftime("%Y-%m-%d")
        query += " WHERE substr(i.date, 1, 10) = ?"
        params = (date_cond,)
    elif timeline == "This Week":
        start = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        query += " WHERE substr(i.date, 1, 10) >= ?"
        params = (start,)
    elif timeline == "This Month":
        start = now.strftime("%Y-%m-01")
        query += " WHERE substr(i.date, 1, 10) >= ?"
        params = (start,)
    elif timeline == "This Year":
        start = now.strftime("%Y-01-01")
        query += " WHERE substr(i.date, 1, 10) >= ?"
        params = (start,)
    
    cursor.execute(query, params)
    cols = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    conn.close()

    if not data:
        raise ValueError(f"No records found for the timeline: {timeline}")

    # Ensure extension is .xlsx
    if not save_path.endswith(".xlsx"):
        save_path = os.path.splitext(save_path)[0] + ".xlsx"

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    
    ws.append(cols)
    for row in data:
        ws.append(row)
        
    # Auto-adjust columns widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    wb.save(save_path)
    return save_path
            
    return save_path

def export_pdf_merged(timeline: str, save_path: str):
    """
    Exports a single merged PDF of all invoices based on timeline.
    """
    from pypdf import PdfWriter
    conn = sqlite3.connect(database.DB_NAME)
    now = datetime.datetime.now()
    
    query = "SELECT pdf_path FROM Invoices"
    params = []
    
    if timeline == "Today":
        date_cond = now.strftime("%Y-%m-%d")
        query += " WHERE substr(date, 1, 10) = ?"
        params = (date_cond,)
    elif timeline == "This Week":
        start = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        query += " WHERE substr(date, 1, 10) >= ?"
        params = (start,)
    elif timeline == "This Month":
        start = now.strftime("%Y-%m-01")
        query += " WHERE substr(date, 1, 10) >= ?"
        params = (start,)
    elif timeline == "This Year":
        start = now.strftime("%Y-01-01")
        query += " WHERE substr(date, 1, 10) >= ?"
        params = (start,)
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No invoices found for the timeline: {timeline}")

    if not save_path.endswith(".pdf"):
        save_path = os.path.splitext(save_path)[0] + ".pdf"

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    
    merger = PdfWriter()
    found_any = False
    for row in rows:
        pdf_path = row[0]
        if pdf_path and os.path.exists(pdf_path):
            try:
                merger.append(pdf_path)
                found_any = True
            except:
                pass
    
    if not found_any:
        raise ValueError("No valid PDF files found to merge.")
        
    with open(save_path, "wb") as f:
        merger.write(f)
                
    return save_path

if __name__ == "__main__":
    pass
