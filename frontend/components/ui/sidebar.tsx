"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Users,
  Upload,
  Play,
  ClipboardCheck,
  Shield,
  GitCompare,
  LogOut,
} from "lucide-react";
import { logout } from "@/lib/api";
import { useUser } from "@/components/auth-guard";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, adminOnly: false },
  { href: "/applicants", label: "Applicants", icon: Users, adminOnly: false },
  { href: "/ingest", label: "Ingest", icon: Upload, adminOnly: true },
  { href: "/pipeline", label: "Pipeline", icon: Play, adminOnly: true },
  { href: "/review", label: "Review", icon: ClipboardCheck, adminOnly: false },
  { href: "/fairness", label: "Fairness", icon: Shield, adminOnly: true },
  { href: "/compare", label: "Compare", icon: GitCompare, adminOnly: true },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = useUser();

  const visibleItems = navItems.filter(
    (item) => !item.adminOnly || user?.role === "admin"
  );

  // Hide sidebar on login page
  if (pathname === "/login") return null;

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // Clear cookie failed, redirect anyway
    }
    router.push("/login");
  };

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-white/10 bg-legacy-green">
      <div className="p-6">
        <h1 className="text-lg font-bold text-white">RMC Admissions Assistant</h1>
        <p className="text-xs text-wash-green">AI-Powered Review Support</p>
      </div>
      <nav className="flex-1 px-3">
        {visibleItems.map((item) => {
          const active = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors mb-1",
                active
                  ? "bg-vitality-green/20 text-vitality-green"
                  : "text-white/80 hover:bg-white/10 hover:text-white"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-white/10 px-3 py-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-white/80 hover:bg-white/10 hover:text-white transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
