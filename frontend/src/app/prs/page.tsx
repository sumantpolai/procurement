"use client";

import { useEffect, useState } from "react";
import PRTable from "@/components/PRTable";
import { fetchPRs, updatePRStatus, PR } from "@/services/api";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function PRPage() {
  const [prs, setPrs] = useState<PR[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadPRs();
    }
  }, [user, authLoading, router]);

  const loadPRs = async () => {
    try {
      setLoading(true);
      const res = await fetchPRs(1, 50);
      setPrs(res.data);
      setError("");
    } catch (err: any) {
      setError("Failed to load Purchase Requests.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await updatePRStatus(id, status);
      loadPRs();
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
          <h1 style={{ marginBottom: '0.5rem' }}>Purchase Requests</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage internal requests for items.</p>
        </div>
        <Link href="/prs/new" className="btn btn-primary">+ Create PR</Link>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger)', color: 'white', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Loading PRs...
        </div>
      ) : (
        <PRTable prs={prs} onUpdateStatus={handleUpdateStatus} />
      )}
    </div>
  );
}
