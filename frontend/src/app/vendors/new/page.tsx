"use client";

import { useState } from "react";
import { createVendor } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function NewVendorPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    pan_no: "",
    gst_no: "",
    bank_name: "",
    account_number: "",
    ifsc_code: "",
    branch: "",
    address: ""
  });
  
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      setError("You must be logged in.");
      return;
    }
    
    setError("");
    setLoading(true);

    try {
      await createVendor({
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        pan_no: formData.pan_no,
        gst_no: formData.gst_no || null,
        bank_details: {
          bank_name: formData.bank_name,
          account_number: formData.account_number,
          ifsc_code: formData.ifsc_code,
          branch: formData.branch,
          address: formData.address
        }
      });
      router.push("/vendors");
    } catch (err: any) {
      setError(err.message || "Failed to create vendor.");
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem', gap: '1rem' }}>
        <Link href="/vendors" className="btn btn-outline" style={{ padding: '0.4rem 0.8rem' }}>&larr; Back</Link>
        <h1 style={{ margin: 0 }}>Register New Vendor</h1>
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
              <h3 style={{ borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Basic Details</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Vendor Name *</label>
              <input type="text" name="name" required className="form-input" value={formData.name} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Email *</label>
              <input type="email" name="email" required className="form-input" value={formData.email} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Phone *</label>
              <input type="tel" name="phone" required className="form-input" value={formData.phone} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">PAN Number *</label>
              <input type="text" name="pan_no" required className="form-input" value={formData.pan_no} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">GST Number (Optional)</label>
              <input type="text" name="gst_no" className="form-input" value={formData.gst_no} onChange={handleChange} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <h3 style={{ borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Bank Details</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Bank Name *</label>
              <input type="text" name="bank_name" required className="form-input" value={formData.bank_name} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Account Number *</label>
              <input type="text" name="account_number" required className="form-input" value={formData.account_number} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">IFSC Code *</label>
              <input type="text" name="ifsc_code" required className="form-input" value={formData.ifsc_code} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="form-label">Branch *</label>
              <input type="text" name="branch" required className="form-input" value={formData.branch} onChange={handleChange} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: '1 / -1' }}>
              <label className="form-label">Bank Address *</label>
              <input type="text" name="address" required className="form-input" value={formData.address} onChange={handleChange} />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
            <Link href="/vendors" className="btn btn-outline">Cancel</Link>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Registering..." : "Register Vendor"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
