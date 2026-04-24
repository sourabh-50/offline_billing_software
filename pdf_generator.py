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
    
    # Row 1: Date (Sticked to the right)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(500, 635, "Date:")
    c.line(505, 633, 555, 633)
    c.setFont("Helvetica", 10)
    c.drawString(505, 635, date)
    
    # Row 2: Name & Receipt No (Aligned on same line)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, 610, "Name:")
    c.line(85, 608, 280, 608)
    
    c.drawRightString(480, 610, "Receipt No.:")
    c.line(485, 608, 555, 608)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(90, 610, customer_name[:35])
    c.setFont("Helvetica", 10)
    c.drawString(485, 610, invoice_number)
    
    # Row 3: Address & Phone (Aligned on same line)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, 585, "Address:")
    c.line(95, 583, 280, 583)
    
    c.drawRightString(480, 585, "Phone: +91")
    c.line(485, 583, 555, 583)
    
    c.setFont("Helvetica", 10)
    c.drawString(100, 585, customer_address[:45])
    c.drawString(485, 585, customer_mobile[:15])
    
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(297.5, 560, "Details") # Lowered to match overlay
    
    # 4. Draw Table Dynamically (Centered on page)
    # Widened table for better data fit, while keeping a 20pt gap from the outer border
    table_width = 510 
    table_x = 297.5 - (table_width / 2) # = 42.5
    table_top = 545
    row_height = 25
    header_height = 25
    total_row_height = 25
    
    num_items = len(items)
    rows_to_draw = max(1, num_items)
    table_bottom = table_top - header_height - (rows_to_draw * row_height) - total_row_height
    
    c.setLineWidth(0.8) # Thicker table lines for dark look
    c.rect(table_x, table_bottom, table_width, table_top - table_bottom)
    c.line(table_x, table_top - header_height, table_x + table_width, table_top - header_height)
    
    total_row_y = table_bottom + total_row_height
    c.line(table_x, total_row_y, table_x + table_width, total_row_y)
    
    cols = [
        {"x": table_x, "lbl": "S.N", "width": 25},
        {"x": table_x + 25, "lbl": "Model Name", "width": 120},
        {"x": table_x + 145, "lbl": "IMEI", "width": 105},
        {"x": table_x + 250, "lbl": "Battery No.", "width": 60},
        {"x": table_x + 310, "lbl": "Charger No.", "width": 60},
        {"x": table_x + 370, "lbl": "Warranty", "width": 60},
        {"x": table_x + 430, "lbl": "Amount", "width": 80}
    ]
    
    c.setFont("Helvetica-Bold", 10)
    for col in cols:
        if col["x"] > table_x:
            if col["lbl"] == "Amount":
                c.line(col["x"], table_bottom, col["x"], table_top)
            else:
                c.line(col["x"], total_row_y, col["x"], table_top)
        c.drawCentredString(col["x"] + (col["width"] / 2), table_top - 17, col["lbl"])
        
    start_y = table_top - header_height - 15
    c.setFont("Helvetica", 10)
    for i, item in enumerate(items):
        y = start_y - (i * row_height)
        c.drawCentredString(cols[0]["x"] + cols[0]["width"]/2, y, str(i + 1))
        c.drawString(cols[1]["x"] + 5, y, item.get('product_name', '')[:22])
        c.drawCentredString(cols[2]["x"] + cols[2]["width"]/2, y, item.get('imei', '-')[:16])
        c.drawCentredString(cols[3]["x"] + cols[3]["width"]/2, y, item.get('battery_num', '-')[:10])
        c.drawCentredString(cols[4]["x"] + cols[4]["width"]/2, y, item.get('charger_num', '-')[:10])
        c.drawCentredString(cols[5]["x"] + cols[5]["width"]/2, y, item.get('warranty', '-')[:8])
        c.drawRightString(cols[6]["x"] + cols[6]["width"] - 15, y, f"{item.get('final_rate', 0.0):.2f}")
        c.line(table_x, y - 10, table_x + table_width, y - 10)
        
    c.setFont("Helvetica-Bold", 10)
    c.drawString(table_x + 5, table_bottom + 8, "In Words :")
    c.setFont("Helvetica", 9)
    c.drawString(table_x + 65, table_bottom + 8, total_words)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(cols[6]["x"] - 10, table_bottom + 8, "Total Payment")
    c.drawRightString(cols[6]["x"] + cols[6]["width"] - 15, table_bottom + 8, f"{total_amount:.2f}")
    
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
