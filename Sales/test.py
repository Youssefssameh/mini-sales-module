# test.py
from base import DATABASE
from product import Product
from partner import Partner
from invoice import Invoice
from sale import SaleOrder


def test_read_existing_data():
    print("\n" + "=" * 60)
    print("TEST 1: Read Existing Data from JSON")
    print("=" * 60)
    
    print(f"\n📦 Products in DB: {len(DATABASE['products'])}")
    for raw_id, data in list(DATABASE["products"].items())[:3]:
        p = Product.from_dict(data)
        print(f"  • {p}")
    
    print(f"\n👥 Partners in DB: {len(DATABASE['partners'])}")
    for raw_id, data in list(DATABASE["partners"].items())[:3]:
        partner = Partner.from_dict(data)
        print(f"  • {partner}")
    
    print(f"\n🧾 Sale Orders in DB: {len(DATABASE['saleorders'])}")
    for raw_id, data in list(DATABASE["saleorders"].items())[:3]:
        so = SaleOrder.from_dict(data)
        print(f"  • {so}")
    
    print(f"\n📄 Invoices in DB: {len(DATABASE['invoices'])}")
    for raw_id, data in list(DATABASE["invoices"].items())[:3]:
        inv = Invoice.from_dict(data)
        print(f"  • {inv}")


def test_create_new_product():
    print("\n" + "=" * 60)
    print("TEST 2: Create New Product")
    print("=" * 60)
    
    p = Product("Test Product - Smart Watch", 2500.0, qty=12).save()
    print(f"\n✅ Product created: {p}")
    
    print("\n📉 Decrease qty by 3:")
    p.decrease_qty(3)
    p.save()
    print(f"  After decrease: {p}")
    
    print("\n📈 Increase qty by 5:")
    p.increase_qty(5)
    p.save()
    print(f"  After increase: {p}")


def test_create_new_partner():
    print("\n" + "=" * 60)
    print("TEST 3: Create New Partner")
    print("=" * 60)
    
    partner = Partner("Test Customer - Kareem", "kareem.test@example.com").save()
    print(f"\n✅ Partner created: {partner}")
    print(f"  Email: {partner.email}")


def test_invoice_workflow():
    print("\n" + "=" * 60)
    print("TEST 4: Invoice Workflow (Draft → Posted)")
    print("=" * 60)
    
    # Use existing partner
    partner_data = DATABASE["partners"]["1"]
    customer = Partner.from_dict(partner_data)
    
    # Use existing products
    prod1_data = DATABASE["products"]["3"]
    prod2_data = DATABASE["products"]["10"]
    p1 = Product.from_dict(prod1_data)
    p2 = Product.from_dict(prod2_data)
    
    inv = Invoice(customer)
    inv.add_line(p1, 2, p1.price)
    inv.add_line(p2, 4, p2.price)
    inv.save()
    customer.save()
    
    print(f"\n✅ Draft Invoice created: {inv}")
    for i, line in enumerate(inv.lines, start=1):
        print(f"   Line {i}: {line.product.name} x{line.qty} @ {line.unit_price} = {line.line_total}")
    print(f"\n💰 Total: {inv.total_amount}")
    print(f"📌 State: {inv.state}")
    
    inv.post()
    inv.save()
    customer.save()
    
    print(f"\n✅ After post()")
    print(f"📌 State: {inv.state}")


def test_sale_order_confirm():
    print("\n" + "=" * 60)
    print("TEST 5: Sale Order Confirm (Stock Check)")
    print("=" * 60)
    
    # Use existing partner
    partner_data = DATABASE["partners"]["2"]
    customer = Partner.from_dict(partner_data)
    
    # Use existing products
    prod_data = DATABASE["products"]["5"]
    product = Product.from_dict(prod_data)
    
    print(f"\n📦 Product before SO: {product}")
    
    so = SaleOrder(customer)
    so.add_line(product, 2)
    so.save()
    
    print(f"\n🧾 Draft Sale Order: {so}")
    print(f"  State: {so.state}")
    print(f"  Lines:")
    for i, line in enumerate(so.lines, start=1):
        print(f"    {i}. {line.product.name} x{line.qty} @ {line.unit_price}")
    
    inv = so.confirm()
    
    print(f"\n✅ After confirm():")
    print(f"  SO State: {so.state}")
    print(f"  Generated Invoice: {inv}")
    print(f"  Invoice State: {inv.state}")
    
    # Reload product to see updated stock
    prod_data_new = DATABASE["products"][str(product.id)]
    product_updated = Product.from_dict(prod_data_new)
    print(f"\n📦 Product after SO confirm: {product_updated}")


def test_partner_total_invoiced():
    print("\n" + "=" * 60)
    print("TEST 6: Calculate Total Invoiced for Partner")
    print("=" * 60)
    
    # Pick partner with invoices
    partner_data = DATABASE["partners"]["5"]
    customer = Partner.from_dict(partner_data)
    
    total = 0.0
    invoices_list = []
    for raw_id, inv_data in DATABASE["invoices"].items():
        if inv_data.get("customer_id") == customer.id:
            inv = Invoice.from_dict(inv_data)
            if inv.state == "posted":
                invoices_list.append(inv)
                total += inv.total_amount
    
    print(f"\n👤 Customer: {customer.name}")
    print(f"📄 Number of invoices: {len(invoices_list)}")
    if invoices_list:
        print("Invoices:")
        for inv in invoices_list:
            if inv.state == "posted":
                print(f"  • {inv.name}: {inv.total_amount} ({inv.state})")
    print(f"\n💵 Total Invoiced Amount: {total}")


def main():
    test_read_existing_data()
    test_create_new_product()
    test_create_new_partner()
    test_invoice_workflow()
    test_sale_order_confirm()
    test_partner_total_invoiced()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed! 🚀")
    print("=" * 60)
    print("\n📄 Data saved to: database.json")
    print("📊 Final DATABASE counts:")
    print(f"  - products: {len(DATABASE['products'])} items")
    print(f"  - partners: {len(DATABASE['partners'])} items")
    print(f"  - invoices: {len(DATABASE['invoices'])} items")
    print(f"  - saleorders: {len(DATABASE['saleorders'])} items")


if __name__ == "__main__":
    main()
