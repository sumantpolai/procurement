"use client";

import { useState, useEffect } from "react";
import { createPR, fetchItems, Item } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function NewPRPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [itemsList, setItemsList] = useState<Item[]>([]);
  const [prItems, setPrItems] = useState<{item_id: string, quantity: number}[]>([
    { item_id: "", quantity: 1 }
  ]);
  
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load available items for selection
    fetchItems(1, 100).then(res => setItemsList(res.data)).catch(console.error);
  }, []);

  const handleAddItemRow = () => {
    setPrItems([...prItems, { item_id: "", quantity: 1 }]);
  };

  const handleRemoveItemRow = (index: number) => {
    setPrItems(prItems.filter((_, i) => i !== index));
  };

  const handleItemChange = (index: number, field: string, value: string | number) => {
    const updated = [...prItems];
    updated[index] = { ...updated[index], [field]: value };
    setPrItems(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    // Validate
    if (prItems.some(i => !i.item_id || i.quantity <= 0)) {
      setError("Please ensure all items are selected and quantity is > 0.");
      return;
    }
    
    setError("");
    setLoading(true);

    try {
      await createPR({
        requested_by: user.id, // using user.id as requested_by string
        items: prItems
      });
      router.push("/prs");
    } catch (err: any) {
      setError(err.message || "Failed to create PR.");
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem', gap: '1rem' }}>
        <Link href="/prs" className="btn btn-outline" style={{ padding: '0.4rem 0.8rem' }}>&larr; Back</Link>
        <h1 style={{ margin: 0 }}>Create Purchase Request</h1>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      <div className="glass" style={{ padding: '2rem' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div>
            <h3 style={{ borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Items Requested</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {prItems.map((prItem, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                  <div style={{ flex: 2, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label className="form-label">Item *</label>
                    <select 
                      required 
                      className="form-input" 
                      value={prItem.item_id} 
                      onChange={(e) => handleItemChange(idx, 'item_id', e.target.value)}
                    >
                      <option value="">-- Select Item --</option>
                      {itemsList.map(item => (
                        <option key={item.id} value={item.id}>{item.name} ({item.code})</option>
                      ))}
                    </select>
                  </div>
                  
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label className="form-label">Quantity *</label>
                    <input 
                      type="number" 
                      min="1" 
                      required 
                      className="form-input" 
                      value={prItem.quantity} 
                      onChange={(e) => handleItemChange(idx, 'quantity', parseInt(e.target.value))}
                    />
                  </div>
                  
                  {prItems.length > 1 && (
                    <button 
                      type="button" 
                      onClick={() => handleRemoveItemRow(idx)}
                      className="btn btn-outline" 
                      style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }}
                    >
                      X
                    </button>
                  )}
                </div>
              ))}
            </div>
            
            <button 
              type="button" 
              onClick={handleAddItemRow}
              className="btn btn-outline" 
              style={{ marginTop: '1rem', width: '100%' }}
            >
              + Add Another Item
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
            <Link href="/prs" className="btn btn-outline">Cancel</Link>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Creating..." : "Create PR"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
