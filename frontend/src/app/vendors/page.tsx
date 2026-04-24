"use client";

import { useEffect, useState } from "react";
import VendorTable from "@/components/VendorTable";
import { fetchVendors, searchVendors, deleteVendor, Vendor } from "@/services/api";
import Modal from "@/components/Modal";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [vendorToDelete, setVendorToDelete] = useState<string | null>(null);
  
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadVendors();
    }
  }, [user, authLoading, router]);

  const loadVendors = async () => {
    try {
      setLoading(true);
      const data = await fetchVendors(1, 50); // Get first 50
      setVendors(data); // Backend returns a direct array based on api.ts
      setError("");
    } catch (err: any) {
      if (err.message === "Failed to fetch user") {
         router.push('/login');
      } else {
        setError("Failed to load vendors. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) {
      return loadVendors();
    }

    try {
      setLoading(true);
      const data = await searchVendors(searchTerm);
      setVendors(data);
      setError("");
    } catch (err) {
      setError("Search failed.");
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = async () => {
    if (!vendorToDelete) return;
    try {
      await deleteVendor(vendorToDelete);
      setVendorToDelete(null);
      loadVendors();
    } catch (err: any) {
      alert(err.message || "Failed to delete vendor.");
    }
  };

  if (authLoading || (!user && loading)) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ marginBottom: '0.5rem' }}>Vendors Directory</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage all your suppliers and their details.</p>
        </div>
        <Link href="/vendors/new" className="btn btn-primary">+ Register Vendor</Link>
      </div>

      <div className="glass" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', width: '100%', gap: '1rem' }}>
          <input
            type="text"
            placeholder="Search vendors by name or email..."
            className="form-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn btn-outline">Search</button>
          {searchTerm && (
            <button type="button" className="btn btn-outline" onClick={() => { setSearchTerm(''); loadVendors(); }}>
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
          Loading vendors...
        </div>
      ) : (
        <VendorTable vendors={vendors} onDelete={setVendorToDelete} />
      )}

      <Modal
        isOpen={!!vendorToDelete}
        onClose={() => setVendorToDelete(null)}
        title="Confirm Deletion"
      >
        <p style={{ marginBottom: '1.5rem' }}>Are you sure you want to delete this vendor? This action cannot be undone.</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button className="btn btn-outline" onClick={() => setVendorToDelete(null)}>Cancel</button>
          <button className="btn btn-danger" onClick={confirmDelete}>Delete Vendor</button>
        </div>
      </Modal>
    </div>
  );
}
