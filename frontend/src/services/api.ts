export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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

export interface PaginatedResponse {
  data: Item[];
  page: number;
  limit: number;
  total: number;
}

export const fetchItems = async (page = 1, limit = 10): Promise<PaginatedResponse> => {
  const res = await fetch(`${API_URL}/api/items/?page=${page}&limit=${limit}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch items');
  return res.json();
};

export const searchItems = async (name: string): Promise<Item[]> => {
  const res = await fetch(`${API_URL}/api/items/search/?name=${encodeURIComponent(name)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to search items');
  return res.json();
};

export const createItem = async (itemData: Partial<Item>): Promise<Item> => {
  const res = await fetch(`${API_URL}/api/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(itemData),
  });
  if (!res.ok) throw new Error('Failed to create item');
  return res.json();
};

export const updateItem = async (id: string, itemData: Partial<Item>): Promise<Item> => {
  const res = await fetch(`${API_URL}/api/items/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(itemData),
  });
  if (!res.ok) throw new Error('Failed to update item');
  return res.json();
};

export const deleteItem = async (id: string): Promise<{message: string}> => {
  const res = await fetch(`${API_URL}/api/items/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || errorData?.message || 'Failed to delete item');
  }
  return res.json();
};
