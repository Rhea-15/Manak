"use client";

import {
  Upload,
  FileText,
  X,
  ArrowRight,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [analysing, setAnalysing] = useState(false);

  const handleFile = (selectedFile: File | undefined) => {
    if (!selectedFile) return;

    // 25 MB limit
    if (selectedFile.size > 25 * 1024 * 1024) {
      alert("File size must be less than 25 MB.");
      return;
    }

    setFile(selectedFile);
  };

  const handleAnalyse = () => {
    if (!file) return;

    setAnalysing(true);

    // Save basic file information so the next page can use it
    localStorage.setItem(
      "manak_uploaded_file",
      JSON.stringify({
        name: file.name,
        size: file.size,
        type: file.type,
      })
    );

    // Small loading effect
    setTimeout(() => {
      router.push("/compliance");
    }, 700);
  };

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">

      {/* ================= HEADER ================= */}

      <header className="border-b border-[#E8DED9] bg-[#FBF8F4]">

        <div className="mx-auto flex h-[76px] max-w-[1400px] items-center justify-between px-8">

          {/* Logo */}

          <button
            type="button"
            onClick={() => router.push("/")}
            className="flex items-center gap-3"
          >

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#74478A] text-white">
              M
            </div>

            <div className="text-left">

              <div className="font-serif text-xl tracking-wide">
                MANAK
              </div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-[#806D7B]">
                AI for Smarter Procurement
              </div>

            </div>

          </button>


          {/* Right side */}

          <div className="flex items-center gap-4">

            <button className="rounded-full border border-[#DED2CE] bg-white/60 px-4 py-2 text-sm text-[#493D50]">
              EN
            </button>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#A35A91] text-xs text-white">
              RS
            </div>

          </div>

        </div>

      </header>


      {/* ================= MAIN ================= */}

      <section className="mx-auto max-w-[1100px] px-8 py-16">

        {/* Heading */}

        <div className="mb-12">

          <div className="mb-4 flex items-center gap-3 text-xs uppercase tracking-[0.28em] text-[#A35A91]">

            <span className="h-px w-8 bg-[#A35A91]" />

            Tender Analysis

          </div>


          <h1 className="max-w-[700px] font-serif text-5xl leading-[1.05] text-[#211735]">

            Upload a tender.

            <br />

            <span className="text-[#74478A]">
              Let MANAK analyse it.
            </span>

          </h1>


          <p className="mt-6 max-w-[650px] text-[17px] leading-8 text-[#706578]">

            Upload your tender document and MANAK will analyse the
            specifications, identify relevant Indian Standards, and
            prepare the document for compliance checking.

          </p>

        </div>


        {/* ================= UPLOAD AREA ================= */}

        <div
          className={`relative overflow-hidden rounded-[28px] border ${
            file
              ? "border-[#B985A7]"
              : "border-[#DCCBCF]"
          } bg-[#FDFBF8] p-10 transition`}
        >

          {/* Decorative pastel circles */}

          <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-[#F1DDE8]/50 blur-2xl" />

          <div className="pointer-events-none absolute -bottom-24 -left-20 h-64 w-64 rounded-full bg-[#F6E5BE]/40 blur-2xl" />


          {!file ? (

            /* ================= EMPTY UPLOAD STATE ================= */

            <label
              htmlFor="file-upload"
              className="relative flex cursor-pointer flex-col items-center justify-center rounded-[22px] border border-dashed border-[#C8B2C7] bg-[#FBF5F8] px-8 py-20 text-center transition hover:border-[#74478A] hover:bg-[#F8EFF6]"
            >

              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-[#E8D5E7] text-[#74478A]">
                <Upload size={27} strokeWidth={1.7} />
              </div>


              <h2 className="font-serif text-2xl text-[#211735]">
                Drop your tender here
              </h2>


              <p className="mt-3 text-sm text-[#806D7B]">
                or click to browse your files
              </p>


              {/* File types */}

              <div className="mt-6 flex gap-2">

                {["PDF", "DOCX", "CSV", "TXT"].map((type) => (

                  <span
                    key={type}
                    className="rounded-full bg-white px-3 py-1.5 text-[11px] text-[#806D7B] shadow-sm"
                  >
                    {type}
                  </span>

                ))}

              </div>


              <p className="mt-5 text-xs text-[#A3989D]">
                Maximum file size: 25 MB
              </p>


              <input
                id="file-upload"
                type="file"
                accept=".pdf,.doc,.docx,.csv,.txt"
                className="hidden"
                onChange={(e) =>
                  handleFile(e.target.files?.[0])
                }
              />

            </label>

          ) : (

            /* ================= FILE SELECTED STATE ================= */

            <div className="relative rounded-[22px] border border-[#DCCBCF] bg-white p-8">

              <div className="flex items-center justify-between">

                {/* File information */}

                <div className="flex items-center gap-4">

                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#E9D9EA] text-[#74478A]">
                    <FileText size={25} />
                  </div>


                  <div>

                    <p className="font-medium text-[#211735]">
                      {file.name}
                    </p>


                    <p className="mt-1 text-xs text-[#806D7B]">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>

                  </div>

                </div>


                {/* Remove file */}

                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-[#F6EEEE] text-[#9B6A72] transition hover:bg-[#F0DDDF]"
                >

                  <X size={16} />

                </button>

              </div>


              {/* Ready message */}

              <div className="mt-8 rounded-2xl bg-[#FBF7F1] p-5">

                <div className="flex items-center gap-3">

                  <CheckCircle2
                    size={19}
                    className="text-[#74478A]"
                  />


                  <div>

                    <p className="text-sm font-medium text-[#211735]">
                      Document ready for analysis
                    </p>


                    <p className="mt-1 text-xs text-[#806D7B]">
                      MANAK can now extract and analyse the specifications.
                    </p>

                  </div>

                </div>

              </div>

            </div>

          )}

        </div>


        {/* ================= BOTTOM ACTION ================= */}

        <div className="mt-8 flex items-center justify-between">

          {/* AI text */}

          <div className="flex items-center gap-2 text-sm text-[#806D7B]">

            <Sparkles
              size={16}
              className="text-[#C97878]"
            />

            AI-powered standards analysis

          </div>


          {/* Analyse button */}

          <button
            type="button"
            disabled={!file || analysing}
            onClick={handleAnalyse}
            className={`flex items-center gap-3 rounded-full px-7 py-3.5 text-sm font-medium transition ${
              file && !analysing
                ? "bg-[#74478A] text-white shadow-lg shadow-[#74478A]/20 hover:bg-[#633B77] hover:-translate-y-0.5"
                : "cursor-not-allowed bg-[#E7DED9] text-[#A3989D]"
            }`}
          >

            {analysing ? (

              <>
                Analysing...

                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              </>

            ) : (

              <>
                Analyse tender
                <ArrowRight size={17} />
              </>

            )}

          </button>

        </div>


        {/* ================= WHAT HAPPENS NEXT ================= */}

        <div className="mt-20 border-t border-[#E4DAD5] pt-10">

          <p className="text-xs uppercase tracking-[0.25em] text-[#A35A91]">
            What happens next
          </p>


          <div className="mt-7 grid grid-cols-1 gap-4 md:grid-cols-3">

            <Step
              number="01"
              title="Extract"
              description="MANAK extracts text and technical specifications from your tender."
            />


            <Step
              number="02"
              title="Understand"
              description="The system identifies products, requirements, and key technical terms."
            />


            <Step
              number="03"
              title="Recommend"
              description="Relevant Indian Standards are matched to your specifications."
            />

          </div>

        </div>

      </section>

    </main>
  );
}


/* ================================================= */
/* STEP COMPONENT */
/* ================================================= */

function Step({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {

  return (

    <div className="rounded-2xl border border-[#E4DAD5] bg-white/60 p-6">

      <span className="text-xs tracking-[0.2em] text-[#C97878]">
        {number}
      </span>


      <h3 className="mt-4 font-serif text-2xl text-[#211735]">
        {title}
      </h3>


      <p className="mt-2 text-sm leading-6 text-[#806D7B]">
        {description}
      </p>

    </div>

  );
}