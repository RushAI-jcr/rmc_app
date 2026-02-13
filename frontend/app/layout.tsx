import type { Metadata } from "next";
import "./globals.css";
import { AuthGuard } from "@/components/auth-guard";

export const metadata: Metadata = {
  title: "Rush Medical College — Admissions Triage",
  description: "Decision-support tool for Rush Medical College admissions review",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-ivory">
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
