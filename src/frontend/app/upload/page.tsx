"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  FileText,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

/* =========================================================
   SAMPLE DOCUMENTS
========================================================= */
const sampleDocuments = [
  {
    id: "sample-1",
    title: "Procurement of Fire Extinguishers & Safety Systems",
    organization: "Central Public Works Department (CPWD)",
    referenceNo: "TENDER/2026/BIS/FS-089",
    category: "Fire Safety",
    fileSize: "2.4 MB",
    fileName: "CPWD_Fire_Safety_Tender_2026.pdf",
  },
  {
    id: "sample-2",
    title: "Supply & Laying of Electrical Wiring for Substation",
    organization: "State Electricity Transmission Corp",
    referenceNo: "SETC/ELEC/2026/112",
    category: "Electrical",
    fileSize: "4.1 MB",
    fileName: "SETC_Electrical_Wiring_Tender.pdf",
  },
  {
    id: "sample-3",
    title: "Structural Steel Supply for Highway Bridge Construction",
    organization: "National Highways Authority of India (NHAI)",
    referenceNo: "NHAI/CIVIL/STEEL/2026/04",
    category: "Civil Construction",
    fileSize: "3.8 MB",
    fileName: "NHAI_Structural_Steel_Procurement.pdf",
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
  const [selectedSample, setSelectedSample] = useState<
    (typeof sampleDocuments)[0] | null
  >(null);
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
        setSelectedSample(null);
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
        setSelectedSample(null);
      } else {
        setErrorMsg("Please upload a valid PDF document.");
      }
    }
  };

  const handleSampleSelect = (sample: (typeof sampleDocuments)[0]) => {
    setSelectedSample(sample);
    setSelectedFile(null);
    setErrorMsg("");
  };

  const handleStartAnalysis = () => {
    if (!selectedFile && !selectedSample) {
      setErrorMsg("Please upload a PDF file or select a sample document.");
      return;
    }

    setIsAnalyzing(true);

    const documentName = selectedFile
      ? selectedFile.name
      : selectedSample?.fileName || "Uploaded_Document.pdf";

    localStorage.setItem("uploadedFileName", documentName);

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
                  or click to browse from your computer (PDF up to 25 MB)
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

        {/* OR DIVIDER */}
        <div className="my-10 flex items-center gap-4">
          <div className="h-px flex-1 bg-[#E4DAD5]" />
          <span className="text-xs text-[#806D7B]">OR TRY A SAMPLE TENDER</span>
          <div className="h-px flex-1 bg-[#E4DAD5]" />
        </div>

        {/* SAMPLE TENDERS */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {sampleDocuments.map((sample) => {
            const isSelected = selectedSample?.id === sample.id;
            return (
              <button
                type="button"
                key={sample.id}
                onClick={() => handleSampleSelect(sample)}
                className={`flex flex-col justify-between rounded-2xl border p-5 text-left transition ${
                  isSelected
                    ? "border-[#74478A] bg-[#EDE0EC] shadow-sm"
                    : "border-[#E4DAD5] bg-white hover:border-[#C5A7C2] hover:bg-[#FDFBFD]"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="rounded-full bg-[#F2EEE8] px-2.5 py-0.5 text-[10px] text-[#806D7B]">
                      {sample.category}
                    </span>
                    {isSelected && (
                      <CheckCircle2 size={16} className="text-[#74478A]" />
                    )}
                  </div>
                  <h4 className="mt-3 font-serif text-sm font-medium leading-snug text-[#211735]">
                    {sample.title}
                  </h4>
                  <p className="mt-2 text-[11px] text-[#806D7B]">
                    {sample.organization}
                  </p>
                </div>
                <div className="mt-4 border-t border-[#EEE7E2] pt-3 text-[10px] text-[#806D7B]">
                  {sample.referenceNo}
                </div>
              </button>
            );
          })}
        </div>

        {/* ACTION BUTTON */}
        <div className="mt-10 text-center">
          <button
            type="button"
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
            className="inline-flex h-14 items-center gap-3 rounded-full bg-[#74478A] px-10 text-sm font-medium text-white transition hover:bg-[#633A77] disabled:opacity-50"
          >
            {isAnalyzing ? (
              <span>Analyzing Document...</span>
            ) : (
              <>
                <span>Run Compliance Check</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </section>
    </main>
  );
}