# JWT Authentication & RBAC Guide

## Overview
Production-level JWT authentication with Role-Based Access Control (RBAC) implemented.

## Roles & Permissions

### 1. Store Staff (`store_staff`)
- **PR**: Read, Create, Update
- **PO**: Read only

### 2. Store Manager (`store_manager`)
- **PR**: Read, Create, Update, Update Status
- **PO**: Read only

### 3. Purchase Staff (`purchase_staff`)
- **PR**: Read only
- **PO**: Read, Create, Update
- **Vendor**: Read, Create, Update

### 4. Purchase Manager (`purchase_manager`)
- **PR**: Read only
- **PO**: Read, Create, Update, Update Status
- **Vendor**: Read, Create, Update, Update Status

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update .env
Already configured with:
```
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Reset Database & Create Default Users
```bash
py reset_db.py
```

This creates 4 default users:
- `store_manager` / `password123`
- `store_staff` / `password123`
- `purchase_manager` / `password123`
- `purchase_staff` / `password123`

## API Usage

### 1. Register New User
**POST** `/auth/register`
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "store_staff"
}
```

**Roles**: `store_staff`, `store_manager`, `purchase_staff`, `purchase_manager`

### 2. Login (Get Token)
**POST** `/auth/login`

**Form Data:**
- username: `store_manager`
- password: `password123`

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Alternative JSON Login:**
**POST** `/auth/login-json`
```json
{
  "username": "store_manager",
  "password": "password123"
}
```

### 3. Use Token in Requests

Add to headers:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example with curl:**
```bash
curl -X GET "http://localhost:8000/pr" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Example with Swagger UI:**
1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button (top right)
3. Enter: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize"

## Access Control Matrix

| Endpoint | Store Staff | Store Manager | Purchase Staff | Purchase Manager |
|----------|-------------|---------------|----------------|------------------|
| **PR - Read** | ✅ | ✅ | ✅ | ✅ |
| **PR - Create** | ✅ | ✅ | ❌ | ❌ |
| **PR - Update** | ✅ | ✅ | ❌ | ❌ |
| **PR - Update Status** | ❌ | ✅ | ❌ | ❌ |
| **PO - Read** | ✅ | ✅ | ✅ | ✅ |
| **PO - Create** | ❌ | ❌ | ✅ | ✅ |
| **PO - Update** | ❌ | ❌ | ✅ | ✅ |
| **PO - Update Status** | ❌ | ❌ | ❌ | ✅ |

## Testing Scenarios

### Scenario 1: Store Manager Creates PR
```bash
# 1. Login as store_manager
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"store_manager","password":"password123"}'

# 2. Create PR (will succeed)
curl -X POST "http://localhost:8000/pr" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_by": "store_manager",
    "items": [{"item_id": "123e4567-e89b-12d3-a456-426614174000", "quantity": 10}]
  }'

# 3. Update PR status (will succeed)
curl -X PATCH "http://localhost:8000/pr/PR_ID/status" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "submitted"}'
```

### Scenario 2: Purchase Staff Creates PO
```bash
# 1. Login as purchase_staff
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"purchase_staff","password":"password123"}'

# 2. Create PO (will succeed)
curl -X POST "http://localhost:8000/po" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...PO_DATA...}'

# 3. Update PO status (will FAIL - only purchase_manager can do this)
curl -X PATCH "http://localhost:8000/po/PO_ID/status" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

### Scenario 3: Unauthorized Access
```bash
# Store staff tries to create PO (will FAIL)
curl -X POST "http://localhost:8000/po" \
  -H "Authorization: Bearer STORE_STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...PO_DATA...}'

# Response: 403 Forbidden
{
  "detail": "Access denied. Required roles: ['purchase_staff', 'purchase_manager']"
}
```

## Error Responses

### 401 Unauthorized (Invalid/Missing Token)
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden (Insufficient Permissions)
```json
{
  "detail": "Access denied. Required roles: ['store_manager']"
}
```

## Security Features

1. **Password Hashing**: Bcrypt with salt
2. **JWT Tokens**: HS256 algorithm
3. **Token Expiration**: 30 minutes (configurable)
4. **Role-Based Access**: Enforced at endpoint level
5. **Active User Check**: Inactive users cannot access
6. **Production-Ready**: Follows industry best practices

## Token Payload
```json
{
  "sub": "store_manager",
  "role": "store_manager",
  "exp": 1713456789
}
```

## Run the Application
```bash
py -m uvicorn app.main:app --reload
```

Access:
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
