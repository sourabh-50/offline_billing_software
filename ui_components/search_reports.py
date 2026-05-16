import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import os
import subprocess
import database
import exporter
from ui_components.autocomplete import ctkAutocompleteEntry
from datetime import datetime, timedelta
import backup_service

class SearchFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        
        hdr = ctk.CTkLabel(header_frame, text="Search Saved Bills", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(header_frame, text="Find and open your saved shop bills", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))
        
        search_bar = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        search_bar.pack(fill="x", pady=(0, 15))
        
        self.entry_query = ctk.CTkEntry(search_bar, placeholder_text="Search by Name, Mobile, or ID...", width=450, height=45, font=("Helvetica", 14))
        self.entry_query.pack(side="left", padx=25, pady=20)
        self.entry_query.bind("<Return>", lambda e: self.do_search())
        self.entry_query.bind("<KeyRelease>", lambda e: self.on_search_typing())
        
        self.search_btn = ctk.CTkButton(search_bar, text="Search", font=("Helvetica", 14, "bold"), height=45, width=150, command=self.do_search)
        self.search_btn.pack(side="left", padx=(0, 25), pady=20)

        # High-Contrast Table Container
        table_container = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        table_container.pack(fill="both", expand=True, pady=10)
        
        cols = ("Bill No", "Customer", "Date", "Amount")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=150, anchor="center")
            
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.results_data = []

    def update_table_style(self):
        mode = ctk.get_appearance_mode()
        bg_col = "#1e1e1e" if mode == "Dark" else "#ffffff"
        fg_col = "#ffffff" if mode == "Dark" else "#000000"
        head_bg = "#2d2d2d" if mode == "Dark" else "#f1f5f9"
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=bg_col, 
                        foreground=fg_col, 
                        fieldbackground=bg_col, 
                        rowheight=45,
                        font=("Helvetica", 11),
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background=head_bg, 
                        foreground=fg_col, 
                        font=("Helvetica", 12, "bold"),
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#3b82f6')], foreground=[('selected', '#ffffff')])

        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.results_data = []

    def on_search_typing(self):
        if not self.entry_query.get().strip():
            self.tree.delete(*self.tree.get_children())
            self.results_data = []

    def do_search(self):
        self.update_table_style()
        query = self.entry_query.get()
        self.results_data = database.search_invoices(query)
        self.tree.delete(*self.tree.get_children())
        for row in self.results_data:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"₹ {row[3]:,.2f}"))

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item: return
        item_idx = self.tree.index(item[0])
        pdf_path = self.results_data[item_idx][4]
        
        if os.path.exists(pdf_path):
            if os.name == 'nt':
                os.startfile(pdf_path)
            else:
                import sys
                subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", pdf_path])
        else:
            messagebox.showerror("Error", f"Bill file not found:\n{pdf_path}")

class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        
        hdr = ctk.CTkLabel(header_frame, text="Sales Reports", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(header_frame, text="Configure and export your sales intelligence", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))
        
        config_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        config_card.pack(fill="x", pady=(10, 20))
        
        # Centered Input Grid
        inputs_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        inputs_frame.pack(pady=40, padx=40)
        
        # Timeline Dropdown
        ctk.CTkLabel(inputs_frame, text="Select Period:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).grid(row=0, column=0, padx=15, sticky="e")
        self.report_tl_var = ctk.StringVar(value="Select Period")
        
        # Container for date inputs (managed by dropdown)
        self.date_inputs_frame = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        
        # Year Input Frame (for Custom Year)
        self.year_input_frame = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        self.year_var = ctk.StringVar(value=str(datetime.now().year))
        self.year_var.trace_add("write", lambda *args: self.validate_buttons())
        ctk.CTkLabel(self.year_input_frame, text="Enter Year:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        self.year_entry = ctk.CTkEntry(self.year_input_frame, width=100, height=45, font=("Helvetica", 14), textvariable=self.year_var)
        self.year_entry.pack(side="left")

        def on_report_tl_change(choice):
            if choice == "Custom Range":
                self.date_inputs_frame.grid(row=0, column=2, columnspan=2, sticky="w")
                self.year_input_frame.grid_remove()
            elif choice == "Custom Year":
                self.year_input_frame.grid(row=0, column=2, sticky="w")
                self.date_inputs_frame.grid_remove()
            else:
                self.date_inputs_frame.grid_remove()
                self.year_input_frame.grid_remove()
            self.validate_buttons()
                
        self.report_tl_menu = ctk.CTkOptionMenu(inputs_frame, variable=self.report_tl_var, 
                                               values=["Today", "This Week", "This Month", "This Year", "Custom Year", "Custom Range"],
                                               command=on_report_tl_change, width=200, height=45, font=("Helvetica", 14))
        self.report_tl_menu.grid(row=0, column=1, padx=15, sticky="w")
        
        # Date Inputs inside the sub-frame
        ctk.CTkLabel(self.date_inputs_frame, text="Start Date:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        s_frame = ctk.CTkFrame(self.date_inputs_frame, fg_color="transparent")
        s_frame.pack(side="left", padx=5)
        
        self.start_var = ctk.StringVar()
        self.start_var.trace_add("write", lambda *args: self.validate_buttons())
        self.start_cal = ctkAutocompleteEntry(s_frame, width=150, height=45, placeholder_text="YYYY-MM-DD", textvariable=self.start_var)
        self.start_cal.pack(side="left")
        ctk.CTkButton(s_frame, text="📅", width=45, height=45, font=("Helvetica", 18), command=lambda: self.open_calendar(self.start_cal)).pack(side="left", padx=(5,0))
        
        ctk.CTkLabel(self.date_inputs_frame, text="End Date:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        e_frame = ctk.CTkFrame(self.date_inputs_frame, fg_color="transparent")
        e_frame.pack(side="left", padx=5)
        
        self.end_var = ctk.StringVar()
        self.end_var.trace_add("write", lambda *args: self.validate_buttons())
        self.end_cal = ctkAutocompleteEntry(e_frame, width=150, height=45, placeholder_text="YYYY-MM-DD", textvariable=self.end_var)
        self.end_cal.pack(side="left")
        ctk.CTkButton(e_frame, text="📅", width=45, height=45, font=("Helvetica", 18), command=lambda: self.open_calendar(self.end_cal)).pack(side="left", padx=(5,0))
        
        self.setup_date_suggestions()
        self.start_cal.bind("<KeyRelease>", lambda e: self.auto_format_date(self.start_cal), add="+")
        self.end_cal.bind("<KeyRelease>", lambda e: self.auto_format_date(self.end_cal), add="+")

        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", pady=20)
        btns_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btns_frame.pack(anchor="center")
        
        self.excel_btn = ctk.CTkButton(btns_frame, text="📦 Export to Excel", font=("Helvetica", 16, "bold"), fg_color="#10b981", hover_color="#059669", height=55, width=220, command=self.export_excel)
        self.excel_btn.pack(side="left", padx=10)
        
        self.pdf_btn = ctk.CTkButton(btns_frame, text="📄 Export to PDF", font=("Helvetica", 16, "bold"), fg_color="#3b82f6", hover_color="#2563eb", height=55, width=220, command=self.export_pdf)
        self.pdf_btn.pack(side="left", padx=10)
        
        # Initial validation to ensure buttons are locked on start
        self.after(100, self.validate_buttons)

    def open_calendar(self, entry_widget):
        try:
            from tkcalendar import Calendar
        except ImportError:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", "tkcalendar module is not installed.")
            return

        top = ctk.CTkToplevel(self)
        top.title("Select Date")
        # Position relative to entry
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        top.geometry(f"300x320+{x}+{y}")
        top.resizable(False, False)
        top.attributes('-topmost', True)
        top.transient(self.winfo_toplevel()) # Keep it on top of the main window
        
        # Set icon for the calendar window
        try:
            if os.path.exists("assets/app_icon.ico"):
                top.after(200, lambda: top.iconbitmap("assets/app_icon.ico"))
        except:
            pass

        # Add a border frame for aesthetics
        container = ctk.CTkFrame(top, corner_radius=10)
        container.pack(fill="both", expand=True, padx=2, pady=2)

        cal = Calendar(container, selectmode='day', date_pattern='y-mm-dd')
        cal.pack(padx=10, pady=(10, 5), fill="both", expand=True)

        def set_date(event=None):
            date_str = cal.get_date()
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, date_str)
            top.destroy()
            
        cal.bind("<<CalendarSelected>>", set_date)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Select", width=120, height=35, command=set_date).pack(side="left", padx=(20, 10), pady=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, height=35, fg_color="transparent", border_width=1, command=top.destroy).pack(side="left", padx=(10, 20), pady=10)

        # Modal behavior
        top.grab_set()
        top.focus_set()

    def setup_date_suggestions(self):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        first_day = today.replace(day=1)
        
        suggestions = [
            today.strftime("%Y-%m-%d"),
            yesterday.strftime("%Y-%m-%d"),
            first_day.strftime("%Y-%m-%d"),
            (first_day - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d"), # Last month start
        ]
        self.start_cal.set_suggestions(suggestions)
        self.end_cal.set_suggestions(suggestions)
        # Clear entries to force manual selection or suggestion pick
        self.start_cal.delete(0, 'end')
        self.end_cal.delete(0, 'end')

    def auto_format_date(self, widget):
        val = widget.get().replace("-", "")
        if len(val) >= 8:
            formatted = f"{val[:4]}-{val[4:6]}-{val[6:8]}"
            if widget.get() != formatted:
                widget.delete(0, 'end')
                widget.insert(0, formatted)

    def get_active_range(self):
        choice = self.report_tl_var.get()
        now = datetime.now()
        s, e = "", ""
        
        if choice == "Today":
            s = e = now.strftime("%Y-%m-%d")
        elif choice == "This Week":
            s = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            e = now.strftime("%Y-%m-%d")
        elif choice == "This Month":
            s = now.strftime("%Y-%m-01")
            e = now.strftime("%Y-%m-%d")
        elif choice == "This Year":
            s = now.strftime("%Y-01-01")
            e = now.strftime("%Y-%m-%d")
        elif choice == "Custom Year":
            y = self.year_var.get().strip()
            if len(y) == 4 and y.isdigit():
                s = f"{y}-01-01"
                e = f"{y}-12-31"
        elif choice == "Custom Range":
            s = self.start_cal.get().strip()
            e = self.end_cal.get().strip()
            # Basic validation against placeholder
            if s == "YYYY-MM-DD" or e == "YYYY-MM-DD":
                s = e = ""
                
        return s, e

    def validate_buttons(self):
        s, e = self.get_active_range()
        if s and e:
            self.excel_btn.configure(state="normal")
            self.pdf_btn.configure(state="normal")
        else:
            self.excel_btn.configure(state="disabled")
            self.pdf_btn.configure(state="disabled")

    def export_excel(self):
        try:
            s, e = self.get_active_range()
            if not s or not e:
                messagebox.showwarning("Selection Required", "Please select a timeline or enter a valid Start and End date.")
                return
            path = os.path.join(database.BASE_DIR, "reports", f"Sales_{s}_to_{e}.xlsx")
            exporter.export_sales_excel(s, e, path)
            messagebox.showinfo("Success", f"Excel report saved to:\n{path}")
            
            # Auto-open the generated file
            if os.path.exists(path):
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    import sys
                    subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", path])
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def export_pdf(self):
        try:
            s, e = self.get_active_range()
            if not s or not e:
                messagebox.showwarning("Selection Required", "Please select a timeline or enter a valid Start and End date.")
                return
            path = os.path.join(database.BASE_DIR, "reports", f"Sales_{s}_to_{e}.pdf")
            exporter.export_sales_pdf(s, e, path)
            messagebox.showinfo("Success", f"PDF report saved to:\n{path}")
            
            # Auto-open the generated file
            if os.path.exists(path):
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    import sys
                    subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", path])
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

class BackupFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 20))
        
        hdr = ctk.CTkLabel(header_frame, text="Data Backup", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(header_frame, text="Export your sales data and merged bill records", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))
        
        config_card = ctk.CTkFrame(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        config_card.pack(fill="x", pady=15)
        
        # Centered Input Grid
        inputs_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        inputs_frame.pack(pady=40, padx=40)
        
        # Timeline Dropdown
        ctk.CTkLabel(inputs_frame, text="Select Period:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).grid(row=0, column=0, padx=15, sticky="e")
        self.backup_tl_var = ctk.StringVar(value="Select Period")
        
        # Container for date inputs (managed by dropdown)
        self.date_inputs_frame = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        
        # Year Input Frame (for Custom Year)
        self.year_input_frame = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        self.year_var = ctk.StringVar(value=str(datetime.now().year))
        self.year_var.trace_add("write", lambda *args: self.validate_buttons())
        ctk.CTkLabel(self.year_input_frame, text="Enter Year:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        self.year_entry = ctk.CTkEntry(self.year_input_frame, width=100, height=45, font=("Helvetica", 14), textvariable=self.year_var)
        self.year_entry.pack(side="left")

        def on_backup_tl_change(choice):
            if choice == "Custom Range":
                self.date_inputs_frame.grid(row=0, column=2, columnspan=2, sticky="w")
                self.year_input_frame.grid_remove()
            elif choice == "Custom Year":
                self.year_input_frame.grid(row=0, column=2, sticky="w")
                self.date_inputs_frame.grid_remove()
            else:
                self.date_inputs_frame.grid_remove()
                self.year_input_frame.grid_remove()
            self.validate_buttons()
                
        self.backup_tl_menu = ctk.CTkOptionMenu(inputs_frame, variable=self.backup_tl_var, 
                                               values=["Today", "This Week", "This Month", "This Year", "Custom Year", "Custom Range", "All Time"],
                                               command=on_backup_tl_change, width=200, height=45, font=("Helvetica", 14))
        self.backup_tl_menu.grid(row=0, column=1, padx=15, sticky="w")
        
        # Date Inputs inside the sub-frame
        ctk.CTkLabel(self.date_inputs_frame, text="Start Date:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        s_frame = ctk.CTkFrame(self.date_inputs_frame, fg_color="transparent")
        s_frame.pack(side="left", padx=5)
        
        self.start_var = ctk.StringVar()
        self.start_var.trace_add("write", lambda *args: self.validate_buttons())
        self.start_cal = ctkAutocompleteEntry(s_frame, width=150, height=45, placeholder_text="YYYY-MM-DD", textvariable=self.start_var)
        self.start_cal.pack(side="left")
        ctk.CTkButton(s_frame, text="📅", width=45, height=45, font=("Helvetica", 18), command=lambda: self.open_calendar(self.start_cal)).pack(side="left", padx=(5,0))
        
        ctk.CTkLabel(self.date_inputs_frame, text="End Date:", font=("Helvetica", 14, "bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        e_frame = ctk.CTkFrame(self.date_inputs_frame, fg_color="transparent")
        e_frame.pack(side="left", padx=5)
        
        self.end_var = ctk.StringVar()
        self.end_var.trace_add("write", lambda *args: self.validate_buttons())
        self.end_cal = ctkAutocompleteEntry(e_frame, width=150, height=45, placeholder_text="YYYY-MM-DD", textvariable=self.end_var)
        self.end_cal.pack(side="left")
        ctk.CTkButton(e_frame, text="📅", width=45, height=45, font=("Helvetica", 18), command=lambda: self.open_calendar(self.end_cal)).pack(side="left", padx=(5,0))
        
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(15, 40))
        btns_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btns_frame.pack(anchor="center")
        
        self.excel_btn = ctk.CTkButton(btns_frame, text="📊 Excel Backup", font=("Helvetica", 16, "bold"), fg_color="#10b981", hover_color="#059669", height=55, width=220, command=self.do_excel_backup)
        self.excel_btn.pack(side="left", padx=10)
        
        self.pdf_btn = ctk.CTkButton(btns_frame, text="📁 Merged PDF Backup", font=("Helvetica", 16, "bold"), fg_color="#3b82f6", hover_color="#2563eb", height=55, width=220, command=self.do_pdf_backup)
        self.pdf_btn.pack(side="left", padx=10)
        
        self.after(100, self.validate_buttons)

    def open_calendar(self, entry_widget):
        try:
            from tkcalendar import Calendar
        except ImportError:
            messagebox.showerror("Error", "tkcalendar module is not installed.")
            return

        top = ctk.CTkToplevel(self)
        top.title("Select Date")
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        top.geometry(f"300x320+{x}+{y}")
        top.resizable(False, False)
        top.attributes('-topmost', True)
        top.transient(self.winfo_toplevel())
        
        container = ctk.CTkFrame(top, corner_radius=10)
        container.pack(fill="both", expand=True, padx=2, pady=2)
        cal = Calendar(container, selectmode='day', date_pattern='y-mm-dd')
        cal.pack(padx=10, pady=(10, 5), fill="both", expand=True)

        def set_date(event=None):
            date_str = cal.get_date()
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, date_str)
            top.destroy()
            
        cal.bind("<<CalendarSelected>>", set_date)
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Select", width=120, height=35, command=set_date).pack(side="left", padx=(20, 10), pady=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, height=35, fg_color="transparent", border_width=1, command=top.destroy).pack(side="left", padx=(10, 20), pady=10)
        top.grab_set()

    def get_active_range(self):
        choice = self.backup_tl_var.get()
        now = datetime.now()
        s, e = "", ""
        
        if choice == "Today":
            s = e = now.strftime("%Y-%m-%d")
        elif choice == "This Week":
            s = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            e = now.strftime("%Y-%m-%d")
        elif choice == "This Month":
            s = now.strftime("%Y-%m-01")
            e = now.strftime("%Y-%m-%d")
        elif choice == "This Year":
            s = now.strftime("%Y-01-01")
            e = now.strftime("%Y-%m-%d")
        elif choice == "All Time":
            s = "2000-01-01"
            e = "2099-12-31"
        elif choice == "Custom Year":
            y = self.year_var.get().strip()
            if len(y) == 4 and y.isdigit():
                s = f"{y}-01-01"
                e = f"{y}-12-31"
        elif choice == "Custom Range":
            s = self.start_var.get().strip()
            e = self.end_var.get().strip()
            if s == "YYYY-MM-DD" or e == "YYYY-MM-DD":
                s = e = ""
        return s, e

    def validate_buttons(self):
        s, e = self.get_active_range()
        if s and e:
            self.excel_btn.configure(state="normal")
            self.pdf_btn.configure(state="normal")
        else:
            self.excel_btn.configure(state="disabled")
            self.pdf_btn.configure(state="disabled")

    def do_excel_backup(self):
        tl = self.backup_tl_var.get()
        s, e = self.get_active_range()
        import tkinter.filedialog as filedialog
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"Backup_{tl}_{s}.xlsx", title="Save Excel Backup", filetypes=[("Excel files", "*.xlsx")])
        if not save_path: return
        
        try:
            final_path = backup_service.export_timeline_backup(tl, save_path, s, e)
            backup_service.create_backup()
            messagebox.showinfo("Success", f"Backup saved successfully!\n{final_path}")
            if os.path.exists(final_path):
                if os.name == 'nt':
                    os.startfile(os.path.dirname(final_path))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def do_pdf_backup(self):
        tl = self.backup_tl_var.get()
        s, e = self.get_active_range()
        import tkinter.filedialog as filedialog
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Full_PDF_Backup_{tl}.pdf", title="Save Merged PDF", filetypes=[("PDF files", "*.pdf")])
        if not save_path: return
        
        try:
            final_path = backup_service.export_pdf_merged(tl, save_path, s, e)
            messagebox.showinfo("Success", f"Merged PDF saved successfully!\n{final_path}")
            if os.path.exists(final_path):
                if os.name == 'nt':
                    os.startfile(os.path.dirname(final_path))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
