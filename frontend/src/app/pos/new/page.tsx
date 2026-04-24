"use client";

import { useState, useEffect } from "react";
import { createPO, fetchItems, fetchVendors, Item, Vendor } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function NewPOPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [itemsList, setItemsList] = useState<Item[]>([]);
  const [vendorsList, setVendorsList] = useState<Vendor[]>([]);
  
  const [formData, setFormData] = useState({
    vendor_id: "",
    po_type: "standard",
    matching_type: "two_way",
    po_date: new Date().toISOString().split('T')[0]
  });

  const [poItems, setPoItems] = useState<{
    item_id: string;
    ordered_qty: number;
    unit_price: number;
    gst_percent: number;
    cgst_percent: number;
    sgst_percent: number;
    igst_percent: number;
    uom: string;
  }>([{
    item_id: "", ordered_qty: 1, unit_price: 0,
    gst_percent: 0, cgst_percent: 0, sgst_percent: 0, igst_percent: 0, uom: "pcs"
  }]);
  
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchItems(1, 100).then(res => setItemsList(res.data)).catch(console.error);
    fetchVendors(1, 100).then(res => setVendorsList(res)).catch(console.error);
  }, []);

  const handleAddItemRow = () => {
    setPoItems([...poItems, {
      item_id: "", ordered_qty: 1, unit_price: 0,
      gst_percent: 0, cgst_percent: 0, sgst_percent: 0, igst_percent: 0, uom: "pcs"
    }]);
  };

  const handleRemoveItemRow = (index: number) => {
    setPoItems(poItems.filter((_, i) => i !== index));
  };

  const handleItemChange = (index: number, field: string, value: string | number) => {
    const updated = [...poItems];
    updated[index] = { ...updated[index], [field]: value };
    
    // Auto populate UOM when item is selected
    if (field === 'item_id') {
      const selectedItem = itemsList.find(i => i.id === value);
      if (selectedItem) {
        updated[index].uom = selectedItem.uom;
      }
    }
    
    setPoItems(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    if (!formData.vendor_id || poItems.some(i => !i.item_id || i.ordered_qty <= 0)) {
      setError("Please ensure vendor and all items are valid.");
      return;
    }
    
    setError("");
    setLoading(true);

    try {
      // Use mock UUIDs for store and location as discussed
      const mockStoreId = "11111111-1111-1111-1111-111111111111";
      const mockLocationId = "22222222-2222-2222-2222-222222222222";

      await createPO({
        ...formData,
        store_id: mockStoreId,
        location_id: mockLocationId,
        created_by: user.id, // AuthContext user ID
        items: poItems
      });
      router.push("/pos");
    } catch (err: any) {
      setError(err.message || "Failed to create PO.");
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem', gap: '1rem' }}>
        <Link href="/pos" className="btn btn-outline" style={{ padding: '0.4rem 0.8rem' }}>&larr; Back</Link>
        <h1 style={{ margin: 0 }}>Create Purchase Order</h1>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      <div className="glass" style={{ padding: '2rem' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <h3 style={{ borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>PO Details</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Vendor *</label>
              <select required className="form-input" value={formData.vendor_id} onChange={(e) => setFormData({...formData, vendor_id: e.target.value})}>
                <option value="">-- Select Vendor --</option>
                {vendorsList.map(vendor => (
                  <option key={vendor.id} value={vendor.id}>{vendor.name}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Date *</label>
              <input type="date" required className="form-input" value={formData.po_date} onChange={(e) => setFormData({...formData, po_date: e.target.value})} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">PO Type *</label>
              <select className="form-input" value={formData.po_type} onChange={(e) => setFormData({...formData, po_type: e.target.value})}>
                <option value="standard">Standard</option>
                <option value="blanket">Blanket</option>
                <option value="contract">Contract</option>
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Matching Type *</label>
              <select className="form-input" value={formData.matching_type} onChange={(e) => setFormData({...formData, matching_type: e.target.value})}>
                <option value="two_way">Two Way</option>
                <option value="three_way">Three Way</option>
              </select>
            </div>
          </div>

          <div>
            <h3 style={{ borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Items Ordered</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {poItems.map((poItem, idx) => (
                <div key={idx} className="glass" style={{ padding: '1rem', background: 'var(--background)', position: 'relative' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                    <div style={{ gridColumn: 'span 2' }}>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>Item *</label>
                      <select required className="form-input" value={poItem.item_id} onChange={(e) => handleItemChange(idx, 'item_id', e.target.value)}>
                        <option value="">-- Select Item --</option>
                        {itemsList.map(item => (
                          <option key={item.id} value={item.id}>{item.name} ({item.code})</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>Qty *</label>
                      <input type="number" min="1" required className="form-input" value={poItem.ordered_qty} onChange={(e) => handleItemChange(idx, 'ordered_qty', parseInt(e.target.value))} />
                    </div>

                    <div>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>Unit Price (₹) *</label>
                      <input type="number" min="0" step="0.01" required className="form-input" value={poItem.unit_price} onChange={(e) => handleItemChange(idx, 'unit_price', parseFloat(e.target.value))} />
                    </div>

                    <div>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>UOM</label>
                      <input type="text" className="form-input" value={poItem.uom} readOnly style={{ backgroundColor: 'var(--surface)' }} />
                    </div>

                    <div>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>GST %</label>
                      <input type="number" min="0" step="0.1" className="form-input" value={poItem.gst_percent} onChange={(e) => handleItemChange(idx, 'gst_percent', parseFloat(e.target.value))} />
                    </div>

                    <div>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>CGST %</label>
                      <input type="number" min="0" step="0.1" className="form-input" value={poItem.cgst_percent} onChange={(e) => handleItemChange(idx, 'cgst_percent', parseFloat(e.target.value))} />
                    </div>

                    <div>
                      <label className="form-label" style={{ fontSize: '0.8rem' }}>SGST %</label>
                      <input type="number" min="0" step="0.1" className="form-input" value={poItem.sgst_percent} onChange={(e) => handleItemChange(idx, 'sgst_percent', parseFloat(e.target.value))} />
                    </div>
                  </div>
                  
                  {poItems.length > 1 && (
                    <button type="button" onClick={() => handleRemoveItemRow(idx)} className="btn btn-outline" style={{ position: 'absolute', top: '1rem', right: '1rem', padding: '0.2rem 0.5rem', color: 'var(--danger)', borderColor: 'var(--danger)' }}>
                      X
                    </button>
                  )}
                </div>
              ))}
            </div>
            
            <button type="button" onClick={handleAddItemRow} className="btn btn-outline" style={{ marginTop: '1rem', width: '100%' }}>
              + Add Another Item
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
            <Link href="/pos" className="btn btn-outline">Cancel</Link>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Creating..." : "Create PO"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
