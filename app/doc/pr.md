# 🧾 Purchase Request (PR) API Documentation

## 1. Overview

The **Purchase Request (PR) module** allows users to create and manage requests for items required in the procurement system.

Each PR can contain **multiple items**, along with their **requested quantities**.

---

## 2. Data Model

### 2.1 Purchase Request (PR)

| Field Name | Type     | Required | Description              |
| ---------- | -------- | -------- | ------------------------ |
| id         | UUID     | Yes      | Unique PR identifier     |
| created_at | DateTime | Yes      | Timestamp of PR creation |

---

### 2.2 PR Item (Line Items)

| Field Name | Type   | Required | Description              |
| ---------- | ------ | -------- | ------------------------ |
| item_id    | UUID   | Yes      | Reference to Item Master |
| item_type  | Enum   | Yes      | Type of item             |
| quantity   | Number | Yes      | Required quantity        |

---

## 3. Enum Definitions

### `item_type`

* text
* service
* inventory_item

---

## 4. API Endpoints

---

### 4.1 Create Purchase Request

**Endpoint**

```
POST /api/pr
```

**Request Body**

```json
{
  "items": [
    {
      "item_id": "a1b2c3d4",
      "item_type": "inventory_item",
      "quantity": 10
    },
    {
      "item_id": "x9y8z7",
      "item_type": "service",
      "quantity": 2
    }
  ]
}
```

**Response (201 Created)**

```json
{
  "id": "pr12345",
  "items": [
    {
      "item_id": "a1b2c3d4",
      "item_type": "inventory_item",
      "quantity": 10
    },
    {
      "item_id": "x9y8z7",
      "item_type": "service",
      "quantity": 2
    }
  ],
  "created_at": "2026-04-17T12:00:00Z"
}
```

---

### 4.2 Get PR by ID

**Endpoint**

```
GET /api/pr/{id}
```

**Response (200 OK)**

```json
{
  "id": "pr12345",
  "items": [
    {
      "item_id": "a1b2c3d4",
      "item_type": "inventory_item",
      "quantity": 10
    }
  ],
  "created_at": "2026-04-17T12:00:00Z"
}
```

**Error (404 Not Found)**

```json
{
  "error": "PR_NOT_FOUND",
  "message": "Purchase Request not found"
}
```

---

### 4.3 Get All PRs

**Endpoint**

```
GET /api/pr
```

**Query Parameters (Optional)**

| Parameter | Type | Default | Description      |
| --------- | ---- | ------- | ---------------- |
| page      | int  | 1       | Page number      |
| limit     | int  | 10      | Records per page |

**Response (200 OK)**

```json
{
  "data": [
    {
      "id": "pr12345",
      "created_at": "2026-04-17T12:00:00Z"
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 1
}
```

---

## 5. Validation Rules

* `items` must not be empty
* `item_id` must exist in Item Master
* `item_type` must be valid
* `quantity` must be greater than 0

---

## 6. Relationships

* One PR → Many Items (1:N relationship)
* `item_id` is a foreign key from Item Master

---

## 7. Database Design

### Table: purchase_request

| Column     | Type      |
| ---------- | --------- |
| id         | UUID      |
| created_at | TIMESTAMP |

---

### Table: pr_items

| Column    | Type    |
| --------- | ------- |
| id        | UUID    |
| pr_id     | UUID    |
| item_id   | UUID    |
| item_type | VARCHAR |
| quantity  | INT     |

---

## 8. Best Practices

* Use transactions while creating PR
* Validate items before saving
* Add index on `item_id`
* Keep enum values consistent

---

## 9. Future Enhancements

* Add status (`draft`, `approved`, `rejected`)
* Add approval workflow
* Add `requested_by` field
* Add audit fields (`created_by`, `updated_at`)
* Implement soft delete

---

## 🔥 Design Suggestion

Instead of storing `item_type` in PR, prefer:

```json
{
  "item_id": "a1b2c3d4",
  "quantity": 10
}
```

Then fetch item details from Item Master.

---
