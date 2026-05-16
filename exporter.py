import os
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

DB_NAME = "database.db"

def get_sales_data(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = '''
        SELECT i.invoice_number, i.date, c.name as Customer_Name, 
               ii.product_name, ii.imei, i.total_amount
        FROM Invoices i
        JOIN Customers c ON i.customer_id = c.customer_id
        JOIN Invoice_Items ii ON i.invoice_id = ii.invoice_id
    '''
    params = []
    if start_date and end_date:
        query += " WHERE i.date >= ? AND i.date <= ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE i.date >= ?"
        params.append(start_date)
        
    cursor.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    conn.close()
    return columns, data

def export_sales_excel(start_date, end_date, output_path):
    from openpyxl import Workbook
    cols, data = get_sales_data(start_date, end_date)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    
    # Write header
    ws.append(cols)
    
    # Write data
    for row in data:
        ws.append(row)
        
    # Auto-adjust column widths
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

    wb.save(output_path)
    return output_path

def export_sales_pdf(start_date, end_date, output_path):
    cols, rows = get_sales_data(start_date, end_date)
    
    # Calculate summary
    # total_amount is the last column (index 5)
    total_sales = sum(row[5] for row in rows) if rows else 0.0
    # invoice_number is the first column (index 0)
    unique_invoices = len(set(row[0] for row in rows)) if rows else 0
    num_invoices = unique_invoices

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "SALES REPORT")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2.0, height - 70, f"Period: {start_date} to {end_date}")

    # Summary
    c.drawString(40, height - 100, f"Total Invoices: {num_invoices}")
    c.drawString(40, height - 115, f"Total Sales: Rs. {total_sales:.2f}")

    # Table
    y = height - 145
    if rows:
        # Group to avoid repeating invoice fields unnecessarily, but simple flattened table is fine
        # Format headers
        formatted_cols = [c.replace("_", " ").title() for c in cols]
        data = [formatted_cols]
        for row in rows:
            # Convert row to strings
            data.append([str(val) for val in row])

        # Define explicit column widths for precise centering
        col_widths = [70, 70, 100, 150, 100, 60]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        table_w, table_h = table.wrapOn(c, width - 60, height)
        # Assuming fits on one page for simplicity, center justify the table
        table.drawOn(c, (width - table_w) / 2.0, y - table_h)

    c.save()
    return output_path

if __name__ == "__main__":
    print("Testing exporter with empty data...")
