import customtkinter as ctk
import sqlite3
import datetime
from database import DB_NAME, get_firms

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        
        text_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_container.pack(side="left")
        
        hdr = ctk.CTkLabel(text_container, text="Dashboard", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(text_container, text="Shop highlights and statistics", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))
        
        # Filter Dropdown
        self.filter_var = ctk.StringVar(value="All Time")
        self.filter_menu = ctk.CTkOptionMenu(header_frame, variable=self.filter_var, 
                                            values=["Today", "This Week", "This Month", "This Year", "All Time"],
                                            command=lambda _: self.refresh_data(),
                                            width=160, height=40, font=("Helvetica", 14, "bold"))
        self.filter_menu.pack(side="right", anchor="s")
        
        # Responsive Metrics Container
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.pack(fill="x", pady=10)
        
        self.sales_card = self.create_metric_card(self.stats_container, "Total Sales", "₹ 0.00", "#10b981")
        self.inv_card = self.create_metric_card(self.stats_container, "Total Bills Count", "0", "#3b82f6")
        
        # Recent Sales Table Card
        self.sales_table_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        self.sales_table_card.pack(fill="both", expand=True, pady=(10, 0))
        
        ctk.CTkLabel(self.sales_table_card, text="📊 Detailed Sales Records", font=("Helvetica", 18, "bold")).pack(anchor="w", padx=25, pady=(25, 10))
        
        # Table Container (Scrollable)
        self.table_container = ctk.CTkScrollableFrame(self.sales_table_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=15, pady=(0, 20))
        
        # Table Headers
        self.create_table_header()
        
        # Firm Details at bottom
        self.create_firm_details_card()

        # Initial layout and binding for responsiveness
        self.bind("<Configure>", self.on_resize)

    def create_table_header(self):
        header_bg = ("#f1f5f9", "#1e1e1e")
        h_frame = ctk.CTkFrame(self.table_container, fg_color=header_bg, height=40, corner_radius=8)
        h_frame.pack(fill="x", pady=(0, 5))
        
        headers = [("Invoice #", 0.2), ("Customer", 0.4), ("Date", 0.2), ("Amount", 0.2)]
        for text, weight in headers:
            lbl = ctk.CTkLabel(h_frame, text=text, font=("Helvetica", 12, "bold"), text_color=("gray40", "gray70"))
            lbl.place(relx=sum([h[1] for h in headers[:headers.index((text, weight))]]), rely=0.5, anchor="w", relwidth=weight)

    def on_resize(self, event=None):
        width = self.winfo_width()
        if width > 600:
            self.stats_container.columnconfigure(0, weight=1)
            self.stats_container.columnconfigure(1, weight=1)
            self.sales_card.grid(row=0, column=0, padx=(0, 10), sticky="ew")
            self.inv_card.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        else:
            self.stats_container.columnconfigure(0, weight=1)
            self.stats_container.columnconfigure(1, weight=0)
            self.sales_card.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
            self.inv_card.grid(row=1, column=0, padx=0, pady=(10, 0), sticky="ew")

    def create_metric_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, corner_radius=18, border_width=1, border_color=("gray85", "gray20"), height=140)
        card.pack_propagate(False)
        
        lbl_title = ctk.CTkLabel(card, text=title, font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70"))
        lbl_title.pack(anchor="w", padx=25, pady=(25, 5))
        
        lbl_val = ctk.CTkLabel(card, text=value, font=("Helvetica", 32, "bold"), text_color=color)
        lbl_val.pack(anchor="w", padx=25)
        
        card.val_label = lbl_val
        return card

    def refresh_data(self):
        try:
            choice = self.filter_var.get()
            now = datetime.datetime.now()
            start_date = None
            
            if choice == "Today":
                start_date = now.strftime("%Y-%m-%d")
            elif choice == "This Week":
                start_date = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            elif choice == "This Month":
                start_date = now.strftime("%Y-%m-01")
            elif choice == "This Year":
                start_date = now.strftime("%Y-01-01")

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # Fetch Totals
            query_total = "SELECT SUM(total_amount), COUNT(invoice_id) FROM Invoices"
            params = []
            if start_date:
                query_total += " WHERE substr(date, 1, 10) >= ?"
                params.append(start_date)
            
            cursor.execute(query_total, params)
            row = cursor.fetchone()
            
            sales = row[0] if row[0] else 0.0
            count = row[1] if row[1] else 0
            
            self.sales_card.val_label.configure(text=f"₹ {sales:,.2f}")
            self.inv_card.val_label.configure(text=str(count))
            
            # Fetch Detailed Records
            query_details = "SELECT i.invoice_number, c.name, i.date, i.total_amount FROM Invoices i JOIN Customers c ON i.customer_id = c.customer_id"
            if start_date:
                query_details += " WHERE substr(i.date, 1, 10) >= ?"
            query_details += " ORDER BY i.date DESC LIMIT 50"
            
            cursor.execute(query_details, params)
            records = cursor.fetchall()
            conn.close()
            
            # Clear current table
            for widget in self.table_container.winfo_children():
                if not isinstance(widget, ctk.CTkFrame) or widget.winfo_height() != 40: # Hack to keep header
                    if widget.winfo_name() != "!ctkframe5": # Better check?
                        pass
            
            # Actually just clear everything except the first child (header)
            widgets = self.table_container.winfo_children()
            for w in widgets[1:]:
                w.destroy()
                
            # Add new rows
            for rec in records:
                row_frame = ctk.CTkFrame(self.table_container, fg_color="transparent", height=35)
                row_frame.pack(fill="x", pady=2)
                
                cols = [0.2, 0.4, 0.2, 0.2]
                for i, val in enumerate(rec):
                    text = f"₹ {val:,.2f}" if i == 3 else str(val)
                    lbl = ctk.CTkLabel(row_frame, text=text, font=("Helvetica", 12), text_color=("gray30", "gray70"))
                    lbl.place(relx=sum(cols[:i]), rely=0.5, anchor="w", relwidth=cols[i])
            
            # Shop info
            firms = get_firms()
            if firms:
                firm_lines = []
                for f in firms:
                    firm_lines.append(f"• {f[1]} | {f[2]} | {f[5]}")
                self.lbl_firm.configure(text="\n".join(firm_lines))
        except Exception as e:
            print(f"Dashboard Refresh Error: {e}")

    def create_firm_details_card(self):
        # Firms Information Card
        self.firm_details_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        self.firm_details_card.pack(fill="x", pady=20)
        
        ctk.CTkLabel(self.firm_details_card, text="📜 Registered Shop Details", font=("Helvetica", 18, "bold")).pack(anchor="w", padx=25, pady=(20, 10))
        
        self.lbl_firm = ctk.CTkLabel(self.firm_details_card, text="Loading shop info...", font=("Helvetica", 14), text_color=("gray50", "gray70"), justify="left")
        self.lbl_firm.pack(pady=(0, 20), padx=25, anchor="w")
