"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles, Search } from "lucide-react";

export default function RecommendationsPage() {
  const [query, setQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <main className="min-h-screen bg-[#FAF6F0] text-[#2D2138]">
      <section className="mx-auto max-w-[960px] px-6 py-8">
        {/* BACK TO HOME */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-medium text-[#7D7086] transition-colors hover:text-[#2D2138]"
        >
          <ArrowLeft size={14} />
          Back to home
        </Link>

        {/* HEADER SECTION */}
        <div className="mt-8">
          <div className="inline-flex items-center gap-1.5 text-[11px] font-semibold tracking-wider text-[#9E6290] uppercase">
            <Sparkles size={13} />
            AI Recommendations
          </div>

          <h1 className="mt-2 font-serif text-5xl leading-[1.15] tracking-tight text-[#2D2138]">
            Find the right <br />
            <span className="text-[#683C74]">Indian Standards.</span>
          </h1>

          <p className="mt-4 max-w-xl text-sm leading-relaxed text-[#7D7086]">
            Describe your product, material, equipment, or procurement requirement and
            MANAK will suggest the applicable Indian Standards.
          </p>
        </div>

        {/* INPUT CARD */}
        <div className="mt-8 rounded-[28px] border border-[#F0E8E1] bg-white p-7 shadow-[0_2px_12px_rgba(0,0,0,0.02)]">
          <label className="block text-xs font-semibold text-[#2D2138]">
            Describe your requirement
          </label>

          <form onSubmit={handleSearch} className="mt-3 space-y-5">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: Stainless steel water storage tank for a residential building..."
              rows={5}
              className="w-full resize-none rounded-[18px] border border-[#ECDCEB] bg-[#FAF3FA]/40 p-4 text-xs leading-relaxed text-[#2D2138] placeholder-[#B39DB0] focus:border-[#683C74] focus:bg-white focus:outline-none"
            />

            <button
              type="submit"
              className="inline-flex items-center gap-2 rounded-full bg-[#683C74] px-6 py-3 text-xs font-medium text-white transition hover:bg-[#563061]"
            >
              <Search size={14} />
              Find applicable standards
            </button>
          </form>
        </div>

        {/* 3 STEP PASTEL PROCESS CARDS */}
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          {/* STEP 1 - PURPLE PASTEL */}
          <div className="rounded-[22px] bg-[#F1E7F2] p-6 text-[#2D2138]">
            <span className="text-xs font-semibold text-[#826688]">01</span>
            <h3 className="mt-2 font-serif text-xl font-medium text-[#2D2138]">
              Understand
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-[#7D7086]">
              MANAK analyses your product or procurement requirement.
            </p>
          </div>

          {/* STEP 2 - PEACH PASTEL */}
          <div className="rounded-[22px] bg-[#F9E9E5] p-6 text-[#2D2138]">
            <span className="text-xs font-semibold text-[#A8726B]">02</span>
            <h3 className="mt-2 font-serif text-xl font-medium text-[#2D2138]">
              Recommend
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-[#7D7086]">
              Relevant Indian Standards are identified from the standards database.
            </p>
          </div>

          {/* STEP 3 - YELLOW PASTEL */}
          <div className="rounded-[22px] bg-[#FAF0D8] p-6 text-[#2D2138]">
            <span className="text-xs font-semibold text-[#A18854]">03</span>
            <h3 className="mt-2 font-serif text-xl font-medium text-[#2D2138]">
              Verify
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-[#7D7086]">
              Review the recommended standards before using them in procurement.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}