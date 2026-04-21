# 🚀 Vendor Management API

---

## 📌 1. Overview

The Vendor module manages vendor details including contact information, bank details, and approval workflow in the procurement system.

### ✨ Features

* Create Vendor
* Get All Vendors (with pagination)
* Search Vendors (name/email)
* Get Vendor by ID
* Update Vendor
* Soft Delete Vendor
* Status Workflow (Draft → Approved / Rejected)

---

## 📌 2. Data Model

### Vendor Table

| Field Name      | Type     | Required | Description                 |
| --------------- | -------- | -------- | --------------------------- |
| id              | Integer  | Yes      | Auto-increment primary key  |
| name            | String   | Yes      | Vendor name                 |
| email           | String   | Yes      | Unique email                |
| phone           | String   | Yes      | Phone number                |
| bank_name       | String   | Yes      | Bank name                   |
| account_number  | String   | Yes      | Account number              |
| ifsc_code       | String   | Yes      | IFSC code                   |
| branch          | String   | Yes      | Bank branch                 |
| address         | String   | Yes      | Bank address                |
| status          | String   | Yes      | draft / approved / rejected |
| approved_by     | String   | No       | Approved by user            |
| rejected_reason | String   | No       | Reason for rejection        |
| is_active       | Boolean  | Yes      | Soft delete flag            |
| created_at      | DateTime | Yes      | Timestamp of creation       |

---

## 📌 3. API Endpoints

---

### 🔹 3.1 Create Vendor

**POST** `/api/vendors`

#### Request Body

```json
{
  "name": "ABC Traders",
  "email": "abc@gmail.com",
  "phone": "9876543210",
  "bank_name": "SBI",
  "account_number": "1111111111",
  "ifsc_code": "SBIN0001111",
  "branch": "Bhubaneswar",
  "address": "Odisha"
}
```

#### Response

```json
{
  "id": 1,
  "name": "ABC Traders",
  "email": "abc@gmail.com",
  "phone": "9876543210",
  "status": "draft",
  "bank_details": {
    "bank_name": "SBI",
    "account_number": "1111111111",
    "ifsc_code": "SBIN0001111",
    "branch": "Bhubaneswar",
    "address": "Odisha"
  },
  "created_at": "2026-04-17T10:00:00Z"
}
```

---

### 🔹 3.2 Get All Vendors

**GET** `/api/vendors?page=1&limit=10`

#### Response

```json
[
  {
    "id": 1,
    "name": "ABC Traders",
    "email": "abc@gmail.com",
    "phone": "9876543210",
    "status": "draft",
    "bank_details": {
      "bank_name": "SBI",
      "account_number": "1111111111",
      "ifsc_code": "SBIN0001111",
      "branch": "Bhubaneswar",
      "address": "Odisha"
    },
    "created_at": "2026-04-17T10:00:00Z"
  }
]
```

---

### 🔹 3.3 Search Vendors

**GET** `/api/vendors/search?search=abc`

#### Features

* Case-insensitive search
* Searches in **name and email**
* Partial match supported

#### Examples

```
/api/vendors/search?search=abc
/api/vendors/search?search=gmail
/api/vendors/search?search=ABC
```

---

### 🔹 3.4 Get Vendor by ID

**GET** `/api/vendors/{id}`

#### Response

```json
{
  "id": 1,
  "name": "ABC Traders",
  "email": "abc@gmail.com",
  "phone": "9876543210",
  "status": "draft",
  "bank_details": {
    "bank_name": "SBI",
    "account_number": "1111111111",
    "ifsc_code": "SBIN0001111",
    "branch": "Bhubaneswar",
    "address": "Odisha"
  },
  "created_at": "2026-04-17T10:00:00Z"
}
```

#### Error

```json
{
  "detail": "Vendor not found"
}
```

---

### 🔹 3.5 Update Vendor

**PUT** `/api/vendors/{id}`

#### Request Body (Partial allowed)

```json
{
  "name": "Updated Vendor",
  "phone": "9999999999"
}
```

---

### 🔹 3.6 Delete Vendor (Soft Delete)

**DELETE** `/api/vendors/{id}`

#### Response

```json
{
  "message": "Vendor deleted successfully"
}
```

#### Behavior

* Sets `is_active = false`
* Vendor will not appear in future queries

---

### 🔹 3.7 Update Vendor Status

**PATCH** `/api/vendors/{id}/status`

---

#### ✅ Approve Vendor

```json
{
  "status": "approved",
  "approved_by": "admin"
}
```

---

#### ❌ Reject Vendor

```json
{
  "status": "rejected",
  "rejected_reason": "Invalid documents"
}
```

---

#### ❌ Invalid Status

```json
{
  "detail": "Invalid status"
}
```

---

## 📌 4. Validation Rules

* Email must be unique
* All required fields must be provided
* `search` parameter is required for search API
* `approved_by` required when status = approved
* `rejected_reason` required when status = rejected
* Only active vendors are returned

---

## 📌 5. Status Flow

```
draft → approved
draft → rejected
```

---

## 📌 6. Database Constraints

* Unique constraint on `email`
* NOT NULL constraints on required fields
* Default values:

  * `status = draft`
  * `is_active = true`

---

## 📌 7. Best Practices

* Use pagination for large datasets
* Do not expose sensitive data unnecessarily
* Validate all inputs using Pydantic schemas
* Keep response structure consistent
* Use soft delete instead of hard delete

---

## 📌 8. Future Enhancements

* Add audit fields (`updated_at`, `updated_by`)
* Implement role-based access control (RBAC)
* Add advanced filtering (status-based search)
* Add multi-level approval workflow

---

## 🎯 Final Status

✔ Fully implemented
✔ Tested via Postman
✔ Production-ready
✔ Clean architecture

---
