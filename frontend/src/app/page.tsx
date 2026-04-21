"use client";

import { useEffect, useState } from "react";
import ItemTable from "@/components/ItemTable";
import { fetchItems, searchItems, deleteItem, Item } from "@/services/api";
import Modal from "@/components/Modal";
import Link from "next/link";

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const [itemToDelete, setItemToDelete] = useState<string | null>(null);

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      setLoading(true);
      const data = await fetchItems(1, 50); // Get first 50 for simplicity
      setItems(data.data);
      setError("");
    } catch (err) {
      setError("Failed to load items. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) {
      return loadItems();
    }

    try {
      setLoading(true);
      const data = await searchItems(searchTerm);
      setItems(data);
      setError("");
    } catch (err) {
      setError("Search failed.");
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = async () => {
    if (!itemToDelete) return;
    try {
      await deleteItem(itemToDelete);
      setItemToDelete(null);
      loadItems();
    } catch (err: any) {
      if (err.message && err.message.toLowerCase().includes('purchase order')) {
        alert("This item is in purchase order");
      } else {
        alert("Failed to delete item.");
      }
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ marginBottom: '0.5rem' }}>Items Dashboard</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage all your procurement items from one place.</p>
        </div>
        <Link href="/new" className="btn btn-primary">+ Create Item</Link>
      </div>

      <div className="glass" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', width: '100%', gap: '1rem' }}>
          <input
            type="text"
            placeholder="Search items by name..."
            className="form-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn btn-outline">Search</button>
          {searchTerm && (
            <button type="button" className="btn btn-outline" onClick={() => { setSearchTerm(''); loadItems(); }}>
              Clear
            </button>
          )}
        </form>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading items...
        </div>
      ) : (
        <ItemTable items={items} onDelete={setItemToDelete} />
      )}

      <Modal
        isOpen={!!itemToDelete}
        onClose={() => setItemToDelete(null)}
        title="Confirm Deletion"
      >
        <p style={{ marginBottom: '1.5rem' }}>Are you sure you want to delete this item? This action cannot be undone.</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button className="btn btn-outline" onClick={() => setItemToDelete(null)}>Cancel</button>
          <button className="btn btn-danger" onClick={confirmDelete}>Delete Item</button>
        </div>
      </Modal>
    </div>
  );
}
