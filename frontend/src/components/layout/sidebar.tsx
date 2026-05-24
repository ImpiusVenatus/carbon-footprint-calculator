"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  BarChart3,
  ClipboardList,
  FileText,
  Leaf,
  LogOut,
  Target,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { clearTokens } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/components/auth/auth-guard";

const navItems = [
  { href: "/overview", label: "Overview", icon: BarChart3 },
  { href: "/activities", label: "Activities", icon: Activity },
  { href: "/factors", label: "Emission Factors", icon: Zap },
  { href: "/targets", label: "Targets", icon: Target },
  { href: "/reports", label: "Reports", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAdmin } = useAuth();

  function logout() {
    clearTokens();
    router.push("/login");
  }

  const items = isAdmin
    ? [...navItems, { href: "/audit", label: "Audit log", icon: ClipboardList }]
    : navItems;

  return (
    <aside className="flex h-full w-64 flex-col border-r border-slate-200 bg-slate-900 text-white">
      <div className="flex items-center gap-2 border-b border-slate-700 px-6 py-5">
        <Leaf className="h-6 w-6 text-emerald-400" />
        <p className="font-semibold">Carbon Footprint</p>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {items.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname === href
                ? "bg-emerald-600 text-white"
                : "text-slate-300 hover:bg-slate-800 hover:text-white",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
      {user && (
        <div className="border-t border-slate-700 px-4 py-3">
          <p className="truncate text-xs text-slate-400">{user.email}</p>
          <span className="mt-1 inline-block rounded bg-slate-800 px-2 py-0.5 text-xs capitalize text-emerald-300">
            {user.role}
          </span>
        </div>
      )}
      <div className="border-t border-slate-700 p-4">
        <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-white" onClick={logout}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </Button>
      </div>
    </aside>
  );
}
