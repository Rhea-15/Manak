"use client";

import Link from "next/link";
import {
  LayoutDashboard,
  Upload,
  Search,
  Sparkles,
  Check,
  GitBranch,
  FileText,
  FolderOpen,
  ArrowUpRight,
} from "lucide-react";

const navigation = [
  {
    name: "Dashboard",
    icon: LayoutDashboard,
    href: "/",
  },
  {
    name: "Upload & Analyse",
    icon: Upload,
    href: "/upload",
  },
  {
    name: "Standards Search",
    icon: Search,
    href: "/search",
  },
  {
    name: "AI Recommendations",
    icon: Sparkles,
    href: "/recommendations",
  },
  {
    name: "Compliance Check",
    icon: Check,
    href: "/compliance",
  },
  {
    name: "Related Standards",
    icon: GitBranch,
    href: "/search",
  },
  {
    name: "Reports",
    icon: FileText,
    href: "/compliance",
  },
  {
    name: "My Workspace",
    icon: FolderOpen,
    href: "/compliance",
  },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-[250px] flex-col border-r border-[#5E3A70] bg-[#74478A] text-white lg:flex">

      {/* Logo */}
      <div className="flex h-[100px] items-center border-b border-white/10 px-7">

        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-full border border-[#E8B7A9] bg-[#D9978A] text-sm font-medium text-[#3C2345]">
            M
          </div>

          <div>
            <h1 className="font-serif text-xl tracking-wide">
              MANAK
            </h1>

            <p className="text-[8px] uppercase tracking-[0.2em] text-white/60">
              AI for Smarter Procurement
            </p>
          </div>

        </div>

      </div>


      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-4 py-7">

        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className="group flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-white/70 transition-all duration-200 hover:bg-white/10 hover:text-white"
            >

              <Icon
                size={18}
                strokeWidth={1.7}
                className="transition-transform group-hover:scale-105"
              />

              <span>{item.name}</span>

            </Link>
          );
        })}

      </nav>


      {/* Bottom info */}
      <div className="border-t border-white/10 p-5">

        <div className="mb-5 rounded-xl bg-white/10 p-4">

          <div className="mb-2 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[#E8B7A9]" />

            <span className="text-xs font-medium text-white">
              BIS Standards
            </span>
          </div>

          <p className="text-[11px] leading-5 text-white/55">
            Explore Indian Standards and keep procurement specifications compliant.
          </p>

          <button className="mt-3 flex items-center gap-1 text-[11px] text-[#F5DDA5]">
            Explore BIS Portal
            <ArrowUpRight size={12} />
          </button>

        </div>


        <div className="px-2 pb-2">

          <p className="text-[10px] uppercase tracking-[0.2em] text-white/40">
            MANAK v1.0
          </p>

          <p className="mt-1 text-[10px] text-white/40">
            Built for transparent procurement
          </p>

        </div>

      </div>

    </aside>
  );
}