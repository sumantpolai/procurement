import { PO } from "@/services/api";

interface POTableProps {
  pos: PO[];
  onUpdateStatus: (id: string, status: string) => void;
}

export default function POTable({ pos, onUpdateStatus }: POTableProps) {
  if (!pos.length) {
    return (
      <div className="glass" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No purchase orders found. Create a new one to get started.
      </div>
    );
  }

  return (
    <div className="glass" style={{ overflow: 'hidden' }}>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table" style={{ minWidth: '900px' }}>
          <thead>
            <tr>
              <th>PO Number</th>
              <th>Vendor</th>
              <th>Date</th>
              <th>Type</th>
              <th>Total Amount</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pos.map((po) => (
              <tr key={po.id}>
                <td style={{ fontWeight: 500, color: 'var(--primary)' }}>{po.po_number}</td>
                <td>{po.vendor_name || po.vendor_id}</td>
                <td>{po.po_date}</td>
                <td>{po.po_type}</td>
                <td>{po.total_amount ? `₹${po.total_amount.toFixed(2)}` : '-'}</td>
                <td>
                  <span className={`badge badge-${po.status.toLowerCase()}`}>
                    {po.status}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <select 
                    className="form-input" 
                    style={{ width: 'auto', display: 'inline-block', padding: '0.2rem 1rem', fontSize: '0.85rem' }}
                    value={po.status}
                    onChange={(e) => onUpdateStatus(po.id, e.target.value)}
                  >
                    <option value="draft">Draft</option>
                    <option value="issued">Issued</option>
                    <option value="acknowledged">Acknowledged</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
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
