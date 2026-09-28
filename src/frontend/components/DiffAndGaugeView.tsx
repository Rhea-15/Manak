'use client';

import React from 'react';

type DiffAndGaugeProps = {
  score?: number | null;
  tenderSpec?: string;
  verifiedSpec?: string;
};

export default function DiffAndGaugeView({
  score = 0,
  tenderSpec = 'No tender requirement provided.',
  verifiedSpec = 'Standard requirements verified by Rules Engine.',
}: DiffAndGaugeProps) {
  const currentScore = Math.round(score ?? 0);
  const label = currentScore >= 80 ? 'Compliant' : currentScore >= 50 ? 'Needs Review' : 'High Risk';
  const strokeColor = currentScore >= 80 ? '#10B981' : currentScore >= 50 ? '#F59E0B' : '#EF4444';

  return (
    <div className="flex flex-col gap-6">
      {/* Compliance Overview Gauge Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[#A35A91] mb-2">
          Calculated Tender Compliance Score
        </h3>
        <div
          className="w-32 h-32 rounded-full border-8 flex flex-col items-center justify-center my-3 transition-colors duration-500"
          style={{ borderColor: strokeColor }}
        >
          <span className="text-3xl font-extrabold text-slate-800">{currentScore}%</span>
          <span className="text-xs font-medium text-slate-500">{label}</span>
        </div>
        <p className="text-xs text-[#806D7B]">Mathematical risk score generated from verified database records.</p>
      </div>

      {/* Specification Comparison Diffs */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[#A35A91] mb-3">
          Live Specification Diff
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs p-4 bg-slate-900 text-slate-100 rounded-xl overflow-x-auto">
          <div>
            <p className="text-amber-400 font-bold mb-2">// Tender Requirement (Extracted)</p>
            <pre className="whitespace-pre-wrap leading-relaxed text-slate-300">{tenderSpec}</pre>
          </div>
          <div className="border-t border-slate-700 md:border-t-0 md:border-l md:pl-4 pt-4 md:pt-0">
            <p className="text-emerald-400 font-bold mb-2">// Verified Indian Standard Specification</p>
            <pre className="whitespace-pre-wrap leading-relaxed text-emerald-300">{verifiedSpec}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}