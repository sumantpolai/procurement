# 🧾 Purchase Order (PO) API Documentation

## 1. Overview

The Purchase Order (PO) module is used to create and manage orders issued to vendors based on approved Purchase Requisitions (PR). It ensures proper tracking of quantities, pricing, taxes, and approvals.

---

## 2. Process Flow

```
Item → Vendor → PR → PO → GR
```

* PO is created **based on PR**
* Vendor must be selected
* Items and pricing must align with PR

---

## 3. Data Model

### 3.1 Purchase Order

| Field Name           | Type   | Required | Description                       |
| -------------------- | ------ | -------- | --------------------------------- |
| id                   | UUID   | Yes      | Unique PO ID                      |
| pr_id                | UUID   | Yes      | Reference to Purchase Requisition |
| vendor_id            | UUID   | Yes      | Selected Vendor                   |
| items                | Array  | Yes      | List of ordered items             |
| pricing_summary      | Object | Yes      | Total pricing details             |
| supporting_documents | Array  | No       | Attached documents                |
| terms_conditions     | String | No       | Terms and conditions              |
| status               | String | Yes      | PO Status                         |
| created_at           | Date   | Yes      | Timestamp                         |

---

### 3.2 PO Item Object

| Field Name    | Type   | Required | Description              |
| ------------- | ------ | -------- | ------------------------ |
| item_id       | UUID   | Yes      | Item reference           |
| item_name     | String | Yes      | Item name                |
| requested_qty | Number | Yes      | Quantity requested in PR |
| order_qty     | Number | Yes      | Quantity ordered         |
| unit_price    | Number | Yes      | Price per unit           |
| uom           | String | Yes      | Unit of measurement      |
| gst           | Number | Yes      | GST percentage           |
| cgst          | Number | Yes      | CGST                     |
| sgst          | Number | Yes      | SGST                     |
| total_price   | Number | Yes      | Total price per item     |

---

### 3.3 Pricing Summary Object

| Field Name       | Type   | Description          |
| ---------------- | ------ | -------------------- |
| subtotal         | Number | Total before tax     |
| total_tax_amount | Number | Total GST            |
| total_amount     | Number | Final payable amount |

---

## 4. APIs

---

### 4.1 Create Purchase Order

**Endpoint**

```
POST /api/po
```

**Request Body**

```json
{
  "pr_id": "pr123",
  "vendor_id": "v123",
  "items": [
    {
      "item_id": "i123",
      "requested_qty": 100,
      "order_qty": 90,
      "unit_price": 50,
      "uom": "Box",
      "gst": 18,
      "cgst": 9,
      "sgst": 9
    }
  ],
  "pricing_summary": {
    "subtotal": 4500,
    "total_tax_amount": 810,
    "total_amount": 5310
  },
  "supporting_documents": [
    "invoice.pdf"
  ],
  "terms_conditions": "Delivery within 7 days"
}
```

**Response (201 Created)**

```json
{
  "id": "po123",
  "status": "CREATED",
  "items": [
    {
      "item_id": "i123",
      "item_name": "Paracetamol 500mg",
      "order_qty": 90,
      "unit_price": 50,
      "total_price": 5310
    }
  ],
  "pricing_summary": {
    "subtotal": 4500,
    "total_tax_amount": 810,
    "total_amount": 5310
  },
  "created_at": "2026-04-17T10:00:00Z"
}
```

---

### 4.2 Get All Purchase Orders

**Endpoint**

```
GET /api/po
```

**Query Parameters (Optional)**

* `page`
* `limit`
* `search` → **search by PO ID only**

**Example**

```
GET /api/po?search=po123
```

**Response (200 OK)**

```json
{
  "data": [
    {
      "id": "po123",
      "total_items": 1,
      "total_quantity": 90,
      "total_amount": 5310,
      "status": "CREATED",
      "created_at": "2026-04-17T10:00:00Z"
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 1
}
```

---

### 4.3 Get Purchase Order by ID

**Endpoint**

```
GET /api/po/{id}
```

**Response (200 OK)**

```json
{
  "id": "po123",
  "items": [
    {
      "item_id": "i123",
      "item_name": "Paracetamol 500mg",
      "requested_qty": 100,
      "order_qty": 90,
      "unit_price": 50,
      "uom": "Box",
      "gst": 18,
      "cgst": 9,
      "sgst": 9,
      "total_price": 5310
    }
  ],
  "pricing_summary": {
    "subtotal": 4500,
    "total_tax_amount": 810,
    "total_amount": 5310
  },
  "supporting_documents": [
    "invoice.pdf"
  ],
  "terms_conditions": "Delivery within 7 days",
  "status": "CREATED",
  "created_at": "2026-04-17T10:00:00Z"
}
```

---

## 5. Business Rules

* PO must always be linked to a valid PR
* Vendor selection is mandatory
* Ordered quantity cannot exceed requested quantity
* PO must exist before GR

---

## 6. Best Practices

* Keep search limited to PO domain
* Return item details in POST & GET by ID
* Keep GET ALL lightweight
* Validate pricing in backend
* Use status lifecycle:
  `CREATED → APPROVED → CLOSED`

---
