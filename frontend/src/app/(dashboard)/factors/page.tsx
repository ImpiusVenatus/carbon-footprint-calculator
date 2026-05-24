"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { Dropdown } from "@/components/ui/dropdown";
import { formatCategory, getScopeLabel, scopeFilterOptions, scopeFormOptions } from "@/lib/scopes";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/components/auth/auth-guard";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { EmissionFactor } from "@/types";

export default function FactorsPage() {
  const { isAdmin } = useAuth();
  const [factors, setFactors] = useState<EmissionFactor[]>([]);
  const [scope, setScope] = useState("");
  const [category, setCategory] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    scope: "2",
    category: "",
    activity_unit: "kWh",
    factor_value: "",
    source: "Custom",
    effective_year: "2024",
    region: "UK",
  });

  function load() {
    const token = getAccessToken();
    if (!token) return;
    api
      .factors(token, { scope: scope || undefined, category: category || undefined, year: 2024 })
      .then((data) => setFactors(data as EmissionFactor[]));
  }

  useEffect(() => {
    load();
  }, [scope, category]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    await api.createFactor(token, {
      scope: form.scope,
      category: form.category,
      activity_unit: form.activity_unit,
      factor_value: parseFloat(form.factor_value),
      source: form.source,
      effective_year: parseInt(form.effective_year),
      region: form.region,
    });
    setShowForm(false);
    load();
  }

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Emission Factors</h1>
        {isAdmin && (
          <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "Add factor"}</Button>
        )}
      </header>

      <section className="flex gap-4">
        <div>
          <Label>Source type</Label>
          <Dropdown
            value={scope}
            onChange={setScope}
            options={scopeFilterOptions()}
            className="mt-1 w-40"
          />
        </div>
        <div className="flex-1">
          <Label>Category</Label>
          <Input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="Search category..."
            className="mt-1"
          />
        </div>
      </section>

      {showForm && isAdmin && (
        <Card>
          <CardHeader>
            <CardTitle>New factor</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid gap-4 md:grid-cols-3">
              <div>
                <Label>Source type</Label>
                <Dropdown
                  value={form.scope}
                  onChange={(v) => setForm({ ...form, scope: v })}
                  options={scopeFormOptions()}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Category</Label>
                <Input
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Unit</Label>
                <Input
                  value={form.activity_unit}
                  onChange={(e) => setForm({ ...form, activity_unit: e.target.value })}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Factor (kg CO2e per unit)</Label>
                <Input
                  type="number"
                  step="any"
                  value={form.factor_value}
                  onChange={(e) => setForm({ ...form, factor_value: e.target.value })}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Source</Label>
                <Input
                  value={form.source}
                  onChange={(e) => setForm({ ...form, source: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div className="flex items-end">
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
                <TableHead>Source type</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Unit</TableHead>
                <TableHead>Factor</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Year</TableHead>
                <TableHead>Region</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {factors.map((f) => (
                <TableRow key={f.id}>
                  <TableCell>{getScopeLabel(f.scope)}</TableCell>
                  <TableCell>{formatCategory(f.category)}</TableCell>
                  <TableCell>{f.activity_unit}</TableCell>
                  <TableCell>{f.factor_value}</TableCell>
                  <TableCell>{f.source}</TableCell>
                  <TableCell>{f.effective_year}</TableCell>
                  <TableCell>{f.region}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </section>
  );
}
