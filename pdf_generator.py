import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def number_to_words(n):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_less_than_1000(num):
        words = ""
        if num >= 100:
            words += units[num // 100] + " Hundred "
            num %= 100
            if num > 0:
                words += "and "
        if num >= 20:
            words += tens[num // 10] + " "
            num %= 10
        if num > 0:
            words += units[num] + " "
        return words.strip()

    if n == 0: return "Zero"
    n = int(n)
    words = ""
    if n >= 100000:
        lakhs = n // 100000
        words += convert_less_than_1000(lakhs) + " Lakh "
        n %= 100000
    if n >= 1000:
        thousands = n // 1000
        words += convert_less_than_1000(thousands) + " Thousand "
        n %= 1000
    if n > 0:
        words += convert_less_than_1000(n)
    return words.strip() + " Rupees Only"

def generate_invoice_pdf(pdf_path, firm_name, gst_number, firm_address, invoice_number, date, customer_name, customer_mobile, customer_address, items, subtotal, cgst, sgst, total_amount, cert_data=None):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    total_words = number_to_words(total_amount)
    
    # 2. Draw Outer Border and Clipped Graphics
    c.setLineWidth(1.5)
    c.setStrokeColorRGB(0, 0, 0)
    
    # Symmetrical border coordinates
    left_x = 22.0
    right_x = 573.0
    bottom_y = 7.0
    top_y = 835.0
    border_w = right_x - left_x
    border_h = top_y - bottom_y
    
    # Clip and Draw Header/Footer
    c.saveState()
    path = c.beginPath()
    path.rect(left_x + 0.5, bottom_y + 0.5, border_w - 1, border_h - 1)
    c.clipPath(path, stroke=0, fill=0)
    
    from utils import get_asset_path
    header_img = get_asset_path("header_img.png")
    footer_img = get_asset_path("footer_img.png")

    if os.path.exists(header_img):
        c.drawImage(header_img, left_x, top_y - 165.8, width=border_w, height=165.8)
    if os.path.exists(footer_img):
        c.drawImage(footer_img, left_x, bottom_y, width=border_w, height=348.9)
    c.restoreState()
    
    # Draw the single unified border rectangle
    c.rect(left_x, bottom_y, border_w, border_h)
    
    # Row 1: Name & Invoice No
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 635, "Name : ")
    c.setFont("Helvetica", 11)
    c.drawString(90, 635, customer_name[:35])
    c.setLineWidth(0.5)
    c.line(85, 633, 280, 633)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(460, 635, "Invoice No. : ")
    c.setFont("Helvetica", 11)
    c.drawString(465, 635, invoice_number)
    c.line(465, 633, 555, 633)
    
    # Row 2: Mobile & Date
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 610, "Mobile : ")
    c.setFont("Helvetica", 11)
    c.drawString(90, 610, customer_mobile[:15])
    c.line(85, 608, 280, 608)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(460, 610, "Date : ")
    c.setFont("Helvetica", 11)
    c.drawString(465, 610, date)
    c.line(465, 608, 555, 608)
    
    # Row 3: Address
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 585, "Address : ")
    c.setFont("Helvetica", 11)
    c.drawString(100, 585, customer_address[:85])
    c.line(95, 583, 555, 583)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(297.5, 545, "Details")
    
    # 4. Draw Table Dynamically (Centered on page)
    table_width = 510 
    table_x = 297.5 - (table_width / 2)
    table_top = 525
    row_height = 25
    header_height = 25
    total_row_height = 25
    
    num_items = len(items)
    rows_to_draw = max(3, num_items)
    table_bottom = table_top - header_height - (rows_to_draw * row_height) - total_row_height
    
    c.setLineWidth(1.0) 
    c.rect(table_x, table_bottom, table_width, table_top - table_bottom)
    c.line(table_x, table_top - header_height, table_x + table_width, table_top - header_height)
    
    # Draw horizontal row separators inside the table for ALL rows
    for r in range(1, rows_to_draw):
        row_y = table_top - header_height - (r * row_height)
        c.line(table_x, row_y, table_x + table_width, row_y)
        
    total_row_y = table_bottom + total_row_height
    c.line(table_x, total_row_y, table_x + table_width, total_row_y)
    
    cols = [
        {"x": table_x, "lbl": "S.N", "width": 30},
        {"x": table_x + 30, "lbl": "Model Name", "width": 110},
        {"x": table_x + 140, "lbl": "IMEI", "width": 100},
        {"x": table_x + 240, "lbl": "Battery No.", "width": 75},
        {"x": table_x + 315, "lbl": "Charger No.", "width": 70},
        {"x": table_x + 385, "lbl": "Warranty", "width": 60},
        {"x": table_x + 445, "lbl": "Amount", "width": 65}
    ]
    
    c.setFont("Helvetica-Bold", 10)
    for col in cols:
        if col["x"] > table_x:
            # The line before 'Amount' goes all the way down. The rest stop at the total row.
            bottom_line_y = table_bottom if col["lbl"] == "Amount" else total_row_y
            c.line(col["x"], bottom_line_y, col["x"], table_top)
        c.drawCentredString(col["x"] + (col["width"] / 2), table_top - 17, col["lbl"])
        
    start_y = table_top - header_height - 17
    
    def draw_fit(text, x, y, max_w, align="center"):
        size = 10
        c.setFont("Helvetica", size)
        while c.stringWidth(text, "Helvetica", size) > max_w - 4 and size > 4:
            size -= 0.5
            c.setFont("Helvetica", size)
        if align == "center":
            c.drawCentredString(x, y, text)
        elif align == "right":
            c.drawRightString(x, y, text)
        else:
            c.drawString(x, y, text)
        c.setFont("Helvetica", 10) # restore
        
    for i, item in enumerate(items):
        y = start_y - (i * row_height)
        draw_fit(str(i + 1), cols[0]["x"] + cols[0]["width"]/2, y, cols[0]["width"])
        draw_fit(item.get('product_name', ''), cols[1]["x"] + 5, y, cols[1]["width"] - 10, "left")
        draw_fit(item.get('imei', '-'), cols[2]["x"] + cols[2]["width"]/2, y, cols[2]["width"])
        draw_fit(item.get('battery_num', '-'), cols[3]["x"] + cols[3]["width"]/2, y, cols[3]["width"])
        draw_fit(item.get('charger_num', '-'), cols[4]["x"] + cols[4]["width"]/2, y, cols[4]["width"])
        draw_fit(item.get('warranty', '-'), cols[5]["x"] + cols[5]["width"]/2, y, cols[5]["width"])
        draw_fit(f"{item.get('final_rate', 0.0):.2f}", cols[6]["x"] + cols[6]["width"] - 5, y, cols[6]["width"] - 10, "right")
        
    c.setFont("Helvetica-Bold", 10)
    c.drawString(table_x + 5, table_bottom + 8, "In Words :")
    c.setFont("Helvetica", 10)
    c.drawString(table_x + 65, table_bottom + 8, total_words)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(cols[6]["x"] - 5, table_bottom + 8, "Total Payment")
    c.drawRightString(cols[6]["x"] + cols[6]["width"] - 5, table_bottom + 8, f"{total_amount:.2f}")
    
    c.save()
    return pdf_path

if __name__ == "__main__":
    test_items = [
        {
            "product_name": "SAMSUNG M32",
            "imei": "358890123456789",
            "battery_num": "B-001",
            "charger_num": "C-999",
            "warranty": "6m",
            "final_rate": 15500.00
        },
        {
            "product_name": "Redmi Note 12",
            "imei": "864112345678901",
            "battery_num": "B-X72",
            "charger_num": "N/A",
            "warranty": "1y",
            "final_rate": 12000.00
        }
    ]
    generate_invoice_pdf("test_multi_invoice.pdf", "Om Sai Mobile Shoppee", "27GEFPS4065Q1ZM", "G. Sinagi Peth, S.T. Stand Road, Kurul, Taluka Mohol", "INV-1300", "2026-04-20", "Abhijeet Haraliya", "7066003766", "Solapur", test_items, 0, 0, 0, 27500.00)
    print("Test Multi Device PDF created.")
