"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/components/auth/auth-guard";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useRouter } from "next/navigation";

interface AuditEntry {
  id: string;
  user_email: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  created_at: string;
}

export default function AuditPage() {
  const { isAdmin, loading } = useAuth();
  const router = useRouter();
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !isAdmin) {
      router.replace("/overview");
    }
  }, [loading, isAdmin, router]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token || !isAdmin) return;
    api
      .auditLog(token)
      .then((rows) => setEntries(rows as AuditEntry[]))
      .catch((e) => setError(e.message));
  }, [isAdmin]);

  if (!isAdmin) return null;

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Audit log</h1>
        <p className="text-sm text-slate-500">Trace of create, update, delete, import, and export actions</p>
      </header>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>Recent activity</CardTitle>
        </CardHeader>
        <CardContent>
          {entries.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-500">No audit entries yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>When</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Entity</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell>{new Date(e.created_at).toLocaleString()}</TableCell>
                    <TableCell>{e.user_email ?? "—"}</TableCell>
                    <TableCell className="capitalize">{e.action}</TableCell>
                    <TableCell>
                      {e.entity_type}
                      {e.entity_id ? ` · ${e.entity_id.slice(0, 8)}…` : ""}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
