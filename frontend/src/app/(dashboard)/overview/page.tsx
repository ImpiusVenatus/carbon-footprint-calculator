"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { TrendingDown, TrendingUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dropdown, YEAR_OPTIONS } from "@/components/ui/dropdown";
import { ScopeDonut } from "@/components/charts/scope-donut";
import { MonthlyTrend } from "@/components/charts/monthly-trend";
import { CategoryBar } from "@/components/charts/category-bar";
import { TargetGauge } from "@/components/charts/target-gauge";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { formatCo2e } from "@/lib/utils";
import type { EmissionsSummary } from "@/types";

export default function OverviewPage() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState<EmissionsSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    api
      .emissionsSummary(token, year)
      .then((s) => setSummary(s as EmissionsSummary))
      .catch((e) => setError(e.message));
  }, [year]);

  const hasData = (summary?.total_co2e_kg ?? 0) > 0;
  const yoy = summary?.yoy_change_percent;
  const yoyDown = yoy != null && yoy < 0;

  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-slate-900">Overview</h1>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Year</span>
          <Dropdown
            value={String(year)}
            onChange={(v) => setYear(Number(v))}
            options={YEAR_OPTIONS}
            className="w-28"
          />
        </div>
      </header>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {!hasData && !error && (
        <Card className="border-dashed">
          <CardContent className="py-10 text-center">
            <p className="text-slate-600">No emissions data for {year} yet.</p>
            <p className="mt-2 text-sm text-slate-500">
              <Link href="/activities" className="text-emerald-600 hover:underline">
                Add an activity
              </Link>{" "}
              to populate your dashboard.
            </p>
          </CardContent>
        </Card>
      )}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader>
            <CardDescription>Total emissions</CardDescription>
            <CardTitle className="flex items-center gap-2 text-3xl">
              {formatCo2e(summary?.total_co2e_kg ?? 0)}
              {yoy != null &&
                (yoyDown ? (
                  <TrendingDown className="h-5 w-5 text-emerald-600" />
                ) : (
                  <TrendingUp className="h-5 w-5 text-amber-600" />
                ))}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">
              {yoy != null
                ? `${yoy > 0 ? "+" : ""}${yoy}% vs ${year - 1}`
                : `Combined total for ${year}`}
            </p>
          </CardContent>
        </Card>
        {summary?.target_progress && (
          <Card className="md:col-span-3">
            <CardHeader>
              <CardTitle>Reduction target progress</CardTitle>
              <CardDescription>
                Base year: {formatCo2e(summary.target_progress.base_year_co2e)} → Current:{" "}
                {formatCo2e(summary.target_progress.current_co2e)}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TargetGauge
                achieved={summary.target_progress.achieved_percent}
                target={summary.target_progress.target_percent}
              />
            </CardContent>
          </Card>
        )}
      </section>

      {hasData && (
        <>
          <section className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Where emissions come from</CardTitle>
                <CardDescription>Direct operations, purchased energy, and indirect activity</CardDescription>
              </CardHeader>
              <CardContent>
                <ScopeDonut data={summary?.by_scope ?? []} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Monthly trend</CardTitle>
              </CardHeader>
              <CardContent>
                <MonthlyTrend data={summary?.monthly ?? []} />
              </CardContent>
            </Card>
          </section>

          <Card>
            <CardHeader>
              <CardTitle>By category</CardTitle>
            </CardHeader>
            <CardContent>
              <CategoryBar data={summary?.by_category ?? []} />
            </CardContent>
          </Card>
        </>
      )}
    </section>
  );
}
