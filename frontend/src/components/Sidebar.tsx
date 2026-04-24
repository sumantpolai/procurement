"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  if (!user && pathname === '/login') {
    return null; // Don't show sidebar on login page
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Link href="/" className="logo-link">
          Procurement<span className="dot">.</span>
        </Link>
      </div>

      <div className="sidebar-content">
        {user ? (
          <nav className="sidebar-nav">
            <ul className="nav-list">
              <li>
                <Link href="/" className={`sidebar-link ${pathname === '/' ? 'active' : ''}`}>
                  <span className="icon">📦</span>
                  <span className="link-text">Items</span>
                </Link>
              </li>
              <li>
                <Link href="/vendors" className={`sidebar-link ${pathname?.startsWith('/vendors') ? 'active' : ''}`}>
                  <span className="icon">🏢</span>
                  <span className="link-text">Vendors</span>
                </Link>
              </li>
              <li>
                <Link href="/prs" className={`sidebar-link ${pathname?.startsWith('/prs') ? 'active' : ''}`}>
                  <span className="icon">📝</span>
                  <span className="link-text">Purchase Requests</span>
                </Link>
              </li>
              <li>
                <Link href="/pos" className={`sidebar-link ${pathname?.startsWith('/pos') ? 'active' : ''}`}>
                  <span className="icon">🛒</span>
                  <span className="link-text">Purchase Orders</span>
                </Link>
              </li>
            </ul>
          </nav>
        ) : (
          <div className="sidebar-login-prompt">
            <p>Please log in to access the dashboard.</p>
            <Link href="/login" className="btn btn-primary" style={{ width: '100%' }}>Login</Link>
          </div>
        )}
      </div>

      {user && (
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar">{user.email?.charAt(0).toUpperCase()}</div>
            <div className="user-details">
              <span className="user-name" title={user.full_name || user.email}>{user.full_name || user.email?.split('@')[0]}</span>
              <span className="user-role">{user.role?.replace('_', ' ')}</span>
            </div>
          </div>
          <button onClick={logout} className="btn btn-outline btn-logout">
            <span className="icon">🚪</span>
            Logout
          </button>
        </div>
      )}
    </aside>
  );
}
