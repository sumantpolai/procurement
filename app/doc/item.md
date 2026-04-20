# 📦 Item Master API Documentation

# TODO





- Sub delete API for items that are not used in any purchase orders

## 1. Overview

The Item Master module is responsible for managing all items used in the procurement system. It supports creation, retrieval, and search operations.

---

## 2. Data Model

| Field Name    | Type   | Required | Description                    |
| ------------- | ------ | -------- | ------------------------------ |
| id            | UUID   | Yes      | Unique identifier for the item |
| name          | String | Yes      | Name of the item               |
| item_type     | Enum   | Yes      | Type of the item               |
| item_category | Enum   | Yes      | Category of the item           |
| uom           | String | Yes      | Unit of Measurement            |
| created_at    | Date   | Yes      | Timestamp of creation          |

---

## 3. Enum Definitions

### 3.1 item_type

* `text`
* `service`
* `inventory_item`

### 3.2 item_category

* `consumable`
* `Pharmaceuticals`
* `equipment`
* `other`

---

## 4. APIs

### 4.1 Create Item

**Endpoint**

```
POST /api/items
```

**Request Body**

```json
{
  "name": "Paracetamol 500mg",
  "item_type": "inventory_item",
  "item_category": "Pharmaceuticals",
  "uom": "Box"
}
```

**Response (201 Created)**

```json
{
  "id": "a1b2c3d4",
  "name": "Paracetamol 500mg",
  "item_type": "inventory_item",
  "item_category": "Pharmaceuticals",
  "uom": "Box",
  "created_at": "2026-04-17T10:00:00Z"
}
```

---

### 4.2 Get All Items

**Endpoint**

```
GET /api/items
```

**Query Parameters (Optional)**

* `page` (default: 1)
* `limit` (default: 10)

**Response (200 OK)**

```json
{
  "data": [
    {
      "id": "a1",
      "name": "Item A",
      "item_type": "service",
      "item_category": "other",
      "uom": "Unit"
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 1
}
```

---

### 4.3 Get Item by ID

**Endpoint**

```
GET /api/items/{id}
```

**Response (200 OK)**

```json
{
  "id": "a1b2c3d4",
  "name": "Paracetamol 500mg",
  "item_type": "inventory_item",
  "item_category": "Pharmaceuticals",
  "uom": "Box"
}
```

**Error (404 Not Found)**

```json
{
  "message": "Item not found"
}
```

---

### 4.4 Search Items

**Endpoint**

```
GET /api/items/search?name=para
```

**Response (200 OK)**

```json
{
  "data": [
    {
      "id": "a1b2c3d4",
      "name": "Paracetamol 500mg",
      "item_type": "inventory_item",
      "item_category": "Pharmaceuticals",
      "uom": "Box"
    }
  ]
}
```

**Behavior**

* Case-insensitive search
* Partial match supported

---

## 5. Best Practices

* Use UUIDs for IDs
* Add indexing on `name` for faster search
* Validate enums strictly
* Add audit fields (`created_by`, `updated_at`) if required

---
