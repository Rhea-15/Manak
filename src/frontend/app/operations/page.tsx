"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

type DocumentItem = {
  document_id: string;
  filename: string;
  bucket: string;
  object_name: string;
  parse_status: string;
  created_at: string;
};

type ReviewItem = {
  id: number;
  document_name: string;
  status: string;
  submitted_by: string | null;
  review_notes: string | null;
};

type AuditItem = {
  id: number;
  user_id: string | null;
  action: string;
  details: string | null;
  created_at: string;
};

type QualityScore = {
  tender_id: string;
  score: number;
  verdict: string;
  critical_alerts: { type: string; message: string; severity: string }[];
};

export default function OperationsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditItem[]>([]);
  const [documentsError, setDocumentsError] = useState<string | null>(null);
  const [reviewsError, setReviewsError] = useState<string | null>(null);
  const [auditError, setAuditError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState("Checking");
  const [tenderId, setTenderId] = useState("");
  const [score, setScore] = useState<QualityScore | null>(null);
  const [scoreError, setScoreError] = useState<string | null>(null);
  const [scoring, setScoring] = useState(false);

  const loadOperationsData = async () => {
    setLoading(true);
    const [healthResult, documentResult, reviewResult, auditResult] = await Promise.allSettled([
      apiRequest<{ status: string }>("/health"),
      apiRequest<{ documents: DocumentItem[] }>("/documents"),
      apiRequest<ReviewItem[]>("/review/queue"),
      apiRequest<AuditItem[]>("/audit/logs"),
    ]);

    setBackendStatus(
      healthResult.status === "fulfilled" ? healthResult.value.status : "Unavailable"
    );
    if (documentResult.status === "fulfilled") {
      setDocuments(documentResult.value.documents);
      setDocumentsError(null);
    } else {
      setDocumentsError(documentResult.reason.message ?? "Could not load documents.");
    }
    if (reviewResult.status === "fulfilled") {
      setReviews(reviewResult.value);
      setReviewsError(null);
    } else {
      setReviewsError(reviewResult.reason.message ?? "Could not load review queue.");
    }
    if (auditResult.status === "fulfilled") {
      setAuditLogs(auditResult.value);
      setAuditError(null);
    } else {
      setAuditError(auditResult.reason.message ?? "Could not load audit logs.");
    }
    setLoading(false);
  };

  useEffect(() => {
    void loadOperationsData();
  }, []);

  const updateReview = async (reviewId: number, action: "approve" | "reject") => {
    try {
      await apiRequest(`/review/${reviewId}/${action}`, { method: "PUT" });
      await loadOperationsData();
    } catch (error) {
      setReviewsError(
        error instanceof Error ? error.message : "Could not update review."
      );
    }
  };

  const getTenderScore = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!tenderId.trim()) return;
    setScoring(true);
    setScoreError(null);
    try {
      const result = await apiRequest<QualityScore>("/api/v1/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tender_id: tenderId.trim() }),
      });
      setScore(result);
    } catch (error) {
      setScoreError(error instanceof Error ? error.message : "Scoring failed.");
    } finally {
      setScoring(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#FBF8F4] text-[#211735]">
      <header className="border-b border-[#E7DDD7] bg-[#FBF8F4]">
        <div className="mx-auto flex h-[76px] max-w-[1200px] items-center justify-between px-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#A35A91]">MANAK</p>
            <h1 className="font-serif text-2xl">Operations</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-[#806D7B]">API: {backendStatus}</span>
            <button
              type="button"
              onClick={() => void loadOperationsData()}
              disabled={loading}
              className="rounded-lg border border-[#DED2CE] bg-white px-4 py-2 text-sm disabled:opacity-50"
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
            <Link href="/" className="text-sm text-[#74478A]">Home</Link>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-[1200px] space-y-12 px-6 py-10">
        <section>
          <h2 className="font-serif text-2xl">Tender quality score</h2>
          <p className="mt-2 text-sm text-[#706578]">Score a tender by its ID.</p>
          <form onSubmit={getTenderScore} className="mt-4 flex max-w-xl gap-3">
            <input
              value={tenderId}
              onChange={(event) => setTenderId(event.target.value)}
              placeholder="Tender ID"
              aria-label="Tender ID"
              className="min-w-0 flex-1 rounded-lg border border-[#DCCBCF] bg-white px-4 py-3 text-sm"
            />
            <button
              type="submit"
              disabled={scoring || !tenderId.trim()}
              className="rounded-lg bg-[#74478A] px-5 py-3 text-sm text-white disabled:opacity-50"
            >
              {scoring ? "Scoring..." : "Get score"}
            </button>
          </form>
          {scoreError && <p role="alert" className="mt-3 text-sm text-[#A55E65]">{scoreError}</p>}
          {score && (
            <div className="mt-5 rounded-xl border border-[#E4DAD5] bg-white p-5">
              <p className="text-sm text-[#806D7B]">{score.tender_id} · {score.verdict}</p>
              <p className="mt-2 font-serif text-4xl text-[#74478A]">{score.score}/100</p>
              {score.critical_alerts.map((alert, index) => (
                <p key={`${alert.type}-${index}`} className="mt-3 text-sm text-[#493D50]">
                  {alert.severity.toUpperCase()}: {alert.message}
                </p>
              ))}
              <p className="mt-3 text-xs text-[#A3989D]">This endpoint currently uses the backend mock scoring service.</p>
            </div>
          )}
        </section>

        <section>
          <h2 className="font-serif text-2xl">Uploaded documents</h2>
          {documentsError && <p role="alert" className="mt-3 text-sm text-[#A55E65]">{documentsError}</p>}
          <div className="mt-4 divide-y divide-[#EEE7E2] border-y border-[#E4DAD5]">
            {documents.map((document) => (
              <article key={document.document_id} className="flex flex-col justify-between gap-2 py-4 sm:flex-row sm:items-center">
                <div>
                  <p className="font-medium">{document.filename}</p>
                  <p className="mt-1 text-xs text-[#806D7B]">{document.bucket}/{document.object_name}</p>
                </div>
                <span className="text-xs text-[#806D7B]">{document.parse_status} · {new Date(document.created_at).toLocaleString()}</span>
              </article>
            ))}
            {!loading && !documentsError && documents.length === 0 && (
              <p className="py-5 text-sm text-[#806D7B]">No documents have been uploaded.</p>
            )}
          </div>
        </section>

        <section>
          <h2 className="font-serif text-2xl">Review queue</h2>
          {reviewsError && <p role="alert" className="mt-3 text-sm text-[#A55E65]">{reviewsError}</p>}
          <div className="mt-4 divide-y divide-[#EEE7E2] border-y border-[#E4DAD5]">
            {reviews.map((review) => (
              <article key={review.id} className="flex flex-col justify-between gap-4 py-4 sm:flex-row sm:items-center">
                <div>
                  <p className="font-medium">{review.document_name}</p>
                  <p className="mt-1 text-xs text-[#806D7B]">{review.status}{review.submitted_by ? ` · submitted by ${review.submitted_by}` : ""}</p>
                  {review.review_notes && <p className="mt-1 text-sm text-[#806D7B]">{review.review_notes}</p>}
                </div>
                {review.status === "pending" && (
                  <div className="flex gap-2">
                    <button type="button" onClick={() => void updateReview(review.id, "approve")} className="rounded-lg bg-[#EAF3E9] px-4 py-2 text-sm text-[#426B46]">Approve</button>
                    <button type="button" onClick={() => void updateReview(review.id, "reject")} className="rounded-lg bg-[#F8E9E8] px-4 py-2 text-sm text-[#A55E65]">Reject</button>
                  </div>
                )}
              </article>
            ))}
            {!loading && !reviewsError && reviews.length === 0 && (
              <p className="py-5 text-sm text-[#806D7B]">The review queue is empty.</p>
            )}
          </div>
        </section>

        <section>
          <h2 className="font-serif text-2xl">Audit log</h2>
          {auditError && <p role="alert" className="mt-3 text-sm text-[#A55E65]">{auditError}</p>}
          <div className="mt-4 divide-y divide-[#EEE7E2] border-y border-[#E4DAD5]">
            {auditLogs.map((entry) => (
              <article key={entry.id} className="py-4">
                <p className="font-medium">{entry.action} <span className="font-normal text-[#806D7B]">· {entry.user_id ?? "Unknown user"}</span></p>
                <p className="mt-1 text-sm text-[#706578]">{entry.details}</p>
                <p className="mt-1 text-xs text-[#A3989D]">{new Date(entry.created_at).toLocaleString()}</p>
              </article>
            ))}
            {!loading && !auditError && auditLogs.length === 0 && (
              <p className="py-5 text-sm text-[#806D7B]">No audit entries are available.</p>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}