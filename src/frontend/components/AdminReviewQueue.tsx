"use client";

import { CheckCircle2, XCircle, Clock } from "lucide-react";
import { mockReviewQueue } from "../app/mocks/auditLog";

export default function AdminReviewQueue() {
  return (
    <div>
      <h2 className="mb-4 text-xl font-bold text-slate-800">
  Pending Review Queue
</h2>
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-[#FBF7F1]">
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Item
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Submitted By
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Status
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {mockReviewQueue.map((item) => (
              <tr key={item.id} className="border-b border-slate-200 last:border-b-0">
                <td className="px-6 py-4 text-slate-800">{item.itemName}</td>
                <td className="px-6 py-4 text-slate-600">{item.submittedBy}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
                    <Clock size={14} /> {item.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button className="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 transition hover:bg-emerald-100">
                      <CheckCircle2 size={14} /> Approve
                    </button>
                    <button className="flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-medium text-rose-700 transition hover:bg-rose-100">
                      <XCircle size={14} /> Reject
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}