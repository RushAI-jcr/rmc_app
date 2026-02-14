import type { Metadata } from "next";
import "./globals.css";
import { AuthGuard } from "@/components/auth-guard";

export const metadata: Metadata = {
  title: "RMC Admissions Assistant",
  description: "AI-powered assistant helping Rush Medical College admissions focus on mission-aligned candidates",
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
