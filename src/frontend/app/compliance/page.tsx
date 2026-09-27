"use client";

import Link from "next/link";
import {
  ArrowUpRight,
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
} from "lucide-react";
import { apiRequest } from "@/lib/api";
import { useEffect, useState } from "react";

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

export default function CompliancePage() {
  const [standard, setStandard] = useState<SelectedStandard | null>(null);
  const [documentName, setDocumentName] = useState("Tender document");
  const [compliance, setCompliance] = useState<ComplianceData | null>(null);
  const [quality, setQuality] = useState<QualityData | null>(null);
  const [verification, setVerification] = useState<VerificationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedDocument = localStorage.getItem("manak_uploaded_file");
    if (storedDocument) {
      try {
        const parsed = JSON.parse(storedDocument);
        if (parsed.filename) setDocumentName(parsed.filename);
      } catch {
        setDocumentName("Tender document");
      }
    }

    const storedStandard = localStorage.getItem("manak_selected_standard");
    if (!storedStandard) {
      setError("Select a matched standard from Recommendations to check compliance.");
      setLoading(false);
      return;
    }

    let selected: SelectedStandard;
    try {
      selected = JSON.parse(storedStandard) as SelectedStandard;
      if (!Number.isInteger(selected.standard_id)) {
        throw new Error("Invalid standard selection.");
      }
      setStandard(selected);
    } catch {
      setError("The selected standard is invalid. Choose it again from Search.");
      setLoading(false);
      return;
    }

    let cancelled = false;
    const loadCompliance = async () => {
      try {
        const standardId = selected.standard_id;
        const [complianceResult, qualityResult, verificationResult] =
          await Promise.all([
            apiRequest<ComplianceData>(`/compliance/${standardId}`),
            apiRequest<QualityData>(`/quality-score/${standardId}`),
            apiRequest<VerificationData>(`/verification/${standardId}`),
          ]);

        if (!cancelled) {
          setCompliance(complianceResult);
          setQuality(qualityResult);
          setVerification(verificationResult);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Could not load compliance results."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void loadCompliance();
    return () => {
      cancelled = true;
    };
  }, []);

  const verificationResults = verification?.results ?? [];
  const verifiedCount = verificationResults.filter(
    (result) => result.status === "verified"
  ).length;
  const needsReviewCount = verificationResults.length - verifiedCount;

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">

      {/* HEADER */}
      <header className="border-b border-[#E7DDD7] bg-[#FBF8F4]">
        <div className="mx-auto flex h-[76px] max-w-[1400px] items-center justify-between px-8">

          {/* LOGO */}
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#74478A] font-serif text-white">
              M
            </div>

            <div>
              <div className="font-serif text-xl tracking-wide">
                MANAK
              </div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-[#806D7B]">
                AI for Smarter Procurement
              </div>
            </div>
          </Link>

          {/* RIGHT */}
          <div className="flex items-center gap-3">
            <button className="rounded-full border border-[#DED2CE] px-4 py-2 text-xs text-[#493D50]">
              EN
            </button>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#A35A91] text-xs text-white">
              RS
            </div>
          </div>
        </div>
      </header>

      {/* MAIN */}
      <section className="mx-auto max-w-[1150px] px-8 py-14">

        {/* HEADING */}
        <div className="max-w-[850px]">

          <div className="mb-4 flex items-center gap-3 text-xs uppercase tracking-[0.28em] text-[#A35A91]">
            <span className="h-px w-8 bg-[#A35A91]" />
            Standards Compliance
          </div>

          <h1 className="font-serif text-5xl leading-[1.05] tracking-[-0.03em]">
            Check your tender
            <br />
            <span className="text-[#74478A]">
              against Indian Standards.
            </span>
          </h1>

          <p className="mt-6 max-w-[700px] text-[17px] leading-8 text-[#706578]">
            MANAK compares your tender requirements with applicable Indian
            Standards and highlights potential compliance issues.
          </p>

        </div>

        {/* DOCUMENT CARD */}
        <div className="mt-12 flex flex-col justify-between gap-6 rounded-[24px] border border-[#E4D7D1] bg-white p-7 md:flex-row md:items-center">

          <div className="flex items-center gap-5">

            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#EDE0EC] text-[#74478A]">
              <FileText size={25} />
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-[#A35A91]">
                Tender document
              </p>

              <h2 className="mt-1 font-serif text-2xl">
                {documentName}
              </h2>

              <p className="mt-1 text-sm text-[#806D7B]">
                {standard?.standard_number ?? "Choose a standard to evaluate"}
              </p>
            </div>

          </div>

          <Link
            href="/upload"
            className="flex items-center justify-center gap-3 rounded-full bg-[#74478A] px-6 py-3 text-sm font-medium text-white transition hover:bg-[#633B77]"
          >
            <Upload size={17} />
            Upload another
            <ArrowUpRight size={15} />
          </Link>

        </div>

        {error && (
          <p role="alert" className="mt-5 rounded-xl bg-[#FFF1D9] p-4 text-sm text-[#8D5B2B]">
            {error}
            {error.toLowerCase().includes("role") || error.toLowerCase().includes("access")
              ? " This endpoint requires a MANAGER or ADMIN role."
              : ""}
          </p>
        )}

        {/* COMPLIANCE SUMMARY */}
        <div className="mt-10 grid gap-6 md:grid-cols-[1fr_280px]">

          {/* SCORE */}
          <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-7">

            <div className="flex items-center gap-3">
              <ShieldCheck
                size={20}
                className="text-[#74478A]"
              />

              <p className="text-xs uppercase tracking-[0.22em] text-[#A35A91]">
                Compliance summary
              </p>
            </div>

            <div className="mt-6 flex flex-wrap items-end gap-3">

              <span className="font-serif text-6xl text-[#74478A]">
                {loading ? "…" : quality?.score != null ? `${Math.round(quality.score)}%` : "—"}
              </span>

              <span className="mb-2 rounded-full bg-[#FFF1D9] px-3 py-1.5 text-xs font-medium text-[#9A6B35]">
                {loading
                  ? "Checking"
                  : compliance?.status === "checked"
                    ? compliance.alerts.length > 0
                      ? "Needs review"
                      : "No alerts"
                    : compliance?.status ?? "Unavailable"}
              </span>

            </div>

            <p className="mt-4 max-w-[600px] text-sm leading-6 text-[#806D7B]">
              Quality score and compliance alerts returned by the backend for this standard.
            </p>

          </div>

          {/* QUICK STATUS */}
          <div className="rounded-[24px] border border-[#E4DAD5] bg-white p-7">

            <p className="text-xs uppercase tracking-[0.22em] text-[#A35A91]">
              Requirements checked
            </p>

            <div className="mt-5 space-y-4">

              <div className="flex items-center justify-between">
                <span className="text-sm text-[#806D7B]">
                  Compliant
                </span>

                <span className="flex items-center gap-2 font-medium text-[#5D8260]">
                  <CheckCircle2 size={17} />
                  {verifiedCount}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-[#806D7B]">
                  Needs review
                </span>

                <span className="flex items-center gap-2 font-medium text-[#B56D70]">
                  <AlertCircle size={17} />
                  {needsReviewCount}
                </span>
              </div>

            </div>

          </div>

        </div>

        <div className="mt-14">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-[#A35A91]">
              Compliance details
            </p>
            <h2 className="mt-3 font-serif text-3xl">
              {standard?.title ?? standard?.standard_number ?? "Select a standard"}
            </h2>
          </div>

          <div className="space-y-3">
            {(compliance?.alerts ?? []).map((alert) => (
              <article key={`${alert.type}-${alert.requirement_name}-${alert.status}`} className="rounded-xl border border-[#E4DAD5] bg-white p-5">
                <div className="flex items-start gap-3">
                  <AlertCircle size={18} className="mt-0.5 shrink-0 text-[#B56D70]" />
                  <div>
                    <p className="font-medium text-[#493D50]">
                      {alert.requirement_name ?? alert.type} · {alert.status.replaceAll("_", " ")}
                    </p>
                    <p className="mt-1 text-sm text-[#806D7B]">{alert.reason}</p>
                  </div>
                </div>
              </article>
            ))}
            {verificationResults.map((result, index) => (
              <article key={`${result.type}-${index}`} className="rounded-xl border border-[#E4DAD5] bg-white p-5">
                <div className="flex items-start gap-3">
                  {result.status === "verified" ? (
                    <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-[#5D8260]" />
                  ) : (
                    <AlertCircle size={18} className="mt-0.5 shrink-0 text-[#B56D70]" />
                  )}
                  <div>
                    <p className="font-medium text-[#493D50]">
                      {result.type} verification · {result.status.replaceAll("_", " ")}
                    </p>
                    <p className="mt-1 text-sm text-[#806D7B]">
                      {result.reason ?? result.source ?? "Verified source"}
                    </p>
                  </div>
                </div>
              </article>
            ))}
            {!loading && !error && (compliance?.alerts.length ?? 0) === 0 && verificationResults.length === 0 && (
              <p className="rounded-xl border border-dashed border-[#D8C8D6] p-6 text-sm text-[#806D7B]">
                The API returned no requirement details for this standard.
              </p>
            )}
          </div>
        </div>

        {/* FOOTER ACTIONS */}
        <div className="mt-12 flex flex-col gap-4 border-t border-[#E4DAD5] pt-8 sm:flex-row sm:items-center sm:justify-between">

          <p className="text-sm text-[#806D7B]">
            Review the highlighted requirements before finalising the tender.
          </p>

          <Link
            href="/recommendations"
            className="flex items-center justify-center gap-3 rounded-full bg-[#74478A] px-6 py-3 text-sm font-medium text-white transition hover:bg-[#633B77]"
          >
            View recommendations
            <ArrowUpRight size={16} />
          </Link>

        </div>

      </section>

    </main>
  );
}
