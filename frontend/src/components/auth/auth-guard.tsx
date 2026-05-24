"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { clearTokens, getAccessToken } from "@/lib/auth";
import { api } from "@/lib/api";
import type { User } from "@/types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionValid, setSessionValid] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me(token)
      .then((u) => {
        setUser(u as User);
        setSessionValid(true);
      })
      .catch(() => {
        clearTokens();
        setUser(null);
        setSessionValid(false);
      })
      .finally(() => setLoading(false));
  }, []);

  const canEdit = user?.role === "admin" || user?.role === "contributor";
  const isAdmin = user?.role === "admin";

  return { user, loading, canEdit, isAdmin, sessionValid };
}

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const { loading, sessionValid } = useAuth();
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !loading) {
      if (!getAccessToken() || !sessionValid) {
        router.replace("/login");
      }
    }
  }, [mounted, loading, sessionValid, router]);

  // Same output on server and first client render — avoids hydration mismatch.
  if (!mounted || loading) {
    return (
      <div className="flex h-screen items-center justify-center text-slate-500">
        Loading...
      </div>
    );
  }

  if (!sessionValid) {
    return null;
  }

  return <>{children}</>;
}
