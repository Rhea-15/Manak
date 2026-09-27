import type { Metadata } from "next";
import Header from "../components/header";
import "./globals.css";

export const metadata: Metadata = {
  title: "MANAK - Intelligent Procurement",
  description: "AI-powered procurement and Indian Standards compliance",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#fbf7f1] text-[#281b3b]">
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}