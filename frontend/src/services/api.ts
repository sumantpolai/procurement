export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

const getErrorMessage = async (res: Response, fallback: string) => {
  const errorData = await res.json().catch(() => null);

  if (typeof errorData?.detail === 'string') return errorData.detail;
  if (typeof errorData?.detail?.message === 'string') return errorData.detail.message;
  if (typeof errorData?.message === 'string') return errorData.message;

  return fallback;
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

export const register = async (userData: Record<string, unknown>) => {
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
  const res = await fetch(`${API_URL}/items/?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to fetch items'));
  return res.json();
};

export const searchItems = async (name: string): Promise<Item[]> => {
  const res = await fetch(`${API_URL}/items/search/?name=${encodeURIComponent(name)}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to search items'));
  return res.json();
};

export const createItem = async (itemData: Partial<Item>): Promise<Item> => {
  const res = await fetch(`${API_URL}/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(itemData),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to create item'));
  return res.json();
};

export const updateItem = async (id: string, itemData: Partial<Item>): Promise<Item> => {
  const res = await fetch(`${API_URL}/items/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(itemData),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to update item'));
  return res.json();
};

export const deleteItem = async (id: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/items/${id}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to delete item'));
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

export interface VendorPayload {
  name: string;
  email: string;
  phone: string;
  pan_no: string;
  gst_no?: string | null;
  bank_name: string;
  account_number: string;
  ifsc_code: string;
  branch: string;
  address: string;
}

export type VendorUpdatePayload = Partial<VendorPayload>;

export interface VendorStatusUpdatePayload {
  status: string;
  approved_by?: string | null;
  rejected_reason?: string | null;
}

const normalizeVendorPayload = (
  vendorData: Partial<Vendor> & Partial<VendorPayload> & { bank_details?: Vendor['bank_details'] }
): VendorUpdatePayload => {
  const bankDetails = vendorData.bank_details;

  return {
    name: vendorData.name,
    email: vendorData.email,
    phone: vendorData.phone,
    pan_no: vendorData.pan_no,
    gst_no: vendorData.gst_no,
    bank_name: vendorData.bank_name ?? bankDetails?.bank_name,
    account_number: vendorData.account_number ?? bankDetails?.account_number,
    ifsc_code: vendorData.ifsc_code ?? bankDetails?.ifsc_code,
    branch: vendorData.branch ?? bankDetails?.branch,
    address: vendorData.address ?? bankDetails?.address,
  };
};

export const fetchVendors = async (page = 1, limit = 10): Promise<Vendor[]> => {
  const res = await fetch(`${API_URL}/vendors/?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to fetch vendors'));
  return res.json();
};

export const searchVendors = async (search: string): Promise<Vendor[]> => {
  const res = await fetch(`${API_URL}/vendors/search?search=${encodeURIComponent(search)}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to search vendors'));
  return res.json();
};

export const createVendor = async (vendorData: VendorPayload): Promise<Vendor> => {
  const res = await fetch(`${API_URL}/vendors/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(normalizeVendorPayload(vendorData)),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to create vendor'));
  return res.json();
};

export const updateVendor = async (
  id: string,
  vendorData: VendorUpdatePayload | Partial<Vendor>
): Promise<Vendor> => {
  const res = await fetch(`${API_URL}/vendors/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(normalizeVendorPayload(vendorData)),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to update vendor'));
  return res.json();
};

export const deleteVendor = async (id: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/vendors/${id}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to delete vendor'));
  return res.json();
};

export const updateVendorStatus = async (
  id: string,
  statusData: VendorStatusUpdatePayload
): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/vendors/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(statusData),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to update vendor status'));
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
  const res = await fetch(`${API_URL}/prs?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to fetch PRs'));
  return res.json();
};

export const createPR = async (prData: Record<string, unknown>): Promise<PR> => {
  const res = await fetch(`${API_URL}/prs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(prData),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to create PR'));
  return res.json();
};

export const updatePRStatus = async (id: string, status: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/prs/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to update PR status'));
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
  const res = await fetch(`${API_URL}/pos?page=${page}&limit=${limit}`, {
    cache: 'no-store',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to fetch POs'));
  return res.json();
};

export const createPO = async (poData: Record<string, unknown>): Promise<PO> => {
  const res = await fetch(`${API_URL}/pos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(poData),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to create PO'));
  return res.json();
};

export const updatePOStatus = async (id: string, status: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/pos/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(await getErrorMessage(res, 'Failed to update PO status'));
  return res.json();
};
