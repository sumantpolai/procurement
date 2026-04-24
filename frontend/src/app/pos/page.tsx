"use client";

import { useEffect, useState } from "react";
import POTable from "@/components/POTable";
import { fetchPOs, updatePOStatus, PO } from "@/services/api";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function POPage() {
  const [pos, setPos] = useState<PO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadPOs();
    }
  }, [user, authLoading, router]);

  const loadPOs = async () => {
    try {
      setLoading(true);
      const res = await fetchPOs(1, 50);
      setPos(res.data);
      setError("");
    } catch (err: any) {
      setError("Failed to load Purchase Orders.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await updatePOStatus(id, status);
      loadPOs();
    } catch (err: any) {
      alert("Failed to update status.");
    }
  };

  if (authLoading || (!user && loading)) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ marginBottom: '0.5rem' }}>Purchase Orders</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage purchase orders to vendors.</p>
        </div>
        <Link href="/pos/new" className="btn btn-primary">+ Create PO</Link>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading POs...
        </div>
      ) : (
        <POTable pos={pos} onUpdateStatus={handleUpdateStatus} />
      )}
    </div>
  );
}
