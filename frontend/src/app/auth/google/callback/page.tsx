"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { handleGoogleCallback } from "@/services/api";
import { useAuth } from "@/context/AuthContext";
import React from "react";

// Suspense boundary wrapper is needed for useSearchParams in Next.js app directory
export default function GoogleCallbackPageWrapper() {
  return (
    <React.Suspense fallback={<LoadingFallback />}>
      <GoogleCallbackPage />
    </React.Suspense>
  );
}

function LoadingFallback() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 'calc(100vh - 150px)' }}>
      <div className="glass" style={{ width: '100%', maxWidth: '400px', padding: '2.5rem', textAlign: 'center' }}>
        <Spinner />
        <h2>Loading...</h2>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <>
      <div style={{ 
        width: '40px', 
        height: '40px', 
        border: '3px solid var(--border)', 
        borderTopColor: 'var(--primary)', 
        borderRadius: '50%', 
        margin: '0 auto 1.5rem',
        animation: 'spin 1s linear infinite'
      }} />
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}

function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState("");
  const effectRan = useRef(false);

  useEffect(() => {
    // Prevent double execution in React Strict Mode
    if (effectRan.current) return;
    effectRan.current = true;

    const code = searchParams.get("code");
    const state = searchParams.get("state");

    if (!code || !state) {
      setError("Missing authorization code or state from Google. Please try logging in again.");
      return;
    }

    const authenticate = async () => {
      try {
        const data = await handleGoogleCallback(code, state);
        login(data.access_token, data.user);
      } catch (err: any) {
        setError(err.message || "Authentication failed. Please check your details.");
      }
    };

    authenticate();
  }, [searchParams, login]);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 'calc(100vh - 150px)'
    }}>
      <div className="glass" style={{ width: '100%', maxWidth: '400px', padding: '2.5rem', textAlign: 'center' }}>
        {error ? (
          <>
            <h2 style={{ color: 'var(--danger)', marginBottom: '1rem' }}>Authentication Error</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error}</p>
            <button className="btn btn-primary" onClick={() => router.push('/login')} style={{ width: '100%' }}>
              Return to Login
            </button>
          </>
        ) : (
          <>
            <Spinner />
            <h2>Authenticating...</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>Please wait while we complete your login securely.</p>
          </>
        )}
      </div>
    </div>
  );
}
