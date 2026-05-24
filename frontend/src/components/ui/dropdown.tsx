"use client";

import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export type DropdownOption = {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
};

interface DropdownProps {
  value: string;
  onChange: (value: string) => void;
  options: DropdownOption[];
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  required?: boolean;
  id?: string;
}

export function Dropdown({
  value,
  onChange,
  options,
  placeholder = "Select...",
  className,
  disabled,
  required,
  id,
}: DropdownProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const selected = options.find((o) => o.value === value);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open]);

  useEffect(() => {
    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    if (open) {
      document.addEventListener("keydown", handleEscape);
      return () => document.removeEventListener("keydown", handleEscape);
    }
  }, [open]);

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      {required && (
        <input
          tabIndex={-1}
          aria-hidden
          value={value}
          required
          onChange={() => {}}
          className="pointer-events-none absolute h-0 w-0 opacity-0"
        />
      )}
      <button
        type="button"
        id={id}
        disabled={disabled}
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "flex h-10 w-full items-center justify-between rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500",
          disabled && "cursor-not-allowed opacity-50",
          selected ? "text-slate-900" : "text-slate-500",
        )}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className="truncate">{selected?.label ?? placeholder}</span>
        <ChevronDown
          className={cn("ml-2 h-4 w-4 shrink-0 text-slate-500 transition-transform", open && "rotate-180")}
        />
      </button>
      {open && (
        <ul
          role="listbox"
          className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border border-slate-200 bg-white py-1 shadow-lg"
        >
          {options.map((option) => (
            <li
              key={option.value}
              role="option"
              aria-selected={option.value === value}
              onClick={() => {
                if (option.disabled) return;
                onChange(option.value);
                setOpen(false);
              }}
              className={cn(
                "flex cursor-pointer flex-col gap-0.5 px-3 py-2 text-sm hover:bg-emerald-50",
                option.value === value && "bg-emerald-50",
                option.disabled && "cursor-not-allowed opacity-50",
              )}
            >
              <span className="flex items-center justify-between gap-2 text-slate-900">
                <span className={cn("truncate", option.value === value && "font-medium")}>{option.label}</span>
                {option.value === value && <Check className="h-4 w-4 shrink-0 text-emerald-600" />}
              </span>
              {option.description && (
                <span className="text-xs leading-snug text-slate-500">{option.description}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export const YEAR_OPTIONS: DropdownOption[] = [2024, 2025, 2026, 2027].map((y) => ({
  value: String(y),
  label: String(y),
}));

