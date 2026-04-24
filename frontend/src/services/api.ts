export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// ========================
// AUTH
// ========================
export const login = async (email: string, password: string) => {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to login');
  }
  return res.json();
};

export const register = async (userData: any) => {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail?.message || errorData?.detail || 'Failed to register');
  }
  return res.json();
};

export const fetchMe = async () => {
  const res = await fetch(`${API_URL}/auth/me`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch user');
  return res.json();
};

export const getGoogleAuthUrl = async () => {
  const res = await fetch(`${API_URL}/auth/google/url`);
  if (!res.ok) throw new Error('Failed to get Google Auth URL');
  return res.json();
};

export const handleGoogleCallback = async (code: string, state: string) => {
  const params = new URLSearchParams({ code, state });
  const res = await fetch(`${API_URL}/auth/google/callback?${params.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail?.message || errorData?.detail || 'Failed to authenticate with Google');
  }
  return res.json();
};

// ========================
// ITEMS
// ========================
export interface Item {
  id: string;
  code: string;
  name: string;
  item_type: 'text' | 'service' | 'inventory_item';
  item_category: 'consumable' | 'Pharmaceuticals' | 'equipment' | 'other';
  uom: string;
  status: 'Draft' | 'Approved' | 'Rejected';
  rejection_reason?: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  limit: number;
  total: number;
}

export const fetchItems = async (page = 1, limit = 10): Promise<PaginatedResponse<Item>> => {
  const res = await fetch(`${API_URL}/api/items/?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch items');
  return res.json();
};

export const searchItems = async (name: string): Promise<Item[]> => {
  const res = await fetch(`${API_URL}/api/items/search/?name=${encodeURIComponent(name)}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to search items');
  return res.json();
};

export const createItem = async (itemData: Partial<Item>): Promise<Item> => {
  const res = await fetch(`${API_URL}/api/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(itemData),
  });
  if (!res.ok) throw new Error('Failed to create item');
  return res.json();
};

export const updateItem = async (id: string, itemData: Partial<Item>): Promise<Item> => {
  const res = await fetch(`${API_URL}/api/items/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(itemData),
  });
  if (!res.ok) throw new Error('Failed to update item');
  return res.json();
};

export const deleteItem = async (id: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/api/items/${id}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || errorData?.message || 'Failed to delete item');
  }
  return res.json();
};

// ========================
// VENDORS
// ========================
export interface Vendor {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  pan_no: string;
  gst_no?: string | null;
  bank_details: {
    bank_name: string;
    account_number: string;
    ifsc_code: string;
    branch: string;
    address: string;
  };
  created_at: string;
}

export const fetchVendors = async (page = 1, limit = 10): Promise<Vendor[]> => {
  const res = await fetch(`${API_URL}/api/vendors/?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch vendors');
  return res.json();
};

export const searchVendors = async (search: string): Promise<Vendor[]> => {
  const res = await fetch(`${API_URL}/api/vendors/search?search=${encodeURIComponent(search)}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to search vendors');
  return res.json();
};

export const createVendor = async (vendorData: Partial<Vendor>): Promise<Vendor> => {
  const res = await fetch(`${API_URL}/api/vendors/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(vendorData),
  });
  if (!res.ok) throw new Error('Failed to create vendor');
  return res.json();
};

export const updateVendor = async (id: string, vendorData: Partial<Vendor>): Promise<Vendor> => {
  const res = await fetch(`${API_URL}/api/vendors/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(vendorData),
  });
  if (!res.ok) throw new Error('Failed to update vendor');
  return res.json();
};

export const deleteVendor = async (id: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/api/vendors/${id}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || errorData?.message || 'Failed to delete vendor');
  }
  return res.json();
};

// ========================
// PR (Purchase Requests)
// ========================
export interface PRItem {
  item_id: string;
  quantity: number;
  item_name?: string;
  uom?: string;
}

export interface PR {
  id: string;
  pr_number: string;
  requested_by: string;
  status: string;
  items: PRItem[];
  created_at: string;
}

export const fetchPRs = async (page = 1, limit = 10): Promise<PaginatedResponse<PR>> => {
  const res = await fetch(`${API_URL}/api/prs/?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch PRs');
  return res.json();
};

export const createPR = async (prData: any): Promise<PR> => {
  const res = await fetch(`${API_URL}/api/prs/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(prData),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || 'Failed to create PR');
  }
  return res.json();
};

export const updatePRStatus = async (id: string, status: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/api/prs/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update PR status');
  return res.json();
};

// ========================
// PO (Purchase Orders)
// ========================
export interface POItem {
  item_id: string;
  ordered_qty: number;
  unit_price: number;
  gst_percent: number;
  cgst_percent: number;
  sgst_percent: number;
  igst_percent: number;
  uom: string;
  hsn_code?: string;
}

export interface PO {
  id: string;
  po_number: string;
  vendor_id: string;
  vendor_name?: string;
  store_id: string;
  po_type: string;
  po_date: string;
  status: string;
  items: POItem[];
  total_amount?: number;
  created_at: string;
}

export const fetchPOs = async (page = 1, limit = 10): Promise<PaginatedResponse<PO>> => {
  const res = await fetch(`${API_URL}/api/pos/?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch POs');
  return res.json();
};

export const createPO = async (poData: any): Promise<PO> => {
  const res = await fetch(`${API_URL}/api/pos/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(poData),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || 'Failed to create PO');
  }
  return res.json();
};

export const updatePOStatus = async (id: string, status: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/api/pos/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update PO status');
  return res.json();
};
