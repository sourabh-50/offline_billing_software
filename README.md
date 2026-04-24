# Premium Billing System (v1.1.0)
### Engineered by Sourabh in association with ScaleAd

A high-performance, offline-first Windows desktop application designed for mobile retail shops and small businesses. This system provides a streamlined billing experience, robust data management, and professional PDF generation.

---

## 🚀 Key Features
- **GST-Free Billing**: Optimized for shops that do not require complex tax filing.
- **Modular Branding**: Easily customizable for different clients (Headers/Footers/Icons).
- **Dynamic Invoicing**: Support for multiple items, IMEI tracking, and automatic totals.
- **Smart Reports**:
  - **Excel Exports**: Auto-adjusting columns for clean accounting.
  - **Merged PDF Backup**: Combine all monthly invoices into a single master PDF.
- **Security**: Built-in password protection and hardware-locked licensing.
- **Cross-Platform Core**: Optimized for Windows 7, 10, and 11.
- **Modern UI**: Theme-aware interface (Light/Dark Mode).

---

## 🛠️ For Engineers (White-Labeling)
This repository uses a **Modular Client Architecture**. The core engine is generic, while client-specific assets are stored in the `clients/` directory.

### To Deploy for a Specific Client:
1.  **Prepare Assets**: Add the client's `header_img.png` and `footer_img.png` to `clients/client_name/`.
2.  **Initialize Data**: Use the provided SQL templates to set the shop's name and prefix in the database.
3.  **Run Deployer**: 
    - Double-click `deploy_client.bat`.
    - Enter the client name.
    - The finished, branded app will be waiting in `dist/Client_Packages/client_name`.

---

## 📦 Build Instructions
1.  Install Python (3.8 for Win7, 3.11+ for Win10/11).
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Build generic: `build_app.bat`.
4.  Build client-specific: `deploy_client.bat`.

---

## 📞 Support & Customization
Developed by **ScaleAd Digital Growth Agency**.
- **Website**: [scalead.in](https://scalead.in)
- **Email**: sourabhshinde5050@gmail.com

*Scale your business with professional digital infrastructure.*
