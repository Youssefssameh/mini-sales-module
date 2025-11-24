# Models Documentation

## BaseModel (`base.py`)

Base class for all domain models. Provides core functionality for persistence and ID management.

### Attributes
- `id` (int): Unique identifier, auto-generated per class
- `name` (str): Display name, validated to be non-empty

### Methods

#### `__init__(self, name, _id=None)`
- If `_id` is provided (from JSON), use it
- Otherwise, generate new ID using class-level counter
- Validates name using property setter

#### `save(self) -> self`
- Converts object to dict using `to_dict()`
- Stores in appropriate table in `DATABASE`
- Writes `DATABASE` to `database.json`
- Returns self for method chaining

#### `delete(self)`
- Removes record from `DATABASE`
- Persists changes to JSON

#### `to_dict(self) -> dict`
- Returns basic attributes: id, name, model
- Subclasses extend this to add their own fields

#### `from_dict(cls, data) -> object`
- Class method to rebuild object from JSON dict
- Must be implemented by subclasses

### Design Notes
- Each model class has its own ID sequence (Product ID 1 is independent of Partner ID 1)
- `_get_table_name()` abstract method determines JSON table name

---

## Product (`product.py`)

Represents a sellable product with stock tracking.

### Attributes
- `id`, `name` (inherited from BaseModel)
- `price` (float): Unit selling price, must be positive
- `qty` (int): Quantity in stock, must be non-negative

### Methods

#### `increase_qty(self, amount: int)`
- Adds `amount` to current stock
- Validates amount is positive

#### `decrease_qty(self, amount: int)`
- Subtracts `amount` from stock
- Raises `ValueError` if insufficient stock
- Used during sale order confirmation

#### `to_dict(self) -> dict`
- Extends BaseModel to include price and qty

#### `from_dict(cls, data) -> Product`
- Rebuilds Product from JSON, including price and qty

### Validation
- Price must be > 0
- Quantity must be >= 0
- Decrease fails if resulting qty would be negative

### Usage Example
p = Product("Laptop", 1000, qty=10).save()
p.decrease_qty(2) # Now qty=8
p.save()

---

## Partner (`partner.py`)

Represents a customer with contact information and relationships to orders/invoices.

### Attributes
- `id`, `name` (inherited)
- `email` (str): Customer email, must contain '@'
- `sale_orders` (list): In-memory list of SaleOrder objects
- `invoices` (list): In-memory list of Invoice objects
- `_sale_order_ids` (list): IDs stored in JSON
- `_invoice_ids` (list): IDs stored in JSON

### Methods

#### `add_sale_order(self, so: SaleOrder)`
- Adds sale order to in-memory list
- Updates `_sale_order_ids`

#### `add_invoice(self, inv: Invoice)`
- Adds invoice to in-memory list
- Updates `_invoice_ids`

#### `total_invoiced_amount(self) -> float`
- Sums total_amount of all invoices in `self.invoices`
- Only works if invoices are loaded in memory via `loaders.py`

#### `to_dict(self) -> dict`
- Includes email and ID lists (sale_order_ids, invoice_ids)

#### `from_dict(cls, data) -> Partner`
- Rebuilds Partner with email and ID lists
- Does NOT rebuild the actual objects (done by loaders)

### Validation
- Email must contain '@' character
- Setter raises ValueError on invalid email

### Design Notes
- Relationships stored as IDs in JSON for simplicity
- `loaders.py` rebuilds object references when needed

---

## Invoice (`invoice.py`)

Represents a customer invoice with line items and state management.

### Components

#### InvoiceLine (helper class)
Not a BaseModel, exists only in memory and as dicts in JSON.

**Attributes:**
- `product` (Product): Reference to product object
- `qty` (int): Quantity invoiced
- `unit_price` (float): Price per unit (can differ from current product.price)

**Properties:**
- `line_total` (float): qty × unit_price

**Methods:**
- `to_dict()`: Returns dict with product_id, qty, unit_price
- `from_dict(data)`: Rebuilds InvoiceLine by fetching Product from DATABASE

#### Invoice (BaseModel)

**Attributes:**
- `customer` (Partner): Customer object
- `state` (str): 'draft' or 'posted'
- `_lines` (list): InvoiceLine objects

**Properties:**
- `lines` (list): Read-only copy of _lines
- `total_amount` (float): Sum of all line_total

**Methods:**

##### `add_line(self, product, qty, unit_price=None)`
- Creates InvoiceLine and appends to _lines
- If unit_price not provided, uses product.price
- Validates qty > 0

##### `post(self)`
- Changes state from 'draft' to 'posted'
- Raises ValueError if already posted
- Does not automatically save (caller must call save())

##### `to_dict(self) -> dict`
- Includes customer_id, state, and lines as list of dicts

##### `from_dict(cls, data) -> Invoice`
- Fetches Partner from DATABASE
- Rebuilds lines using line_dicts parameter
- Links invoice to customer via `customer.add_invoice(self)`

### Workflow
1. Created in draft state (either manually or via SaleOrder.confirm())
2. Can be edited while in draft
3. Post to finalize (state → 'posted')
4. Posted invoices should not be modified

---

## SaleOrder (`sale.py`)

Represents a customer order with workflow: draft → confirmed (generates invoice, decreases stock).

### Components

#### SaleOrderLine (helper class)

**Attributes:**
- `product` (Product)
- `qty` (int)
- `unit_price` (float)

**Properties:**
- `line_total` (float): qty × unit_price

**Methods:**
- `to_dict()`, `from_dict()`: Similar to InvoiceLine

#### SaleOrder (BaseModel)

**Attributes:**
- `customer` (Partner)
- `state` (str): 'draft', 'confirmed', or 'cancelled'
- `invoice` (Invoice): Reference to generated invoice (None if draft)
- `_lines` (list): SaleOrderLine objects

**Properties:**
- `lines` (list): Read-only copy
- `total_amount` (float): Sum of line totals

**Methods:**

##### `add_line(self, product, qty, unit_price=None)`
- Adds line to order
- Validates qty > 0
- Does NOT check stock (check happens at confirm)

##### `confirm(self) -> Invoice`
- Checks state is 'draft'
- Validates stock availability for all lines
- Decreases product stock for each line
- Saves all affected products
- Creates Invoice from order lines
- Changes state to 'confirmed'
- Saves self, invoice, and customer
- Returns the created invoice

##### `to_dict(self) -> dict`
- Includes customer_id, state, invoice_id, lines

##### `from_dict(cls, data) -> SaleOrder`
- Rebuilds from JSON
- If invoice_id exists, fetches and links Invoice
- Links to customer via `customer.add_sale_order(self)`

### Workflow Example
so = SaleOrder(customer)
so.add_line(product1, 2)
so.add_line(product2, 5)
so.save() # Draft, no stock impact

inv = so.confirm() # Stock decreased, invoice created, state=confirmed


---

## Loaders (`loaders.py`)

Utility module to rebuild object graph from JSON database.

### Function: `load_all()`

Returns: `(products_by_id, partners_by_id, orders_by_id, invoices_by_id)`

**Steps:**
1. Rebuild all Products from `DATABASE["products"]`
2. Rebuild all Partners from `DATABASE["partners"]`
3. Rebuild all Invoices:
   - Each Invoice constructor calls `customer.add_invoice(self)`
   - Populates `partner.invoices` list
4. Rebuild all SaleOrders:
   - Each SaleOrder constructor calls `customer.add_sale_order(self)`
   - Populates `partner.sale_orders` list

**Usage:**
products, partners, orders, invoices = load_all()

Now you can navigate relationships:
for partner in partners.values():
print(partner.name)
for inv in partner.invoices:
print(f" Invoice {inv.id}: {inv.total_amount}")


**When to use:**
- Debug view in main menu
- When you need to traverse relationships (partner → invoices → lines → products)
- Testing and data analysis

**Note:** Most menu functions work directly on DATABASE dicts and don't need loaders. Loaders are for when you want the full ORM-like experience.



