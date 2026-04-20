import Link from 'next/link';

export default function Navbar() {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 10,
      background: 'var(--surface)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--surface-border)',
      boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '70px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link href="/" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)' }}>
            Procurement
          </Link>
          <span style={{ color: 'var(--text-muted)' }}>|</span>
          <span style={{ fontWeight: 500 }}>Items Portal</span>
        </div>
        
        <nav>
          <ul style={{ listStyle: 'none', display: 'flex', gap: '1.5rem', margin: 0, padding: 0 }}>
            <li>
              <Link href="/" style={{ fontWeight: 500, color: 'var(--foreground)' }}>Dashboard</Link>
            </li>
            <li>
              <Link href="/new" className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>
                + New Item
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
