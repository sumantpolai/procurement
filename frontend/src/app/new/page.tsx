"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import ItemForm from "@/components/ItemForm";
import { createItem, Item } from "@/services/api";

export default function CreateItemPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (data: Partial<Item>) => {
    try {
      setLoading(true);
      setError("");
      await createItem(data);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to create item");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>Create New Item</h1>
        <p style={{ color: 'var(--text-muted)' }}>Add a new procurement item to the catalog.</p>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      <ItemForm onSubmit={handleSubmit} isLoading={loading} />
    </div>
  );
}
