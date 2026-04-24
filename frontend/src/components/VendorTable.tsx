import { Vendor } from "@/services/api";

interface VendorTableProps {
  vendors: Vendor[];
  onDelete: (id: string) => void;
}

export default function VendorTable({ vendors, onDelete }: VendorTableProps) {
  if (!vendors.length) {
    return (
      <div className="glass" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No vendors found. Try adjusting your search or create a new vendor.
      </div>
    );
  }

  return (
    <div className="glass" style={{ overflow: 'hidden' }}>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table" style={{ minWidth: '800px' }}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Status</th>
              <th>PAN / GST</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {vendors.map((vendor) => (
              <tr key={vendor.id}>
                <td style={{ fontWeight: 500 }}>{vendor.name}</td>
                <td>{vendor.email}</td>
                <td>{vendor.phone}</td>
                <td>
                  <span className={`badge badge-${vendor.status.toLowerCase()}`}>
                    {vendor.status}
                  </span>
                </td>
                <td>
                  <div style={{ fontSize: '0.85rem' }}>
                    <div>PAN: {vendor.pan_no}</div>
                    {vendor.gst_no && <div style={{ color: 'var(--text-muted)' }}>GST: {vendor.gst_no}</div>}
                  </div>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <button 
                    onClick={() => onDelete(vendor.id)}
                    className="btn btn-outline"
                    style={{ color: 'var(--danger)', borderColor: 'transparent', padding: '0.25rem 0.5rem' }}
                    title="Delete Vendor"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
