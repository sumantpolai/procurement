"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import ItemForm from "@/components/ItemForm";
import { updateItem, fetchItems, Item } from "@/services/api";

export default function EditItemPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  
  const [initialData, setInitialData] = useState<Partial<Item> | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Ideally we would have a fetchItemById, but we can search or find it from the list
    // A quick hack for now is to fetch recent items and find it, or since API doesn't have fetchById,
    // wait, I will check the API again. Ah, no GET /api/items/{id} in FastAPI routes!
    // So we fetch the list and find it. Or we assume it's there.
    
    const loadData = async () => {
      try {
        const res = await fetchItems(1, 100);
        const item = res.data.find(i => i.id === id);
        if (item) {
          setInitialData(item);
        } else {
          setError("Item not found");
        }
      } catch (err) {
        setError("Failed to fetch item data");
      } finally {
        setFetching(false);
      }
    };
    
    if (id) loadData();
  }, [id]);

  const handleSubmit = async (data: Partial<Item>) => {
    try {
      setLoading(true);
      setError("");
      await updateItem(id, data);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to update item");
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return <div style={{ textAlign: 'center', padding: '3rem' }}>Loading item data...</div>;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>Edit Item</h1>
        <p style={{ color: 'var(--text-muted)' }}>Update the details of this procurement item.</p>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      {initialData && (
        <ItemForm initialData={initialData} onSubmit={handleSubmit} isLoading={loading} />
      )}
    </div>
  );
}
