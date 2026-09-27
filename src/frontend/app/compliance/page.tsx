"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
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
  ArrowLeft,
  Upload,
  Shield,
  Check,
  AlertCircle,
  Sparkles,
  ArrowUpRight,
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
    tenderRequirement: "Operating temperature range specified as 0°C to 50°C.",
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
  const [isAnalyzed, setIsAnalyzed] = useState(false);

  useEffect(() => {
    const storedName = localStorage.getItem("uploadedFileName");
    if (storedName) {
      setUploadedFileName(storedName);
      setIsAnalyzed(true);
    }
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFileName(file.name);
      localStorage.setItem("uploadedFileName", file.name);
      setIsAnalyzed(true);
    }
  };

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
    <div className="min-h-screen bg-[#FAF6F0] text-[#2D2138]">
      <main className="mx-auto max-w-[1000px] px-6 py-8">
        {/* BACK TO DASHBOARD */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-medium text-[#7D7086] transition-colors hover:text-[#2D2138]"
        >
          <ArrowLeft size={14} />
          Back to dashboard
        </Link>

        {/* HEADER SECTION */}
        <div className="mt-8">
          <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wider text-[#9E6290] uppercase">
            <span className="h-[1px] w-4 bg-[#9E6290]"></span>
            STANDARDS COMPLIANCE
          </div>

          <h1 className="mt-3 font-serif text-5xl leading-[1.15] tracking-tight text-[#2D2138]">
            Check your tender <br />
            <span className="text-[#683C74]">against Indian Standards.</span>
          </h1>

          <p className="mt-4 max-w-xl text-xs leading-relaxed text-[#7D7086]">
            Upload your tender document and let MANAK identify applicable standards, compare
            requirements, and highlight potential compliance issues.
          </p>
        </div>

        {/* START COMPLIANCE CHECK / UPLOAD CARD */}
        <div className="mt-8 rounded-[28px] border border-[#F0E8E1] bg-gradient-to-r from-white via-white to-[#FCF7FA] p-7 shadow-[0_2px_12px_rgba(0,0,0,0.02)]">
          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#F1E7F2] text-[#683C74]">
                <FileText size={22} strokeWidth={1.75} />
              </div>
              <div>
                <span className="text-[10px] font-bold tracking-wider text-[#9E6290] uppercase">
                  Tender Document
                </span>
                <h3 className="font-serif text-lg font-medium text-[#2D2138]">
                  {uploadedFileName ? uploadedFileName : "Start a compliance check"}
                </h3>
                <p className="text-[11px] text-[#7D7086]">
                  {uploadedFileName
                    ? "File processed successfully"
                    : "PDF, DOCX or other supported tender documents"}
                </p>
              </div>
            </div>

            <label className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-[#683C74] px-6 py-3 text-xs font-medium text-white transition hover:bg-[#563061]">
              <Upload size={14} />
              <span>{uploadedFileName ? "Upload new tender" : "Upload tender"}</span>
              <ArrowUpRight size={14} className="opacity-70" />
              <input
                type="file"
                className="hidden"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileUpload}
              />
            </label>
          </div>
        </div>

        {/* HOW MANAK CHECKS - 3 STEP GRID */}
        <div className="mt-10">
          <div className="text-[10px] font-bold tracking-wider text-[#9E6290] uppercase">
            HOW MANAK CHECKS
          </div>
          <h2 className="mt-1 font-serif text-2xl font-medium text-[#2D2138]">
            From tender specification to compliance.
          </h2>

          <div className="mt-6 grid grid-cols-1 divide-y divide-[#F0E8E1] rounded-[28px] border border-[#F0E8E1] bg-white shadow-[0_2px_12px_rgba(0,0,0,0.02)] md:grid-cols-3 md:divide-x md:divide-y-0">
            {/* STEP 1 */}
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#F1E7F2] text-[#683C74]">
                  <Shield size={18} />
                </div>
                <span className="text-xs font-semibold text-[#826688]">01</span>
              </div>
              <h4 className="mt-4 font-serif text-base font-medium text-[#2D2138]">
                Identify standards
              </h4>
              <p className="mt-1 text-[11px] leading-relaxed text-[#7D7086]">
                MANAK identifies the Indian Standards that are relevant to your tender requirements.
              </p>
            </div>

            {/* STEP 2 */}
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#F9E9E5] text-[#A8726B]">
                  <Check size={18} />
                </div>
                <span className="text-xs font-semibold text-[#A8726B]">02</span>
              </div>
              <h4 className="mt-4 font-serif text-base font-medium text-[#2D2138]">
                Compare requirements
              </h4>
              <p className="mt-1 text-[11px] leading-relaxed text-[#7D7086]">
                Tender specifications are compared with the applicable standard requirements.
              </p>
            </div>

            {/* STEP 3 */}
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#FAF0D8] text-[#A18854]">
                  <AlertCircle size={18} />
                </div>
                <span className="text-xs font-semibold text-[#A18854]">03</span>
              </div>
              <h4 className="mt-4 font-serif text-base font-medium text-[#2D2138]">
                Highlight issues
              </h4>
              <p className="mt-1 text-[11px] leading-relaxed text-[#7D7086]">
                Potential gaps, mismatches, and specifications needing attention are highlighted.
              </p>
            </div>
          </div>
        </div>

        {/* REPORT SECTION OR EMPTY PLACEHOLDER */}
        {!isAnalyzed ? (
          <div className="mt-6 flex flex-col items-center justify-center rounded-[28px] border border-dashed border-[#ECDCEB] bg-[#FAF6F0]/50 py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#F1E7F2] text-[#683C74]">
              <Sparkles size={20} />
            </div>
            <h3 className="mt-4 font-serif text-2xl font-medium text-[#2D2138]">
              Your compliance report will appear here
            </h3>
            <p className="mt-2 max-w-sm text-xs leading-relaxed text-[#7D7086]">
              Once you upload and analyse a tender, MANAK will show the applicable standards and compliance findings here.
            </p>
          </div>
        ) : (
          <div className="mt-10 space-y-8 border-t border-[#E4DAD5] pt-10">
            {/* SUMMARY BANNER */}
            <div className="rounded-[28px] border border-[#F0E8E1] bg-white p-7 shadow-[0_2px_12px_rgba(0,0,0,0.02)]">
              <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
                <div className="flex items-start gap-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#F1E7F2] text-[#683C74]">
                    <FileText size={24} />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="rounded-full bg-[#F1E7F2] px-3 py-1 text-xs font-medium text-[#683C74]">
                        {mockTenderInfo.referenceNo}
                      </span>
                      <span className="text-xs text-[#7D7086]">
                        {mockTenderInfo.category}
                      </span>
                    </div>
                    <h2 className="mt-2 font-serif text-2xl text-[#2D2138]">
                      {uploadedFileName ? uploadedFileName : mockTenderInfo.title}
                    </h2>
                    <p className="mt-1 text-xs text-[#7D7086]">
                      Issued by: {mockTenderInfo.organization}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-6 border-t border-[#F0E8E1] pt-4 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
                  <div className="text-center">
                    <div className="font-serif text-3xl text-[#683C74]">
                      {mockTenderInfo.overallScore}%
                    </div>
                    <div className="text-[11px] text-[#7D7086]">
                      Compliance Score
                    </div>
                  </div>
                  <div className="h-8 w-px bg-[#F0E8E1]" />
                  <div className="text-center">
                    <div className="font-serif text-3xl text-[#2D2138]">
                      {mockTenderInfo.totalClausesAnalyzed}
                    </div>
                    <div className="text-[11px] text-[#7D7086]">
                      Clauses Analyzed
                    </div>
                  </div>
                  <div className="h-8 w-px bg-[#F0E8E1]" />
                  <div className="text-center">
                    <div className="font-serif text-3xl text-[#C04848]">
                      {mockTenderInfo.nonCompliantClauses}
                    </div>
                    <div className="text-[11px] text-[#7D7086]">
                      Non-Compliant
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* TAB BUTTONS */}
            <div className="flex flex-wrap items-center gap-2 border-b border-[#F0E8E1] pb-3">
              <button
                type="button"
                onClick={() => setActiveTab("overview")}
                className={`flex items-center gap-2 rounded-full px-5 py-2.5 text-xs font-medium transition cursor-pointer ${
                  activeTab === "overview"
                    ? "bg-[#683C74] text-white"
                    : "text-[#7D7086] hover:bg-[#F1E7F2]"
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
                    ? "bg-[#683C74] text-white"
                    : "text-[#7D7086] hover:bg-[#F1E7F2]"
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
                    ? "bg-[#683C74] text-white"
                    : "text-[#7D7086] hover:bg-[#F1E7F2]"
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
                    ? "bg-[#683C74] text-white"
                    : "text-[#7D7086] hover:bg-[#F1E7F2]"
                }`}
              >
                <AlertTriangle size={15} />
                Non-Compliance Matrix
                <span className="rounded-full bg-[#C04848] px-2 py-0.5 text-[10px] text-white">
                  {mockNonCompliances.length}
                </span>
              </button>
            </div>

            {/* TAB CONTENTS */}
            {activeTab === "overview" && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 gap-5 md:grid-cols-4">
                  <div className="rounded-[22px] border border-[#F0E8E1] bg-white p-6">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#7D7086]">
                        Overall Compliance
                      </span>
                      <CheckCircle2 size={18} className="text-[#3B7A57]" />
                    </div>
                    <div className="mt-3 font-serif text-3xl text-[#2D2138]">
                      85.4%
                    </div>
                    <p className="mt-1 text-[11px] text-[#3B7A57]">
                      Above average compliance
                    </p>
                  </div>

                  <div className="rounded-[22px] border border-[#F0E8E1] bg-white p-6">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#7D7086]">
                        Compliant Clauses
                      </span>
                      <CheckCircle2 size={18} className="text-[#3B7A57]" />
                    </div>
                    <div className="mt-3 font-serif text-3xl text-[#3B7A57]">
                      41 / 48
                    </div>
                    <p className="mt-1 text-[11px] text-[#7D7086]">
                      Fully matching BIS standards
                    </p>
                  </div>

                  <div className="rounded-[22px] border border-[#F0E8E1] bg-white p-6">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#7D7086]">
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

                  <div className="rounded-[22px] border border-[#F0E8E1] bg-white p-6">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#7D7086]">
                        Ambiguous Statements
                      </span>
                      <HelpCircle size={18} className="text-[#D9822B]" />
                    </div>
                    <div className="mt-3 font-serif text-3xl text-[#D9822B]">
                      4
                    </div>
                    <p className="mt-1 text-[11px] text-[#7D7086]">
                      Needs clarification
                    </p>
                  </div>
                </div>

                <div className="rounded-[28px] border border-[#F0E8E1] bg-white p-7">
                  <h3 className="font-serif text-xl text-[#2D2138]">
                    Normative Standards Referenced
                  </h3>
                  <p className="mt-1 text-xs text-[#7D7086]">
                    Standards detected within this tender document and their
                    compliance status
                  </p>

                  <div className="mt-6 space-y-4">
                    <div className="flex items-center justify-between rounded-xl border border-[#F0E8E1] bg-[#FAF6F0] p-4">
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#F1E7F2] text-xs font-semibold text-[#683C74]">
                          IS
                        </div>
                        <div>
                          <div className="text-sm font-medium text-[#2D2138]">
                            IS 15683:2018
                          </div>
                          <div className="text-xs text-[#7D7086]">
                            Portable Fire Extinguishers — Performance & Construction
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
                          className="text-xs font-medium text-[#683C74] hover:underline cursor-pointer"
                        >
                          View in Tree
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center justify-between rounded-xl border border-[#F0E8E1] bg-[#FAF6F0] p-4">
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#F1E7F2] text-xs font-semibold text-[#683C74]">
                          IS
                        </div>
                        <div>
                          <div className="text-sm font-medium text-[#2D2138]">
                            IS 2190:2024
                          </div>
                          <div className="text-xs text-[#7D7086]">
                            Selection, Installation & Maintenance of Fire Extinguishers
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
                          className="text-xs font-medium text-[#683C74] hover:underline cursor-pointer"
                        >
                          View in Tree
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "tree" && <NormativeTreeGraph />}
            {activeTab === "diff" && <DiffAndGaugeView />}

            {activeTab === "non-compliance" && (
              <div className="space-y-6">
                <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Search
                        size={16}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-[#7D7086]"
                      />
                      <input
                        type="text"
                        placeholder="Filter by clause or keyword..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="h-10 rounded-xl border border-[#F0E8E1] bg-white pl-9 pr-4 text-xs text-[#2D2138] outline-none placeholder:text-[#B39DB0] focus:border-[#683C74]"
                      />
                    </div>

                    <div className="relative">
                      <select
                        value={selectedSeverity}
                        onChange={(e) => setSelectedSeverity(e.target.value)}
                        className="h-10 appearance-none rounded-xl border border-[#F0E8E1] bg-white pl-4 pr-8 text-xs text-[#2D2138] outline-none focus:border-[#683C74]"
                      >
                        <option value="all">All Severities</option>
                        <option value="high">High Severity</option>
                        <option value="medium">Medium Severity</option>
                        <option value="low">Low Severity</option>
                      </select>
                      <ChevronDown
                        size={14}
                        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[#7D7086]"
                      />
                    </div>
                  </div>

                  <div className="text-xs text-[#7D7086]">
                    Showing {filteredNCs.length} of {mockNonCompliances.length}{" "}
                    non-compliance issues
                  </div>
                </div>

                <div className="space-y-4">
                  {filteredNCs.map((nc) => (
                    <div
                      key={nc.id}
                      className="rounded-[22px] border border-[#F0E8E1] bg-white p-6 shadow-[0_2px_12px_rgba(0,0,0,0.02)]"
                    >
                      <div className="flex items-center justify-between border-b border-[#F0E8E1] pb-4">
                        <div className="flex items-center gap-3">
                          <span className="font-medium text-[#683C74]">
                            {nc.clause}
                          </span>
                          <span className="text-xs text-[#7D7086]">|</span>
                          <span className="text-xs font-medium text-[#2D2138]">
                            {nc.standard}
                          </span>
                          <span className="rounded-full bg-[#FAF6F0] px-3 py-0.5 text-[10px] text-[#7D7086]">
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

                      <div className="mt-4 rounded-xl bg-[#FAF6F0] p-4">
                        <div className="text-[11px] font-semibold text-[#683C74]">
                          Gap Analysis
                        </div>
                        <p className="mt-1 text-xs text-[#7D7086]">
                          {nc.gapAnalysis}
                        </p>
                      </div>

                      <div className="mt-4 flex items-center justify-between border-t border-[#F0E8E1] pt-4 text-xs">
                        <div className="flex items-center gap-2 text-[#2D2138]">
                          <ArrowRight size={14} className="text-[#683C74]" />
                          <span className="font-medium">Recommended Action:</span>
                          <span className="text-[#7D7086]">
                            {nc.actionRequired}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}