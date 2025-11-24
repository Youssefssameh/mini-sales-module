# base.py
from abc import ABC
from storage import save_database, load_database

# Load DATABASE when program starts
DATABASE = load_database()


class BaseModel(ABC):
    """
    Base model:
    - auto-increment ID (per subclass)
    - name with validation
    - save/delete to JSON DB
    """

    def __init__(self, name, _id=None):
        # name
        self._name = None
        self.name = name

        # per-class auto-increment ID
        if _id is not None:
            self._id = _id
        else:
            cls = self.__class__
            if not hasattr(cls, "_next_id"):
                cls._next_id = 1
            self._id = cls._next_id
            cls._next_id += 1

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    # ---------------------------
    # Persistence
    # ---------------------------
    def save(self):
        """Save record into the fake JSON database."""
        table = self._get_table_name()
        if table not in DATABASE:
            DATABASE[table] = {}
        DATABASE[table][str(self.id)] = self.to_dict()
        save_database(DATABASE)
        return self

    def delete(self):
        """Delete record from the fake JSON database."""
        table = self._get_table_name()
        if table in DATABASE and str(self.id) in DATABASE[table]:
            del DATABASE[table][str(self.id)]
            save_database(DATABASE)

    def _get_table_name(self):
        """
        Convert class name to table name:
        Product  -> products
        Partner  -> partners
        SaleOrder -> saleorders
        Invoice  -> invoices
        """
        return self.__class__.__name__.lower() + "s"

    # ---------------------------
    # Serialization
    # ---------------------------
    def to_dict(self):
        """Base fields for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "model": self.__class__.__name__,
        }

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
