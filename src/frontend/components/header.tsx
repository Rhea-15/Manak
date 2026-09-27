"use client";

import { useState, useRef, useEffect } from "react";
import {
  Search,
  Globe,
  ChevronDown,
  FileText,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

const languages = [
  { name: "English", code: "EN" },
  { name: "Hindi", code: "HI" },
  { name: "Marathi", code: "MR" },
  { name: "Gujarati", code: "GU" },
  { name: "Bengali", code: "BN" },
  { name: "Tamil", code: "TA" },
  { name: "Telugu", code: "TE" },
  { name: "Kannada", code: "KN" },
  { name: "Malayalam", code: "ML" },
  { name: "Punjabi", code: "PA" },
];

export default function Header() {
  const [language, setLanguage] = useState("English");
  const [isLangOpen, setIsLangOpen] = useState(false);
  const [isUserDashboardOpen, setIsUserDashboardOpen] = useState(false);

  const langRef = useRef<HTMLDivElement>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);

  const selectedLang =
    languages.find((l) => l.name === language) || languages[0];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setIsLangOpen(false);
      }
      if (
        dashboardRef.current &&
        !dashboardRef.current.contains(event.target as Node)
      ) {
        setIsUserDashboardOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-50 flex h-20 items-center justify-between border-b border-[#E4DAD5] bg-[#FBF8F4] px-8">
      {/* LOGO */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#74478A] text-lg font-bold text-white">
          M
        </div>
        <div>
          <span className="font-serif text-xl font-bold tracking-tight text-[#211735]">
            MANAK
          </span>
          <p className="text-[10px] font-medium tracking-wider text-[#806D7B] uppercase">
            AI FOR SMARTER PROCUREMENT
          </p>
        </div>
      </div>

      {/* SEARCH BAR */}
      <div className="hidden max-w-md flex-1 px-8 md:block">
        <div className="flex h-10 items-center gap-2 rounded-full border border-[#D9C7D6] bg-white px-4">
          <Search className="text-[#806D7B]" size={14} />
          <input
            type="text"
            placeholder="Search IS Codes, standards, or type in natural language..."
            className="w-full bg-transparent text-xs text-[#211735] outline-none placeholder:text-[#A3989D]"
          />
        </div>
      </div>

      {/* CONTROLS */}
      <div className="flex items-center gap-4">
        {/* LANGUAGE DROPDOWN */}
        <div className="relative" ref={langRef}>
          <button
            type="button"
            onClick={() => setIsLangOpen(!isLangOpen)}
            className="flex items-center gap-2 rounded-full border border-[#D9C7D6] bg-white px-4 py-2 text-xs font-medium text-[#74478A] shadow-sm transition hover:border-[#A35A91] hover:bg-[#F8EFF7] cursor-pointer"
          >
            <Globe size={15} />
            <span>{selectedLang.code}</span>
            <ChevronDown
              size={14}
              className={`transition-transform duration-200 ${
                isLangOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {isLangOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-2xl border border-[#D9C7D6] bg-white py-2 shadow-xl z-50">
              <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#A3989D]">
                Select Language
              </div>
              <div className="max-h-60 overflow-y-auto">
                {languages.map((lang) => (
                  <button
                    key={lang.name}
                    type="button"
                    onClick={() => {
                      setLanguage(lang.name);
                      setIsLangOpen(false);
                    }}
                    className={`flex w-full items-center justify-between px-4 py-2 text-xs transition ${
                      language === lang.name
                        ? "bg-[#F0E3EF] font-semibold text-[#74478A]"
                        : "text-[#211735] hover:bg-[#F8EFF7]"
                    }`}
                  >
                    <span>{lang.name}</span>
                    <span className="text-[10px] text-[#806D7B]">
                      {lang.code}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* USER PROFILE & AI DASHBOARD DROPDOWN */}
        <div className="relative" ref={dashboardRef}>
          <button
            type="button"
            onClick={() => setIsUserDashboardOpen(!isUserDashboardOpen)}
            className="flex items-center gap-3 border-l border-[#E4DAD5] pl-4 focus:outline-none cursor-pointer"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#74478A] text-xs font-bold text-white shadow-sm">
              AM
            </div>
            <div className="hidden flex-col text-left sm:flex">
              <span className="text-xs font-semibold text-[#211735]">
                Aarav Mehta
              </span>
              <span className="text-[10px] text-[#806D7B]">
                Organization Member
              </span>
            </div>
            <ChevronDown
              size={14}
              className={`text-[#806D7B] transition-transform duration-200 ${
                isUserDashboardOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {/* USER AI WORKSPACE OVERVIEW CARD */}
          {isUserDashboardOpen && (
            <div className="absolute right-0 mt-3 w-80 rounded-2xl border border-[#E4DAD5] bg-white p-5 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="flex items-center gap-3 pb-4 border-b border-[#F0E8EF]">
                <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#74478A] text-sm font-bold text-white">
                  AM
                </div>
                <div>
                  <h4 className="font-serif text-base font-bold text-[#211735]">
                    Aarav Mehta
                  </h4>
                  <p className="text-[11px] text-[#806D7B]">
                    Organization Member • ID #88412
                  </p>
                </div>
              </div>

              <div className="mt-4 mb-3">
                <span className="text-[10px] font-bold tracking-wider text-[#988295] uppercase">
                  USER AI WORKSPACE OVERVIEW
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-[#F0E8EF] bg-[#FCF8FB] p-3">
                  <div className="flex items-center gap-1.5 text-[11px] text-[#806D7B]">
                    <FileText size={13} className="text-[#74478A]" />
                    <span>Evaluations</span>
                  </div>
                  <p className="mt-2 text-xl font-bold text-[#211735]">24</p>
                </div>

                <div className="rounded-xl border border-[#F0E8EF] bg-[#FCF8FB] p-3">
                  <div className="flex items-center gap-1.5 text-[11px] text-[#806D7B]">
                    <CheckCircle2 size={13} className="text-[#5D8260]" />
                    <span>Compliance Rate</span>
                  </div>
                  <p className="mt-2 text-xl font-bold text-[#211735]">
                    98.2%
                  </p>
                </div>
              </div>

              <div className="mt-3 rounded-xl border border-[#F0E8EF] bg-[#FCF8FB] p-3">
                <div className="flex items-center justify-between text-[11px] text-[#806D7B]">
                  <div className="flex items-center gap-1.5 font-medium text-[#74478A]">
                    <Sparkles size={13} />
                    <span>Recent AI Audit Search</span>
                  </div>
                  <span className="text-[10px] text-[#A3989D]">Today</span>
                </div>
                <p className="mt-1.5 text-xs font-semibold leading-snug text-[#211735]">
                  IS 456:2000 Structural Code Alignment Check
                </p>
              </div>

              <div className="mt-4 flex items-center justify-between pt-3 border-t border-[#F0E8EF] text-[11px]">
                <span className="flex items-center gap-1.5 text-[#5D8260] font-medium">
                  <span className="h-2 w-2 rounded-full bg-[#5D8260]" />
                  Active Session
                </span>
                <button
                  type="button"
                  onClick={() => setIsUserDashboardOpen(false)}
                  className="font-medium text-[#74478A] hover:underline cursor-pointer"
                >
                  Close Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}