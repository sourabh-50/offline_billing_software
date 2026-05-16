import customtkinter as ctk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import qrcode
import os
import ctypes
import sys

import config
from database import is_auth_setup, setup_auth, verify_auth, init_db, remove_auth
from ui_components.dashboard import DashboardFrame
from ui_components.new_invoice import NewInvoiceFrame
from ui_components.search_reports import SearchFrame, ReportsFrame
from ui_components.settings_page import SettingsFrame
from ui_components.stock_management import StockFrame
import backup_service
import license_manager

import sys
from utils import get_asset_path

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Enable Taskbar Icon on Windows - Must be called early
try:
    if os.name == 'nt':
        myappid = 'scalead.billingsystem.omsai.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(f"{config.APP_NAME} v{config.VERSION}")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.minsize(1000, 700)
        
        if os.name == 'nt':
            # Defer zoomed state so it isn't overridden by window manager
            self.after(0, lambda: self.state('zoomed'))
        
        # Set App Icon
        try:
            icon_path_png = get_asset_path("assets/app_icon.png")
            icon_path_ico = get_asset_path("assets/app_icon.ico")
            
            if os.path.exists(icon_path_png):
                self.logo_pil = Image.open(icon_path_png)
                # Keep reference to prevent garbage collection
                self.icon_photo = ImageTk.PhotoImage(self.logo_pil.resize((256, 256)))
                self.iconphoto(True, self.icon_photo)
            
            if os.name == 'nt' and os.path.exists(icon_path_ico):
                self.after(200, lambda: self.iconbitmap(icon_path_ico))
        except Exception as e:
            print(f"Icon Load Error: {e}")
            
        init_db()

        self.container = ctk.CTkFrame(self, fg_color=("#f1f5f9", "#000000"))
        self.container.pack(fill="both", expand=True)
        
        if not license_manager.is_software_activated():
            self.show_activation_screen()
        elif not is_auth_setup():
            # If no password setup, go direct to dashboard
            self.show_main_screen()
        else:
            self.show_login_screen()

    def show_activation_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        act_frame = ctk.CTkFrame(self.container, corner_radius=25, border_width=1, border_color=("gray85", "gray20"))
        act_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_lbl = ctk.CTkLabel(act_frame, text="🛡️ Software Activation", font=("Helvetica", 32, "bold"))
        title_lbl.pack(pady=(50, 10), padx=60)
        
        hw_id = license_manager.get_hardware_id()
        info_lbl = ctk.CTkLabel(act_frame, text="This software is locked to this machine.\nPlease provide this ID to your vendor to unlock.", 
                                font=("Helvetica", 15), text_color=("gray50", "gray70"))
        info_lbl.pack(pady=(0, 30), padx=60)
        
        hw_box = ctk.CTkEntry(act_frame, width=380, height=55, justify="center", font=("Courier", 18, "bold"))
        hw_box.insert(0, hw_id)
        hw_box.configure(state="readonly")
        hw_box.pack(pady=10)
        
        def copy_hw():
            self.clipboard_clear()
            self.clipboard_append(hw_id)
            messagebox.showinfo("Copied", "ID copied to clipboard!")
            
        copy_btn = ctk.CTkButton(act_frame, text="Copy ID", width=180, height=45, font=("Helvetica", 14, "bold"), command=copy_hw)
        copy_btn.pack(pady=(0, 40))
        
        key_entry = ctk.CTkEntry(act_frame, width=380, height=50, placeholder_text="Enter Activation Key", font=("Helvetica", 15))
        key_entry.pack(pady=10)
        
        def on_activate():
            val = key_entry.get().strip()
            if license_manager.activate_software(val):
                messagebox.showinfo("Success", "Software Unlocked. Welcome.")
                if not is_auth_setup():
                    self.show_main_screen()
                else:
                    self.show_login_screen()
            else:
                messagebox.showerror("Error", "Invalid Activation Key.")
        
        btn = ctk.CTkButton(act_frame, text="Unlock Now", font=("Helvetica", 16, "bold"), width=380, height=50, command=on_activate)
        btn.pack(pady=(25, 50))

    def show_login_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        login_frame = ctk.CTkFrame(self.container, corner_radius=25, border_width=1, border_color=("gray85", "gray20"))
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_lbl = ctk.CTkLabel(login_frame, text="Login Securely", font=("Helvetica", 32, "bold"))
        title_lbl.pack(pady=(50, 10), padx=80)
        
        desc_lbl = ctk.CTkLabel(login_frame, text="Enter your password to start billing.", font=("Helvetica", 15), text_color=("gray50", "gray70"))
        desc_lbl.pack(pady=(0, 35), padx=80)
        
        pwd_entry = ctk.CTkEntry(login_frame, show="*", width=320, placeholder_text="Password", height=50, font=("Helvetica", 15))
        pwd_entry.pack(pady=10)
        pwd_entry.focus()
        
        def on_login():
            pwd = pwd_entry.get()
            if verify_auth(pwd):
                self.show_main_screen()
            else:
                messagebox.showerror("Denied", "Incorrect password.")
                
        btn = ctk.CTkButton(login_frame, text="Login", command=on_login, font=("Helvetica", 16, "bold"), width=320, height=50)
        btn.pack(pady=(35, 60))
        
        self.bind('<Return>', lambda event: on_login())

    def create_scalead_qr(self):
        qr_dir = "assets"
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
        
        data = "https://scalead.in"
        
        try:
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgPathImage
            svg_img = qrcode.make(data, image_factory=factory)
            svg_img.save(os.path.join(qr_dir, "qr_code.svg"))
        except:
            pass

        def gen_transparent_png(fill_color, back_color, filename):
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
            datas = img.getdata()
            newData = []
            bg_rgb = (255, 255, 255) if back_color == "white" else (0, 0, 0)
            for item in datas:
                if item[0:3] == bg_rgb:
                    newData.append((bg_rgb[0], bg_rgb[1], bg_rgb[2], 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            path = os.path.join(qr_dir, filename)
            img.save(path)
            return path

        light_path = gen_transparent_png("black", "white", "qr_light.png")
        dark_path = gen_transparent_png("white", "black", "qr_dark.png")
        return light_path, dark_path

    def show_main_screen(self):
        self.unbind('<Return>')
        for widget in self.container.winfo_children():
            widget.destroy()

        sidebar = ctk.CTkFrame(self.container, width=280, corner_radius=0, border_width=0)
        sidebar.pack(side="left", fill="y")
        
        # Logo and Title
        try:
            logo_img = ctk.CTkImage(light_image=self.logo_pil, dark_image=self.logo_pil, size=(80, 80))
            logo_img_lbl = ctk.CTkLabel(sidebar, image=logo_img, text="")
            logo_img_lbl.pack(pady=(40, 0))
        except:
            pass
            
        logo_lbl = ctk.CTkLabel(sidebar, text=config.SIDEBAR_NAME, font=("Helvetica", 32, "bold"), text_color="#ef4444")
        logo_lbl.pack(pady=(10, 5), padx=20)
        sub_logo = ctk.CTkLabel(sidebar, text="Mobile Billing Software", font=("Helvetica", 14), text_color=("gray50", "gray70"))
        sub_logo.pack(pady=(0, 40))

        self.main_area = ctk.CTkFrame(self.container, corner_radius=25, fg_color=("#f8fafc", "#09090b"), border_width=1, border_color=("gray85", "gray20"))
        self.main_area.pack(side="right", fill="both", expand=True, padx=25, pady=25)

        self.frames = {}
        self.nav_buttons = {}
        
        buttons = [
            ("Home", "Dashboard"), 
            ("New Bill", "New Invoice"), 
            ("Stock", "Stock"),
            ("Search Bills", "Search"), 
            ("Reports", "Reports"), 
            ("Backup", "Backup"),
            ("Settings", "Settings")
        ]
        
        for text, key in buttons:
            btn = ctk.CTkButton(sidebar, text=f"  {text}", font=("Helvetica", 17, "bold"), fg_color="transparent", 
                                text_color=("gray30", "gray70"), hover_color=("gray85", "gray20"), anchor="w", corner_radius=12,
                                height=58, command=lambda k=key: self.show_frame(k))
            btn.pack(fill="x", pady=5, padx=25)
            self.nav_buttons[key] = btn
            
        # 🏁 Footer Frame for Credits
        footer_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=20)
            
        dev_lbl = ctk.CTkLabel(footer_frame, text="DEVELOPED BY ScaleAd", font=("Helvetica", 11, "bold"), text_color="gray50")
        dev_lbl.pack()

        # Initialize Frames
        self.frames["Dashboard"] = DashboardFrame(self.main_area)
        self.frames["New Invoice"] = NewInvoiceFrame(self.main_area)
        self.frames["Stock"] = StockFrame(self.main_area)
        self.frames["Search"] = SearchFrame(self.main_area)
        self.frames["Reports"] = ReportsFrame(self.main_area)
        self.frames["Settings"] = SettingsFrame(self.main_area, self)

        self.show_frame("Dashboard")

    def show_frame(self, name):
        if name == "Backup":
            self.run_backup()
            return

        for b_name, btn in self.nav_buttons.items():
            if b_name == name:
                btn.configure(fg_color=("#3b82f6", "#ffffff"), text_color=("#ffffff", "#000000"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray30", "gray70"))
            
        for child in self.main_area.winfo_children():
            child.pack_forget()
            
        frame = self.frames[name]
        frame.pack(fill="both", expand=True)
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()

    def run_backup(self):
        modal = ctk.CTkToplevel(self)
        modal.title("System Backup")
        modal.geometry("480x380")
        modal.attributes('-topmost', True)
        
        # Set icon for the modal window
        try:
            if hasattr(self, 'icon_photo'):
                modal.iconphoto(True, self.icon_photo)
            if os.path.exists("assets/app_icon.ico"):
                modal.after(200, lambda: modal.iconbitmap("assets/app_icon.ico"))
        except:
            pass

        modal.grab_set()         
        ctk.CTkLabel(modal, text="Data Backup", font=("Helvetica", 24, "bold")).pack(pady=(40, 10))
        ctk.CTkLabel(modal, text="Select which records to export:", font=("Helvetica", 15), text_color=("gray50", "gray70")).pack(pady=(0, 35))
        
        timeline_var = ctk.StringVar(value="Select Timeline")
        
        # Container for custom dates
        custom_dates_frame = ctk.CTkFrame(modal, fg_color="transparent")
        
        start_date_var = ctk.StringVar()
        end_date_var = ctk.StringVar()
        custom_year_var = ctk.StringVar(value=str(datetime.datetime.now().year))
        
        def on_timeline_change(choice):
            custom_dates_frame.pack_forget()
            custom_year_frame.pack_forget()
            if choice == "Custom Range":
                custom_dates_frame.pack(pady=10)
                modal.geometry("480x520")
            elif choice == "Custom Year":
                custom_year_frame.pack(pady=10)
                modal.geometry("480x450")
            else:
                modal.geometry("480x380")
        
        dropdown = ctk.CTkOptionMenu(modal, variable=timeline_var, values=["Today", "This Week", "This Month", "This Year", "Custom Year", "All Time", "Custom Range"], 
                                    width=300, height=50, font=("Helvetica", 15), command=on_timeline_change)
        dropdown.pack(pady=10)
        
        # Setup Custom Year Input
        custom_year_frame = ctk.CTkFrame(modal, fg_color="transparent")
        ctk.CTkLabel(custom_year_frame, text="Year:", font=("Helvetica", 14, "bold")).pack(side="left", padx=10)
        ctk.CTkEntry(custom_year_frame, width=150, height=40, textvariable=custom_year_var).pack(side="left", padx=5)
        
        # Setup Custom Date Inputs
        row1 = ctk.CTkFrame(custom_dates_frame, fg_color="transparent")
        row1.pack(pady=5)
        ctk.CTkLabel(row1, text="From:", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
        start_ent = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=150, textvariable=start_date_var)
        start_ent.pack(side="left", padx=5)
        
        row2 = ctk.CTkFrame(custom_dates_frame, fg_color="transparent")
        row2.pack(pady=5)
        ctk.CTkLabel(row2, text="To:", font=("Helvetica", 12, "bold")).pack(side="left", padx=15)
        end_ent = ctk.CTkEntry(row2, placeholder_text="YYYY-MM-DD", width=150, textvariable=end_date_var)
        end_ent.pack(side="left", padx=5)
        
        def process_excel_backup():
            tl = timeline_var.get()
            if tl == "Select Timeline":
                messagebox.showwarning("Selection Required", "Please select a backup timeline.")
                return
                
            s = start_date_var.get()
            e = end_date_var.get()
            cy = custom_year_var.get().strip()
            
            if tl == "Custom Range" and (not s or not e):
                messagebox.showwarning("Input Required", "Please enter both Start and End dates for Custom Range.")
                return
            if tl == "Custom Year" and not cy:
                messagebox.showwarning("Input Required", "Please enter a valid year.")
                return

            import tkinter.filedialog as filedialog
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"Bills_Backup_{tl.replace(' ','_')}.xlsx", title="Save Excel Backup", filetypes=[("Excel files", "*.xlsx")])
            if not save_path:
                return
            
            try:
                # If custom year, we can just set s and e here or handle in service
                if tl == "Custom Year":
                    s = f"{cy}-01-01"
                    e = f"{cy}-12-31"
                    
                final_path = backup_service.export_timeline_backup(tl, save_path, s, e)
                backup_service.create_backup()
                messagebox.showinfo("Success", f"Excel backup saved to:\n{final_path}")
                modal.destroy()
            except ValueError as e:
                messagebox.showwarning("No Data", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def process_pdf_backup():
            tl = timeline_var.get()
            if tl == "Select Timeline":
                messagebox.showwarning("Selection Required", "Please select a backup timeline.")
                return
                
            s = start_date_var.get()
            e = end_date_var.get()
            cy = custom_year_var.get().strip()
            
            if tl == "Custom Range" and (not s or not e):
                messagebox.showwarning("Input Required", "Please enter both Start and End dates for Custom Range.")
                return
            if tl == "Custom Year" and not cy:
                messagebox.showwarning("Input Required", "Please enter a valid year.")
                return

            import tkinter.filedialog as filedialog
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Full_PDF_Backup_{tl.replace(' ','_')}.pdf", title="Save Merged PDF", filetypes=[("PDF files", "*.pdf")])
            if not save_path:
                return
            
            try:
                if tl == "Custom Year":
                    s = f"{cy}-01-01"
                    e = f"{cy}-12-31"
                    
                final_path = backup_service.export_pdf_merged(tl, save_path, s, e)
                messagebox.showinfo("Success", f"Merged PDF saved to:\n{final_path}")
                modal.destroy()
            except ValueError as e:
                messagebox.showwarning("No Data", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ctk.CTkButton(modal, text="Start Excel Backup", font=("Helvetica", 16, "bold"), width=300, height=50, command=process_excel_backup).pack(pady=(25, 10))
        ctk.CTkButton(modal, text="Start PDF Backup (Merged PDF)", font=("Helvetica", 16, "bold"), fg_color="#3b82f6", hover_color="#2563eb", width=300, height=50, command=process_pdf_backup).pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
