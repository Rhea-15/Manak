"use client";

import {
  Sparkles,
  FileCheck2,
  AlertTriangle,
  ArrowRight,
  Download,
  Copy,
  Check,
} from "lucide-react";
import { useState } from "react";

/* =========================================================
   RECOMMENDATIONS DATA
========================================================= */
const recommendations = [
  {
    id: "rec-1",
    clause: "Section 4.2.1 — Extinguisher Capacity",
    type: "Critical Amendment",
    issue:
      "Tender specifies 4 kg capacity for ABC powder extinguishers, violating IS 15683:2018 Clause 5.2.",
    originalText:
      "The contractor shall supply 4 kg capacity ABC dry chemical powder fire extinguishers for all commercial office floors.",
    suggestedText:
      "The contractor shall supply minimum 6 kg capacity ABC dry chemical powder fire extinguishers conforming to IS 15683:2018 for all commercial office floors.",
    rationale:
      "IS 15683:2018 mandates a minimum 6 kg capacity for ABC dry powder units in commercial facilities to ensure adequate fire rating.",
  },
  {
    id: "rec-2",
    clause: "Section 6.1.3 — Hydrostatic Test Intervals",
    type: "Specification Fix",
    issue:
      "Uniform 5-year testing interval violates IS 2190:2024 Table 3 for CO2 extinguishers.",
    originalText:
      "All fire extinguishers shall undergo hydrostatic pressure testing every 5 years from the date of manufacture.",
    suggestedText:
      "Hydrostatic pressure testing shall be conducted every 3 years for CO2 type extinguishers and every 5 years for ABC/water type extinguishers in accordance with IS 2190:2024 Table 3.",
    rationale:
      "CO2 cylinders operate under significantly higher pressure and require more frequent hydrostatic testing per IS 2190:2024.",
  },
  {
    id: "rec-3",
    clause: "Section 8.4 — Temperature Operating Range",
    type: "Clause Expansion",
    issue:
      "Narrow operating range (0°C to 50°C) limits outdoor compliance under IS 15683:2018.",
    originalText:
      "Extinguishers must be operable within ambient temperature conditions ranging from 0°C to 50°C.",
    suggestedText:
      "Extinguishers must be operable within an ambient temperature range of -10°C to +55°C as mandated by IS 15683:2018 Clause 4.3.",
    rationale:
      "Ensures full operability during extreme weather conditions across Indian climate zones.",
  },
];

/* =========================================================
   PAGE
========================================================= */
export default function RecommendationsPage() {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">
      {/* PAGE CONTENT */}
      <section className="mx-auto max-w-[1150px] px-8 py-14">
        {/* HEADING */}
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#DED2CE] bg-white px-4 py-1.5 text-xs text-[#74478A]">
              <Sparkles size={14} />
              AI Drafted Amendments
            </div>
            <h1 className="font-serif text-4xl leading-tight text-[#211735]">
              Recommended Tender Amendments
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-[#706578]">
              Ready-to-use clause modifications generated automatically to bring
              your tender specifications into 100% compliance with BIS standards.
            </p>
          </div>

          <button
            type="button"
            className="flex items-center gap-2 rounded-xl bg-[#74478A] px-5 py-3 text-xs font-medium text-white transition hover:bg-[#633A77]"
          >
            <Download size={15} />
            Export Corrigendum PDF
          </button>
        </div>

        {/* LIST OF RECOMMENDATIONS */}
        <div className="mt-10 space-y-6">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="rounded-[22px] border border-[#E4DAD5] bg-white p-7 shadow-[0_4px_20px_rgba(116,71,138,0.03)]"
            >
              <div className="flex items-center justify-between border-b border-[#EEE7E2] pb-4">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-[#74478A]">
                    {rec.clause}
                  </span>
                  <span className="rounded-full bg-[#EDE0EC] px-3 py-0.5 text-[10px] text-[#74478A]">
                    {rec.type}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs text-[#C04848]">
                  <AlertTriangle size={14} />
                  <span>Non-Compliant</span>
                </div>
              </div>

              {/* ISSUE SUMMARY */}
              <div className="mt-4 text-xs text-[#706578]">
                <strong className="text-[#211735]">Identified Defect: </strong>
                {rec.issue}
              </div>

              {/* COMPARISON */}
              <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-[#F0E6E6] bg-[#FFFBFB] p-4">
                  <div className="text-[11px] font-semibold text-[#C04848]">
                    Current Tender Clause
                  </div>
                  <p className="mt-2 text-xs leading-relaxed text-[#493D50]">
                    "{rec.originalText}"
                  </p>
                </div>

                <div className="relative rounded-xl border border-[#E6F0E8] bg-[#FBFCFB] p-4">
                  <div className="flex items-center justify-between">
                    <div className="text-[11px] font-semibold text-[#3B7A57]">
                      Suggested Compliant Clause
                    </div>
                    <button
                      type="button"
                      onClick={() => handleCopy(rec.id, rec.suggestedText)}
                      className="flex items-center gap-1 text-[11px] text-[#74478A] hover:underline"
                    >
                      {copiedId === rec.id ? (
                        <>
                          <Check size={12} className="text-[#3B7A57]" />
                          <span className="text-[#3B7A57]">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy size={12} />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className="mt-2 text-xs leading-relaxed text-[#211735]">
                    "{rec.suggestedText}"
                  </p>
                </div>
              </div>

              {/* RATIONALE */}
              <div className="mt-4 flex items-start gap-2 rounded-xl bg-[#FBF8F4] p-4 text-xs text-[#706578]">
                <FileCheck2 size={16} className="shrink-0 text-[#74478A]" />
                <div>
                  <strong className="text-[#211735]">BIS Standard Rationale: </strong>
                  {rec.rationale}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}