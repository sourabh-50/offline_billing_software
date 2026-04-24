# ScaleAd Premium Billing System - Engineering Documentation

## 1. Project Overview
This is a high-performance, offline-first billing system designed for mobile retail shops. It is built using Python, CustomTkinter (UI), and SQLite (Database).

## 2. Technical Stack
- **GUI**: `customtkinter` (Modern Tkinter wrapper)
- **Database**: `sqlite3` (Embedded)
- **PDF Generation**: `reportlab` & `pypdf` (for merging)
- **Excel Export**: `openpyxl`
- **Build Tool**: `PyInstaller`

## 3. Directory Structure
- `app.py`: Main entry point and window management.
- `config.py`: Centralized app settings (Version, Name, Colors).
- `database.py`: All SQL logic and DB schema.
- `pdf_generator.py`: Invoice layout and PDF styling.
- `backup_service.py`: Excel exports and PDF archival logic.
- `utils.py`: Cross-platform path handling.
- `ui_components/`: Modular UI frames (Dashboard, Search, Settings).
- `assets/`: App icons and QR codes.

## 4. White-Labeling & Customization
To customize this app for a specific client:
1.  **App Name/Version**: Edit `config.py`.
2.  **Branding**: Replace `header_img.png` and `footer_img.png` in the root or via the app's Branding tab.
3.  **App Icon**: Replace `assets/app_icon.ico` and `assets/app_icon.png`.

## 5. Maintenance Revenue Model (Firm Management)
The UI **does not** allow clients to change their Firm/Shop name, GST, or Address. This ensures they must contact you (ScaleAd) for updates.
**To add or change a Shop/Firm:**
- Open `database.db` using a SQLite browser (or code).
- Insert/Update the `Firms` table.
- Example SQL:
  ```sql
  INSERT INTO Firms (firm_name, gst_number, address, contact, invoice_prefix)
  VALUES ('Omsai Mobile', '27AAAAA0000A1Z5', 'Shop No 1, Main Road', '9876543210', 'OM');
  ```

## 6. Build & Deployment
Use the included `build_app.bat`:
1.  Ensure Python is installed.
2.  Run `pip install -r requirements.txt`.
3.  Double-click `build_app.bat`.
4.  The final app will be in `dist/Premium Billing System/`.

**Windows 7 Support**: If the client is on Windows 7, you **must** build the app using Python 3.8.

## 7. Multi-Client Management (White-Labeling)
The repository is structured to support multiple clients using the same core engine.
- **Core Engine**: The main files in the root are generic.
- **Client Profiles**: Stored in the `clients/` directory.
- **To Setup a New Client:**
    1. Create a new folder in `clients/name/`.
    2. Add their specific `header_img.png` and `footer_img.png`.
    3. Create a `firm_setup.sql` to initialize their shop name and details in the DB.
    4. Copy their images to the root and edit `config.py` with their specific app name before running `build_app.bat`.
