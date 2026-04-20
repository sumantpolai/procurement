"use client";

import { useState, FormEvent, useEffect } from "react";
import { Item } from "@/services/api";

interface ItemFormProps {
  initialData?: Partial<Item>;
  onSubmit: (data: Partial<Item>) => Promise<void>;
  isLoading: boolean;
}

export default function ItemForm({ initialData, onSubmit, isLoading }: ItemFormProps) {
  const [formData, setFormData] = useState<Partial<Item>>({
    name: "",
    item_type: "text",
    item_category: "consumable",
    uom: "",
    status: "Draft",
    created_by: "admin", // default value for created_by
    rejection_reason: "",
  });

  useEffect(() => {
    if (initialData) {
      setFormData((prev) => ({ ...prev, ...initialData }));
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="glass" style={{ padding: '2rem' }}>
      <div className="form-group">
        <label className="form-label" htmlFor="name">Item Name</label>
        <input required type="text" id="name" name="name" className="form-input" value={formData.name || ''} onChange={handleChange} placeholder="e.g. Dell XPS 15" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="item_type">Item Type</label>
          <select id="item_type" name="item_type" className="form-select" value={formData.item_type || 'text'} onChange={handleChange}>
            <option value="text">Text</option>
            <option value="service">Service</option>
            <option value="inventory_item">Inventory Item</option>
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="item_category">Category</label>
          <select id="item_category" name="item_category" className="form-select" value={formData.item_category || 'consumable'} onChange={handleChange}>
            <option value="consumable">Consumable</option>
            <option value="Pharmaceuticals">Pharmaceuticals</option>
            <option value="equipment">Equipment</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="uom">Unit of Measure (UoM)</label>
          <input required type="text" id="uom" name="uom" className="form-input" value={formData.uom || ''} onChange={handleChange} placeholder="e.g. PCS, KG" />
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="status">Status</label>
          <select id="status" name="status" className="form-select" value={formData.status || 'Draft'} onChange={handleChange}>
            <option value="Draft">Draft</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      {formData.status === 'Rejected' && (
        <div className="form-group">
          <label className="form-label" htmlFor="rejection_reason">Rejection Reason</label>
          <textarea required id="rejection_reason" name="rejection_reason" className="form-input" value={formData.rejection_reason || ''} onChange={handleChange} placeholder="Please provide a reason for rejection..." rows={3} style={{ resize: 'vertical' }} />
        </div>
      )}

      {!initialData && (
        <div className="form-group">
          <label className="form-label" htmlFor="created_by">Created By</label>
          <input required type="text" id="created_by" name="created_by" className="form-input" value={formData.created_by || ''} onChange={handleChange} />
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
        <button type="button" className="btn btn-outline" onClick={() => window.history.back()}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : (initialData ? 'Update Item' : 'Create Item')}
        </button>
      </div>
    </form>
  );
}
