"use client";

import Link from "next/link";
import { ArrowUpRight, Upload, FileText, CheckCircle2, AlertCircle, ShieldCheck } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { useEffect, useState } from "react";
import NormativeTreeGraph from "../../components/NormativeTreeGraph";
import DiffAndGaugeView from "../../components/DiffAndGaugeView";

type SelectedStandard = {
  standard_id: number;
  standard_number?: string;
  title?: string;
};

type ComplianceData = {
  status: string;
  alerts: { type: string; requirement_name?: string; reason: string; status: string }[];
};

type QualityData = { score?: number; status?: string };

type VerificationData = {
  status: string;
  results: { type: string; status: string; reason?: string; source?: string }[];
};

type GraphData = {
  found?: boolean;
  standard_number?: string;
  title?: string;
  linked_standards?: { standard_number: string; title: string; relationship: string }[];
};

export default function CompliancePage() {
  const [standard, setStandard] = useState<SelectedStandard | null>(null);
  const [documentName, setDocumentName] = useState("Tender document");
  const [tenderSpec, setTenderSpec] = useState("");
  const [compliance, setCompliance] = useState<ComplianceData | null>(null);
  const [quality, setQuality] = useState<QualityData | null>(null);
  const [verification, setVerification] = useState<VerificationData | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedDocument = localStorage.getItem("manak_uploaded_file");
    if (storedDocument) {
      try {
        const parsed = JSON.parse(storedDocument);
        if (parsed.filename) setDocumentName(parsed.filename);
        if (parsed.extracted_data?.pages?.[0]?.raw_text) {
          setTenderSpec(parsed.extracted_data.pages[0].raw_text.trim());
        }
      } catch {
        setDocumentName("Tender document");
      }
    }

    const storedStandard = localStorage.getItem("manak_selected_standard");
    if (!storedStandard) {
      setError("Select a matched standard from Recommendations to inspect live compliance.");
      setLoading(false);
      return;
    }

    let selected: SelectedStandard;
    try {
      selected = JSON.parse(storedStandard) as SelectedStandard;
      setStandard(selected);
    } catch {
      setError("The selected standard data is invalid.");
      setLoading(false);
      return;
    }

    let cancelled = false;
    const loadComplianceData = async () => {
      try {
        const id = selected.standard_id;
        const [comp, qual, verif] = await Promise.all([
          apiRequest<ComplianceData>(`/compliance/${id}`),
          apiRequest<QualityData>(`/quality-score/${id}`),
          apiRequest<VerificationData>(`/verification/${id}`),
        ]);

        let graph: { graph?: GraphData } | null = null;
        try {
          if (selected.standard_number) {
            graph = await apiRequest<{ graph?: GraphData }>(`/graph/standard/${encodeURIComponent(selected.standard_number)}`);
          }
        } catch {
          // If no graph entries exist for this standard in Neo4j, default safely
        }

        if (!cancelled) {
          setCompliance(comp);
          setQuality(qual);
          setVerification(verif);
          if (graph?.graph) setGraphData(graph.graph);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load live compliance data.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void loadComplianceData();
    return () => {
      cancelled = true;
    };
  }, []);

  const verificationResults = verification?.results ?? [];
  const verifiedCount = verificationResults.filter((r) => r.status === "verified").length;
  const needsReviewCount = verificationResults.length - verifiedCount;

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">
      {/* HEADER */}
      <header className="border-b border-[#E7DDD7] bg-[#FBF8F4]">
        <div className="mx-auto flex h-[76px] max-w-[1400px] items-center justify-between px-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#74478A] font-serif text-white">M</div>
            <div>
              <div className="font-serif text-xl tracking-wide">MANAK</div>
              <div className="text-[8px] uppercase tracking-[0.22em] text-[#806D7B]">AI for Smarter Procurement</div>
            </div>
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-[1150px] px-8 py-14">
        <div className="max-w-[850px]">
          <div className="mb-4 flex items-center gap-3 text-xs uppercase tracking-[0.28em] text-[#A35A91]">
            <span className="h-px w-8 bg-[#A35A91]" /> Standards Compliance
          </div>
          <h1 className="font-serif text-5xl leading-tight">
            Check your tender against <span className="text-[#74478A]">Indian Standards.</span>
          </h1>
        </div>

        {/* DOCUMENT BAR */}
        <div className="mt-10 flex flex-col justify-between gap-6 rounded-[24px] border border-[#E4D7D1] bg-white p-7 md:flex-row md:items-center">
          <div className="flex items-center gap-5">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#EDE0EC] text-[#74478A]">
              <FileText size={25} />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-[#A35A91]">Tender Document</p>
              <h2 className="mt-1 font-serif text-2xl">{documentName}</h2>
              <p className="mt-1 text-sm text-[#806D7B]">{standard?.standard_number ?? "No standard selected"}</p>
            </div>
          </div>
          <Link href="/upload" className="flex items-center gap-2 rounded-full bg-[#74478A] px-6 py-3 text-sm text-white">
            <Upload size={16} /> Upload another <ArrowUpRight size={14} />
          </Link>
        </div>

        {error && <p className="mt-4 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">{error}</p>}

        {/* LIVE METRICS */}
        <div className="mt-8 grid gap-6 md:grid-cols-[1fr_280px]">
          <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-7">
            <div className="flex items-center gap-3">
              <ShieldCheck size={20} className="text-[#74478A]" />
              <p className="text-xs uppercase tracking-[0.22em] text-[#A35A91]">Live Compliance Status</p>
            </div>
            <div className="mt-6 flex items-end gap-3">
              <span className="font-serif text-6xl text-[#74478A]">
                {loading ? "…" : quality?.score != null ? `${Math.round(quality.score)}%` : "—"}
              </span>
              <span className="mb-2 rounded-full bg-[#FFF1D9] px-3 py-1.5 text-xs font-medium text-[#9A6B35]">
                {loading ? "Calculating..." : compliance?.status === "checked" ? "Checked against DB" : "Evaluating"}
              </span>
            </div>
          </div>

          <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-7">
            <p className="text-xs uppercase tracking-[0.22em] text-[#A35A91]">Requirements Status</p>
            <div className="mt-5 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#806D7B]">Verified Active</span>
                <span className="flex items-center gap-1 font-medium text-emerald-600"><CheckCircle2 size={16} /> {verifiedCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#806D7B]">Needs Review</span>
                <span className="flex items-center gap-1 font-medium text-rose-600"><AlertCircle size={16} /> {needsReviewCount}</span>
              </div>
            </div>
          </div>
        </div>

        {/* DYNAMIC REACT FLOW GRAPH */}
        <div className="mt-12">
          <h2 className="mb-4 font-serif text-2xl">Normative Reference Tree (Live Neo4j Graph)</h2>
          <NormativeTreeGraph graphData={graphData} />
        </div>

        {/* DYNAMIC DIFF AND GAUGE VIEW */}
        <div className="mt-12">
          <h2 className="mb-4 font-serif text-2xl">Specification Diff & Gauge Analysis</h2>
          <DiffAndGaugeView
            score={quality?.score}
            tenderSpec={tenderSpec}
            verifiedSpec={`${standard?.standard_number ?? ''} - ${standard?.title ?? ''}`}
          />
        </div>
      </section>
    </main>
  );
}