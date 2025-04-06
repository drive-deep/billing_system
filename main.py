import os
import json
from datetime import datetime
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox

# Company Metadata
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

COMPANY_NAME = config["COMPANY"]["NAME"]
COMPANY_GST = config["COMPANY"]["GST"]
COMPANY_ADDRESS = config["COMPANY"]["ADDRESS"]
MOBILE_NUMBER = config["COMPANY"]["MOBILE"]

BANK_ACCOUNT = config["BANK"]["ACCOUNT"]
IFSC_CODE = config["BANK"]["IFSC"]
BANK_NAME = config["BANK"]["BANK_NAME"]
BRANCH_NAME = config["BANK"]["BRANCH"]

# Global list to store items
items = []

# Function to generate invoice
def generate_invoice(bill_no, customer_name, customer_address, items):
    if not items:
        messagebox.showerror("Error", "No items added to the invoice!")
        return None

    subtotal = sum(item['price'] * item['quantity'] for item in items)
    gst_amount = sum((item['price'] * item['quantity'] * item['gst_rate']) / 100 for item in items)
    cgst_amount = sum((item['price'] * item['quantity'] * item['cgst_rate']) / 100 for item in items)
    total_amount = subtotal + gst_amount + cgst_amount

    invoice = {
        "bill_no": bill_no,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_name": customer_name,
        "customer_address": customer_address,
        "items": items,
        "subtotal": subtotal,
        "gst_amount": gst_amount,
        "cgst_amount": cgst_amount,
        "total_amount": total_amount
    }
    return invoice

# Function to save invoice as PDF
def save_invoice_as_pdf(invoice):
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join("bills", date_str)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"invoice_{invoice['bill_no']}.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 20)
    pdf.cell(190, 10, COMPANY_NAME, ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(190, 6, f"GSTIN: {COMPANY_GST}", ln=True, align='C')
    pdf.cell(190, 6, COMPANY_ADDRESS, ln=True, align='C')
    pdf.cell(190, 6, f"Phone: {MOBILE_NUMBER}", ln=True, align='C')

    pdf.ln(5)

    # Invoice Title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "TAX INVOICE", ln=True, align='C')

    pdf.ln(5)

    # Bill Details
    pdf.set_font("Arial", size=11)
    pdf.cell(100, 8, f"Bill No: {invoice['bill_no']}", ln=False)
    pdf.cell(90, 8, f"Date: {invoice['date']}", ln=True)
    pdf.cell(190, 8, f"Customer Name: {invoice['customer_name']}", ln=True)
    pdf.multi_cell(190, 8, f"Customer Address: {invoice['customer_address']}")

    pdf.ln(5)

    # Table Headers
    pdf.set_font("Arial", "B", 11)
    col_widths = [40, 25, 25, 25, 25, 40]
    headers = ["Item", "Price", "Qty", "GST (%)", "CGST (%)", "Total"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", size=10)
    for item in invoice["items"]:
        total_price = item['price'] * item['quantity'] + \
                      (item['price'] * item['quantity'] * item['gst_rate']) / 100 + \
                      (item['price'] * item['quantity'] * item['cgst_rate']) / 100

        row = [
            item["name"],
            f"{item['price']:.2f}",
            f"{item['quantity']}",
            f"{item['gst_rate']:.2f}",
            f"{item['cgst_rate']:.2f}",
            f"{total_price:.2f}"
        ]
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 8, cell, border=1, align='C')
        pdf.ln()

    pdf.ln(5)

    pdf.set_font("Arial", size=12)

    y_position = pdf.get_y()

    pdf.set_xy(10, y_position)
    pdf.multi_cell(90, 8,
        "Bank Details:\n"
        f"Bank Name: {BANK_NAME}\n"
        f"A/C Number: {BANK_ACCOUNT}\n"
        f"IFSC Code: {IFSC_CODE}\n"
        f"Branch: {BRANCH_NAME}\n",
        border=1
    )

    pdf.set_xy(110, y_position)
    pdf.multi_cell(90, 8,
        f"Invoice Summary:\n"
        f"Invoice No: {invoice['bill_no']}\n"
        f"Date: {invoice['date']}\n"
        f"Total Amount: Rs. {invoice['total_amount']:.2f}\n",
        border=1
    )

    pdf.set_y(max(pdf.get_y(), y_position + 40))

    pdf.ln(15)

    pdf.set_font("Arial", "I", 9)
    pdf.cell(190, 6, "This is a computer-generated invoice and does not require a signature.", ln=True, align='C')

    pdf.output(file_path)
    messagebox.showinfo("Invoice", f"Invoice saved as {file_path}")

# Tkinter GUI setup
def add_row():
    global items
    name = name_entry.get()
    price = price_entry.get()
    quantity = quantity_entry.get()
    gst_rate = gst_rate_entry.get()
    cgst_rate = cgst_rate_entry.get()

    if name and price and quantity and gst_rate and cgst_rate:
        item = {
            "name": name,
            "price": float(price),
            "quantity": int(quantity),
            "gst_rate": float(gst_rate),
            "cgst_rate": float(cgst_rate)
        }
        items.append(item)
        item_listbox.insert(tk.END, f"{name} - {price} x {quantity}")

        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        gst_rate_entry.delete(0, tk.END)
        cgst_rate_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Input Error", "Please fill all fields.")

def remove_row():
    global items
    selected_index = item_listbox.curselection()
    if selected_index:
        items.pop(selected_index[0])
        item_listbox.delete(selected_index)

def generate_invoice_gui():
    bill_no = bill_no_entry.get()
    customer_name = customer_name_entry.get()
    customer_address = customer_address_entry.get("1.0", tk.END).strip()

    if bill_no and customer_name and customer_address:
        invoice = generate_invoice(bill_no, customer_name, customer_address, items)
        if invoice:
            save_invoice_as_pdf(invoice)
    else:
        messagebox.showerror("Input Error", "Please fill all invoice details.")

# GUI layout
root = tk.Tk()
root.title("Billing System")

fields = ["Item Name", "Price", "Quantity", "GST Rate (%)", "CGST Rate (%)"]
entries = []
for i, field in enumerate(fields):
    tk.Label(root, text=field).grid(row=i, column=0)
    entry = tk.Entry(root)
    entry.grid(row=i, column=1)
    entries.append(entry)

name_entry, price_entry, quantity_entry, gst_rate_entry, cgst_rate_entry = entries

tk.Button(root, text="Add Item", command=add_row).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="Remove Item", command=remove_row).grid(row=6, column=0, columnspan=2)

item_listbox = tk.Listbox(root, height=10, width=50)
item_listbox.grid(row=7, column=0, columnspan=2)

tk.Label(root, text="Bill No").grid(row=8, column=0)
bill_no_entry = tk.Entry(root)
bill_no_entry.grid(row=8, column=1)

tk.Label(root, text="Customer Name").grid(row=9, column=0)
customer_name_entry = tk.Entry(root)
customer_name_entry.grid(row=9, column=1)

tk.Label(root, text="Customer Address").grid(row=10, column=0)
customer_address_entry = tk.Text(root, height=3, width=30)
customer_address_entry.grid(row=10, column=1)

tk.Button(root, text="Generate Invoice", command=generate_invoice_gui).grid(row=11, column=0, columnspan=2)

root.mainloop()
