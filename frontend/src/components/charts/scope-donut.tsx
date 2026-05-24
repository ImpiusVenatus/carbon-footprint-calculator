"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { chartScopeName } from "@/lib/scopes";

const COLORS = ["#059669", "#0284c7", "#7c3aed"];

export function ScopeDonut({ data }: { data: { scope: string; co2e_kg: number }[] }) {
  const chartData = data.map((d) => ({
    name: chartScopeName(d.scope),
    value: d.co2e_kg,
  }));

  if (chartData.every((d) => d.value === 0)) {
    return <p className="py-12 text-center text-sm text-slate-400">No emissions data yet</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
        >
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} kg CO2e`, "Emissions"]} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
