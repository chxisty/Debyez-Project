import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "Aegis Series-7 HCS | Evidence-Based AI Knowledge System",
  description: "Debyez Technologies Aegis Series-7 Hydraulic Control System (HCS) Knowledge Ingestion and Verification Engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full">
      <body className="min-h-full bg-[#0b0f19] text-slate-100 flex antialiased">
        <Sidebar />
        <main className="flex-1 min-w-0 h-screen overflow-y-auto bg-[#0b0f19] flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
