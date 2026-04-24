import hashlib

def generate_key(hw_id):
    SECRET_SALT = "OmSaiDevLock2026_PremiumBilling"
    key = hashlib.sha256((hw_id + SECRET_SALT).encode()).hexdigest()[:20].upper()
    return key

if __name__ == "__main__":
    print("==================================================")
    print("   ScaleAd Premium Billing - LICENSE GENERATOR")
    print("==================================================")
    hw_id = input("\nEnter the Hardware ID from the Client's Laptop: ").strip()
    if hw_id:
        final_key = generate_key(hw_id)
        print(f"\nSUCCESS! The Activation Key for this client is:\n")
        print(f">>> {final_key} <<<\n")
        print("==================================================")
    else:
        print("Error: Hardware ID cannot be empty.")
    input("\nPress Enter to close...")
