import hashlib

def generate_key(hw_id):
    """
    Generate an activation key for a given Hardware ID.
    The secret salt here MUST match the one in license_manager.py
    """
    SECRET_SALT = "OmSaiDevLock2026_PremiumBilling"
    key = hashlib.sha256((hw_id + SECRET_SALT).encode()).hexdigest()[:20].upper()
    return key

if __name__ == "__main__":
    print("=== Omsai Billing Software Key Generator ===")
    hw_id = input("Enter Customer's Machine ID: ").strip()
    if hw_id:
        key = generate_key(hw_id)
        print("-" * 40)
        print(f"Activation Key: {key}")
        print("-" * 40)
    else:
        print("Error: Machine ID cannot be empty.")
