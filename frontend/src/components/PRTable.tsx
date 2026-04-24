import { PR } from "@/services/api";

interface PRTableProps {
  prs: PR[];
  onUpdateStatus: (id: string, status: string) => void;
}

export default function PRTable({ prs, onUpdateStatus }: PRTableProps) {
  if (!prs.length) {
    return (
      <div className="glass" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No purchase requests found. Create a new one to get started.
      </div>
    );
  }

  return (
    <div className="glass" style={{ overflow: 'hidden' }}>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table" style={{ minWidth: '800px' }}>
          <thead>
            <tr>
              <th>PR Number</th>
              <th>Requested By</th>
              <th>Date</th>
              <th>Items Count</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {prs.map((pr) => (
              <tr key={pr.id}>
                <td style={{ fontWeight: 500, color: 'var(--primary)' }}>{pr.pr_number}</td>
                <td>{pr.requested_by}</td>
                <td>{new Date(pr.created_at).toLocaleDateString()}</td>
                <td>{pr.items?.length || 0} items</td>
                <td>
                  <span className={`badge badge-${pr.status.toLowerCase()}`}>
                    {pr.status}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <select 
                    className="form-input" 
                    style={{ width: 'auto', display: 'inline-block', padding: '0.2rem 1rem', fontSize: '0.85rem' }}
                    value={pr.status}
                    onChange={(e) => onUpdateStatus(pr.id, e.target.value)}
                  >
                    <option value="draft">Draft</option>
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
