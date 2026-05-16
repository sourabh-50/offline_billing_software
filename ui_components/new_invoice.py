import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import datetime
import os
import database
from pdf_generator import generate_invoice_pdf
from ui_components.autocomplete import ctkAutocompleteEntry
import subprocess
import sys

class NewInvoiceFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 20))
        hdr = ctk.CTkLabel(header_frame, text="Create New Bill", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(header_frame, text="Generate dynamic bill for mobile sales", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))

        self.firm_var = ctk.StringVar()
        self.firms = {}

        # Customer Details Card
        cust_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        cust_card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(cust_card, text="👤 Customer Details", font=("Helvetica", 18, "bold"), text_color="#3b82f6").pack(anchor="w", padx=25, pady=(20, 15))
        
        c_fields = ctk.CTkFrame(cust_card, fg_color="transparent")
        c_fields.pack(fill="x", padx=25, pady=(0, 25))
        
        f_name = ctk.CTkFrame(c_fields, fg_color="transparent")
        f_name.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(f_name, text="Full Name", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(anchor="w")
        self.cust_name = ctk.CTkEntry(f_name, placeholder_text="Full Name", height=45, width=280, font=("Helvetica", 14))
        self.cust_name.pack(fill="x")
        
        f_mobile = ctk.CTkFrame(c_fields, fg_color="transparent")
        f_mobile.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(f_mobile, text="Mobile No.", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(anchor="w")
        self.mobile_var = ctk.StringVar()
        self.mobile_var.trace_add("write", self.limit_mobile_length)
        self.cust_mobile = ctk.CTkEntry(f_mobile, placeholder_text="Mobile No.", height=45, width=200, font=("Helvetica", 14),
                                              textvariable=self.mobile_var)
        self.cust_mobile.pack(fill="x")
        
        f_addr = ctk.CTkFrame(c_fields, fg_color="transparent")
        f_addr.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(f_addr, text="Complete Address", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(anchor="w")
        self.cust_address = ctk.CTkEntry(f_addr, placeholder_text="Complete Address", height=45, font=("Helvetica", 14))
        self.cust_address.pack(fill="x")

        # Dynamic Devices Card
        self.products = []
        dev_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        dev_card.pack(fill="x", pady=15)

        d_header = ctk.CTkFrame(dev_card, fg_color="transparent")
        d_header.pack(fill="x", padx=25, pady=(20, 15))
        ctk.CTkLabel(d_header, text="📱 Mobile Details", font=("Helvetica", 18, "bold"), text_color="#3b82f6").pack(side="left")
        ctk.CTkButton(d_header, text="+ Add Mobile", font=("Helvetica", 13, "bold"), height=35, width=130, command=self.add_product_row).pack(side="right")

        col_frame = ctk.CTkFrame(dev_card, fg_color=("gray95", "gray15"), corner_radius=10)
        col_frame.pack(fill="x", padx=25, pady=5)
        
        col_frame.columnconfigure((0,1,2,3,4,5), weight=1)
        col_frame.columnconfigure(6, weight=0, minsize=50)
        
        headers = ["Model Name", "IMEI No.", "Battery No.", "Charger No.", "Warranty", "Price (₹)", ""]
        for i, text in enumerate(headers):
            ctk.CTkLabel(col_frame, text=text, font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).grid(row=0, column=i, padx=5, pady=10, sticky="w")

        self.prod_rows_frame = ctk.CTkFrame(dev_card, fg_color="transparent")
        self.prod_rows_frame.pack(fill="both", expand=True, padx=20, pady=(0, 25))
        self.add_product_row()

        # Action Area
        action_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        action_card.pack(fill="x", pady=(15, 40))
        
        self.lbl_totals = ctk.CTkLabel(action_card, text="₹ 0.00", font=("Helvetica", 36, "bold"), text_color="#10b981")
        self.lbl_totals.pack(side="left", padx=30, pady=25)

        self.btn_save = ctk.CTkButton(action_card, text="Save & Print Bill", font=("Helvetica", 18, "bold"), height=55, width=300, command=self.save_invoice)
        self.btn_save.pack(side="right", padx=25, pady=25)

    def limit_mobile_length(self, *args):
        value = self.mobile_var.get()
        # Remove non-digits
        clean_value = "".join(filter(str.isdigit, value))
        # Limit to 10 characters
        if len(clean_value) > 10:
            clean_value = clean_value[:10]
        
        if value != clean_value:
            self.mobile_var.set(clean_value)

    def refresh_data(self):
        firms_data = database.get_firms()
        self.firms = {f"{f[1]}": f for f in firms_data}
        if self.firms:
            # Auto-select the first firm (usually only one)
            self.firm_var.set(list(self.firms.keys())[0])
            
        # Initialize suggestions only for products
        # Merge product names from items and stock
        self.stock_map = {s[1]: s for s in database.get_all_stock()}
        historic_names = database.get_all_product_names()
        self.all_product_names = list(set(list(self.stock_map.keys()) + historic_names))
        
        for p in self.products:
            p['model'].set_suggestions(self.all_product_names)

    def get_product_suggestions(self):
        # Dynamically fetch latest names ONLY from stock
        stock_names = [s[1] for s in database.get_all_stock()]
        return list(set(stock_names))

    def add_product_row(self):
        row_frame = ctk.CTkFrame(self.prod_rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        row_frame.columnconfigure((0,1,2,3,4,5), weight=1)
        row_frame.columnconfigure(6, weight=0, minsize=50)
        
        args = {"font": ("Helvetica", 13), "height": 40}
        p_model = ctkAutocompleteEntry(row_frame, placeholder_text="Model", suggestions_callback=self.get_product_suggestions, **args)
        p_model.grid(row=0, column=0, padx=2, sticky="ew")
        
        def force_upper(*args, var=None):
            val = var.get()
            if any(c.islower() for c in val):
                var.set(val.upper())
                
        def force_numeric(*args, var=None):
            val = var.get()
            clean = ''.join(c for c in val if c.isdigit() or c == '.')
            if val != clean:
                var.set(clean)

        var_imei = ctk.StringVar()
        var_imei.trace_add("write", lambda *args, v=var_imei: force_upper(var=v))
        p_imei = ctk.CTkEntry(row_frame, placeholder_text="IMEI", textvariable=var_imei, **args)
        p_imei.grid(row=0, column=1, padx=2, sticky="ew")
        
        var_batt = ctk.StringVar()
        var_batt.trace_add("write", lambda *args, v=var_batt: force_upper(var=v))
        p_batt = ctk.CTkEntry(row_frame, placeholder_text="Batt #", textvariable=var_batt, **args)
        p_batt.grid(row=0, column=2, padx=2, sticky="ew")
        
        var_chg = ctk.StringVar()
        var_chg.trace_add("write", lambda *args, v=var_chg: force_upper(var=v))
        p_chg = ctk.CTkEntry(row_frame, placeholder_text="Chg #", textvariable=var_chg, **args)
        p_chg.grid(row=0, column=3, padx=2, sticky="ew")
        
        p_war = ctk.CTkEntry(row_frame, placeholder_text="6m / 1y", **args)
        p_war.grid(row=0, column=4, padx=2, sticky="ew")
        
        var_price = ctk.StringVar()
        var_price.trace_add("write", lambda *args, v=var_price: force_numeric(var=v))
        p_price = ctk.CTkEntry(row_frame, placeholder_text="Price", textvariable=var_price, **args)
        p_price.grid(row=0, column=5, padx=2, sticky="ew")
        
        def remove_me():
            if len(self.products) > 1:
                row_frame.destroy()
                self.products = [p for p in self.products if p['frame'] != row_frame]
                self.update_totals()
            
        rm_btn = ctk.CTkButton(row_frame, text="✖", width=40, height=40, fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", command=remove_me)
        rm_btn.grid(row=0, column=6, padx=(5, 0), sticky="e")
        
        def on_product_select(event):
            name = p_model.get()
            if name in self.stock_map:
                stock_item = self.stock_map[name]
                # sid, model, imei, qty, price
                if not p_imei.get():
                    p_imei.insert(0, stock_item[2] or "")
                if not p_price.get():
                    p_price.insert(0, str(stock_item[4]))
                self.update_totals()

        p_model.bind("<<AutocompleteSelected>>", on_product_select)
        p_price.bind("<KeyRelease>", lambda e: self.update_totals())

        self.products.append({
            'frame': row_frame,
            'model': p_model, 'imei': p_imei, 'batt': p_batt,
            'chg': p_chg, 'war': p_war, 'price': p_price
        })

    def update_totals(self):
        subtotal = 0.0
        for p in self.products:
            try:
                rate = float(p['price'].get() or 0.0)
                subtotal += rate
            except ValueError:
                pass
        
        self.lbl_totals.configure(text=f"₹ {subtotal:,.2f}")
        return subtotal

    def save_invoice(self):
        if not self.cust_name.get().strip():
            messagebox.showerror("Error", "Customer name is required.")
            return
        
        mobile = self.cust_mobile.get().strip()
        if mobile and len(mobile) != 10:
            messagebox.showerror("Error", "Mobile number must be exactly 10 digits.")
            return

        pdf_dir = database.get_setting("pdf_storage_path")
        if not pdf_dir or not os.path.isdir(pdf_dir):
            messagebox.showinfo("Select Folder", "Please select where you want to save your bills.")
            selected_dir = filedialog.askdirectory(title="Select Folder for PDF Storage")
            if not selected_dir: return
            database.set_setting("pdf_storage_path", selected_dir)
            pdf_dir = selected_dir

        firm_key = self.firm_var.get()
        firm_data = self.firms[firm_key]
        firm_id = firm_data[0]
        
        gross_total = self.update_totals()

        items = []
        for p in self.products:
            try:
                r = float(p['price'].get() or 0.0)
                if p['model'].get().strip():
                    items.append({
                        "product_name": p['model'].get().strip(),
                        "imei": p['imei'].get().strip() or "-",
                        "battery_num": p['batt'].get().strip() or "-",
                        "charger_num": p['chg'].get().strip() or "-",
                        "warranty": p['war'].get().strip() or "-",
                        "quantity": 1,
                        "price": r,
                        "discount": 0.0,
                        "final_rate": r,
                        "hsn": ""
                    })
            except ValueError:
                messagebox.showerror("Error", "Check price values in mobile details.")
                return

        if not items:
            messagebox.showerror("Error", "No mobile details entered.")
            return

        customer_id = database.get_or_create_customer(self.cust_name.get(), self.cust_mobile.get(), self.cust_address.get())
        invoice_num = database.get_next_invoice_number(firm_id)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_inv = invoice_num.replace('/', '_')
        pdf_path = os.path.abspath(os.path.join(pdf_dir, f"{safe_inv}.pdf"))

        database.create_invoice(
            invoice_num, firm_id, customer_id, date_str[:10],
            gross_total, 0.0, 0.0, gross_total, pdf_path, {}, items
        )

        # Call the generator from pdf_generator.py
        generate_invoice_pdf(
            pdf_path, firm_data[1], firm_data[2], firm_data[3], invoice_num, date_str[:10],
            self.cust_name.get(), self.cust_mobile.get(), self.cust_address.get(),
            items, gross_total, 0.0, 0.0, gross_total
        )

        messagebox.showinfo("Success", f"Bill Saved Successfully!\nSaved at: {pdf_path}")
        
        if os.name == 'nt':
            os.startfile(pdf_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, pdf_path])

        self.cust_name.delete(0, 'end')
        self.cust_mobile.delete(0, 'end')
        self.cust_address.delete(0, 'end')
        for p in self.products:
            p['frame'].destroy()
        self.products.clear()
        self.add_product_row()
        self.update_totals()

