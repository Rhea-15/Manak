"use client";

import AdminReviewQueue from "../../components/AdminReviewQueue";
import AuditLogView from "../../components/AuditLogView";

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-10 py-14">
      <p className="mb-2 text-xs font-medium uppercase tracking-[0.3em] text-purple-600">
        Governance
      </p>
    <h1 className="font-serif text-4xl font-bold text-slate-800">Admin Governance</h1>
      <p className="mt-3 max-w-xl text-sm text-slate-500">
        Review pending items and track every action taken on the platform.
      </p>

      <div className="mt-10">
        <AdminReviewQueue />
      </div>

      <div className="mt-10">
        <AuditLogView />
      </div>
    </main>
  );
}