# main.py
from base import DATABASE
from product import Product
from partner import Partner
from invoice import Invoice
from sale import SaleOrder
from loaders import load_all
from storage import save_database


# =========================
# Products
# =========================

def create_product():
    print("\n=== Create Product ===")
    name = input("Product name: ").strip()
    price = float(input("Price: "))
    qty = int(input("Quantity in stock: "))
    p = Product(name, price, qty).save()
    print(f"Product created: {p}")


def list_products():
    print("\n=== Products ===")
    if not DATABASE["products"]:
        print("No products found.")
        return
    for raw_id, data in DATABASE["products"].items():
        p = Product.from_dict(data)
        print(f"  • {p}")


def select_product():
    # Let user select a product from the list
    if not DATABASE["products"]:
        print("No products found. Create a product first.")
        return None

    products = []
    print("\nAvailable products:")
    for raw_id, data in DATABASE["products"].items():
        p = Product.from_dict(data)
        products.append(p)
        print(f"  {len(products)}) {p}")

    try:
        idx = int(input("Select product number: "))
        return products[idx - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def edit_product_menu():
    print("\n=== Edit Product ===")
    prod = select_product()
    if not prod:
        return

    print(f"\nCurrent: {prod}")
    print("Leave field empty if you don't want to change it.\n")

    # Update price if provided
    new_price_str = input(f"New price (current {prod.price}): ").strip()
    if new_price_str != "":
        try:
            new_price = float(new_price_str)
            prod.price = new_price
        except ValueError:
            print("Invalid price, keeping old value.")

    # Update quantity if provided
    new_qty_str = input(f"New qty (current {prod.qty}): ").strip()
    if new_qty_str != "":
        try:
            new_qty = int(new_qty_str)
            if new_qty < 0:
                print("Quantity cannot be negative, keeping old value.")
            else:
                prod.qty = new_qty
        except ValueError:
            print("Invalid quantity, keeping old value.")

    prod.save()
    print("Product updated:", prod)


def remove_product_menu():
    print("\n=== Remove Product ===")
    prod = select_product()
    if not prod:
        return

    confirm = input(f"Are you sure you want to delete {prod.name}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    table = "products"
    if table in DATABASE and str(prod.id) in DATABASE[table]:
        del DATABASE[table][str(prod.id)]
        save_database(DATABASE)
        print("Product deleted.")
    else:
        print("Product not found in database.")


def manage_products_menu():
    while True:
        print("\n" + "─" * 40)
        print("Manage Products")
        print("─" * 40)
        print("1) Add Product")
        print("2) Edit Product (price / qty)")
        print("3) Remove Product")
        print("4) List Products")
        print("0) Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            create_product()
        elif choice == "2":
            edit_product_menu()
        elif choice == "3":
            remove_product_menu()
        elif choice == "4":
            list_products()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


# =========================
# Customers (Partners)
# =========================

def create_partner():
    print("\n=== Create Partner (Customer) ===")
    name = input("Customer name: ").strip()

    # Keep asking until valid email is provided
    while True:
        email = input("Customer email (must contain '@'): ").strip()
        try:
            c = Partner(name, email).save()
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter a valid email like 'name@example.com'.")

    print(f"Partner created: {c}")


def list_partners():
    print("\n=== Partners ===")
    if not DATABASE["partners"]:
        print("No partners found.")
        return
    for raw_id, data in DATABASE["partners"].items():
        p = Partner.from_dict(data)
        print(f"  • {p}")


def select_partner():
    # Let user pick a partner from the list
    if not DATABASE["partners"]:
        print("No partners found. Create a partner first.")
        return None

    partners = []
    print("\nAvailable customers:")
    for raw_id, data in DATABASE["partners"].items():
        p = Partner.from_dict(data)
        partners.append(p)
        print(f"  {len(partners)}) {p}")

    try:
        idx = int(input("Select customer number: "))
        return partners[idx - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def edit_partner_menu():
    print("\n=== Edit Customer ===")
    partner = select_partner()
    if not partner:
        return

    print(f"\nCurrent: {partner}")
    print("Leave field empty if you don't want to change it.\n")

    # Update name if provided
    new_name = input(f"New name (current {partner.name}): ").strip()
    if new_name != "":
        partner.name = new_name

    # Update email with validation loop
    while True:
        new_email = input(f"New email (current {partner.email}): ").strip()
        if new_email == "":
            break
        try:
            partner.email = new_email
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter a valid email like 'name@example.com'.")

    partner.save()
    print("Customer updated:", partner)


def remove_partner_menu():
    print("\n=== Remove Customer ===")
    partner = select_partner()
    if not partner:
        return

    # Warn if customer has related records
    row = DATABASE["partners"].get(str(partner.id), {})
    so_ids = row.get("sale_order_ids", [])
    inv_ids = row.get("invoice_ids", [])
    if so_ids or inv_ids:
        print("Warning: this customer has linked sale orders or invoices.")
        print("   Sale orders IDs:", so_ids)
        print("   Invoice IDs:", inv_ids)

    confirm = input(f"Are you sure you want to delete {partner.name}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    table = "partners"
    if table in DATABASE and str(partner.id) in DATABASE[table]:
        del DATABASE[table][str(partner.id)]
        save_database(DATABASE)
        print("Customer deleted.")
    else:
        print("Customer not found in database.")


def view_customer_total_invoiced():
    print("\n=== Customer Total Invoiced ===")
    customer = select_partner()
    if not customer:
        return

    # Find all invoices for this customer
    total = 0.0
    invoices_list = []
    for raw_id, inv_data in DATABASE["invoices"].items():
        if inv_data.get("customer_id") == customer.id:
            inv = Invoice.from_dict(inv_data)
            if inv.state == "posted":
                invoices_list.append(inv)
                total += inv.total_amount

    print(f"\nCustomer: {customer.name}")
    print(f"Number of invoices: {len(invoices_list)}")
    if invoices_list:
        print("Invoices:")
        for inv in invoices_list:
            if inv.state == "posted":
                print(f"  • Invoice ID {inv.id}, state={inv.state}, total={inv.total_amount}")
    print(f"\nTotal Invoiced Amount: {total}")


def manage_customers_menu():
    while True:
        print("\n" + "─" * 40)
        print("Manage Customers")
        print("─" * 40)
        print("1) Add Customer")
        print("2) Edit Customer")
        print("3) Remove Customer")
        print("4) List Customers")
        print("5) View Customer Total Invoiced")
        print("0) Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            create_partner()
        elif choice == "2":
            edit_partner_menu()
        elif choice == "3":
            remove_partner_menu()
        elif choice == "4":
            list_partners()
        elif choice == "5":
            view_customer_total_invoiced()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


# =========================
# Helpers
# =========================

def get_all_products_list():
    products = []
    for raw_id, data in DATABASE["products"].items():
        products.append(Product.from_dict(data))
    return products


# =========================
# Sale Orders + Invoices
# =========================

def create_sale_order_and_invoice():
    print("\n=== Create Sale Order + Invoice ===")

    customer = select_partner()
    if not customer:
        return

    products = get_all_products_list()
    if not products:
        print("No products found. Create products first.")
        return

    so = SaleOrder(customer)

    # Add lines to sale order
    while True:
        print("\nAvailable products:")
        for i, p in enumerate(products, start=1):
            print(f"  {i}) {p.name} (Price: {p.price}, Stock: {p.qty})")

        choice = input("Select product number (or press Enter to finish): ").strip()
        if choice == "":
            break

        try:
            p_idx = int(choice)
            if p_idx < 1 or p_idx > len(products):
                print("Invalid product number.")
                continue
        except ValueError:
            print("Invalid input.")
            continue

        prod = products[p_idx - 1]
        try:
            qty = int(input("Quantity: "))
        except ValueError:
            print("Invalid quantity.")
            continue

        # Check stock before adding
        if qty > prod.qty:
            print(f"Error: Not enough stock! Requested {qty}, available {prod.qty}")
            continue

        try:
            so.add_line(prod, qty)
        except ValueError as e:
            print(f"Error: {e}")
            continue

    if not so.lines:
        print("No lines added. Sale order cancelled.")
        return

    so.save()
    print("\nDraft Sale Order created:")
    print("  ", so)
    for i, line in enumerate(so.lines, start=1):
        print(f"   • Line {i}: {line.product.name} x{line.qty} @ {line.unit_price} = {line.line_total}")
    print(f"   Total: {so.total_amount}")

    confirm = input("\nConfirm order and create invoice? (y/n): ").strip().lower()
    if confirm != "y":
        print("Sale order left in draft state.")
        return

    try:
        inv = so.confirm()
    except ValueError as e:
        print(f"Error while confirming: {e}")
        return

    print("\nOrder confirmed and invoice created:")
    print("  SaleOrder:", so)
    print("  Invoice:", inv)
    for i, line in enumerate(inv.lines, start=1):
        print(f"   • Inv Line {i}: {line.product.name} x{line.qty} @ {line.unit_price} = {line.line_total}")
    print(f"   Invoice total: {inv.total_amount}")


def list_sale_orders():
    print("\n=== Sale Orders ===")
    if not DATABASE["saleorders"]:
        print("No sale orders found.")
        return
    for raw_id, data in DATABASE["saleorders"].items():
        so = SaleOrder.from_dict(data)
        print(f"  • {so}")


def list_invoices():
    print("\n=== Invoices ===")
    if not DATABASE["invoices"]:
        print("No invoices found.")
        return
    for raw_id, data in DATABASE["invoices"].items():
        inv = Invoice.from_dict(data)
        print(f"  • {inv}")


def post_invoice_menu():
    print("\n=== Post Invoice ===")
    if not DATABASE["invoices"]:
        print("No invoices found.")
        return

    invoices = []
    for raw_id, data in DATABASE["invoices"].items():
        inv = Invoice.from_dict(data)
        invoices.append(inv)

    for i, inv in enumerate(invoices, start=1):
        print(f"  {i}) {inv}")

    try:
        idx = int(input("Select invoice number: "))
        inv = invoices[idx - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    if inv.state == "posted":
        print("Invoice is already posted.")
        return

    try:
        inv.post()
        inv.save()
        inv.customer.save()
        print("Invoice posted:", inv)
    except ValueError as e:
        print(f"Error: {e}")


def view_partner_details():
    print("\n=== Partner Details ===")
    customer = select_partner()
    if not customer:
        return

    row = DATABASE["partners"].get(str(customer.id))
    print("\nPartner object:", customer)
    print("Raw DB row:", row)


def cancel_sale_order_menu():
    # Mark order as cancelled without stock rollback
    print("\n=== Cancel Sale Order (mark only) ===")
    if not DATABASE["saleorders"]:
        print("No sale orders found.")
        return

    orders = []
    for raw_id, data in DATABASE["saleorders"].items():
        so = SaleOrder.from_dict(data)
        orders.append(so)

    for i, so in enumerate(orders, start=1):
        print(f"  {i}) {so}")

    try:
        idx = int(input("Select sale order number: "))
        so = orders[idx - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    if so.state == "cancelled":
        print("Order is already cancelled.")
        return

    if so.state == "confirmed":
        print("Warning: this order is confirmed; this demo only marks it cancelled (no stock rollback).")

    confirm = input("Mark this order as cancelled? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancel action aborted.")
        return

    so.state = "cancelled"
    so.save()
    print("Sale order cancelled:", so)


def confirm_sale_order_menu():
    # Confirm a draft sale order and generate invoice
    print("\n=== Confirm Sale Order ===")
    if not DATABASE["saleorders"]:
        print("No sale orders found.")
        return

    orders = []
    for raw_id, data in DATABASE["saleorders"].items():
        so = SaleOrder.from_dict(data)
        orders.append(so)

    for i, so in enumerate(orders, start=1):
        print(f"  {i}) {so}")

    try:
        idx = int(input("Select sale order number: "))
        so = orders[idx - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    if so.state != "draft":
        print(f"Order state is '{so.state}', only draft orders can be confirmed.")
        return

    confirm = input("Confirm this order and create invoice? (y/n): ").strip().lower()
    if confirm != "y":
        print("Confirmation aborted.")
        return

    try:
        inv = so.confirm()
    except ValueError as e:
        print(f"Error while confirming: {e}")
        return

    print("\nOrder confirmed and invoice created:")
    print("  SaleOrder:", so)
    print("  Invoice:", inv)
    for i, line in enumerate(inv.lines, start=1):
        print(f"   • Inv Line {i}: {line.product.name} x{line.qty} @ {line.unit_price} = {line.line_total}")
    print(f"   Invoice total: {inv.total_amount}")


def debug_show_loaded():
    password = input("Enter password to view objects: ").strip()
    if password != "0000":
        print("Wrong password. Access denied.")
        return

    print("\n=== Debug: DATABASE as Objects ===")

    print("\nProducts:")
    if DATABASE["products"]:
        for raw_id, data in DATABASE["products"].items():
            obj = Product.from_dict(data)
            print(f"  • {obj}")
    else:
        print("  No products found.")

    print("\nPartners:")
    if DATABASE["partners"]:
        for raw_id, data in DATABASE["partners"].items():
            obj = Partner.from_dict(data)
            print(f"  • {obj}")
    else:
        print("  No partners found.")

    print("\nSale Orders:")
    if DATABASE["saleorders"]:
        for raw_id, data in DATABASE["saleorders"].items():
            obj = SaleOrder.from_dict(data)
            print(f"  • {obj}")
    else:
        print("  No sale orders found.")

    print("\nInvoices:")
    if DATABASE["invoices"]:
        for raw_id, data in DATABASE["invoices"].items():
            obj = Invoice.from_dict(data)
            print(f"  • {obj}")
    else:
        print("  No invoices found.")


# =========================
# Main menu
# =========================

def main_menu():
    while True:
        print("\n" + "═" * 50)
        print("Mini Odoo Sales System - Main Menu")
        print("═" * 50)
        print("1) Manage Products")
        print("2) Manage Customers")
        print("3) Create Sale Order + Invoice (confirm now)")
        print("4) List Sale Orders")
        print("5) List Invoices")
        print("6) Post existing Invoice")
        print("7) View Partner details (raw DB)")
        print("8) Cancel Sale Order ")
        print("9) Show all objects (password protected)")
        print("10) Confirm existing Sale Order (draft -> confirmed + invoice)")
        print("0) Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            manage_products_menu()
        elif choice == "2":
            manage_customers_menu()
        elif choice == "3":
            create_sale_order_and_invoice()
        elif choice == "4":
            list_sale_orders()
        elif choice == "5":
            list_invoices()
        elif choice == "6":
            post_invoice_menu()
        elif choice == "7":
            view_partner_details()
        elif choice == "8":
            cancel_sale_order_menu()
        elif choice == "9":
            debug_show_loaded()
        elif choice == "10":
            confirm_sale_order_menu()
        elif choice == "0":
            print("Bye! See you later.")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main_menu()
