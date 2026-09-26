"use client";

import Link from "next/link";
import { Bell, ChevronDown } from "lucide-react";
import { useState } from "react";

export default function Header() {
  const [languageOpen, setLanguageOpen] = useState(false);
  const [language, setLanguage] = useState("EN");

  const languages = ["EN", "हिन्दी", "मराठी"];

  return (
    <header className="border-b border-[#E7DDD7] bg-[#FBF8F4]">
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


        {/* SEARCH */}
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
              className="..."
            />
          </div>
        </div>


        {/* RIGHT SIDE */}
        <div className="flex items-center gap-5">

          {/* LANGUAGE */}
          <div className="relative">

            <button
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


            {/* LANGUAGE DROPDOWN */}
            {languageOpen && (
              <div className="absolute right-0 top-[48px] z-50 w-36 overflow-hidden rounded-xl border border-[#E4D8E0] bg-white p-1 shadow-lg">

                {languages.map((lang) => (
                  <button
                    key={lang}
                    onClick={() => {
                      setLanguage(lang);
                      setLanguageOpen(false);
                    }}
                    className={`w-full rounded-lg px-4 py-2.5 text-left text-sm transition ${
                      language === lang
                        ? "bg-[#EDE0EC] font-medium text-[#74478A]"
                        : "text-[#493D50] hover:bg-[#F7F1F6]"
                    }`}
                  >
                    {lang}
                  </button>
                ))}

              </div>
            )}

          </div>


          {/* NOTIFICATION */}
          <button aria-label="Notifications" className="relative flex h-10 w-10 items-center justify-center rounded-full text-[#493D50] transition hover:bg-white">

            <Bell size={21} strokeWidth={1.7} />

            <span className="absolute right-[8px] top-[7px] h-2 w-2 rounded-full bg-[#C97878]" />

          </button>


          {/* PROFILE */}
          <button className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#A35A91] text-xs text-white">
              RS
            </div>

            <div className="hidden text-left sm:block">

              <div className="text-sm font-medium text-[#211735]">
                Riya Sharma
              </div>

              <div className="text-xs text-[#806D7B]">
                Procurement Officer
              </div>

            </div>

            <ChevronDown
              size={15}
              className="hidden text-[#806D7B] sm:block"
            />

          </button>

        </div>

      </div>
    </header>
  );
}