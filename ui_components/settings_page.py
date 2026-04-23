import customtkinter as ctk
import tkinter.messagebox as messagebox
import database
import datetime
import os
import sys
import subprocess

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        
        hdr = ctk.CTkLabel(header_frame, text="System Settings", font=("Helvetica", 32, "bold"))
        hdr.pack(anchor="w")
        sub_hdr = ctk.CTkLabel(header_frame, text="Configure your branding, security, and appearance", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_hdr.pack(anchor="w", pady=(5, 0))

        # Main Tabbed Container
        self.tabview = ctk.CTkTabview(self, corner_radius=18, border_width=1, border_color=("gray85", "gray20"))
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("About")
        self.tabview.add("Security")
        self.tabview.add("Maintenance")
        self.tabview.add("Appearance")
        
        self.setup_about_tab()
        self.setup_security_tab()
        self.setup_maintenance_tab()
        self.setup_appearance_tab()

    def setup_about_tab(self):
        tab = self.tabview.tab("About")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 1. Shop Details
        shop_lbl = ctk.CTkLabel(container, text="Om Sai Mobile Shopee", font=("Helvetica", 32, "bold"), text_color="#ef4444")
        shop_lbl.pack(pady=(10, 5))
        tag_lbl = ctk.CTkLabel(container, text="Billing & Inventory System", font=("Helvetica", 16), text_color="gray50")
        tag_lbl.pack(pady=(0, 20))
        
        ctk.CTkFrame(container, height=1, fg_color=("gray85", "gray20")).pack(fill="x", pady=10)
        
        # 2. Development Credits
        credits_lbl = ctk.CTkLabel(container, text="Developed & Engineered By", font=("Helvetica", 14, "bold"), text_color="gray60")
        credits_lbl.pack(pady=(10, 5))
        
        # 3. Compact ScaleAd Section
        sa_frame = ctk.CTkFrame(container, corner_radius=15, border_width=1, border_color=("gray85", "gray20"))
        sa_frame.pack(fill="x", pady=10, padx=10)
        
        sa_title = ctk.CTkLabel(sa_frame, text="ScaleAd", font=("Helvetica", 24, "bold"), text_color="#3b82f6")
        sa_title.pack(pady=(15, 5))
        sa_tag = ctk.CTkLabel(sa_frame, text="Digital Growth Agency | scalead.in", font=("Helvetica", 13, "italic"), text_color="gray50")
        sa_tag.pack(pady=(0, 15))
        
        sa_desc = ctk.CTkLabel(sa_frame, text="Providing high-performance Web & App Development, SEO, and Performance Marketing solutions to businesses worldwide.\n\nLooking for a customized system? We can build, modify, or engineer any ERP, CRM, or Billing Software exactly as per your unique requirements.", 
                               font=("Helvetica", 12), wraplength=450, text_color=("gray30", "gray70"))
        sa_desc.pack(pady=(0, 15))

        # 4. QR Code integration inside About
        try:
            from PIL import Image
            lp, dp = self.app.create_scalead_qr()
            l_img = Image.open(lp)
            d_img = Image.open(dp)
            qr_image = ctk.CTkImage(light_image=l_img, dark_image=d_img, size=(120, 120))
            qr_label = ctk.CTkLabel(sa_frame, image=qr_image, text="")
            qr_label.pack(pady=(10, 20))
        except:
            pass
            
        footer = ctk.CTkLabel(container, text="Version 1.0.0 © 2026", font=("Helvetica", 11), text_color="gray40")
        footer.pack(pady=0)

    def setup_security_tab(self):
        tab = self.tabview.tab("Security")
        
        card = ctk.CTkFrame(tab, corner_radius=15, border_width=1, border_color=("gray85", "gray20"))
        card.pack(pady=50, padx=50, fill="x")
        
        ctk.CTkLabel(card, text="Password Management", font=("Helvetica", 22, "bold")).pack(pady=(30, 20))
        
        # Change Password
        cp_frame = ctk.CTkFrame(card, fg_color="transparent")
        cp_frame.pack(pady=10)
        
        self.new_pwd = ctk.CTkEntry(cp_frame, placeholder_text="Enter New Password", show="*", width=300, height=45)
        self.new_pwd.pack(side="left", padx=10)
        
        ctk.CTkButton(cp_frame, text="Update Password", width=150, height=45, command=self.update_pwd).pack(side="left", padx=10)
        
        # Remove Password
        ctk.CTkLabel(card, text="Dangerous Zone", font=("Helvetica", 14, "bold"), text_color="red").pack(pady=(40, 10))
        
        def remove_pwd():
            if messagebox.askyesno("Confirm", "Are you sure you want to REMOVE password protection?\nThis will allow anyone to open the app directly."):
                database.remove_auth()
                messagebox.showinfo("Success", "Password Protection Disabled.")
                # We don't force reload, but it will affect next restart
                
        ctk.CTkButton(card, text="Remove Password Protection", fg_color="transparent", border_width=1, border_color="red", 
                      text_color="red", hover_color="#fee2e2", width=300, height=45, command=remove_pwd).pack(pady=(0, 40))

    def update_pwd(self):
        pwd = self.new_pwd.get()
        if len(pwd) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters.")
            return
        database.setup_auth(pwd)
        messagebox.showinfo("Success", "Password Updated Successfully!")
        self.new_pwd.delete(0, 'end')

    def setup_maintenance_tab(self):
        tab = self.tabview.tab("Maintenance")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text="Data Cleanup & Optimization", font=("Helvetica", 22, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(container, text="Delete old records to keep the system fast and clean.", font=("Helvetica", 14), text_color="gray50").pack(pady=(0, 30))
        
        card = ctk.CTkFrame(container, corner_radius=15, border_width=1, border_color=("gray85", "gray20"))
        card.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(card, text="Select Cleanup Range:", font=("Helvetica", 16, "bold")).pack(pady=(25, 10))
        
        self.clean_range = ctk.StringVar(value="Last Week")
        range_dropdown = ctk.CTkOptionMenu(card, variable=self.clean_range, 
                                          values=["Last Week", "Last Month", "Last Year", "All Data", "Custom Range"],
                                          width=350, height=45, font=("Helvetica", 14), command=self.on_range_change)
        range_dropdown.pack(pady=10)
        
        # Custom Date Range Frame (hidden by default)
        self.custom_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        self.start_date_ent = ctk.CTkEntry(self.custom_frame, placeholder_text="Start: YYYY-MM-DD", width=165, height=40)
        self.start_date_ent.pack(side="left", padx=5)
        
        self.end_date_ent = ctk.CTkEntry(self.custom_frame, placeholder_text="End: YYYY-MM-DD", width=165, height=40)
        self.end_date_ent.pack(side="left", padx=5)
        
        # Desktop Shortcut Card
        sc_card = ctk.CTkFrame(container, corner_radius=15, border_width=1, border_color=("gray85", "gray20"))
        sc_card.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(sc_card, text="Quick Access", font=("Helvetica", 16, "bold")).pack(pady=(25, 10))
        
        ctk.CTkButton(sc_card, text="Create Desktop Shortcut", fg_color="transparent", border_width=1,
                      text_color=("gray20", "gray80"), font=("Helvetica", 14), width=350, height=45, 
                      command=self.create_desktop_shortcut).pack(pady=(0, 25))

        # Action Button
        self.clean_btn = ctk.CTkButton(card, text="Permanently Clear Selected Data", fg_color="#ef4444", hover_color="#dc2626",
                                      text_color="white", font=("Helvetica", 15, "bold"), width=350, height=50, command=self.perform_cleanup)
        self.clean_btn.pack(pady=(30, 40))

    def on_range_change(self, val):
        if val == "Custom Range":
            self.custom_frame.pack(pady=10)
        else:
            self.custom_frame.pack_forget()

    def perform_cleanup(self):
        choice = self.clean_range.get()
        now = datetime.datetime.now()
        start_date = ""
        end_date = None
        
        if choice == "Last Week":
            start_date = (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        elif choice == "Last Month":
            start_date = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        elif choice == "Last Year":
            start_date = (now - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        elif choice == "All Data":
            start_date = "1900-01-01"
        elif choice == "Custom Range":
            start_date = self.start_date_ent.get().strip()
            end_date = self.end_date_ent.get().strip()
            if not start_date:
                messagebox.showerror("Error", "Please enter at least a start date.")
                return

        # Double Confirmation
        if not messagebox.askyesno("⚠️ DANGER ZONE", f"Are you sure you want to PERMANENTLY DELETE records for {choice}?\n\nThis cannot be undone and will also delete associated PDF files."):
            return
            
        if not messagebox.askyesno("Final Confirmation", "FINAL WARNING: Are you absolutely certain? This is the last chance to cancel."):
            return
            
        try:
            count = database.clear_records_by_date(start_date, end_date)
            if count > 0:
                messagebox.showinfo("Success", f"Cleanup complete. {count} records and their files were deleted.")
                # Update dashboard if open
                if "Dashboard" in self.app.frames:
                    self.app.frames["Dashboard"].refresh_data()
            else:
                messagebox.showinfo("No Data", "No records found within the selected range.")
        except Exception as e:
            messagebox.showerror("Error", f"Cleanup failed: {e}")

    def create_desktop_shortcut(self):
        try:
            # Determine path to the executable or script
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller Bundle
                target = sys.executable
                icon_path = target
            else:
                # Running as Script
                target = os.path.abspath("app.py")
                icon_path = os.path.abspath("assets/app_icon.ico")

            shortcut_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "Omsai Billing Software.lnk")
            
            # PowerShell script to create the shortcut
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{target}'
            $Shortcut.IconLocation = '{icon_path}'
            $Shortcut.WorkingDirectory = '{os.path.dirname(target)}'
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            messagebox.showinfo("Success", "Desktop shortcut created successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create shortcut: {e}")

    def setup_appearance_tab(self):
        tab = self.tabview.tab("Appearance")
        
        card = ctk.CTkFrame(tab, corner_radius=15, border_width=1, border_color=("gray85", "gray20"))
        card.pack(pady=50, padx=50, fill="x")
        
        ctk.CTkLabel(card, text="Theme Settings", font=("Helvetica", 22, "bold")).pack(pady=(30, 20))
        
        def change_mode(new_mode):
            ctk.set_appearance_mode(new_mode)
            if hasattr(self.app, 'mode_toggle'):
                self.app.mode_toggle.set(new_mode)
            # Refresh treeview styles across app
            if "Search" in self.app.frames:
                self.app.frames["Search"].update_table_style()

        ctk.CTkLabel(card, text="Select Preferred Mode:", font=("Helvetica", 14), text_color="gray50").pack(pady=5)
        
        seg_btn = ctk.CTkSegmentedButton(card, values=["Light", "Dark", "System"], command=change_mode, width=400, height=50)
        seg_btn.set(ctk.get_appearance_mode())
        seg_btn.pack(pady=(10, 50))
