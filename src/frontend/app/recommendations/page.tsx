"use client";

import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  FileText,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import Header from "@/components/header";
import { apiRequest } from "@/lib/api";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Recommendation = {
  item_id: string;
  standard_id: number | null;
  original_spec: string;
  ai_suggested_spec: string;
  compliant: boolean;
  mandatory_marks: string[];
  allied_standards: string[];
  source: string;
};

type UploadedDocument = {
  document_id?: string;
  filename?: string;
  extracted_data?: {
    pages?: {
      raw_text?: string;
      entities?: { text: string }[];
    }[];
  } | null;
};

export default function RecommendationsPage() {
  const router = useRouter();

  const [fileName, setFileName] = useState("Tender document");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const storedFile = localStorage.getItem("manak_uploaded_file");

    if (!storedFile) {
      setError("Upload a tender before requesting recommendations.");
      setLoading(false);
      return;
    }

    const loadRecommendations = async () => {
      try {
        const document = JSON.parse(storedFile) as UploadedDocument;
        if (document.filename) setFileName(document.filename);

        const specifications = (document.extracted_data?.pages ?? [])
          .map((page) =>
            page.raw_text?.trim() ||
            page.entities?.map((entity) => entity.text).join("; ") ||
            ""
          )
          .filter(Boolean);

        if (!specifications.length) {
          throw new Error(
            "No extracted text is available. Upload a supported PDF or TXT document."
          );
        }

        const results = await Promise.all(
          specifications.map((original_spec, index) =>
            apiRequest<Recommendation>("/api/v1/recommendation", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                item_id: `${document.document_id ?? "tender"}-${index + 1}`,
                original_spec,
              }),
            })
          )
        );

        if (!cancelled) setRecommendations(results);
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Could not load recommendations."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }

    };

    void loadRecommendations();
    return () => {
      cancelled = true;
    };
  }, []);

  const categories = [
    "All",
    ...Array.from(
      new Set(
        recommendations.map((item) =>
          item.compliant ? "Compliant" : "Needs verification"
        )
      )
    ),
  ];

  const filteredRecommendations =
    selectedCategory === "All"
      ? recommendations
      : recommendations.filter(
          (item) =>
            (item.compliant ? "Compliant" : "Needs verification") ===
            selectedCategory
        );

  const openCompliance = (recommendation: Recommendation) => {
    if (recommendation.standard_id === null) return;
    localStorage.setItem(
      "manak_selected_standard",
      JSON.stringify({
        standard_id: recommendation.standard_id,
        standard_number: recommendation.ai_suggested_spec.match(
          /\bIS\s+\d{1,6}:\d{4}\b/i
        )?.[0],
        title: recommendation.ai_suggested_spec,
      })
    );
    router.push("/compliance");
  };

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">

      {/* HEADER */}

      <Header />


      {/* PAGE */}

      <section className="mx-auto max-w-[1150px] px-8 py-14">

        {/* LABEL */}

        <div className="mb-4 flex items-center gap-3 text-xs uppercase tracking-[0.28em] text-[#A35A91]">

          <span className="h-px w-8 bg-[#A35A91]" />

          AI Recommendations

        </div>


        {/* HEADING */}

        <div className="flex flex-col justify-between gap-8 lg:flex-row lg:items-end">

          <div>

            <h1 className="font-serif text-5xl leading-[1.05] tracking-[-0.03em]">

              Standards matched

              <br />

              <span className="text-[#74478A]">
                to your tender.
              </span>

            </h1>


            <p className="mt-6 max-w-[700px] text-[17px] leading-8 text-[#706578]">

              MANAK analyses your tender specifications and recommends
              Indian Standards based on the requirements it identifies.

            </p>

          </div>

        </div>


        {/* DOCUMENT */}

        <div className="mt-10 flex flex-col justify-between gap-5 rounded-[22px] border border-[#E4DAD5] bg-white p-6 md:flex-row md:items-center">

          <div className="flex items-center gap-4">

            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#EDE0EC] text-[#74478A]">

              <FileText size={22} />

            </div>


            <div>

              <p className="text-xs uppercase tracking-[0.18em] text-[#A3989D]">
                Based on
              </p>

              <p className="mt-1 font-medium text-[#211735]">
                {fileName}
              </p>

            </div>

          </div>


          <div className="flex items-center gap-2 text-sm text-[#74478A]">

            <Sparkles size={16} />

            {loading ? "Analyzing tender..." : "Analysis response"}

          </div>

        </div>

        {error && (
          <p role="alert" className="mt-4 text-sm text-[#A55E65]">
            {error}
          </p>
        )}


        {/* SUMMARY */}

        <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">

          <InfoCard
            icon={<BookOpen size={19} />}
            number={recommendations.length}
            title="Requirements analyzed"
            description="Extracted tender pages sent to the API"
          />


          <InfoCard
            icon={<CheckCircle2 size={19} />}
            number={
              recommendations.filter((item) => item.compliant).length
            }
            title="Compliant"
            description="API responses marked compliant"
          />


          <InfoCard
            icon={<ShieldCheck size={19} />}
            number={recommendations.filter((item) => !item.compliant).length}
            title="Needs verification"
            description="Requirements requiring review"
          />

        </div>


        {/* CATEGORY FILTER */}

        <div className="mt-12">

          <div className="flex flex-wrap items-center gap-2">

            {categories.map((category) => (

              <button
                key={category}
                type="button"
                onClick={() => setSelectedCategory(category)}
                className={`rounded-full px-5 py-2.5 text-xs font-medium transition ${
                  selectedCategory === category
                    ? "bg-[#74478A] text-white"
                    : "border border-[#DDD1CC] bg-white text-[#806D7B] hover:bg-[#F3EBF1]"
                }`}
              >
                {category}
              </button>

            ))}

          </div>

        </div>


        {/* RECOMMENDATIONS */}

        <div className="mt-6 space-y-5">

          {filteredRecommendations.map((recommendation) => (

            <RecommendationCard
              key={recommendation.item_id}
              recommendation={recommendation}
              onViewStandard={() => openCompliance(recommendation)}
            />

          ))}

          {!loading && !error && recommendations.length === 0 && (
            <p className="rounded-xl border border-dashed border-[#D8C8D6] p-6 text-sm text-[#806D7B]">
              No recommendation results were returned.
            </p>
          )}

        </div>


        {/* FOOTER CTA */}

        <div className="relative mt-12 overflow-hidden rounded-[24px] bg-[#74478A] px-8 py-9 text-white">

          <div className="absolute -right-20 -top-24 h-60 w-60 rounded-full bg-white/10 blur-3xl" />

          <div className="relative flex flex-col justify-between gap-6 md:flex-row md:items-center">

            <div>

              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[#F4D99A]">

                <Sparkles size={14} />

                Next step

              </div>


              <h2 className="mt-3 font-serif text-2xl">
                Ready to check compliance?
              </h2>


              <p className="mt-2 max-w-[620px] text-sm leading-6 text-white/70">

                Review how your tender specifications align with the
                recommended Indian Standards.

              </p>

            </div>


            <button
              type="button"
              onClick={() => router.push("/compliance")}
              className="flex shrink-0 items-center gap-3 rounded-full bg-white px-6 py-3 text-sm font-medium text-[#74478A] transition hover:bg-[#F8F3F9]"
            >

              Check compliance

              <ArrowRight size={16} />

            </button>

          </div>

        </div>

      </section>

    </main>
  );
}


/* ================================================= */
/* INFO CARD */
/* ================================================= */

function InfoCard({
  icon,
  number,
  title,
  description,
}: {
  icon: React.ReactNode;
  number: number;
  title: string;
  description: string;
}) {

  return (

    <div className="rounded-[22px] border border-[#E4DAD5] bg-white p-6">

      <div className="flex items-center gap-3 text-[#74478A]">

        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#EDE0EC]">
          {icon}
        </div>

        <span className="text-xs uppercase tracking-[0.15em] text-[#806D7B]">
          {title}
        </span>

      </div>


      <p className="mt-5 font-serif text-4xl text-[#211735]">
        {number}
      </p>


      <p className="mt-1 text-sm text-[#806D7B]">
        {description}
      </p>

    </div>

  );
}


/* ================================================= */
/* RECOMMENDATION CARD */
/* ================================================= */

function RecommendationCard({
  recommendation,
  onViewStandard,
}: {
  recommendation: Recommendation;
  onViewStandard: () => void;
}) {

  return (

    <article className="group rounded-[24px] border border-[#E4DAD5] bg-white p-7 transition duration-200 hover:-translate-y-0.5 hover:border-[#C5A7C2] hover:shadow-[0_12px_35px_rgba(116,71,138,0.07)]">

      <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">

        <div className="flex gap-5">

          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#F0E3EF] text-[#74478A]">

            <BookOpen size={21} />

          </div>


          <div>

            <div className="flex flex-wrap items-center gap-3">

              <span className={`rounded-full px-3 py-1 text-[10px] ${recommendation.compliant ? "bg-[#EDF5ED] text-[#5D8260]" : "bg-[#FFF1D9] text-[#9A6B35]"}`}>
                {recommendation.compliant ? "Compliant" : "Verification required"}
              </span>

            </div>


            <h2 className="mt-3 font-serif text-[24px] leading-8 text-[#211735]">
              {recommendation.ai_suggested_spec}
            </h2>


            <p className="mt-3 max-w-[720px] text-sm leading-6 text-[#806D7B]">
              <span className="font-medium text-[#493D50]">Tender text: </span>
              {recommendation.original_spec}
            </p>

          </div>

        </div>


        <div className="shrink-0 text-xs text-[#806D7B]">
          Source: {recommendation.source}
        </div>

      </div>


      <div className="mt-6 flex items-center justify-between border-t border-[#EEE7E2] pt-4">

        <div className="flex flex-wrap items-center gap-2 text-xs text-[#806D7B]">
          {recommendation.mandatory_marks.length ? (
            <>
              <CheckCircle2 size={14} className="text-[#5D8260]" />
              Mandatory marks: {recommendation.mandatory_marks.join(", ")}
            </>
          ) : (
            <span>No mandatory marks returned</span>
          )}
        </div>


        <button
          type="button"
          onClick={onViewStandard}
          disabled={recommendation.standard_id === null}
          className="flex items-center gap-2 text-xs font-medium text-[#74478A] disabled:cursor-not-allowed disabled:opacity-50"
        >

          View standard

          <ChevronRight size={14} />

        </button>

      </div>

    </article>

  );
}