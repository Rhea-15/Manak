"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { ChevronDown, Activity, FileCheck, Clock, ShieldCheck } from "lucide-react";

export default function Header() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  // Sync state with URL or default to EN
  const currentLangCode = searchParams.get("lang") || "EN";
  const [language, setLanguage] = useState(currentLangCode);
  const [languageOpen, setLanguageOpen] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);

  const languages = [
    { code: "EN", name: "English" },
    { code: "HI", name: "Hindi (हिन्दी)" },
    { code: "MR", name: "Marathi (मराठी)" },
    { code: "GU", name: "Gujarati (ગુજરાતી)" },
    { code: "BN", name: "Bengali (বাংলা)" },
    { code: "TA", name: "Tamil (தமிழ்)" },
    { code: "TE", name: "Telugu (తెలుగు)" },
    { code: "KN", name: "Kannada (ಕನ್ನಡ)" },
    { code: "ML", name: "Malayalam (മലയാളം)" },
    { code: "PA", name: "Punjabi (ਪੰਜਾਬੀ)" },
  ];

  useEffect(() => {
    setLanguage(currentLangCode);
  }, [currentLangCode]);

  const handleLanguageChange = (code: string) => {
    setLanguage(code);
    setLanguageOpen(false);

    // Update URL params seamlessly
    const params = new URLSearchParams(searchParams.toString());
    params.set("lang", code);
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <header className="border-b border-[#E7DDD7] bg-[#FBF8F4] sticky top-0 z-50">
      <div className="mx-auto flex h-[76px] max-w-[1400px] items-center justify-between px-8">

        {/* LOGO */}
        <Link
          href="/"
          className="flex items-center gap-3 transition-opacity hover:opacity-80"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#74478A] font-serif text-white">
            M
          </div>

          <div>
            <div className="font-serif text-xl tracking-wide text-[#211735]">
              MANAK
            </div>

            <div className="text-[8px] uppercase tracking-[0.22em] text-[#806D7B]">
              AI for Smarter Procurement
            </div>
          </div>
        </Link>

        {/* SEARCH BAR */}
        <div className="hidden w-[48%] md:block">
          <div className="flex h-[55px] items-center rounded-full border border-[#D4B7D5] bg-[#F1E4F0] px-5">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              className="text-[#74478A]"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-4-4" />
            </svg>

            <input
              type="text"
              placeholder="Search IS Codes, standards, or type in natural language..."
              suppressHydrationWarning
              className="w-full bg-transparent px-3 text-sm text-[#211735] placeholder-[#806D7B] focus:outline-none"
            />
          </div>
        </div>

        {/* RIGHT SIDE CONTROLS */}
        <div className="flex items-center gap-5">

          {/* LANGUAGE SWITCHER */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setLanguageOpen(!languageOpen)}
              className="flex items-center gap-2 rounded-full border border-[#DED2CE] bg-[#FBF8F4] px-4 py-2 text-sm text-[#493D50] transition hover:bg-white"
            >
              {language}

              <ChevronDown
                size={15}
                className={`transition-transform ${
                  languageOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* 10-LANGUAGE DROPDOWN */}
            {languageOpen && (
              <div className="absolute right-0 top-[48px] z-50 w-56 overflow-hidden rounded-xl border border-[#E4D8E0] bg-white p-2 shadow-xl">
                <p className="px-2 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-[#A35A91]">
                  Select Language
                </p>
                <div className="grid grid-cols-2 gap-1">
                  {languages.map((item) => (
                    <button
                      key={item.code}
                      type="button"
                      onClick={() => handleLanguageChange(item.code)}
                      className={`rounded-lg px-2.5 py-1.5 text-left text-xs transition ${
                        language === item.code
                          ? "bg-[#EDE0EC] font-medium text-[#74478A]"
                          : "text-[#493D50] hover:bg-[#F7F1F6]"
                      }`}
                    >
                      {item.code}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* USER PROFILE */}
          <div className="relative">
            <button 
              type="button"
              onClick={() => setDashboardOpen(!dashboardOpen)}
              className="flex items-center gap-3 rounded-full p-1.5 transition hover:bg-white/80"
              aria-label="User profile and dashboard"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#A35A91] text-xs font-semibold text-white shadow-sm">
                AM
              </div>

              <div className="hidden text-left sm:block">
                <div className="text-sm font-medium text-[#211735]">
                  Aarav Mehta
                </div>

                <div className="text-xs text-[#806D7B]">
                  Organization Member
                </div>
              </div>

              <ChevronDown
                size={15}
                className={`hidden text-[#806D7B] transition-transform sm:block ${
                  dashboardOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* AI USER DASHBOARD POPOVER */}
            {dashboardOpen && (
              <div className="absolute right-0 top-[56px] z-50 w-80 rounded-2xl border border-[#E4D8E0] bg-white p-5 shadow-2xl transition-all">
                <div className="flex items-center gap-3 border-b border-[#F0E6EE] pb-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#74478A] text-sm font-bold text-white">
                    AM
                  </div>
                  <div>
                    <h4 className="font-serif text-base font-semibold text-[#211735]">Aarav Mehta</h4>
                    <p className="text-xs text-[#806D7B]">Organization Member • ID #88412</p>
                  </div>
                </div>

                <div className="mt-4 space-y-3">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-[#806D7B]">
                    User AI Workspace Overview
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="rounded-xl bg-[#FBF8F4] p-3 border border-[#E7DDD7]">
                      <div className="flex items-center gap-1.5 text-[#74478A] font-medium mb-1">
                        <FileCheck size={14} />
                        Evaluations
                      </div>
                      <div className="text-lg font-bold text-[#211735]">24</div>
                    </div>

                    <div className="rounded-xl bg-[#FBF8F4] p-3 border border-[#E7DDD7]">
                      <div className="flex items-center gap-1.5 text-[#74478A] font-medium mb-1">
                        <ShieldCheck size={14} />
                        Compliance Rate
                      </div>
                      <div className="text-lg font-bold text-[#211735]">98.2%</div>
                    </div>
                  </div>

                  <div className="mt-2 rounded-xl border border-[#E4D8E0] bg-[#FAF5F9] p-3">
                    <div className="flex items-center justify-between text-xs font-medium text-[#493D50] mb-2">
                      <span className="flex items-center gap-1">
                        <Activity size={13} className="text-[#74478A]" />
                        Recent AI Audit Search
                      </span>
                      <span className="text-[10px] text-[#806D7B]">Today</span>
                    </div>
                    <p className="text-xs text-[#211735] font-sans">
                      IS 456:2000 Structural Code Alignment Check
                    </p>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-[#F0E6EE] flex justify-between items-center text-xs">
                  <span className="text-[11px] text-[#806D7B] flex items-center gap-1">
                    <Clock size={12} /> Active Session
                  </span>
                  <button 
                    type="button"
                    onClick={() => setDashboardOpen(false)}
                    className="text-[#74478A] font-medium hover:underline"
                  >
                    Close Dashboard
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>

      </div>
    </header>
  );
}