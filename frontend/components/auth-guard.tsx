"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getMe } from "@/lib/api";
import { Sidebar } from "@/components/ui/sidebar";

const PUBLIC_PATHS = ["/login"];

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  const isPublic = PUBLIC_PATHS.includes(pathname);

  useEffect(() => {
    if (isPublic) {
      setChecked(true);
      return;
    }

    getMe()
      .then(() => setChecked(true))
      .catch(() => {
        router.replace(`/login?returnTo=${encodeURIComponent(pathname)}`);
      });
  }, [pathname, router, isPublic]);

  // Login page: no sidebar, no margin
  if (isPublic) {
    return <>{children}</>;
  }

  // Loading auth check
  if (!checked) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-raw-umber">Loading...</p>
      </div>
    );
  }

  // Authenticated: show sidebar + content
  return (
    <>
      <Sidebar />
      <main className="ml-64 min-h-screen p-8">{children}</main>
    </>
  );
}
