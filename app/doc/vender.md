# 🚀 Vendor Management API using FastAPI

## 📌 Project Overview

This API allows you to manage vendor details including:
- Name
- Email (unique)
- Phone
- Bank Details (Bank Name, Account Number, IFSC Code, Branch, Address)

## 📌 Database model
The Vendor model is defined as follows:


| Field Name     | Type   | Required | Description |
|----------------|--------|----------|-------------|
| id             | Integer| Yes      | Unique identifier for the vendor (auto-increment) |
| name           | String | Yes      | Name of the vendor |
| email          | String | Yes      | Email of the vendor (unique) |
| phone          | String | Yes      | Phone number of the vendor |
| bank_name      | String | Yes      | Name of the bank |
| account_number | String | Yes      | Bank account number |
| ifsc_code      | String | Yes      | IFSC code of the bank |
| branch         | String | Yes      | Branch of the bank |
| address        | String | Yes      | Address of the bank |



## 📌 Vendor Details Structure

Each vendor contains the following information:

```json
{
  "id": 1,
  "name": "ABC Traders",
  "email": "abc@gmail.com",
  "phone": "9876543210",
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_number": "1234567890",
    "ifsc_code": "SBIN0001234",
    "branch": "Bhubaneswar Main Branch",
    "address": "Bhubaneswar, Odisha, India"
  }
}

## 📌 API Endpoints

### 1. Create Vendor
Method: POST
- **Endpoint**: `/vendor`

{
  "name": "ABC Traders",
  "email": "abc@gmail.com",
  "phone": "9876543210",
  "bank_name": "State Bank of India",
  "account_number": "1234567890",
  "ifsc_code": "SBIN0001234",
  "branch": "Bhubaneswar Main Branch",
  "address": "Bhubaneswar, Odisha"
}

# 2. Get All Vendors
Method: GET
Endpoint: /vendors/

[
  {
    "id": 1,
    "name": "ABC Traders",
    "email": "abc@gmail.com",
    "phone": "9876543210",
    "bank_details": {
      "bank_name": "State Bank of India",
      "account_number": "1234567890",
      "ifsc_code": "SBIN0001234",
      "branch": "Bhubaneswar Main Branch",
      "address": "Bhubaneswar, Odisha"
    }
  }
]

### 3. Get Vendor by ID
- **Endpoint**: `/vendor/{id}`

{
  "id": 1,
  "name": "ABC Traders",
  "email": "abc@gmail.com",
  "phone": "9876543210",
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_number": "1234567890",
    "ifsc_code": "SBIN0001234",
    "branch": "Bhubaneswar Main Branch",
    "address": "Bhubaneswar, Odisha"
  }
}