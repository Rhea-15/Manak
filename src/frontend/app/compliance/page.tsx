"use client";

import Link from "next/link";
import { 
  ArrowUpRight, Upload, FileText, CheckCircle2, AlertCircle, 
  ShieldCheck, GitBranch, LayoutTemplate, AlertTriangle 
} from "lucide-react";
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
  
  // Real-time Data States
  const [compliance, setCompliance] = useState<ComplianceData | null>(null);
  const [quality, setQuality] = useState<QualityData | null>(null);
  const [verification, setVerification] = useState<VerificationData | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  
  // UI States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("summary");

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

        let graphRes: any = null;
        try {
          if (selected.standard_number) {
            graphRes = await apiRequest(`/graph/standard/${encodeURIComponent(selected.standard_number)}`);
          }
        } catch {
          // Default safely if graph missing
        }

        if (!cancelled) {
          setCompliance(comp);
          setQuality(qual);
          setVerification(verif);
          const resolvedGraph = graphRes?.graph ?? graphRes?.data ?? graphRes;
          if (resolvedGraph && (resolvedGraph.standard_number || resolvedGraph.linked_standards)) {
            setGraphData(resolvedGraph);
          }
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
    return () => { cancelled = true; };
  }, []);

  const verificationResults = verification?.results ?? [];
  const verifiedCount = verificationResults.filter((r) => r.status === "verified").length;
  const needsReviewCount = compliance?.alerts?.length ?? (verificationResults.length - verifiedCount);
  const totalClauses = verificationResults.length || 1; 

  const tabs = [
    { id: "summary", label: "Compliance Summary", icon: ShieldCheck },
    { id: "tree", label: "Standards Navigator", icon: GitBranch },
    { id: "diff", label: " Requirement Analyzer", icon: LayoutTemplate },
    { id: "matrix", label: "Non-Compliance Matrix", icon: AlertTriangle, badge: needsReviewCount > 0 ? needsReviewCount : undefined },
  ];

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">
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

      <section className="mx-auto max-w-[1200px] px-8 py-10">
        
        {/* Document Header */}
        <div className="mb-10 flex flex-col justify-between gap-6 rounded-[24px] bg-white p-7 shadow-sm md:flex-row md:items-center">
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
          <Link href="/upload" className="flex items-center gap-2 rounded-full border border-[#DCCBCF] bg-white px-6 py-3 text-sm text-[#74478A] transition hover:bg-[#F8F3F9]">
            <Upload size={16} /> Upload another <ArrowUpRight size={14} />
          </Link>
        </div>

        {error && <p className="mb-6 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">{error}</p>}

        {/* Tab Navigation */}
        <div className="mb-8 flex flex-wrap items-center gap-2 border-b border-[#E4DAD5] pb-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition ${
                  isActive ? "bg-[#74478A] text-white" : "text-[#806D7B] hover:bg-[#F3EBF1]"
                }`}
              >
                <Icon size={16} />
                {tab.label}
                {tab.badge !== undefined && (
                  <span className={`ml-1 flex h-5 w-5 items-center justify-center rounded-full text-[10px] ${isActive ? 'bg-rose-500 text-white' : 'bg-rose-100 text-rose-600'}`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* TAB CONTENTS */}
        
        {/* 1. COMPLIANCE SUMMARY TAB */}
        {activeTab === "summary" && (
          <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* 4 Metric Cards */}
            <div className="grid grid-cols-1 gap-5 md:grid-cols-4">
              <MetricCard 
                title="Overall Compliance" 
                value={`${loading ? "…" : Math.round(quality?.score ?? 0)}%`} 
                subtitle={quality?.score && quality.score >= 80 ? "Above average compliance" : "Below average compliance"}
                icon={<CheckCircle2 size={18} className="text-emerald-600" />}
              />
              <MetricCard 
                title="Compliant Clauses" 
                value={`${loading ? "…" : verifiedCount} / ${loading ? "…" : totalClauses}`} 
                subtitle="Matching BIS standards"
                icon={<CheckCircle2 size={18} className="text-emerald-600" />}
              />
              <MetricCard 
                title="Non-Compliant Clauses" 
                value={`${loading ? "…" : needsReviewCount}`} 
                subtitle="Requires tender amendment"
                icon={<AlertCircle size={18} className="text-rose-500" />}
                isAlert={needsReviewCount > 0}
              />
              <MetricCard 
                title="Ambiguous Statements" 
                value="0" 
                subtitle="Needs clarification"
                icon={<AlertTriangle size={18} className="text-amber-500" />}
              />
            </div>

            {/* Normative Standards Referenced List */}
            <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-7 shadow-sm">
              <h3 className="font-serif text-2xl text-[#211735]">Normative Standards Referenced</h3>
              <p className="mt-1 text-sm text-[#806D7B]">Standards detected within this tender document and their compliance status</p>
              
              <div className="mt-6 space-y-4">
                {/* Main Standard */}
                <div className="flex items-center justify-between rounded-xl border border-[#EEE7E2] bg-[#FBF8F4] p-5 transition hover:border-[#DCCBCF]">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#EDE0EC] text-xs font-bold text-[#74478A]">IS</div>
                    <div>
                      <p className="font-medium text-[#211735]">{standard?.standard_number}</p>
                      <p className="text-sm text-[#806D7B]">{standard?.title}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    {needsReviewCount > 0 ? (
                       <span className="text-sm font-medium text-rose-600">{needsReviewCount} Gaps Found</span>
                    ) : (
                       <span className="text-sm font-medium text-emerald-600">Fully Compliant</span>
                    )}
                    <button onClick={() => setActiveTab("tree")} className="text-sm font-medium text-[#74478A] hover:underline">View in Tree</button>
                  </div>
                </div>

                {/* Linked Standards from Neo4j */}
                {graphData?.linked_standards?.map((link, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-[#EEE7E2] bg-white p-5 transition hover:border-[#DCCBCF]">
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#F3F0F4] text-xs font-bold text-[#806D7B]">IS</div>
                      <div>
                        <p className="font-medium text-[#211735]">{link.standard_number}</p>
                        <p className="text-sm text-[#806D7B]">{link.title || 'Normative Reference'}</p>
                      </div>
                    </div>
                    <button onClick={() => setActiveTab("tree")} className="text-sm font-medium text-[#74478A] hover:underline">View in Tree</button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 2. NORMATIVE REFERENCE TREE TAB */}
        {activeTab === "tree" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-7 shadow-sm">
              <h2 className="mb-6 font-serif text-2xl">Dependency Graph</h2>
              <NormativeTreeGraph graphData={graphData} />
            </div>
          </div>
        )}

        {/* 3. DIFF & GAUGE VIEW TAB */}
        {activeTab === "diff" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
             <DiffAndGaugeView
                score={quality?.score}
                tenderSpec={tenderSpec}
                verifiedSpec={`${standard?.standard_number ?? ''} - ${standard?.title ?? ''}`}
              />
          </div>
        )}

        {/* 4. NON-COMPLIANCE MATRIX TAB */}
        {activeTab === "matrix" && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="font-serif text-2xl">Non-Compliance Issues</h2>
              <span className="text-sm text-[#806D7B]">Showing {compliance?.alerts?.length || 0} issues</span>
            </div>

            {compliance?.alerts?.length ? (
              <div className="space-y-6">
                {compliance.alerts.map((alert, idx) => (
                  <div key={idx} className="rounded-[24px] border border-[#E4DAD5] bg-white p-7 shadow-sm">
                    <div className="mb-5 flex items-center justify-between border-b border-[#EEE7E2] pb-4">
                      <h3 className="font-medium text-[#211735]">{alert.type} | {standard?.standard_number}</h3>
                      <span className="rounded-full bg-rose-50 px-3 py-1 text-xs font-bold text-rose-600">HIGH SEVERITY</span>
                    </div>

                    <div className="grid gap-6 md:grid-cols-2">
                       <div className="rounded-xl border border-rose-100 bg-[#FFFCF9] p-5">
                          <p className="mb-2 text-sm font-bold text-rose-800">Tender Gap / Missing Element</p>
                          <p className="text-sm text-[#493D50]">{alert.reason}</p>
                       </div>
                       <div className="rounded-xl border border-emerald-100 bg-[#F4FAF6] p-5">
                          <p className="mb-2 text-sm font-bold text-emerald-800">IS Standard Mandate</p>
                          <p className="text-sm text-[#493D50]">Requirement '{alert.requirement_name || alert.type}' must be verified and active to pass compliance.</p>
                       </div>
                    </div>

                    <div className="mt-5 rounded-lg bg-[#FAF7FA] p-4 text-sm text-[#74478A]">
                      <span className="font-bold">→ Recommended Action:</span> Provide valid verification records for {alert.requirement_name || alert.type} to comply with {standard?.standard_number}.
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-12 text-center shadow-sm">
                <CheckCircle2 size={48} className="mx-auto mb-4 text-emerald-500" />
                <h3 className="font-serif text-2xl text-[#211735]">No compliance issues found</h3>
                <p className="mt-2 text-[#806D7B]">This tender currently passes all rules engine checks.</p>
              </div>
            )}
          </div>
        )}

      </section>
    </main>
  );
}

// Sub-component for the 4 metric cards on the Summary tab
function MetricCard({ title, value, subtitle, icon, isAlert = false }: any) {
  return (
    <div className={`flex flex-col justify-between rounded-2xl border ${isAlert ? 'border-rose-200 bg-rose-50/30' : 'border-[#E4DAD5] bg-white'} p-6 shadow-sm`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-[#806D7B]">{title}</span>
        {icon}
      </div>
      <div className="mt-4">
        <p className={`font-serif text-4xl ${isAlert ? 'text-rose-600' : 'text-[#211735]'}`}>{value}</p>
        <p className="mt-1 text-xs text-[#A3989D]">{subtitle}</p>
      </div>
    </div>
  );
}