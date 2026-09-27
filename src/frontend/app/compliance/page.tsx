"use client";

import { useEffect, useState } from "react";
import {
  FileText,
  AlertTriangle,
  GitBranch,
  Search,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ShieldCheck,
  ChevronDown,
  ArrowRight,
} from "lucide-react";

import NormativeTreeGraph from "@/components/NormativeTreeGraph";
import DiffAndGaugeView from "@/components/DiffAndGaugeView";

/* =========================================================
   TYPES & DATA
========================================================= */
interface NonComplianceItem {
  id: string;
  clause: string;
  standard: string;
  tenderRequirement: string;
  isStandardRequirement: string;
  gapAnalysis: string;
  severity: "high" | "medium" | "low";
  category: string;
  actionRequired: string;
}

const mockNonCompliances: NonComplianceItem[] = [
  {
    id: "nc-1",
    clause: "Section 4.2.1",
    standard: "IS 15683:2018",
    tenderRequirement:
      "Portable fire extinguishers shall have a minimum capacity of 4 kg for ABC dry powder type.",
    isStandardRequirement:
      "IS 15683:2018 Clause 5.2 specifies a minimum capacity of 6 kg for ABC dry powder extinguishers in commercial premises.",
    gapAnalysis:
      "Tender specifies 4 kg capacity which is below the IS 15683:2018 minimum of 6 kg for commercial deployment.",
    severity: "high",
    category: "Capacity Requirement",
    actionRequired:
      "Update tender specifications to mandate 6 kg ABC dry powder extinguishers to comply with IS 15683:2018.",
  },
  {
    id: "nc-2",
    clause: "Section 6.1.3",
    standard: "IS 2190:2024",
    tenderRequirement:
      "Maintenance and hydrostatic testing interval specified as 5 years for all fire extinguisher types.",
    isStandardRequirement:
      "IS 2190:2024 Table 3 requires hydrostatic pressure testing every 3 years for CO2 extinguishers and 5 years for ABC powder type.",
    gapAnalysis:
      "Uniform 5-year testing interval violates IS 2190:2024 for CO2 type extinguishers which require 3-year testing intervals.",
    severity: "medium",
    category: "Maintenance Protocol",
    actionRequired:
      "Specify separate hydrostatic test intervals: 3 years for CO2 and 5 years for ABC/water type extinguishers.",
  },
  {
    id: "nc-3",
    clause: "Section 8.4",
    standard: "IS 15683:2018",
    tenderRequirement:
      "Operating temperature range specified as 0°C to 50°C.",
    isStandardRequirement:
      "IS 15683:2018 Clause 4.3 requires operating temperature range of -10°C to +55°C for all-weather outdoor deployment.",
    gapAnalysis:
      "Tender temperature range (0°C to 50°C) is narrower than IS standard requirement (-10°C to +55°C).",
    severity: "low",
    category: "Environmental Limits",
    actionRequired:
      "Expand operating temperature range in tender to -10°C to +55°C.",
  },
];

const mockTenderInfo = {
  title: "Procurement of Fire Safety Equipment & Extinguishers",
  referenceNo: "TENDER/2026/BIS/FS-089",
  organization: "Central Public Works Department (CPWD)",
  publishDate: "12 Feb 2026",
  submissionDeadline: "15 Mar 2026",
  category: "Fire Safety & Protection",
  estimatedValue: "₹45,00,000",
  totalClausesAnalyzed: 48,
  compliantClauses: 41,
  nonCompliantClauses: 3,
  ambiguousClauses: 4,
  overallScore: 85,
};

/* =========================================================
   PAGE COMPONENT
========================================================= */
export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "tree" | "diff" | "non-compliance"
  >("overview");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  useEffect(() => {
    const storedName = localStorage.getItem("uploadedFileName");
    if (storedName) {
      setUploadedFileName(storedName);
    }
  }, []);

  const filteredNCs = mockNonCompliances.filter((nc) => {
    const matchesSeverity =
      selectedSeverity === "all" || nc.severity === selectedSeverity;
    const matchesSearch =
      nc.clause.toLowerCase().includes(searchTerm.toLowerCase()) ||
      nc.standard.toLowerCase().includes(searchTerm.toLowerCase()) ||
      nc.tenderRequirement.toLowerCase().includes(searchTerm.toLowerCase()) ||
      nc.category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-[#FBF8F4] text-[#211735]">
      <main className="mx-auto max-w-[1300px] px-8 py-10">
        {/* TENDER DOCUMENT BANNER */}
        <div className="mb-8 rounded-[22px] border border-[#E4DAD5] bg-white p-7 shadow-[0_4px_20px_rgba(116,71,138,0.04)]">
          <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
            <div className="flex items-start gap-5">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-[#F0E3EF] text-[#74478A]">
                <FileText size={26} strokeWidth={1.6} />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <span className="rounded-full bg-[#EDE0EC] px-3 py-1 text-xs font-medium text-[#74478A]">
                    {mockTenderInfo.referenceNo}
                  </span>
                  <span className="text-xs text-[#806D7B]">
                    {mockTenderInfo.category}
                  </span>
                </div>
                <h1 className="mt-2 font-serif text-2xl font-normal text-[#211735]">
                  {uploadedFileName
                    ? uploadedFileName
                    : mockTenderInfo.title}
                </h1>
                <p className="mt-1 text-xs text-[#806D7B]">
                  Issued by: {mockTenderInfo.organization}
                </p>
              </div>
            </div>

            {/* QUICK STATS */}
            <div className="flex flex-wrap items-center gap-6 border-t border-[#EEE7E2] pt-4 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
              <div className="text-center">
                <div className="font-serif text-3xl text-[#74478A]">
                  {mockTenderInfo.overallScore}%
                </div>
                <div className="text-[11px] text-[#806D7B]">
                  Compliance Score
                </div>
              </div>
              <div className="h-8 w-px bg-[#E4DAD5]" />
              <div className="text-center">
                <div className="font-serif text-3xl text-[#211735]">
                  {mockTenderInfo.totalClausesAnalyzed}
                </div>
                <div className="text-[11px] text-[#806D7B]">
                  Clauses Analyzed
                </div>
              </div>
              <div className="h-8 w-px bg-[#E4DAD5]" />
              <div className="text-center">
                <div className="font-serif text-3xl text-[#C04848]">
                  {mockTenderInfo.nonCompliantClauses}
                </div>
                <div className="text-[11px] text-[#806D7B]">
                  Non-Compliant
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* TABS NAVIGATION */}
        <div className="mb-8 flex items-center gap-2 border-b border-[#E4DAD5] pb-3">
          <button
            type="button"
            onClick={() => setActiveTab("overview")}
            className={`flex items-center gap-2 rounded-full px-5 py-2.5 text-xs font-medium transition cursor-pointer ${
              activeTab === "overview"
                ? "bg-[#74478A] text-white"
                : "text-[#706578] hover:bg-[#F3EBF1]"
            }`}
          >
            <ShieldCheck size={15} />
            Compliance Summary
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("tree")}
            className={`flex items-center gap-2 rounded-full px-5 py-2.5 text-xs font-medium transition cursor-pointer ${
              activeTab === "tree"
                ? "bg-[#74478A] text-white"
                : "text-[#706578] hover:bg-[#F3EBF1]"
            }`}
          >
            <GitBranch size={15} />
            Normative Reference Tree
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("diff")}
            className={`flex items-center gap-2 rounded-full px-5 py-2.5 text-xs font-medium transition cursor-pointer ${
              activeTab === "diff"
                ? "bg-[#74478A] text-white"
                : "text-[#706578] hover:bg-[#F3EBF1]"
            }`}
          >
            <FileText size={15} />
            Diff & Gauge View
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("non-compliance")}
            className={`flex items-center gap-2 rounded-full px-5 py-2.5 text-xs font-medium transition cursor-pointer ${
              activeTab === "non-compliance"
                ? "bg-[#74478A] text-white"
                : "text-[#706578] hover:bg-[#F3EBF1]"
            }`}
          >
            <AlertTriangle size={15} />
            Non-Compliance Matrix
            <span className="rounded-full bg-[#C04848] px-2 py-0.5 text-[10px] text-white">
              {mockNonCompliances.length}
            </span>
          </button>
        </div>

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 gap-5 md:grid-cols-4">
              <div className="rounded-[20px] border border-[#E4DAD5] bg-white p-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#806D7B]">
                    Overall Compliance
                  </span>
                  <CheckCircle2 size={18} className="text-[#3B7A57]" />
                </div>
                <div className="mt-3 font-serif text-3xl text-[#211735]">
                  85.4%
                </div>
                <p className="mt-1 text-[11px] text-[#3B7A57]">
                  Above average compliance
                </p>
              </div>

              <div className="rounded-[20px] border border-[#E4DAD5] bg-white p-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#806D7B]">
                    Compliant Clauses
                  </span>
                  <CheckCircle2 size={18} className="text-[#3B7A57]" />
                </div>
                <div className="mt-3 font-serif text-3xl text-[#3B7A57]">
                  41 / 48
                </div>
                <p className="mt-1 text-[11px] text-[#806D7B]">
                  Fully matching BIS standards
                </p>
              </div>

              <div className="rounded-[20px] border border-[#E4DAD5] bg-white p-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#806D7B]">
                    Non-Compliant Clauses
                  </span>
                  <XCircle size={18} className="text-[#C04848]" />
                </div>
                <div className="mt-3 font-serif text-3xl text-[#C04848]">
                  3
                </div>
                <p className="mt-1 text-[11px] text-[#C04848]">
                  Requires tender amendment
                </p>
              </div>

              <div className="rounded-[20px] border border-[#E4DAD5] bg-white p-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#806D7B]">
                    Ambiguous Statements
                  </span>
                  <HelpCircle size={18} className="text-[#D9822B]" />
                </div>
                <div className="mt-3 font-serif text-3xl text-[#D9822B]">
                  4
                </div>
                <p className="mt-1 text-[11px] text-[#806D7B]">
                  Needs clarification
                </p>
              </div>
            </div>

            <div className="rounded-[22px] border border-[#E4DAD5] bg-white p-7">
              <h2 className="font-serif text-xl text-[#211735]">
                Normative Standards Referenced
              </h2>
              <p className="mt-1 text-xs text-[#806D7B]">
                Standards detected within this tender document and their
                compliance status
              </p>

              <div className="mt-6 space-y-4">
                <div className="flex items-center justify-between rounded-xl border border-[#EEE7E2] bg-[#FBF8F4] p-4">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#EDE0EC] text-xs font-semibold text-[#74478A]">
                      IS
                    </div>
                    <div>
                      <div className="text-sm font-medium text-[#211735]">
                        IS 15683:2018
                      </div>
                      <div className="text-xs text-[#806D7B]">
                        Portable Fire Extinguishers — Performance &
                        Construction
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="rounded-full bg-[#FDF2F2] px-3 py-1 text-xs font-medium text-[#C04848]">
                      2 Gaps Found
                    </span>
                    <button
                      type="button"
                      onClick={() => setActiveTab("tree")}
                      className="text-xs font-medium text-[#74478A] hover:underline cursor-pointer"
                    >
                      View in Tree
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-xl border border-[#EEE7E2] bg-[#FBF8F4] p-4">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#EDE0EC] text-xs font-semibold text-[#74478A]">
                      IS
                    </div>
                    <div>
                      <div className="text-sm font-medium text-[#211735]">
                        IS 2190:2024
                      </div>
                      <div className="text-xs text-[#806D7B]">
                        Selection, Installation & Maintenance of Fire
                        Extinguishers
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="rounded-full bg-[#FFF8F0] px-3 py-1 text-xs font-medium text-[#D9822B]">
                      1 Gap Found
                    </span>
                    <button
                      type="button"
                      onClick={() => setActiveTab("tree")}
                      className="text-xs font-medium text-[#74478A] hover:underline cursor-pointer"
                    >
                      View in Tree
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: NORMATIVE TREE GRAPH */}
        {activeTab === "tree" && <NormativeTreeGraph />}

        {/* TAB 3: DIFF & GAUGE VIEW */}
        {activeTab === "diff" && <DiffAndGaugeView />}

        {/* TAB 4: NON-COMPLIANCE MATRIX */}
        {activeTab === "non-compliance" && (
          <div className="space-y-6">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search
                    size={16}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-[#806D7B]"
                  />
                  <input
                    type="text"
                    placeholder="Filter by clause or keyword..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="h-10 rounded-xl border border-[#E4DAD5] bg-white pl-9 pr-4 text-xs text-[#211735] outline-none placeholder:text-[#806D7B] focus:border-[#74478A]"
                  />
                </div>

                <div className="relative">
                  <select
                    value={selectedSeverity}
                    onChange={(e) => setSelectedSeverity(e.target.value)}
                    className="h-10 appearance-none rounded-xl border border-[#E4DAD5] bg-white pl-4 pr-8 text-xs text-[#211735] outline-none focus:border-[#74478A]"
                  >
                    <option value="all">All Severities</option>
                    <option value="high">High Severity</option>
                    <option value="medium">Medium Severity</option>
                    <option value="low">Low Severity</option>
                  </select>
                  <ChevronDown
                    size={14}
                    className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[#806D7B]"
                  />
                </div>
              </div>

              <div className="text-xs text-[#806D7B]">
                Showing {filteredNCs.length} of {mockNonCompliances.length}{" "}
                non-compliance issues
              </div>
            </div>

            <div className="space-y-4">
              {filteredNCs.map((nc) => (
                <div
                  key={nc.id}
                  className="rounded-[22px] border border-[#E4DAD5] bg-white p-6 shadow-[0_4px_20px_rgba(116,71,138,0.03)]"
                >
                  <div className="flex items-center justify-between border-b border-[#EEE7E2] pb-4">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-[#74478A]">
                        {nc.clause}
                      </span>
                      <span className="text-xs text-[#806D7B]">|</span>
                      <span className="text-xs font-medium text-[#211735]">
                        {nc.standard}
                      </span>
                      <span className="rounded-full bg-[#F2EEE8] px-3 py-0.5 text-[10px] text-[#806D7B]">
                        {nc.category}
                      </span>
                    </div>

                    <span
                      className={`rounded-full px-3 py-1 text-[10px] font-medium uppercase tracking-wider ${
                        nc.severity === "high"
                          ? "bg-[#FDF2F2] text-[#C04848]"
                          : nc.severity === "medium"
                          ? "bg-[#FFF8F0] text-[#D9822B]"
                          : "bg-[#F5F7FA] text-[#5A6A85]"
                      }`}
                    >
                      {nc.severity} Severity
                    </span>
                  </div>

                  <div className="mt-4 grid grid-cols-1 gap-6 md:grid-cols-2">
                    <div className="rounded-xl border border-[#F0E6E6] bg-[#FFFBFB] p-4">
                      <div className="text-[11px] font-semibold text-[#C04848]">
                        Tender Requirement
                      </div>
                      <p className="mt-2 text-xs leading-relaxed text-[#493D50]">
                        {nc.tenderRequirement}
                      </p>
                    </div>

                    <div className="rounded-xl border border-[#E6F0E8] bg-[#FBFCFB] p-4">
                      <div className="text-[11px] font-semibold text-[#3B7A57]">
                        IS Standard Mandate
                      </div>
                      <p className="mt-2 text-xs leading-relaxed text-[#493D50]">
                        {nc.isStandardRequirement}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 rounded-xl bg-[#FBF8F4] p-4">
                    <div className="text-[11px] font-semibold text-[#74478A]">
                      Gap Analysis
                    </div>
                    <p className="mt-1 text-xs text-[#706578]">
                      {nc.gapAnalysis}
                    </p>
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-[#EEE7E2] pt-4 text-xs">
                    <div className="flex items-center gap-2 text-[#211735]">
                      <ArrowRight size={14} className="text-[#74478A]" />
                      <span className="font-medium">Recommended Action:</span>
                      <span className="text-[#706578]">
                        {nc.actionRequired}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}