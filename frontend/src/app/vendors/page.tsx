"use client";

import { useCallback, useEffect, useState } from "react";
import VendorTable from "@/components/VendorTable";
import { fetchVendors, searchVendors, deleteVendor, Vendor } from "@/services/api";
import Modal from "@/components/Modal";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

const getErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [vendorToDelete, setVendorToDelete] = useState<string | null>(null);
  
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const loadVendors = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchVendors(1, 50);
      setVendors(data);
      setError("");
    } catch (error: unknown) {
      const message = getErrorMessage(error, "Failed to load vendors.");
      if (message === "Failed to fetch user") {
         router.push('/login');
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      const timeoutId = window.setTimeout(() => {
        void loadVendors();
      }, 0);

      return () => window.clearTimeout(timeoutId);
    }
  }, [user, authLoading, router, loadVendors]);

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
    } catch (error: unknown) {
      setError(getErrorMessage(error, "Search failed."));
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
    } catch (error: unknown) {
      alert(getErrorMessage(error, "Failed to delete vendor."));
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
