"use client";

import { useEffect, useState } from "react";

type AuditEntry = {
  id: number;
  user_id: string;
  action: string;
  details: string;
  created_at: string;
};

export default function AuditLogView() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/audit/logs", {
      headers: { "X-User-Role": "ADMIN" },
    })
      .then((res) => res.json())
      .then((data) => {
        setEntries(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load audit logs:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-slate-500">Loading audit log...</p>;

  return (
    <div>
      <h2 className="mb-4 text-xl font-bold text-slate-800">
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
            {entries.map((entry) => (
              <tr key={entry.id} className="border-b border-slate-200 last:border-b-0">
                <td className="px-6 py-4 text-slate-600">
                  {new Date(entry.created_at).toLocaleString('en-US', { timeZone: 'UTC' })}
                </td>
                <td className="px-6 py-4 text-slate-800">{entry.user_id}</td>
                <td className="px-6 py-4">
                  <span
                    className={
                      entry.action.includes("APPROVE")
                        ? "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700"
                        : "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700"
                    }
                  >
                    {entry.action}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-600">{entry.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}