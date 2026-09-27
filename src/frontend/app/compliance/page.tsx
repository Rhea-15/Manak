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

import NormativeTreeGraph from "../../components/NormativeTreeGraph";
import DiffAndGaugeView from "../../components/DiffAndGaugeView";

export default function CompliancePage() {
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
                Tender_Requirements.pdf
              </h2>

              <p className="mt-1 text-sm text-[#806D7B]">
                Analysed by MANAK
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

        {/* COMPLIANCE SUMMARY & GAUGE */}
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
                82%
              </span>

              <span className="mb-2 rounded-full bg-[#FFF1D9] px-3 py-1.5 text-xs font-medium text-[#9A6B35]">
                Partially Compliant
              </span>

            </div>

            <p className="mt-4 max-w-[600px] text-sm leading-6 text-[#806D7B]">
              Most requirements are aligned with the applicable standard.
              One requirement needs further review.
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
                  4
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-[#806D7B]">
                  Needs review
                </span>

                <span className="flex items-center gap-2 font-medium text-[#B56D70]">
                  <AlertCircle size={17} />
                  1
                </span>
              </div>

            </div>

          </div>

        </div>

        {/* TRACK B DELIVERABLE: NORMATIVE TREE GRAPH */}
        <div className="mt-14">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-[#A35A91]">
              Hierarchy & Standards Mapping
            </p>

            <h2 className="mt-3 font-serif text-3xl">
              Normative Reference Tree
            </h2>
          </div>

          <div className="overflow-hidden rounded-[24px] border border-[#E4DAD5] bg-white p-4 shadow-sm">
            <NormativeTreeGraph />
          </div>
        </div>

        {/* TRACK B DELIVERABLE: DIFF AND GAUGE VIEW */}
        <div className="mt-14">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-[#A35A91]">
              Detailed Analysis Engine
            </p>

            <h2 className="mt-3 font-serif text-3xl">
              Specification Diff & Gauge Analysis
            </h2>
          </div>

          <DiffAndGaugeView />
        </div>

        {/* COMPARISON */}
        <div className="mt-14">

          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-[#A35A91]">
              Requirement comparison
            </p>

            <h2 className="mt-3 font-serif text-3xl">
              Tender vs applicable standard
            </h2>
          </div>

          {/* COMPARISON CARD */}
          <div className="overflow-hidden rounded-[24px] border border-[#E4DAD5] bg-white">

            {/* COLUMN HEADERS */}
            <div className="grid border-b border-[#E4DAD5] md:grid-cols-2">

              <div className="border-b border-[#E4DAD5] bg-[#FBF7F1] px-7 py-5 md:border-b-0 md:border-r">
                <p className="text-xs uppercase tracking-[0.2em] text-[#806D7B]">
                  Tender requirement
                </p>
              </div>

              <div className="bg-[#FBF7F1] px-7 py-5">
                <p className="text-xs uppercase tracking-[0.2em] text-[#806D7B]">
                  Applicable Indian Standard
                </p>
              </div>

            </div>

            {/* COMPARISON CONTENT */}
            <div className="grid md:grid-cols-2">

              {/* LEFT */}
              <div className="border-b border-[#E4DAD5] p-7 md:border-b-0 md:border-r">

                <div className="mb-4 flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#E9A4A4]" />

                  <span className="text-xs font-medium text-[#A56B70]">
                    Requirement
                  </span>
                </div>

                <p className="text-[17px] leading-8 text-[#211735]">
                  The supplied material must comply with applicable quality
                  specifications.
                </p>

              </div>

              {/* RIGHT */}
              <div className="p-7">

                <div className="mb-4 flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#A9D9B2]" />

                  <span className="text-xs font-medium text-[#5D8260]">
                    Standard
                  </span>
                </div>

                <p className="text-[17px] leading-8 text-[#211735]">
                  Materials shall comply with the applicable quality
                  specifications and prescribed permissible limits.
                </p>

              </div>

            </div>

            {/* STATUS */}
            <div className="border-t border-[#E4DAD5] bg-[#FFF9F3] px-7 py-5">

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                <div className="flex items-center gap-3">

                  <AlertCircle
                    size={19}
                    className="text-[#B56D70]"
                  />

                  <div>
                    <p className="text-sm font-medium text-[#493D50]">
                      Difference detected
                    </p>

                    <p className="mt-1 text-xs text-[#806D7B]">
                      The standard specifies permissible limits that are not
                      explicitly mentioned in the tender.
                    </p>
                  </div>

                </div>

                <span className="w-fit rounded-full bg-[#F7E2E2] px-4 py-2 text-xs font-medium text-[#A55E65]">
                  Needs Review
                </span>

              </div>

            </div>

          </div>

        </div>

        {/* SECOND REQUIREMENT */}
        <div className="mt-6 overflow-hidden rounded-[24px] border border-[#E4DAD5] bg-white">

          <div className="grid md:grid-cols-2">

            <div className="border-b border-[#E4DAD5] p-7 md:border-b-0 md:border-r">

              <div className="mb-4 flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#A9D9B2]" />

                <span className="text-xs font-medium text-[#5D8260]">
                  Requirement
                </span>
              </div>

              <p className="text-[17px] leading-8 text-[#211735]">
                Materials must meet the required strength and durability
                specifications.
              </p>

            </div>

            <div className="p-7">

              <div className="mb-4 flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#A9D9B2]" />

                <span className="text-xs font-medium text-[#5D8260]">
                  Standard
                </span>
              </div>

              <p className="text-[17px] leading-8 text-[#211735]">
                Materials shall satisfy the specified strength and durability
                requirements.
              </p>

            </div>

          </div>

          <div className="border-t border-[#E4DAD5] bg-[#F5FAF5] px-7 py-5">

            <div className="flex items-center gap-3">

              <CheckCircle2
                size={19}
                className="text-[#5D8260]"
              />

              <p className="text-sm font-medium text-[#5D8260]">
                Requirement appears compliant
              </p>

            </div>

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