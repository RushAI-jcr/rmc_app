"use client";

import { Suspense, useState, useRef, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { login, getMe } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);
  const submitting = useRef(false);

  const returnTo = searchParams.get("returnTo") || "/ingest";

  useEffect(() => {
    getMe()
      .then(() => router.replace(returnTo))
      .catch(() => setChecking(false));
  }, [router, returnTo]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError(null);

    try {
      const result = await login(username, password);
      // Role-aware default redirect: reviewers -> /review, admins -> /ingest
      const defaultPath = result.role === "admin" ? "/ingest" : "/review";
      const target = searchParams.get("returnTo") || defaultPath;
      router.push(target);
    } catch {
      setError("Invalid username or password");
      submitting.current = false;
    }
  };

  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-raw-umber">Checking session...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ivory">
      <div className="w-full max-w-sm rounded-lg border border-gray bg-white p-8 shadow-sm">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-legacy-green">RMC Admissions Assistant</h1>
          <p className="text-sm text-raw-umber">AI helps you focus on mission-aligned candidates</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="mb-1 block text-sm font-medium">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              className="w-full rounded-md border border-gray px-3 py-2 text-sm focus:border-legacy-green focus:outline-none focus:ring-1 focus:ring-legacy-green"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              className="w-full rounded-md border border-gray px-3 py-2 text-sm focus:border-legacy-green focus:outline-none focus:ring-1 focus:ring-legacy-green"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-600">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="w-full rounded-md bg-legacy-green px-4 py-2 text-sm font-medium text-white hover:bg-legacy-green/90 transition-colors"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <p className="text-raw-umber">Loading...</p>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
