# invoice.py
from base import BaseModel, DATABASE
from partner import Partner
from product import Product


class InvoiceLine:
    """
    Single line on an invoice:
    - product
    - qty
    - unit_price
    """

    def __init__(self, product: Product, qty: int, unit_price: float = None):
        self.product = product
        self.qty = qty
        self.unit_price = unit_price if unit_price is not None else product.price

    @property
    def line_total(self):
        return self.unit_price * self.qty

    def to_dict(self):
        return {
            "product_id": self.product.id,
            "qty": self.qty,
            "unit_price": self.unit_price,
        }

    @classmethod
    def from_dict(cls, data):
        prod_data = DATABASE["products"].get(str(data["product_id"]))
        if not prod_data:
            raise ValueError(f"Product with id {data['product_id']} not found in database")
        product = Product.from_dict(prod_data)
        return cls(
            product=product,
            qty=data["qty"],
            unit_price=data["unit_price"],
        )


class Invoice(BaseModel):
    """
    Invoice:
    - customer (Partner)
    - lines (InvoiceLine[])
    - state: draft / posted
    - total_amount (computed)
    """

    def __init__(self, customer: Partner, lines=None, state="draft",
                _id=None, name=None, line_dicts=None):
        if name is None:
            name = "INV"
        super().__init__(name, _id=_id)

        self.customer = customer
        self.state = state
        self._lines = []

        # build from objects
        if lines is not None:
            for line in lines:
                self.add_line(line.product, line.qty, line.unit_price)

        # build from dicts (DB)
        if line_dicts is not None:
            for ld in line_dicts:
                self._lines.append(InvoiceLine.from_dict(ld))

        # link to partner in memory
        self.customer.add_invoice(self)

    # ---------------------------
    # Lines
    # ---------------------------
    @property
    def lines(self):
        return list(self._lines)

    def add_line(self, product: Product, qty: int, unit_price: float = None):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        self._lines.append(InvoiceLine(product, qty, unit_price))

    # ---------------------------
    # Computed
    # ---------------------------
    @property
    def total_amount(self):
        return sum(l.line_total for l in self._lines)

    # ---------------------------
    # Workflow
    # ---------------------------
    def post(self):
        if self.state != "draft":
            raise ValueError("Only draft invoices can be posted")
        self.state = "posted"

    # ---------------------------
    # Persistence
    # ---------------------------
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "customer_id": self.customer.id,
            "state": self.state,
            "lines": [l.to_dict() for l in self._lines],
        })
        return base

    @classmethod
    def from_dict(cls, data):
        partner_data = DATABASE["partners"].get(str(data["customer_id"]))
        if not partner_data:
            raise ValueError(f"Partner with id {data['customer_id']} not found in database")
        customer = Partner.from_dict(partner_data)
        return cls(
            customer=customer,
            state=data.get("state", "draft"),
            _id=data.get("id"),
            name=data.get("name"),
            line_dicts=data.get("lines", []),
        )

    def __str__(self):
        return f"Invoice(id={self.id}, customer={self.customer.name}, total={self.total_amount}, state={self.state})"
