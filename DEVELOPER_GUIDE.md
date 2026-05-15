# 🚀 Master Developer & Deployment Guide
### Offline Billing Software v1.1.0

This guide is your "source of truth" for building, customizing, and maintaining the software manually.

---

## 🛠️ Section 1: Technical Architecture
To manage the software yourself, you need to understand where the "brain" is:

1.  **`config.py`**: This is the heart of the white-labeling. 
    *   `APP_NAME`: Controls the window title.
    *   `SIDEBAR_NAME`: Controls the vertical text on the sidebar.
    *   `SHOP_NAME`: Controls the "About" page and the default shop name in the database.
2.  **`database.py`**:
    *   The `init_db()` function uses `config.SHOP_NAME` to set up the first firm.
    *   If you change the shop name in `config.py`, you **MUST** delete the old `database.db` file so it can recreate itself with the new name.
3.  **`ui_components/new_invoice.py`**:
    *   Contains the **Mobile Number Restriction**. It uses a `trace_add` on a `StringVar` to delete any characters over 10 or any non-numeric input instantly.

---

## 🏗️ Section 2: Building the "Single-File" EXE
We use **PyInstaller** in "One-File" mode so you don't have to deal with DLL errors.

### The Manual Command:
Open your terminal in the project folder and run:
```powershell
python -m PyInstaller --noconfirm MobileShopBiller.spec
```

### Why use the `.spec` file?
The `MobileShopBiller.spec` file contains instructions to bundle your `assets`, `header_img.png`, and `footer_img.png` inside the EXE. If you add new images or folders, you must add them to the `datas=[]` list in this file.

---

## 🤖 Section 3: AI Prompts for Future Changes
If I am not around, you can copy-paste these prompts into any AI (ChatGPT, Claude, etc.) to get instant code help:

### Prompt 1: Adding a new field to the Bill
> "I am working on a Python CustomTkinter billing app. In `ui_components/new_invoice.py`, I want to add a new input field for 'Discount Percentage' next to the Price field. It should automatically update the Total when the user types. Here is the current code: [Paste new_invoice.py code]"

### Prompt 2: Changing the Branding Logic
> "I want to change how the sidebar logo looks. In `app.py`, find the `sidebar_label` and help me change the font to 'Roboto' and make it bold. Also, ensure it pulls the name from `config.py`. [Paste app.py code]"

### Prompt 3: Fixing a "DLL Not Found" error
> "I built my app with PyInstaller, but when I run it, it says 'python313.dll not found.' I want to convert my `MobileShopBiller.spec` file from 'One-Directory' to 'One-File' mode so it becomes a single portable EXE. Help me modify the spec file."

---

## 📦 Section 4: The "Super Deploy" Workflow
If you want to build a new version for a client called "NewShop":
1.  Create `clients/NewShop/` and put `header_img.png` and `footer_img.png` there.
2.  Run `super_deploy.bat`.
3.  Answer the prompts.
4.  Grab the `.exe` from `dist/Client_Packages/NewShop/`.
5.  **Important**: Before giving it to the client, delete the `database.db` file in that folder so it starts fresh for them.

---

## 🛡️ Troubleshooting
*   **App won't open**: Check if `database.db` is corrupted. Delete it and try again.
*   **Images missing in PDF**: Ensure `header_img.png` is in the same folder as the `.exe` (The `super_deploy.bat` does this for you).
*   **Window too big**: Change `self.geometry("1000x750")` in `app.py`.
