"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Dropdown } from "@/components/ui/dropdown";
import { getScopeLabel, targetScopeOptions } from "@/lib/scopes";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/components/auth/auth-guard";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { ReductionTarget } from "@/types";

export default function TargetsPage() {
  const { isAdmin } = useAuth();
  const [targets, setTargets] = useState<ReductionTarget[]>([]);
  const [form, setForm] = useState({
    scope: "all",
    base_year: "2024",
    target_year: "2030",
    reduction_percent: "30",
  });

  function load() {
    const token = getAccessToken();
    if (!token) return;
    api.targets(token).then((t) => setTargets(t as ReductionTarget[]));
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    await api.createTarget(token, {
      scope: form.scope,
      base_year: parseInt(form.base_year),
      target_year: parseInt(form.target_year),
      reduction_percent: parseFloat(form.reduction_percent),
    });
    load();
  }

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Targets</h1>
      </header>

      {isAdmin && (
        <Card>
          <CardHeader>
            <CardTitle>New target</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid gap-4 md:grid-cols-4">
              <div>
                <Label>Applies to</Label>
                <Dropdown
                  value={form.scope}
                  onChange={(v) => setForm({ ...form, scope: v })}
                  options={targetScopeOptions()}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Base year</Label>
                <Input
                  type="number"
                  value={form.base_year}
                  onChange={(e) => setForm({ ...form, base_year: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Target year</Label>
                <Input
                  type="number"
                  value={form.target_year}
                  onChange={(e) => setForm({ ...form, target_year: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Reduction %</Label>
                <Input
                  type="number"
                  value={form.reduction_percent}
                  onChange={(e) => setForm({ ...form, reduction_percent: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Button type="submit">Save</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Applies to</TableHead>
                <TableHead>Base year</TableHead>
                <TableHead>Target year</TableHead>
                <TableHead>Reduction</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {targets.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{getScopeLabel(t.scope, "full")}</TableCell>
                  <TableCell>{t.base_year}</TableCell>
                  <TableCell>{t.target_year}</TableCell>
                  <TableCell>{t.reduction_percent}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </section>
  );
}
