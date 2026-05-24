export type ScopeValue = "1" | "2" | "3" | "all" | "";

export const SCOPE_INFO: Record<
  "1" | "2" | "3",
  { short: string; label: string; description: string }
> = {
  "1": {
    short: "Direct",
    label: "Direct emissions",
    description: "Fuel and operations you control on-site (vehicles, gas, generators)",
  },
  "2": {
    short: "Energy",
    label: "Purchased energy",
    description: "Electricity, heating, or cooling bought from a utility",
  },
  "3": {
    short: "Indirect",
    label: "Indirect emissions",
    description: "Travel, commuting, goods, waste, and other value-chain activity",
  },
};

const CATEGORY_LABELS: Record<string, string> = {
  natural_gas: "Natural gas",
  diesel: "Diesel",
  petrol: "Petrol",
  refrigerant_r410a: "Refrigerant (R410A)",
  electricity: "Electricity",
  district_heating: "District heating",
  business_travel_air: "Business travel (air)",
  business_travel_rail: "Business travel (rail)",
  employee_commuting: "Employee commuting",
  waste_landfill: "Waste to landfill",
  purchased_goods: "Purchased goods",
  water_supply: "Water supply",
};

export function formatCategory(category: string): string {
  return (
    CATEGORY_LABELS[category] ??
    category.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

export function getScopeLabel(scope: string, variant: "short" | "full" = "short"): string {
  if (scope === "all" || scope === "") return "All sources";
  const info = SCOPE_INFO[scope as "1" | "2" | "3"];
  if (!info) return scope;
  return variant === "full" ? info.label : info.short;
}

export function getScopeDescription(scope: string): string | undefined {
  return SCOPE_INFO[scope as "1" | "2" | "3"]?.description;
}

/** User-facing label for an emission factor in dropdowns and lists */
export function formatFactorLabel(category: string, unit: string): string {
  return `${formatCategory(category)} (${unit})`;
}

export function scopeFilterOptions() {
  return [
    { value: "", label: "All sources" },
    ...(["1", "2", "3"] as const).map((s) => ({
      value: s,
      label: SCOPE_INFO[s].label,
      description: SCOPE_INFO[s].description,
    })),
  ];
}

export function scopeFormOptions() {
  return (["1", "2", "3"] as const).map((s) => ({
    value: s,
    label: SCOPE_INFO[s].label,
    description: SCOPE_INFO[s].description,
  }));
}

export function targetScopeOptions() {
  return [
    { value: "all", label: "All sources", description: "Target applies to your entire footprint" },
    ...(["1", "2", "3"] as const).map((s) => ({
      value: s,
      label: SCOPE_INFO[s].label,
      description: SCOPE_INFO[s].description,
    })),
  ];
}

export function chartScopeName(scope: string): string {
  const info = SCOPE_INFO[scope as "1" | "2" | "3"];
  return info?.label ?? scope;
}
