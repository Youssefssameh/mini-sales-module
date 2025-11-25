# Mini Odoo Sales System

A simplified sales management system inspired by Odoo ERP, built with Python and JSON-based storage. This console application demonstrates core concepts of order management, invoicing, and inventory tracking.

## Features

- **Product Management**: Create, edit, delete, and list products with stock tracking
- **Customer Management**: Manage customer records with email validation
- **Sale Orders**: Create draft orders, confirm them, and automatically generate invoices
- **Invoice Management**: Create invoices, post them, and track customer billing
- **Stock Control**: Automatic inventory updates when orders are confirmed
- **Customer Analytics**: Calculate total invoiced amount per customer

## System Requirements

- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

## Installation

1. Clone or download this repository
2. Ensure all project files are in the same directory:
   - `base.py`
   - `storage.py`
   - `product.py`
   - `partner.py`
   - `invoice.py`
   - `sale.py`
   - `loaders.py`
   - `main.py`
   - `database.json`

## Running the Application
python main.py

The application will load data from `database.json` and present a menu-driven interface.

## Project Structure

mini-odoo-sales/
├── base.py # Base model class with ID generation and persistence
├── storage.py # JSON database read/write functions
├── product.py # Product model with stock management
├── partner.py # Customer/Partner model with email validation
├── invoice.py # Invoice and InvoiceLine models
├── sale.py # SaleOrder and SaleOrderLine models
├── loaders.py # Rebuild objects and relationships from JSON
├── main.py # Console UI and menu system
├── database.json # JSON file acting as database
└── test.py # Test suite for all features


## Data Model Overview

### Products
- Attributes: name, price, quantity in stock
- Operations: increase/decrease stock, update price

### Partners (Customers)
- Attributes: name, email (validated)
- Relationships: one-to-many with Sale Orders and Invoices

### Sale Orders
- Attributes: customer, lines, state (draft/confirmed/cancelled), invoice reference
- Workflow: draft → confirmed (generates invoice and decreases stock)

### Invoices
- Attributes: customer, lines, state (draft/posted)
- Workflow: draft → posted (marks as finalized)

### Lines (Sale Order / Invoice)
- Attributes: product, quantity, unit price
- Computed: line total (qty × price)

## Workflow Examples

### Creating and Confirming a Sale Order

1. Select "Create Sale Order + Invoice" from main menu
2. Choose a customer
3. Add products and quantities
4. System checks stock availability before adding each line
5. Confirm the order:
   - Stock is decreased for each product
   - Invoice is automatically created in draft state
   - Sale order state changes to "confirmed"

### Posting an Invoice

1. Select "Post existing Invoice"
2. Choose an invoice in draft state
3. Confirm posting
4. Invoice state changes to "posted" (finalized)

## Key Design Patterns

### Persistence
All models inherit from `BaseModel` which provides:
- Automatic ID generation (per-class counter)
- `save()` method to persist to JSON
- `to_dict()` / `from_dict()` for serialization

### Relationships
- Stored as IDs in JSON (`customer_id`, `product_id`, etc.)
- Reconstructed as object references in memory
- `loaders.py` rebuilds full object graph from JSON

### Validation
- Email validation in Partner model
- Stock availability check before order confirmation
- State transitions (e.g., only draft orders can be confirmed)

## Testing

Run the test suite:
       python test.py

Tests cover:
- Reading existing data
- Creating new products and partners
- Invoice workflow (draft → posted)
- Sale order confirmation and stock updates
- Customer total invoiced calculation

## Password-Protected Features

Debug view (option 9 in main menu) requires password: `0000`

## Limitations & Known Issues

- Cancel Sale Order only marks state as cancelled (no stock rollback)
- No support for discounts or taxes
- No multi-currency support
- JSON storage is not suitable for concurrent access

## Future Enhancements

- Add proper cancel workflow with stock reversal
- Implement payment tracking
- Add discount and tax calculation
- Create web or GUI interface
- Use a real database (SQLite, PostgreSQL)
- Add user authentication and permissions

## License

Educational project - feel free to use and modify.

## Author

Created as a learning project to demonstrate OOP, data persistence, and business workflow implementation in Python.
