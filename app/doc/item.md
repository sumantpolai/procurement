# 📦 Item Master API Documentation

## 1. Overview
The Item Master module is responsible for managing all items used in the procurement system. It supports creation, retrieval, and search operations.

---

## 2. Data Model

| Field Name     | Type   | Required | Description |
|----------------|--------|----------|-------------|
| id             | UUID   | Yes      | Unique identifier for the item |
| name           | String | Yes      | Name of the item |
| item_type      | Enum   | Yes      | Type of the item |
| item_category  | Enum   | Yes      | Category of the item |
| uom            | String | Yes      | Unit of Measurement |
| created_at     | Date   | Yes      | Timestamp of creation |

---

## 3. Enum Definitions

### 3.1 item_type
- `text`
- `service`
- `inventory_item`

### 3.2 item_category
- `consumable`
- `pharmacitucals`
- `equipment`
- `other`

---

## 4. APIs

---

### 4.1 Create Item

**Endpoint**
  /item
**Request Body**
```json
{
  "name": "Paracetamol 500mg",
  "item_type": "inventory_item",
  "item_category": "pharmacitucals",
  "uom": "Box"
}


{
  "id": "a1b2c3d4",
  "name": "Paracetamol 500mg",
  "item_type": "inventory_item",
  "item_category": "pharmacitucals",
  "uom": "Box",
  "created_at": "2026-04-17T10:00:00Z"
}