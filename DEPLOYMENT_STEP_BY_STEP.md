# 🚀 Step-by-Step Deployment Guide: From Code to Client Laptop

This guide is designed for anyone (even non-technical users) to build and install this software for any business. Follow these 5 phases in order.

---

## 🟢 PHASE 1: Branding (The Visuals)
Before you build the app, you need the client's logo and branding ready.

1.  **Open the `clients` folder** in your project.
2.  **Create a new folder** named after your client (e.g., `mahesh_mobile`).
3.  **Prepare 2 Images**:
    - `header_img.png`: This goes at the top of the bill (1200x400 pixels is best).
    - `footer_img.png`: This goes at the bottom (1200x800 pixels is best).
4.  **Place these 2 images** inside your new client folder (`clients/mahesh_mobile/`).

---

## 🔵 PHASE 2: Database Setup (The Shop Info)
You need to tell the software which shop it belongs to.

1.  **Open `clients/omsai/firm_setup.sql`** to use as a template.
2.  **Copy the code** and change the details (Shop Name, Address, Contact).
3.  **To Apply the Info**:
    - Open the `database.db` file using a tool like **DB Browser for SQLite** (Free).
    - Go to the "Execute SQL" tab.
    - Paste your code and hit the "Play" button.
    - Click **Write Changes** at the top.

---

## 🟡 PHASE 3: The One-Click Build
Now, let's turn the code into a Windows application.

1.  **Run the script**: Double-click the file named `deploy_client.bat`.
2.  **Enter the Name**: A black window will appear. Type your client folder name (e.g., `mahesh_mobile`) and press **Enter**.
3.  **Wait**: The computer will work for about 1-2 minutes.
4.  **Find the Result**: When it finishes, go to the folder:
    `dist \ Client_Packages \ mahesh_mobile`
    
**Congratulations!** This folder contains the "Portable" version of the app. You can copy this folder to any laptop and it will work.

---

## 🟠 PHASE 4: Creating a "Real App" Installer (Optional but Professional)
If you want a single "Setup.exe" file (like a real app), follow these steps:

1.  **Download & Install**: [Inno Setup](https://jrsoftware.org/isdl.php) (It's free).
2.  **Open the Script**: Open the file `installer_script.iss` in this project using Inno Setup.
3.  **Adjust the Path**: Find **Line 26** and change `omsai` to your current client's name (e.g., `mahesh_mobile`).
4.  **Build**: Click the **"Compile"** button (looks like a play button) in Inno Setup.
5.  **Get the Setup File**: Your professional installer will be waiting in:
    `dist \ Installers \ BillingSystem_Setup.exe`

---

## 🔴 PHASE 5: Installation on the Client's Laptop
Now, you need to get the app onto the client's machine.

### Method A: Using AnyDesk (Best for Remote Support)
1.  Connect to the client's laptop.
2.  Open the **File Transfer** tool in AnyDesk.
3.  Upload the `BillingSystem_Setup.exe` (from Phase 4) or the entire ZIP of your build folder (from Phase 3) to their Desktop.
4.  **On their laptop**: Double-click the file and follow the "Next, Next, Install" steps.

### Method B: Using Google Drive / WeTransfer
1.  Upload your `BillingSystem_Setup.exe` to Google Drive.
2.  Send the link to the client.
3.  Ask them to download and run it.

---

## 🏁 FINAL CHECKLIST BEFORE DELIVERY
- [ ] Does the "New Bill" screen show the **correct Shop Name**?
- [ ] Does the printed PDF show the **correct Header/Footer**?
- [ ] Did you set a **Password** in the Security tab?
- [ ] Is the app **Activated**? (Use the Hardware ID to generate a key).

**Support Tip**: Always keep a copy of the client's `database.db` and their `clients/name/` folder on your own PC so you can help them if they lose their data!
