# 🧾 Purchase Request (PR) API Documentation

## 1. Overview

The **Purchase Request (PR) module** is used to request items required in the procurement system.

Each PR contains one or more items along with required quantities and follows a defined lifecycle (draft → approval → processing).

---

## 2. Data Model

### 2.1 Purchase Request (PR)

| Field Name   | Type     | Required | Description              |
| ------------ | -------- | -------- | ------------------------ |
| id           | UUID     | Yes      | Unique PR identifier     |
| requested_by | String   | Yes      | User who created the PR  |
| status       | Enum     | Yes      | Current status of the PR |
| created_at   | DateTime | Yes      | Timestamp of creation    |
| updated_at   | DateTime | No       | Last updated timestamp   |

---

### 2.2 PR Item (Line Items)

| Field Name | Type   | Required | Description              |
| ---------- | ------ | -------- | ------------------------ |
| item_id    | UUID   | Yes      | Reference to Item Master |
| quantity   | Number | Yes      | Required quantity        |

---

## 3. Enum Definitions

### 3.1 `status`

* `draft`
* `submitted`
* `approved`
* `rejected`

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
  "requested_by": "user123",
  "items": [
    {
      "item_id": "a1b2c3d4",
      "quantity": 10
    },
    {
      "item_id": "x9y8z7",
      "quantity": 2
    }
  ]
}
```

**Response (201 Created)**

```json
{
  "id": "pr12345",
  "requested_by": "user123",
  "status": "draft",
  "items": [
    {
      "item_id": "a1b2c3d4",
      "quantity": 10
    },
    {
      "item_id": "x9y8z7",
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
  "requested_by": "user123",
  "status": "draft",
  "items": [
    {
      "item_id": "a1b2c3d4",
      "quantity": 10
    }
  ],
  "created_at": "2026-04-17T12:00:00Z",
  "updated_at": "2026-04-17T12:10:00Z"
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
      "requested_by": "user123",
      "status": "draft",
      "total_items": 2,
      "created_at": "2026-04-17T12:00:00Z"
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 1
}
```

---

### 4.4 Update PR Status

**Endpoint**

```
PATCH /api/pr/{id}/status
```

**Request Body**

```json
{
  "status": "submitted"
}
```

**Response (200 OK)**

```json
{
  "message": "PR status updated successfully"
}
```

---

## 5. Validation Rules

* `requested_by` must not be empty
* `items` must not be empty
* `item_id` must exist in Item Master
* `quantity` must be greater than 0
* Duplicate `item_id` entries are not allowed in the same PR
* Status must follow valid transitions

---

## 6. Relationships

* One PR → Many Items (1:N relationship)
* `item_id` is a foreign key from Item Master

---

## 7. Database Design

### Table: `purchase_request`

| Column       | Type      |
| ------------ | --------- |
| id           | UUID      |
| requested_by | VARCHAR   |
| status       | VARCHAR   |
| created_at   | TIMESTAMP |
| updated_at   | TIMESTAMP |

---

### Table: `pr_items`

| Column   | Type |
| -------- | ---- |
| id       | UUID |
| pr_id    | UUID |
| item_id  | UUID |
| quantity | INT  |

---

## 8. Status Flow

```
draft → submitted → approved → rejected
```

---

## 9. Best Practices

* Use database transactions while creating PR
* Validate all item references before saving
* Add index on `item_id` for faster lookup
* Keep PR lightweight (do not duplicate item data)
* Maintain consistent enum naming (lowercase)

---

## 10. Future Enhancements

* Add approval workflow (multi-level)
* Add `updated_by` field
* Add comments/remarks on approval
* Implement soft delete (`is_active`)
* Add notifications on status change

---
