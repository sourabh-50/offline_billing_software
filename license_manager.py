import os
import sqlite3
import hashlib
import uuid
import subprocess
import platform

DB_NAME = "database.db"

def get_hardware_id():
    """Generates a unique hardware ID based on MAC address and system info to bind the software to the PC."""
    mac = uuid.getnode()
    system_info = platform.node() + platform.system() + platform.machine()
    raw_id = f"{mac}-{system_info}"
    return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()

def verify_license_key(hw_id, key):
    """Verifies that the provided license key is valid for the hardware ID.
    The secret salt here must match the key generator."""
    SECRET_SALT = "OmSaiDevLock2026_PremiumBilling"
    expected_key = hashlib.sha256((hw_id + SECRET_SALT).encode()).hexdigest()[:20].upper()
    return key == expected_key

def is_software_activated():
    """Checks if the database has a valid license key stored for this PC."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS License (key TEXT)")
        cursor.execute("SELECT key FROM License LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            saved_key = row[0]
            hw_id = get_hardware_id()
            return verify_license_key(hw_id, saved_key)
        return False
    except Exception:
        return False

def activate_software(key):
    """Activates the software if the key is valid."""
    hw_id = get_hardware_id()
    if verify_license_key(hw_id, key):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS License (key TEXT)")
        cursor.execute("DELETE FROM License")
        cursor.execute("INSERT INTO License (key) VALUES (?)", (key,))
        conn.commit()
        conn.close()
        return True
    return False
