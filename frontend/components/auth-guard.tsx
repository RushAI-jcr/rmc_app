"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getMe } from "@/lib/api";
import type { UserInfo } from "@/lib/types";
import { Sidebar } from "@/components/ui/sidebar";

const PUBLIC_PATHS = ["/login"];

const UserContext = createContext<UserInfo | null>(null);

export function useUser(): UserInfo | null {
  return useContext(UserContext);
}

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [checked, setChecked] = useState(false);

  const isPublic = PUBLIC_PATHS.includes(pathname);

  useEffect(() => {
    if (isPublic) {
      setChecked(true);
      return;
    }

    getMe()
      .then((data) => {
        setUser(data);
        setChecked(true);
      })
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

  // Authenticated: show sidebar + content with user context
  return (
    <UserContext.Provider value={user}>
      <Sidebar />
      <main className="ml-64 min-h-screen p-8">{children}</main>
    </UserContext.Provider>
  );
}
