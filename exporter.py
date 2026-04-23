import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

DB_NAME = "database.db"

def get_sales_data(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT i.invoice_number, i.date, c.name as Customer_Name, 
               ii.product_name, ii.imei, i.total_amount, (i.cgst + i.sgst) as Total_GST
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
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def export_sales_excel(start_date, end_date, output_path):
    df = get_sales_data(start_date, end_date)
    df.to_excel(output_path, index=False)
    return output_path

def export_sales_pdf(start_date, end_date, output_path):
    df = get_sales_data(start_date, end_date)
    total_sales = df['total_amount'].sum() if not df.empty else 0.0
    total_gst = df['Total_GST'].sum() if not df.empty else 0.0
    num_invoices = df['invoice_number'].nunique() if not df.empty else 0

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "SALES REPORT")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2.0, height - 70, f"Period: {start_date} to {end_date}")

    # Summary
    c.drawString(40, height - 100, f"Total Invoices: {num_invoices}")
    c.drawString(40, height - 115, f"Total Sales: Rs. {total_sales:.2f}")
    c.drawString(40, height - 130, f"Total GST: Rs. {total_gst:.2f}")

    # Table
    y = height - 160
    if not df.empty:
        # Group to avoid repeating invoice fields unnecessarily, but simple flattened table is fine
        data = [df.columns.tolist()]
        for _, row in df.iterrows():
            # Convert row to strings
            data.append([str(val) for val in row.values])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        table.wrapOn(c, width - 60, height)
        # Assuming fits on one page for simplicity
        table.drawOn(c, 30, y - table._height)

    c.save()
    return output_path

if __name__ == "__main__":
    print("Testing exporter with empty data...")
