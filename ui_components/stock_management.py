import customtkinter as ctk
import tkinter.messagebox as messagebox
import database

class StockFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        hdr = ctk.CTkLabel(title_frame, text="Stock Management", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(title_frame, text="Track and manage your mobile inventory", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))
        
        # Total Stock Card at top right
        self.stock_summary_card = ctk.CTkFrame(header_frame, corner_radius=15, fg_color=("#ffffff", "#1e1e1e"), border_width=1, border_color=("gray85", "gray20"))
        self.stock_summary_card.pack(side="right", padx=10)
        
        ctk.CTkLabel(self.stock_summary_card, text="Total Stock Count", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(padx=20, pady=(10, 0))
        self.total_stock_lbl = ctk.CTkLabel(self.stock_summary_card, text="0", font=("Helvetica", 24, "bold"), text_color="#f59e0b")
        self.total_stock_lbl.pack(padx=20, pady=(0, 10))

        # Main Layout: Left (Form) and Right (Table)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Left Panel - Add Stock Form
        form_panel = ctk.CTkFrame(content_frame, width=320, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        form_panel.pack(side="left", fill="y", padx=(0, 20))
        form_panel.pack_propagate(False)
        
        ctk.CTkLabel(form_panel, text="➕ Add/Edit Item", font=("Helvetica", 18, "bold"), text_color="#3b82f6").pack(pady=20, padx=25, anchor="w")
        
        ctk.CTkLabel(form_panel, text="Model Name", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(anchor="w", padx=25)
        self.model_entry = ctk.CTkEntry(form_panel, placeholder_text="Model Name", height=45, font=("Helvetica", 14))
        self.model_entry.pack(fill="x", padx=25, pady=(0, 10))
        
        def force_numeric(*args, var=None):
            val = var.get()
            clean = ''.join(c for c in val if c.isdigit() or c == '.')
            if val != clean:
                var.set(clean)

        ctk.CTkLabel(form_panel, text="Quantity", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(anchor="w", padx=25)
        self.var_qty = ctk.StringVar()
        self.var_qty.trace_add("write", lambda *args, v=self.var_qty: force_numeric(var=v))
        self.qty_entry = ctk.CTkEntry(form_panel, placeholder_text="Quantity", height=45, font=("Helvetica", 14), textvariable=self.var_qty)
        self.qty_entry.pack(fill="x", padx=25, pady=(0, 10))
        
        ctk.CTkLabel(form_panel, text="Unit Price (₹)", font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70")).pack(anchor="w", padx=25)
        self.var_price = ctk.StringVar()
        self.var_price.trace_add("write", lambda *args, v=self.var_price: force_numeric(var=v))
        self.price_entry = ctk.CTkEntry(form_panel, placeholder_text="Unit Price (₹)", height=45, font=("Helvetica", 14), textvariable=self.var_price)
        self.price_entry.pack(fill="x", padx=25, pady=(0, 10))
        
        self.add_btn = ctk.CTkButton(form_panel, text="Add to Stock", font=("Helvetica", 16, "bold"), height=50, fg_color="#10b981", hover_color="#059669", command=self.save_stock)
        self.add_btn.pack(fill="x", padx=25, pady=(20, 10))
        
        self.clear_btn = ctk.CTkButton(form_panel, text="Clear Form", font=("Helvetica", 14), height=40, fg_color="transparent", border_width=1, text_color=("gray30", "gray70"), command=self.clear_form)
        self.clear_btn.pack(fill="x", padx=25, pady=5)

        # Right Panel - Stock Table
        table_panel = ctk.CTkFrame(content_frame, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        table_panel.pack(side="right", fill="both", expand=True)
        
        # Search Bar for Table
        search_frame = ctk.CTkFrame(table_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=25, pady=(20, 15))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Search stock by model...", height=40, font=("Helvetica", 14))
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())
        
        # Table Headers
        headers_frame = ctk.CTkFrame(table_panel, fg_color=("gray95", "gray15"), height=40, corner_radius=10)
        headers_frame.pack(fill="x", padx=25, pady=5)
        headers_frame.pack_propagate(False)
        
        cols = [("Model Name", 0.45), ("Qty", 0.2), ("Total Price", 0.2), ("Actions", 0.15)]
        for text, weight in cols:
            lbl = ctk.CTkLabel(headers_frame, text=text, font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70"))
            lbl.place(relx=sum(c[1] for c in cols[:cols.index((text, weight))]) + 0.05, rely=0.5, anchor="w")

        # Scrollable Table Content
        self.scroll_frame = ctk.CTkScrollableFrame(table_panel, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))
        
        self.selected_stock_id = None
        self.refresh_data()

    def refresh_data(self):
        # Clear current rows
        for child in self.scroll_frame.winfo_children():
            child.destroy()
            
        search_term = self.search_entry.get().lower()
        stock_data = database.get_all_stock()
        
        total_q = sum(item[3] for item in stock_data)
        self.total_stock_lbl.configure(text=str(total_q))
        
        for item in stock_data:
            sid, model, imei, qty, price = item
            if search_term and search_term not in model.lower():
                continue
                
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", height=40)
            row.pack(fill="x", pady=2)
            
            # Model Name
            ctk.CTkLabel(row, text=model, font=("Helvetica", 13), anchor="w").place(relx=0.05, rely=0.5, anchor="w", relwidth=0.4)
            
            # Qty with +/- buttons
            qty_frame = ctk.CTkFrame(row, fg_color="transparent")
            qty_frame.place(relx=0.5, rely=0.5, anchor="w", relwidth=0.15)
            
            ctk.CTkButton(qty_frame, text="-", width=20, height=20, font=("Helvetica", 14, "bold"), fg_color="transparent", text_color="gray50", hover_color=("gray85", "gray20"), command=lambda i=sid: self.adjust_qty(i, -1)).pack(side="left")
            qty_color = "#ef4444" if qty <= 2 else ("gray30", "gray70")
            ctk.CTkLabel(qty_frame, text=str(qty), font=("Helvetica", 13, "bold"), text_color=qty_color).pack(side="left", padx=5)
            ctk.CTkButton(qty_frame, text="+", width=20, height=20, font=("Helvetica", 14, "bold"), fg_color="transparent", text_color="gray50", hover_color=("gray85", "gray20"), command=lambda i=sid: self.adjust_qty(i, 1)).pack(side="left")
            
            # Total Price (dynamically adjusted based on qty)
            total_price = qty * price
            price_text = f"₹{total_price:,.2f}"
            ctk.CTkLabel(row, text=price_text, font=("Helvetica", 13)).place(relx=0.7, rely=0.5, anchor="w", relwidth=0.15)
            
            # Actions (Edit/Delete)
            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.place(relx=0.85, rely=0.5, anchor="w", relwidth=0.15)
            
            edit_btn = ctk.CTkButton(action_frame, text="Edit", width=35, height=25, font=("Helvetica", 11), fg_color="transparent", text_color="#3b82f6", hover_color=("gray85", "gray20"), command=lambda i=item: self.load_for_edit(i))
            edit_btn.pack(side="left", padx=2)
            
            del_btn = ctk.CTkButton(action_frame, text="Delete", width=45, height=25, font=("Helvetica", 11), fg_color="transparent", text_color="#ef4444", hover_color="#fee2e2", command=lambda i=sid: self.delete_item(i))
            del_btn.pack(side="left", padx=2)
            
            # Separator
            ctk.CTkFrame(self.scroll_frame, height=1, fg_color=("gray90", "gray20")).pack(fill="x", padx=10)

    def load_for_edit(self, item):
        self.selected_stock_id, model, imei, qty, price = item
        self.model_entry.delete(0, 'end')
        self.model_entry.insert(0, model)
        self.qty_entry.delete(0, 'end')
        self.qty_entry.insert(0, str(qty))
        self.price_entry.delete(0, 'end')
        self.price_entry.insert(0, str(price))
        
        self.add_btn.configure(text="Update Item", fg_color="#3b82f6", hover_color="#2563eb")

    def clear_form(self):
        self.selected_stock_id = None
        self.model_entry.delete(0, 'end')
        self.qty_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.add_btn.configure(text="Add to Stock", fg_color="#10b981", hover_color="#059669")

    def save_stock(self):
        model = self.model_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        price_str = self.price_entry.get().strip()
        
        if not model or not qty_str or not price_str:
            messagebox.showerror("Error", "Model, Quantity and Price are required.")
            return
            
        try:
            qty = int(qty_str)
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number.")
            return
            
        if self.selected_stock_id:
            database.update_stock_item(self.selected_stock_id, model, "", qty, price)
            messagebox.showinfo("Success", "Stock item updated successfully.")
        else:
            database.add_stock(model, "", qty, price)
            messagebox.showinfo("Success", "Stock item added successfully.")
            
        self.clear_form()
        self.refresh_data()

    def delete_item(self, sid):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this stock item?"):
            database.delete_stock_item(sid)
            self.refresh_data()

    def adjust_qty(self, sid, amount):
        # Fetch current stock to find quantity
        stock_data = database.get_all_stock()
        for item in stock_data:
            if item[0] == sid:
                current_qty = item[3]
                new_qty = max(0, current_qty + amount)
                database.update_stock_item(sid, item[1], item[2], new_qty, item[4])
                self.refresh_data()
                break
