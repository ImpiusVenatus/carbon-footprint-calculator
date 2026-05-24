"use client";

export function TargetGauge({
  achieved,
  target,
}: {
  achieved: number;
  target: number;
}) {
  const pct = Math.min(100, Math.max(0, achieved));

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-sm">
        <span className="text-slate-500">Progress toward {target}% reduction goal</span>
        <span className="font-semibold text-emerald-700">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-4 w-full overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
