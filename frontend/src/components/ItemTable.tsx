"use client";

import Link from "next/link";
import { Item } from "@/services/api";

interface ItemTableProps {
  items: Item[];
  onDelete: (id: string) => void;
}

export default function ItemTable({ items, onDelete }: ItemTableProps) {
  const getBadgeClass = (status: string) => {
    switch (status) {
      case 'Approved': return 'badge-approved';
      case 'Rejected': return 'badge-rejected';
      default: return 'badge-draft';
    }
  };

  if (items.length === 0) {
    return (
      <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
        <h3 style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>No items found</h3>
        <p style={{ marginBottom: '2rem', color: 'var(--text-muted)' }}>Get started by creating a new procurement item.</p>
        <Link href="/new" className="btn btn-primary">Create Item</Link>
      </div>
    );
  }

  return (
    <div className="glass table-container animate-fade-in">
      <table className="data-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Type</th>
            <th>Category</th>
            <th>Status</th>
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td style={{ fontWeight: 500 }}>{item.code}</td>
              <td>{item.name}</td>
              <td style={{ textTransform: 'capitalize' }}>{item.item_type.replace('_', ' ')}</td>
              <td style={{ textTransform: 'capitalize' }}>{item.item_category}</td>
              <td>
                <span className={`badge ${getBadgeClass(item.status)}`}>
                  {item.status}
                </span>
                {item.status === 'Rejected' && item.rejection_reason && (
                  <div style={{ fontSize: '0.75rem', marginTop: '0.25rem', color: 'var(--danger)' }} title={item.rejection_reason}>
                    Reason provided
                  </div>
                )}
              </td>
              <td style={{ textAlign: 'right' }}>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                  <Link href={`/${item.id}`} className="btn btn-outline" style={{ padding: '0.25rem 0.75rem' }}>
                    Edit
                  </Link>
                  <button onClick={() => onDelete(item.id)} className="btn btn-danger" style={{ padding: '0.25rem 0.75rem' }}>
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
