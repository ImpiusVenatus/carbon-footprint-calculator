"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Dropdown } from "@/components/ui/dropdown";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/components/auth/auth-guard";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { formatCo2e } from "@/lib/utils";
import { formatFactorLabel, getScopeLabel } from "@/lib/scopes";
import type { ActivityEntry, EmissionFactor, ImportPreviewRow } from "@/types";

const emptyForm = {
  emission_factor_id: "",
  description: "",
  quantity: "",
  unit: "kWh",
  period_start: "2026-01-01",
  period_end: "2026-01-31",
};

function toDateInput(value: string) {
  return value.slice(0, 10);
}

export default function ActivitiesPage() {
  const { canEdit } = useAuth();
  const [activities, setActivities] = useState<ActivityEntry[]>([]);
  const [factors, setFactors] = useState<EmissionFactor[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [preview, setPreview] = useState<ImportPreviewRow[]>([]);
  const [message, setMessage] = useState("");

  const factorOptions = useMemo(
    () => [
      { value: "", label: "Choose activity type..." },
      ...factors.map((f) => ({
        value: f.id,
        label: formatFactorLabel(f.category, f.activity_unit),
      })),
    ],
    [factors],
  );

  function load() {
    const token = getAccessToken();
    if (!token) return;
    api.activities(token).then((a) => setActivities(a as ActivityEntry[]));
    api.factors(token, { year: 2024 }).then((f) => setFactors(f as EmissionFactor[]));
  }

  useEffect(() => {
    load();
  }, []);

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }

  function startEdit(activity: ActivityEntry) {
    setEditingId(activity.id);
    setForm({
      emission_factor_id: activity.emission_factor_id,
      description: activity.description,
      quantity: String(activity.quantity),
      unit: activity.unit,
      period_start: toDateInput(activity.period_start),
      period_end: toDateInput(activity.period_end),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    const payload = { ...form, quantity: parseFloat(form.quantity) };
    try {
      if (editingId) {
        const result = await api.updateActivity(token, editingId, payload);
        const co2e = (result as { emission?: { co2e_kg: number } }).emission?.co2e_kg;
        setMessage(co2e != null ? `Updated — ${formatCo2e(co2e)} calculated.` : "Entry updated.");
      } else {
        await api.createActivity(token, payload);
        setMessage("Activity saved.");
      }
      resetForm();
      load();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Error");
    }
  }

  async function handleDelete(id: string) {
    const token = getAccessToken();
    if (!token || !confirm("Delete this entry?")) return;
    await api.deleteActivity(token, id);
    if (editingId === id) resetForm();
    load();
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    const token = getAccessToken();
    if (!file || !token) return;
    const result = (await api.importPreview(token, file)) as { rows: ImportPreviewRow[] };
    setPreview(result.rows);
  }

  async function confirmImport() {
    const token = getAccessToken();
    if (!token) return;
    const validRows = preview
      .filter((r) => r.valid)
      .map((r) => ({
        category: r.category,
        quantity: r.quantity,
        unit: r.unit,
        period_start: r.period_start,
        period_end: r.period_end,
        emission_factor_id: r.emission_factor_id,
      }));
    await api.importConfirm(token, validRows);
    setPreview([]);
    setMessage(`Imported ${validRows.length} rows.`);
    load();
  }

  function downloadTemplate() {
    const csv = "category,quantity,unit,period_start,period_end\nelectricity,1000,kWh,2026-01-01,2026-01-31\n";
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "activities_template.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Activities</h1>
      </header>

      {message && <p className="text-sm text-emerald-700">{message}</p>}

      {canEdit && (
        <Card>
          <CardHeader>
            <CardTitle>{editingId ? "Edit entry" : "New entry"}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
              <fieldset>
                <Label>Activity type</Label>
                <Dropdown
                  value={form.emission_factor_id}
                  onChange={(v) => {
                    const f = factors.find((x) => x.id === v);
                    setForm({
                      ...form,
                      emission_factor_id: v,
                      unit: f?.activity_unit || form.unit,
                    });
                  }}
                  options={factorOptions}
                  placeholder="Choose activity type..."
                  required
                  className="mt-1"
                />
                <p className="mt-1.5 text-xs text-slate-500">
                  Match what you are recording — e.g. an electricity bill → Electricity (kWh).
                </p>
              </fieldset>
              <fieldset>
                <Label>Description</Label>
                <Input
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  required
                  className="mt-1"
                />
              </fieldset>
              <fieldset>
                <Label>Quantity</Label>
                <Input
                  type="number"
                  step="any"
                  value={form.quantity}
                  onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                  required
                  className="mt-1"
                />
              </fieldset>
              <fieldset>
                <Label>Unit</Label>
                <Input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} required className="mt-1" />
              </fieldset>
              <fieldset>
                <Label>Period start</Label>
                <Input
                  type="date"
                  value={form.period_start}
                  onChange={(e) => setForm({ ...form, period_start: e.target.value })}
                  required
                  className="mt-1"
                />
              </fieldset>
              <fieldset>
                <Label>Period end</Label>
                <Input
                  type="date"
                  value={form.period_end}
                  onChange={(e) => setForm({ ...form, period_end: e.target.value })}
                  required
                  className="mt-1"
                />
              </fieldset>
              <fieldset className="flex gap-2 md:col-span-2">
                <Button type="submit">{editingId ? "Update" : "Save"}</Button>
                {editingId && (
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Cancel
                  </Button>
                )}
              </fieldset>
            </form>
          </CardContent>
        </Card>
      )}

      {canEdit && (
        <Card>
          <CardHeader>
            <CardTitle>Import CSV</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Input type="file" accept=".csv" onChange={handleImport} className="max-w-xs" />
              <Button type="button" variant="outline" onClick={downloadTemplate}>
                Download template
              </Button>
            </div>
            {preview.length > 0 && (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Row</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Qty</TableHead>
                      <TableHead>Unit</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {preview.map((r) => (
                      <TableRow key={r.row_number} className={r.valid ? "bg-emerald-50" : "bg-red-50"}>
                        <TableCell>{r.row_number}</TableCell>
                        <TableCell>{r.category}</TableCell>
                        <TableCell>{r.quantity}</TableCell>
                        <TableCell>{r.unit}</TableCell>
                        <TableCell>{r.valid ? "Valid" : r.error}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <Button onClick={confirmImport} disabled={!preview.some((r) => r.valid)}>
                  Confirm import
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          {activities.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-500">
              No activities yet.{" "}
              {canEdit ? (
                <>Add an entry above or <Link href="/factors" className="text-emerald-600 hover:underline">browse factors</Link>.</>
              ) : (
                "Check back once your team adds data."
              )}
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Description</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead>CO2e</TableHead>
                  <TableHead>Source</TableHead>
                  {canEdit && <TableHead />}
                </TableRow>
              </TableHeader>
              <TableBody>
                {activities.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>{a.description}</TableCell>
                    <TableCell>
                      {a.quantity} {a.unit}
                    </TableCell>
                    <TableCell>
                      {toDateInput(a.period_start)} — {toDateInput(a.period_end)}
                    </TableCell>
                    <TableCell>{a.emission ? formatCo2e(a.emission.co2e_kg) : "—"}</TableCell>
                    <TableCell>{a.emission ? getScopeLabel(a.emission.scope) : "—"}</TableCell>
                    {canEdit && (
                      <TableCell className="space-x-2">
                        <Button variant="outline" size="sm" onClick={() => startEdit(a)}>
                          Edit
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => handleDelete(a.id)}>
                          Delete
                        </Button>
                      </TableCell>
                    )}
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
