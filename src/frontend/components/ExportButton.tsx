"use client";

import { saveAs } from "file-saver";

type BOQItem = {
  id: number;
  itemName: string;
  specification: string;
  quantity: number;
  unit: string;
  complianceStatus: string;
};

export default function ExportButton({ data }: { data: BOQItem[] }) {
  function handleExport() {
    const headers = ["Item", "Specification", "Quantity", "Unit", "Compliance"];
    const rows = data.map((item) => [
      item.itemName,
      item.specification,
      item.quantity,
      item.unit,
      item.complianceStatus,
    ]);

    const csvContent = [headers, ...rows]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8" });
    saveAs(blob, `tender_export_${Date.now()}.csv`);
  }

    return (
    <button
      onClick={handleExport}
           className="flex items-center gap-2 rounded-xl bg-[#75468b] px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-[#653b78]"
    >
      Export to GeM/CPPP (CSV)
    </button>
  );
}