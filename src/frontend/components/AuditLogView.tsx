"use client";

import { mockAuditLog } from "../app/mocks/auditLog";

export default function AuditLogView() {
  return (
    <div>
      <h2 className="mb-4 font-serif text-2xl font-bold text-slate-800">
  Audit Log
</h2>
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-[#FBF7F1]">
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Timestamp
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Actor
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Action
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500">
                Target
              </th>
            </tr>
          </thead>
          <tbody>
            {mockAuditLog.map((entry) => (
              <tr key={entry.id} className="border-b border-slate-200 last:border-b-0">
                <td className="px-6 py-4 text-slate-600">
                  {new Date(entry.timestamp).toLocaleString('en-US', { timeZone: 'UTC' })}
                </td>
                <td className="px-6 py-4 text-slate-800">{entry.actor}</td>
                <td className="px-6 py-4">
                  <span
                    className={
                      entry.action === "APPROVED"
                        ? "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700"
                        : "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700"
                    }
                  >
                    {entry.action}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-600">{entry.target}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}