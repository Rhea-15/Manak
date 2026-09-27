"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  Sparkles,
} from "lucide-react";

/* =========================================================
   SUPPORTED FILE TYPES (cosmetic badges)
========================================================= */
const supportedTypes = ["PDF", "DOCX", "CSV", "TXT"];

/* =========================================================
   WHAT HAPPENS NEXT STEPS
========================================================= */
const processSteps = [
  {
    number: "01",
    title: "Extract",
    description:
      "MANAK extracts text and technical specifications from your tender.",
  },
  {
    number: "02",
    title: "Understand",
    description:
      "The system identifies products, requirements, and key technical terms.",
  },
  {
    number: "03",
    title: "Recommend",
    description:
      "Relevant Indian Standards are matched to your specifications.",
  },
];

/* =========================================================
   PAGE
========================================================= */
export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setErrorMsg("");

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setSelectedFile(file);
      } else {
        setErrorMsg("Please upload a valid PDF document.");
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMsg("");
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setSelectedFile(file);
      } else {
        setErrorMsg("Please upload a valid PDF document.");
      }
    }
  };

  const handleStartAnalysis = () => {
    if (!selectedFile) {
      setErrorMsg("Please upload a PDF file to analyse.");
      return;
    }

    setIsAnalyzing(true);

    localStorage.setItem("uploadedFileName", selectedFile.name);

    setTimeout(() => {
      router.push("/compliance");
    }, 1200);
  };

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">
      {/* PAGE CONTENT */}
      <section className="mx-auto max-w-[1000px] px-8 py-14">
        {/* HEADING */}
        <div className="text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#DED2CE] bg-white px-4 py-1.5 text-xs text-[#806D7B]">
            <ShieldCheck size={14} className="text-[#74478A]" />
            AI-Powered Tender Compliance Checker
          </div>
          <h1 className="font-serif text-4xl font-normal leading-tight tracking-tight text-[#211735]">
            Upload Procurement Tender Document
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-[#706578]">
            Upload your PDF tender or RFQ to automatically analyze compliance
            against Indian Standards (IS), identify missing normative codes, and
            highlight technical non-compliances.
          </p>
        </div>

        {/* DRAG & DROP BOX */}
        <div className="mt-10">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer rounded-[24px] border-2 border-dashed p-10 text-center transition ${
              isDragging
                ? "border-[#74478A] bg-[#F5EEF5]"
                : selectedFile
                ? "border-[#3B7A57] bg-[#F4F9F5]"
                : "border-[#D9C7D6] bg-white hover:border-[#BFA6BD] hover:bg-[#FDFBFD]"
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".pdf"
              className="hidden"
            />

            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[#F0E3EF] text-[#74478A]">
              {selectedFile ? (
                <CheckCircle2 size={32} className="text-[#3B7A57]" />
              ) : (
                <Upload size={28} strokeWidth={1.8} />
              )}
            </div>

            {selectedFile ? (
              <div className="mt-4">
                <p className="text-xs uppercase tracking-wider text-[#3B7A57]">
                  File Selected
                </p>
                <h3 className="mt-1 font-serif text-xl text-[#211735]">
                  {selectedFile.name}
                </h3>
                <p className="mt-1 text-xs text-[#806D7B]">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • PDF
                </p>
              </div>
            ) : (
              <div className="mt-4">
                <h3 className="font-serif text-xl text-[#211735]">
                  Drag & Drop your Tender PDF here
                </h3>
                <p className="mt-2 text-xs text-[#806D7B]">
                  or click to browse from your computer
                </p>

                {/* SUPPORTED FILE TYPE BADGES */}
                <div className="mt-5 flex items-center justify-center gap-2">
                  {supportedTypes.map((type) => (
                    <span
                      key={type}
                      className="rounded-full border border-[#E4DAD5] bg-white px-3 py-1 text-[11px] text-[#806D7B]"
                    >
                      {type}
                    </span>
                  ))}
                </div>

                <p className="mt-3 text-[11px] text-[#A99AA6]">
                  Maximum file size: 25 MB
                </p>
              </div>
            )}
          </div>

          {errorMsg && (
            <div className="mt-3 flex items-center justify-center gap-2 text-xs text-[#C04848]">
              <AlertCircle size={14} />
              {errorMsg}
            </div>
          )}
        </div>

        {/* AI TAG + ANALYSE BUTTON ROW */}
        <div className="mt-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-[#806D7B]">
            <Sparkles size={14} className="text-[#74478A]" />
            AI-powered standards analysis
          </div>

          <button
            type="button"
            onClick={handleStartAnalysis}
            disabled={isAnalyzing || !selectedFile}
            className={`inline-flex h-11 items-center gap-2 rounded-full px-6 text-sm font-medium transition ${
              selectedFile
                ? "bg-[#74478A] text-white hover:bg-[#633A77]"
                : "bg-[#EDE7E3] text-[#A99AA6]"
            } disabled:cursor-not-allowed`}
          >
            {isAnalyzing ? (
              <span>Analyzing...</span>
            ) : (
              <>
                <span>Analyse tender</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>

        {/* WHAT HAPPENS NEXT */}
        <div className="mt-14 border-t border-[#EEE4DD] pt-10">
          <div className="mb-6 text-xs font-medium uppercase tracking-[0.2em] text-[#806D7B]">
            What happens next
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {processSteps.map((step) => (
              <div
                key={step.number}
                className="rounded-2xl border border-[#E4DAD5] bg-white p-6"
              >
                <div className="text-xs font-medium text-[#B37B92]">
                  {step.number}
                </div>
                <h4 className="mt-2 font-serif text-xl text-[#211735]">
                  {step.title}
                </h4>
                <p className="mt-2 text-sm leading-relaxed text-[#706578]">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}