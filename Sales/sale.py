# sale.py
from base import BaseModel, DATABASE
from partner import Partner
from product import Product
from invoice import Invoice


class SaleOrderLine:
    """
    A single line in a sale order.
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
            raise ValueError(f"Product with id {data['product_id']} not found")
        product = Product.from_dict(prod_data)
        return cls(
            product=product,
            qty=data["qty"],
            unit_price=data["unit_price"],
        )


class SaleOrder(BaseModel):
    """
    Sale order:
    - customer (Partner)
    - lines
    - state: draft / confirmed
    - invoice_id: link to created invoice
    """

    def __init__(self, customer: Partner, state="draft",
        _id=None, name=None, line_dicts=None, invoice_id=None):
        if name is None:
            name = "SO"
        super().__init__(name, _id=_id)

        self.customer = customer
        self.state = state
        self._lines = []
        self.invoice_id = invoice_id

        if line_dicts is not None:
            for ld in line_dicts:
                self._lines.append(SaleOrderLine.from_dict(ld))

        # link to partner
        self.customer.add_sale_order(self)

    # ---------------------------
    # Lines
    # ---------------------------
    @property
    def lines(self):
        return list(self._lines)

    def add_line(self, product: Product, qty: int, unit_price: float = None):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        self._lines.append(SaleOrderLine(product, qty, unit_price))

    # ---------------------------
    # Computed
    # ---------------------------
    @property
    def total_amount(self):
        return sum(l.line_total for l in self._lines)

    # ---------------------------
    # Workflow
    # ---------------------------
    def confirm(self):
        """
        Confirm order:
        - check state and lines
        - check and decrease stock
        - create invoice
        """
        if self.state != "draft":
            raise ValueError("Only draft orders can be confirmed")
        if not self._lines:
            raise ValueError("Cannot confirm an empty order")

        # check stock
        for line in self._lines:
            if line.qty > line.product.qty:
                raise ValueError(
                    f"Not enough stock for {line.product.name}: "
                    f"requested {line.qty}, available {line.product.qty}"
                )

        # decrease stock
        for line in self._lines:
            line.product.decrease_qty(line.qty)
            line.product.save()

        # change state
        self.state = "confirmed"

        # create invoice
        invoice_lines = list(self._lines)  # reuse same lines objects
        inv = Invoice(self.customer, lines=invoice_lines)
        inv.save()
        self.invoice_id = inv.id

        # save order & customer (for IDs)
        self.save()
        self.customer.save()

        return inv



    # ---------------------------
    # Persistence
    # ---------------------------
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "customer_id": self.customer.id,
            "state": self.state,
            "invoice_id": self.invoice_id,
            "lines": [l.to_dict() for l in self._lines],
        })
        return base

    @classmethod
    def from_dict(cls, data):
        partner_data = DATABASE["partners"].get(str(data["customer_id"]))
        if not partner_data:
            raise ValueError(f"Partner with id {data['customer_id']} not found")
        customer = Partner.from_dict(partner_data)
        return cls(
            customer=customer,
            state=data.get("state", "draft"),
            _id=data.get("id"),
            name=data.get("name"),
            line_dicts=data.get("lines", []),
            invoice_id=data.get("invoice_id"),
        )

    def __str__(self):
        return f"SaleOrder(id={self.id}, customer={self.customer.name}, total={self.total_amount}, state={self.state}, invoice_id={self.invoice_id})"
