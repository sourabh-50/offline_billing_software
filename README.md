# Premium Billing System (v1.1.0)
### Engineered by Sourabh

A high-performance, offline-first Windows desktop application designed for mobile retail shops and small businesses. This system provides a streamlined billing experience, robust data management, and professional PDF generation.

---

## 🚀 Key Features
- **Dynamic Stock Management**: Real-time total price calculation that updates instantly as you adjust item quantities.
- **Professional PDF Invoicing**: 
  - **Symmetrical Layout**: Perfectly aligned margins and headers for a premium look.
  - **Smart Text Fitting**: Uniform font sizes with intelligent truncation to prevent text overlap.
- **GST-Free Billing**: Optimized for shops that do not require complex tax filing.
- **Modular Branding**: Easily customizable for different clients (Headers/Footers/Icons).
- **Advanced Search & Reports**:
  - **Auto-Clearing Search**: Responsive search bills interface that clears instantly when the query is removed.
  - **Excel Exports**: Auto-adjusting columns for clean accounting.
  - **Merged PDF Backup**: Combine all monthly invoices into a single master PDF.
- **Adaptive UI**: Automatically launches in full-screen mode, adapting to any monitor resolution.
- **Security**: Built-in password protection and hardware-locked licensing.
- **Modern Design**: Theme-aware interface built with CustomTkinter (Light/Dark Mode).

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
Developed by **Sourabh**.
- **Website**: [scalead.in](https://scalead.in)
- **Email**: sourabhshinde5050@gmail.com


