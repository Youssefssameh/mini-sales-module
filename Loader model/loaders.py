# loaders.py
from base import DATABASE
from product import Product
from partner import Partner
from invoice import Invoice
from sale import SaleOrder


def load_all():
    """
    Load all objects from DATABASE (JSON) and rebuild relations in memory.
    Returns 4 dicts:
    products_by_id, partners_by_id, orders_by_id, invoices_by_id
    """
    products_by_id = {}
    partners_by_id = {}
    orders_by_id = {}
    invoices_by_id = {}

    # 1) load products
    for raw_id, data in DATABASE["products"].items():
        obj = Product.from_dict(data)
        products_by_id[obj.id] = obj

    # 2) load partners
    for raw_id, data in DATABASE["partners"].items():
        obj = Partner.from_dict(data)
        partners_by_id[obj.id] = obj

    # 3) load invoices and link to partner
    for raw_id, data in DATABASE["invoices"].items():
        inv = Invoice.from_dict(data)
        invoices_by_id[inv.id] = inv
        # link both sides in memory
        inv.customer.add_invoice(inv)

    # 4) load sale orders and link to partner
    for raw_id, data in DATABASE["saleorders"].items():
        so = SaleOrder.from_dict(data)
        orders_by_id[so.id] = so
        so.customer.add_sale_order(so)
        

    return products_by_id, partners_by_id, orders_by_id, invoices_by_id
