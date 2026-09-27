"use client";

import BOQTable from "../../components/BOQTable";
import { mockBOQItems } from "../mocks/boqItems";
import ExportButton from "../../components/ExportButton";

export default function BOQPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-10 py-14">
      <p className="mb-2 text-xs font-medium uppercase tracking-[0.3em] text-purple-600">
        Bill of Quantities
      </p>
     <h1 className="font-serif text-4xl font-bold text-slate-800">BOQ Items</h1>
      <p className="mt-3 max-w-xl text-sm text-slate-500">
        Review parsed line items and their compliance status before export.
      </p>

      <div className="mt-8">
        <BOQTable data={mockBOQItems} />
      </div>

      <div className="mt-6">
        <ExportButton data={mockBOQItems} />
      </div>
    </main>
  );
}