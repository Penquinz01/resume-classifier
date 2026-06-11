"use client";

/**
 * Navbar — minimal top navigation inspired by Linear/Vercel.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Upload" },
  { href: "/history", label: "History" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link href="/" className="navbar-brand">
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="navbar-logo"
          >
            <rect width="20" height="20" rx="4" fill="currentColor" />
            <path
              d="M6 14V6h2.5c1.38 0 2.5 1.12 2.5 2.5S9.88 11 8.5 11H8v3H6zm2-5h.5c.28 0 .5-.22.5-.5S8.78 8 8.5 8H8v1zm4 5V6h2.5c.83 0 1.5.67 1.5 1.5 0 .53-.28 1-.7 1.27.57.2 1 .77 1 1.43 0 .93-.67 1.8-1.8 1.8H12zm2-5h.3c.17 0 .2-.11.2-.25s-.03-.25-.2-.25H14v.5zm0 2.5h.5c.28 0 .5-.11.5-.25s-.22-.25-.5-.25H14v.5z"
              fill="#0D0D0D"
            />
          </svg>
          <span>Resume Classifier</span>
        </Link>

        <nav className="navbar-nav">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`navbar-link ${isActive ? "navbar-link-active" : ""}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
