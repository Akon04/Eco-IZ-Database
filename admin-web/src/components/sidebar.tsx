"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/components/auth-provider";
import { navigation } from "@/lib/navigation";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <aside className="sidebar">
      <h1 className="brand">
        ECO<span>IZ</span>
      </h1>
      <p className="sidebar-note">
        Admin workspace for moderation, eco catalog management, and platform
        analytics.
      </p>
      <nav className="nav-list" aria-label="Admin navigation">
        {navigation.map((item) => {
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <strong>{user?.username}</strong>
          <span className="muted">
            {user?.role} · {user?.email}
          </span>
        </div>
        <button type="button" className="ghost-button sidebar-button" onClick={handleLogout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
