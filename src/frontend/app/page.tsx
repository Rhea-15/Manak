"use client";

import Link from "next/link";
import {
  ArrowUpRight,
  Search,
  Sparkles,
  ShieldCheck,
  Upload,
} from "lucide-react";
import Header from "@/components/header";

export default function Home() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#fbf7f1] text-[#281b3b]">

      {/* HEADER */}
      <Header />

      {/* HERO */}
      <section className="relative min-h-[760px] px-6 pt-24">

        {/* LEFT DECORATIVE SHAPE */}
        <div className="pointer-events-none absolute left-[-180px] top-[80px] hidden h-[650px] w-[520px] lg:block">
          <div className="absolute inset-0 rounded-full border border-[#d8a29d]/40" />

          <div className="absolute left-[-40px] top-[100px] h-[390px] w-[390px] rounded-full bg-[#e9b5a9]/20" />

          <div className="absolute left-[80px] top-[170px] h-[300px] w-[300px] rounded-full bg-[#d7b7d9]/20" />

          {/* Minimal India/BIS document illustration */}
          <div className="absolute left-[115px] top-[160px] h-[310px] w-[220px] rotate-[-8deg] rounded-[12px] border border-[#9f718d]/20 bg-white/35 p-7 shadow-sm">
            <div className="mb-8 h-2 w-20 rounded-full bg-[#75468b]/20" />
            <div className="space-y-3">
              <div className="h-2 w-full rounded-full bg-[#75468b]/10" />
              <div className="h-2 w-5/6 rounded-full bg-[#a85886]/10" />
              <div className="h-2 w-4/6 rounded-full bg-[#c57d82]/10" />
            </div>

            <div className="absolute bottom-8 left-7 right-7 rounded-lg border border-[#75468b]/10 p-4">
              <div className="mb-3 h-2 w-16 rounded-full bg-[#75468b]/15" />
              <div className="h-1.5 w-full rounded-full bg-[#c57d82]/10" />
              <div className="mt-2 h-1.5 w-4/5 rounded-full bg-[#e8b995]/20" />
            </div>
          </div>
        </div>

        {/* RIGHT DECORATIVE SHAPE */}
        <div className="pointer-events-none absolute right-[-170px] top-[80px] hidden h-[650px] w-[520px] lg:block">
          <div className="absolute inset-0 rounded-full border border-[#d8a29d]/40" />

          <div className="absolute right-[-30px] top-[130px] h-[410px] w-[410px] rounded-full bg-[#e8c49f]/20" />

          <div className="absolute right-[90px] top-[210px] h-[300px] w-[300px] rounded-full bg-[#e4c5d0]/20" />

          {/* Standards document */}
          <div className="absolute right-[110px] top-[150px] h-[350px] w-[240px] rotate-[8deg] rounded-[14px] border border-[#75468b]/15 bg-white/40 p-8 shadow-sm">
            <div className="mb-7 flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-[#75468b]/10" />
              <div className="h-2 w-24 rounded-full bg-[#75468b]/15" />
            </div>

            <div className="space-y-4">
              <div className="h-2 w-full rounded-full bg-[#75468b]/10" />
              <div className="h-2 w-11/12 rounded-full bg-[#a85886]/10" />
              <div className="h-2 w-4/5 rounded-full bg-[#c57d82]/10" />
              <div className="h-2 w-10/12 rounded-full bg-[#e8b995]/15" />
            </div>

            <div className="absolute bottom-10 left-8 right-8 rounded-xl border border-[#a85886]/10 p-5">
              <div className="mb-4 h-2 w-20 rounded-full bg-[#a85886]/15" />
              <div className="h-2 w-full rounded-full bg-[#c57d82]/10" />
              <div className="mt-2 h-2 w-3/4 rounded-full bg-[#e8b995]/15" />
            </div>
          </div>
        </div>

        {/* HERO CONTENT */}
        <div className="relative z-10 mx-auto max-w-4xl text-center">

          <p className="mb-8 text-[12px] font-medium uppercase tracking-[0.35em] text-[#a85886]">
            Intelligent Procurement · Indian Standards
          </p>

          <h1 className="font-serif text-6xl leading-[0.98] tracking-[-0.04em] md:text-8xl">
            Find the right
            <br />

            <span className="bg-gradient-to-r from-[#75468b] via-[#a85886] to-[#c57d82] bg-clip-text text-transparent">
              standards, effortlessly.
            </span>
          </h1>

          <p className="mx-auto mt-9 max-w-2xl text-[17px] leading-7 text-[#716879]">
            MANAK helps procurement teams understand tender specifications,
            discover applicable Indian Standards, and check compliance —
            all in one place.
          </p>

          {/* BUTTONS */}
          <div className="mt-10 flex justify-center gap-4">

            <Link
              href="/upload"
              className="group flex items-center gap-3 rounded-xl bg-[#75468b] px-7 py-4 text-sm font-medium text-white shadow-lg shadow-[#75468b]/15 transition hover:-translate-y-0.5 hover:bg-[#653b78]"
            >
              <Upload size={18} />
              Upload a tender
              <ArrowUpRight
                size={17}
                className="transition-transform group-hover:translate-x-1 group-hover:-translate-y-1"
              />
            </Link>

            <Link
              href="/search"
              className="flex items-center gap-3 rounded-xl border border-[#b58cae] bg-white/50 px-7 py-4 text-sm font-medium text-[#75468b] transition hover:bg-white"
            >
              <Search size={18} />
              Explore standards
            </Link>

          </div>
        </div>

        {/* FEATURE SECTION */}
        <div className="relative z-10 mx-auto mt-20 max-w-5xl">

          <div className="mb-6">
            <p className="text-[11px] font-medium uppercase tracking-[0.3em] text-[#a85886]">
              Everything you need
            </p>

            <h2 className="mt-3 font-serif text-3xl leading-tight md:text-4xl">
              From tender document
              <br />
              to compliant procurement.
            </h2>
          </div>

          {/* 2 × 2 FEATURE GRID */}
          <div className="overflow-hidden rounded-2xl border border-[#dfd2ca] bg-white/45 backdrop-blur">

            {/* ROW 1 */}
            <div className="grid md:grid-cols-2">

              <Feature
                icon={<Upload size={21} />}
                title="Upload & Analyse"
                description="Upload a tender document and let MANAK identify the relevant standards."
                color="purple"
                href="/upload"
              />

              <Feature
                icon={<Search size={21} />}
                title="Search Standards"
                description="Find applicable Indian Standards using natural language."
                color="rose"
                href="/search"
                border
              />

            </div>

            {/* ROW 2 */}
            <div className="grid border-t border-[#dfd2ca] md:grid-cols-2">

              <Feature
                icon={<Sparkles size={21} />}
                title="AI Recommendations"
                description="Get AI-powered recommendations based on your specifications."
                color="rose"
                href="/recommendations"
              />

              <Feature
                icon={<ShieldCheck size={21} />}
                title="Check Compliance"
                description="Verify tender specifications against applicable requirements."
                color="peach"
                href="/compliance"
                border
              />

            </div>

          </div>
        </div>

      </section>

      {/* FOOTER */}
      <footer className="border-t border-[#e5dbd3] bg-[#fbf7f1] px-8 py-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between">

          <div>
            <p className="font-serif text-xl tracking-wide">
              MANAK
            </p>

            <p className="mt-1 text-[9px] uppercase tracking-[0.25em] text-[#8a7d88]">
              AI for smarter procurement
            </p>
          </div>

          <p className="text-xs text-[#817783]">
            Built for transparent, compliant procurement · MANAK v1.0
          </p>

        </div>
      </footer>

    </div>
  );
}


/* -------------------------------- */
/* FEATURE CARD COMPONENT */
/* -------------------------------- */

function Feature({
  icon,
  title,
  description,
  color,
  href,
  border = false,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: "purple" | "rose" | "peach";
  href: string;
  border?: boolean;
}) {
  const iconColors = {
    purple: "bg-[#75468b] text-white",
    rose: "bg-[#c57d82] text-white",
    peach: "bg-[#e5a875] text-white",
  };

  return (
    <Link
      href={href}
      className={`group flex items-center gap-6 p-7 transition hover:bg-white/70 ${
        border ? "md:border-l md:border-[#dfd2ca]" : ""
      }`}
    >
      <div
        className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-full ${iconColors[color]} shadow-sm`}
      >
        {icon}
      </div>

      <div className="flex-1">
        <h3 className="font-serif text-xl">
          {title}
        </h3>

        <p className="mt-1 max-w-sm text-sm leading-6 text-[#716879]">
          {description}
        </p>
      </div>

      <ArrowUpRight
        size={20}
        className="shrink-0 text-[#4b3d50] transition-transform group-hover:translate-x-1 group-hover:-translate-y-1"
      />
    </Link>
  );
}