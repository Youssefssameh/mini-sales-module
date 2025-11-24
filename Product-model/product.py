# product.py
from base import BaseModel, DATABASE


class Product(BaseModel):
    """
    Product model:
    - name
    - price
    - qty (stock quantity)
    """

    def __init__(self, name, price, qty=0, _id=None):
        super().__init__(name, _id=_id)
        self.price = price
        self.qty = qty

    # ---------------------------
    # Properties
    # ---------------------------
    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value is None:
            raise ValueError("Price must be provided")
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @property
    def qty(self):
        return self._qty

    @qty.setter
    def qty(self, value):
        if value is None:
            raise ValueError("Quantity must be provided")
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        self._qty = value

    # ---------------------------
    # Stock management
    # ---------------------------
    def increase_qty(self, amount):
        if amount <= 0:
            raise ValueError("Increase amount must be positive")
        self._qty += amount

    def decrease_qty(self, amount):
        if amount <= 0:
            raise ValueError("Decrease amount must be positive")
        if amount > self._qty:
            raise ValueError(
                f"Not enough stock for {self.name} "
                f"(requested {amount}, available {self._qty})"
            )
        self._qty -= amount

    # ---------------------------
    # Persistence
    # ---------------------------
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "price": self.price,
            "qty": self.qty,
        })
        return base

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            price=data["price"],
            qty=data.get("qty", 0),
            _id=data.get("id"),
        )

    # ---------------------------
    # Representation
    # ---------------------------
    def __str__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, qty={self.qty})"

