import flet as ft
import sqlite3
import json

# Load company details from config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Database functions
def save_invoice(invoice_no, date, customer_name, customer_address, items, total_amount):
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO invoices (invoice_no, date, customer_name, customer_address, items, total_amount) VALUES (?, ?, ?, ?, ?, ?)",
                   (invoice_no, date, customer_name, customer_address, json.dumps(items), total_amount))
    
    conn.commit()
    conn.close()

def get_invoices():
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, invoice_no, date, customer_name, total_amount FROM invoices")
    invoices = cursor.fetchall()
    conn.close()
    return invoices

# Flet UI
def main(page: ft.Page):
    page.title = "Billing System"
    page.scroll = "auto"

    invoice_no = ft.TextField(label="Invoice No", value="1001")
    date = ft.TextField(label="Date")
    customer_name = ft.TextField(label="Customer Name")
    customer_address = ft.TextField(label="Customer Address")
    
    # Company details from config
    company_name = ft.Text(config["company_name"], size=24, weight=ft.FontWeight.BOLD)
    address = ft.Text(config["address"])
    gstin = ft.Text(f"GSTIN: {config['gstin']}")
    
    item_list = ft.Column()
    
    def add_item(e):
        row = ft.Row([
            ft.TextField(label="Particulars"),
            ft.TextField(label="HSN Code"),
            ft.TextField(label="Qty"),
            ft.TextField(label="Rate"),
            ft.Text(value="0.00", size=14, weight=ft.FontWeight.BOLD),
        ])
        item_list.controls.append(row)
        page.update()

    def save_bill(e):
        items = []
        total_amount = 0
        for row in item_list.controls:
            particulars = row.controls[0].value
            qty = int(row.controls[2].value or 0)
            rate = float(row.controls[3].value or 0)
            amount = qty * rate
            total_amount += amount
            items.append({"particulars": particulars, "qty": qty, "rate": rate, "amount": amount})

        save_invoice(invoice_no.value, date.value, customer_name.value, customer_address.value, items, total_amount)
        refresh_invoice_list()

    invoice_list = ft.Column()
    
    def refresh_invoice_list():
        invoice_list.controls.clear()
        for invoice in get_invoices():
            invoice_list.controls.append(ft.Text(f"Invoice {invoice[1]} | {invoice[3]} | {invoice[2]} | ₹{invoice[4]}"))
        page.update()
    
    refresh_invoice_list()

    page.add(
        ft.Column([
            company_name,
            address,
            gstin,
            invoice_no, date,
            customer_name, customer_address,
            ft.Divider(),
            item_list,
            ft.ElevatedButton(text="Add Item", on_click=add_item),
            ft.ElevatedButton(text="Save Invoice", on_click=save_bill),
            ft.Divider(),
            ft.Text("Invoices List:", size=18, weight=ft.FontWeight.BOLD),
            invoice_list,
        ])
    )

ft.app(target=main)
