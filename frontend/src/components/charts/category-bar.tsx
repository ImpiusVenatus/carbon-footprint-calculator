"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function CategoryBar({ data }: { data: { category: string; co2e_kg: number }[] }) {
  if (!data.length) {
    return <p className="py-12 text-center text-sm text-slate-400">No category data yet</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="category" tick={{ fontSize: 11 }} width={75} />
        <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} kg`, "CO2e"]} />
        <Bar dataKey="co2e_kg" fill="#0284c7" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
