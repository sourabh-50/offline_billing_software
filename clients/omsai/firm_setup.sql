-- Firm Setup for Omsai Mobile Shopee
-- Use this script to initialize the database for this specific client.

DELETE FROM Firms;

INSERT INTO Firms (firm_name, gst_number, address, contact, invoice_prefix)
VALUES (
    'Om Sai Mobile Shopee', 
    'N/A', 
    'Your Shop Address Here', 
    '9876543210', 
    'OM'
);

-- Note: The images for this client are in clients/omsai/
-- Copy header_img.png and footer_img.png to the root folder before building.
