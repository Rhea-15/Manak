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
      <div className="bg-white p-7 rounded-[24px] border border-[#E4DAD5] shadow-sm">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[#A35A91] mb-4">
          Live Specification Diff
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-[13px]">
          
          {/* Left Side: Extracted Tender (Light Purple Theme) */}
          <div className="p-6 bg-[#FAF4FB] border border-[#E7D6E9] rounded-2xl">
            <p className="text-[#74478A] font-bold mb-3 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#A35A91]"></span>
              Tender Requirement (Extracted)
            </p>
            <pre className="whitespace-pre-wrap leading-relaxed text-[#4A3B54]">
              {tenderSpec}
            </pre>
          </div>

          {/* Right Side: Verified Standard (Light Green Theme) */}
          <div className="p-6 bg-[#F3F9F4] border border-[#CEE6D3] rounded-2xl">
            <p className="text-[#2F6D38] font-bold mb-3 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#52A360]"></span>
              Verified Indian Standard Specification
            </p>
            <pre className="whitespace-pre-wrap leading-relaxed text-[#213B26]">
              {verifiedSpec}
            </pre>
          </div>

        </div>
      </div>
    </div>
  );
}