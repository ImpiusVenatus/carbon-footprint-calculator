"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Dropdown, YEAR_OPTIONS } from "@/components/ui/dropdown";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function ReportsPage() {
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [loading, setLoading] = useState(false);

  async function handleExport() {
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    try {
      const blob = await api.exportReport(token, Number(year));
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "emissions_report_" + year + ".csv";
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Reports</h1>
      </header>
      <Card>
        <CardHeader>
          <CardTitle>Export CSV</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div>
            <Label>Year</Label>
            <Dropdown value={year} onChange={setYear} options={YEAR_OPTIONS} className="mt-1 w-32" />
          </div>
          <Button onClick={handleExport} disabled={loading}>
            {loading ? "Exporting..." : "Download"}
          </Button>
        </CardContent>
      </Card>
    </section>
  );
}
