"use client";

import { useReactTable, getCoreRowModel, flexRender, createColumnHelper } from '@tanstack/react-table';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

type BOQItem = {
  id: number;
  itemName: string;
  specification: string;
  quantity: number;
  unit: string;
  complianceStatus: string;
};

const columnHelper = createColumnHelper<BOQItem>();

const columns = [
  columnHelper.accessor('itemName', { header: 'Item' }),
  columnHelper.accessor('specification', { header: 'IS Spec' }),
  columnHelper.accessor('quantity', { header: 'Qty' }),
  columnHelper.accessor('unit', { header: 'Unit' }),
  columnHelper.accessor('complianceStatus', {
    header: 'Compliance',
    cell: (info) =>
      info.getValue() === 'compliant' ? (
        <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
          <CheckCircle2 size={14} /> Compliant
        </span>
      ) : (
        <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
          <AlertTriangle size={14} /> Flagged
        </span>
      ),
  }),
];

export default function BOQTable({ data }: { data: BOQItem[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
           <tr key={headerGroup.id} className="border-b border-slate-200 bg-[#FBF7F1]">
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-6 py-4 text-xs font-medium uppercase tracking-wide text-slate-500"
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-b border-slate-200 last:border-b-0">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-6 py-4 text-slate-800">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}