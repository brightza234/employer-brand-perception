"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/themes", label: "Theme Breakdown" },
  { href: "/trend", label: "Trend" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-black/10 dark:border-white/10">
      <nav className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-4">
        <span className="font-semibold tracking-tight">Employer Brand Perception</span>
        <div className="flex gap-4 text-sm">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={
                pathname === link.href
                  ? "font-medium text-foreground"
                  : "text-foreground/60 hover:text-foreground"
              }
            >
              {link.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
