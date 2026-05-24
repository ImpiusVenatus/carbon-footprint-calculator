"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function MonthlyTrend({ data }: { data: { month: string; co2e_kg: number }[] }) {
  if (!data.length) {
    return <p className="py-12 text-center text-sm text-slate-400">No monthly data yet</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} kg`, "CO2e"]} />
        <Line type="monotone" dataKey="co2e_kg" stroke="#059669" strokeWidth={2} dot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
