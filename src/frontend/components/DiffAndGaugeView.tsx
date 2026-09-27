'use client';

import React from 'react';

const gaugeData = { score: 78, label: 'Compliant' };

const originalSpec = `{
  "grade": "M20",
  "minCement": "300 kg/m3",
  "maxWCRatio": 0.55
}`;

const verifiedSpec = `{
  "grade": "M25",
  "minCement": "320 kg/m3",
  "maxWCRatio": 0.50
}`;

export default function DiffAndGaugeView() {
  return (
    <div className="flex flex-col gap-6 p-4">
      {/* Compliance Overview Gauge Card matching Ananya's UI style */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center">
        <h3 className="text-lg font-bold text-slate-800 mb-2">Tender Compliance Overview</h3>
        <div className="w-32 h-32 rounded-full border-8 border-emerald-500 border-t-amber-400 flex flex-col items-center justify-center my-2">
          <span className="text-2xl font-extrabold text-slate-800">{gaugeData.score}%</span>
          <span className="text-xs text-slate-500">{gaugeData.label}</span>
        </div>
      </div>

      {/* Specification Diff Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 mb-3">Specification Comparison Diffs</h3>
        <div className="grid grid-cols-2 gap-4 font-mono text-xs p-4 bg-slate-900 text-slate-100 rounded-lg">
          <div>
            <p className="text-amber-400 font-bold mb-1">// Tender Requirement</p>
            <pre>{originalSpec}</pre>
          </div>
          <div>
            <p className="text-emerald-400 font-bold mb-1">// Verified IS Standard</p>
            <pre>{verifiedSpec}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}