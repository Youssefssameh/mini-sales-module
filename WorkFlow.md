# System Workflows

## 1. Product Management Workflow

### Create Product
1. User enters name, price, quantity
2. Product object created with auto-generated ID
3. Validated: price > 0, qty >= 0
4. Saved to `DATABASE["products"]`
5. Written to `database.json`

### Edit Product
1. User selects product from list
2. Optionally updates price and/or qty
3. Validation applied
4. Saved to update existing record

### Delete Product
1. User selects product
2. Confirmation prompt
3. Record removed from `DATABASE["products"]`
4. Changes persisted to JSON

**Stock Updates:**
- Manual: via Edit Product
- Automatic decrease: when Sale Order is confirmed
- No automatic increase (purchases not implemented)

---

## 2. Customer Management Workflow

### Create Customer
1. User enters name and email
2. Email validated (must contain '@')
3. Partner object saved
4. Empty sale_order_ids and invoice_ids lists initialized

### Edit Customer
1. Select customer
2. Update name and/or email
3. Email re-validated if changed
4. Save updates

### Delete Customer
1. Select customer
2. System warns if customer has linked orders/invoices
3. User confirms
4. Record deleted (orphans orders/invoices in current implementation)

### View Total Invoiced
1. Select customer
2. System loops through `DATABASE["invoices"]`
3. Filters by `customer_id`
4. Sums `total_amount` of posted invoices
5. Displays list and total

---

## 3. Sale Order Workflow

### Draft Creation
1. User selects customer
2. Adds products one by one:
   - System displays available stock
   - User enters quantity
   - **Stock check**: if qty > product.qty, addition is blocked
   - Line added to order
3. User finishes selection (press Enter)
4. Sale Order saved in 'draft' state
5. No stock impact at this stage

### Confirmation
1. User chooses to confirm draft order (option 3 or 10)
2. System performs final stock validation for all lines
3. If validation passes:
   - **Stock decreased** for each product
   - Products saved with new quantities
   - **Invoice created** in draft state with same lines
   - Invoice saved and linked to order
   - Sale Order state → 'confirmed'
   - Sale Order saved
   - Customer's sale_order_ids and invoice_ids updated
4. If validation fails: error shown, order remains draft

### Cancellation (Mark Only)
1. User selects order
2. Confirms cancellation
3. State changed to 'cancelled'
4. **No stock rollback** in current implementation

**State Diagram:**
draft → confirmed (generates invoice, decreases stock)
draft → cancelled (no stock impact)
confirmed → cancelled (WARNING: no stock rollback)

---

## 4. Invoice Workflow

### Creation
Invoices are created in two ways:

**A. Automatically from Sale Order:**
- When Sale Order is confirmed
- Invoice created with same lines, customer, and totals
- Invoice saved in 'draft' state
- Linked to Sale Order via `invoice_id`

**B. Manually (not implemented in current menu):**
- Could create standalone Invoice
- Use case: invoicing without a sale order

### Posting
1. User selects draft invoice from list
2. Confirms posting
3. Invoice state → 'posted'
4. Invoice saved
5. Customer saved (to update invoice_ids)

**State Diagram:**
draft → posted (finalized, should not be edited)


### Viewing
- List all invoices: shows id, customer, total, state
- View via customer details: shows raw database row with IDs

---

## 5. Relationship Management

### Partner ↔ Sale Orders
- **Storage**: Partner has `sale_order_ids` list (IDs only)
- **Runtime**: Partner has `sale_orders` list (objects, populated by loaders or during creation)
- **Update**: When SaleOrder is created, calls `customer.add_sale_order(self)`

### Partner ↔ Invoices
- **Storage**: Partner has `invoice_ids` list
- **Runtime**: Partner has `invoices` list (objects)
- **Update**: When Invoice is created, calls `customer.add_invoice(self)`

### Sale Order → Invoice
- **Storage**: SaleOrder has `invoice_id` (int or null)
- **Runtime**: SaleOrder has `invoice` (object or None)
- **Update**: During `SaleOrder.confirm()`, invoice created and linked

### Lines → Products
- **Storage**: Line has `product_id` (int)
- **Runtime**: Line has `product` (Product object)
- **Update**: During line creation or `from_dict()`

---

## 6. Data Persistence Flow

### Save Operation
Object.save()
→ Object.to_dict() (serialize)
→ DATABASE[table][id] = dict
→ save_database(DATABASE)
→ write to database.json

### Load Operation
load_database()
→ read database.json
→ parse JSON
→ return DATABASE dict

Model.from_dict(data)
→ fetch related objects from DATABASE
→ reconstruct object with relationships
→ return object instance

### Full Load with Relationships
load_all()
→ rebuild all Products
→ rebuild all Partners
→ rebuild all Invoices (links to Partners)
→ rebuild all SaleOrders (links to Partners and Invoices)
→ return all objects as dicts keyed by ID


---

## 7. Error Handling

### Product Stock
- **Add line with qty > stock**: Blocked before adding
- **Confirm order with insufficient stock**: ValueError raised, order stays draft

### Email Validation
- **Invalid email on create/edit**: ValueError, loop until valid email entered

### State Transitions
- **Post already-posted invoice**: Error message, no change
- **Confirm non-draft order**: Error message
- **Cancel already-cancelled order**: Info message

### Missing Data
- **from_dict with missing customer**: ValueError with clear message
- **from_dict with missing product**: ValueError

---

## 8. Testing Workflow

Run `python test.py` to execute:

1. **Read existing data**: Verify JSON loads correctly
2. **Create new product**: Test save, increase_qty, decrease_qty
3. **Create new partner**: Test email validation
4. **Invoice workflow**: Draft → add lines → post
5. **Sale order confirm**: Draft → add lines → confirm → verify stock decrease
6. **Total invoiced**: Calculate sum for a customer

Each test prints step-by-step results and validates expected outcomes.






