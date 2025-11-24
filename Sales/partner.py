# partner.py
from base import BaseModel, DATABASE


class Partner(BaseModel):
    """
    Partner (Customer):
    - name
    - email
    - sale_orders (runtime list)
    - invoices (runtime list)
    """

    def __init__(self, name, email, _id=None,
        sale_order_ids=None, invoice_ids=None):
        super().__init__(name, _id=_id)
        self.email = email

        # runtime relations (objects)
        self.sale_orders = []
        self.invoices = []

        # IDs from DB (for future advanced loading if needed)
        self._sale_order_ids = sale_order_ids or []
        self._invoice_ids = invoice_ids or []

    # ---------------------------
    # Properties
    # ---------------------------
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not value or "@" not in value:
            raise ValueError("Invalid email address")
        self._email = value

    # ---------------------------
    # Relations
    # ---------------------------
    def add_sale_order(self, order):
        if order not in self.sale_orders:
            self.sale_orders.append(order)

    def add_invoice(self, invoice):
        if invoice not in self.invoices:
            self.invoices.append(invoice)

    # ---------------------------
    # Business logic
    # ---------------------------
    def total_orders(self):
        return len(self.sale_orders)

    def total_invoiced_amount(self):
        total = 0
        for inv in self.invoices:
            total += inv.total_amount
        return total

    # ---------------------------
    # Persistence
    # ---------------------------
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "email": self.email,
            "sale_order_ids": [o.id for o in self.sale_orders],
            "invoice_ids": [i.id for i in self.invoices],
        })
        return base

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            email=data["email"],
            _id=data.get("id"),
            sale_order_ids=data.get("sale_order_ids", []),
            invoice_ids=data.get("invoice_ids", []),
        )

    # ---------------------------
    # Representation
    # ---------------------------
    def __str__(self):
        return f"Partner(id={self.id}, name={self.name}, email={self.email})"
