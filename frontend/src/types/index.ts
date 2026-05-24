export type Scope = "1" | "2" | "3";

export type UserRole = "admin" | "contributor" | "viewer";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  organization_id: string;
}

export interface EmissionFactor {
  id: string;
  organization_id: string | null;
  scope: Scope;
  category: string;
  activity_unit: string;
  factor_value: number;
  source: string;
  effective_year: number;
  region: string;
  is_active: boolean;
}

export interface Emission {
  id: string;
  co2e_kg: number;
  scope: Scope;
  factor_value_used: number;
  calculated_at: string;
}

export interface ActivityEntry {
  id: string;
  organization_id: string;
  emission_factor_id: string;
  description: string;
  quantity: number;
  unit: string;
  period_start: string;
  period_end: string;
  created_by: string;
  emission?: Emission | null;
}

export interface EmissionsSummary {
  total_co2e_kg: number;
  previous_year_co2e_kg?: number | null;
  yoy_change_percent?: number | null;
  by_scope: { scope: string; co2e_kg: number }[];
  by_category: { category: string; co2e_kg: number }[];
  monthly: { month: string; co2e_kg: number }[];
  target_progress?: {
    base_year_co2e: number;
    current_co2e: number;
    target_percent: number;
    achieved_percent: number;
  } | null;
}

export interface ReductionTarget {
  id: string;
  organization_id: string;
  scope: string;
  base_year: number;
  target_year: number;
  reduction_percent: number;
}

export interface ImportPreviewRow {
  row_number: number;
  category: string;
  quantity: number;
  unit: string;
  period_start: string;
  period_end: string;
  valid: boolean;
  error: string | null;
  emission_factor_id: string | null;
}
