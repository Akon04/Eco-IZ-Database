"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/components/auth-provider";
import { Sidebar } from "@/components/sidebar";
import { StatePanel } from "@/components/state-panel";

type AppFrameProps = {
  children: React.ReactNode;
};

export function AppFrame({ children }: AppFrameProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const isLoginPage = pathname === "/login";

  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (!isAuthenticated && !isLoginPage) {
      router.replace("/login");
      return;
    }

    if (isAuthenticated && isLoginPage) {
      router.replace("/");
    }
  }, [isAuthenticated, isLoading, isLoginPage, router]);

  if (isLoading) {
    return (
      <div className="auth-shell">
        <StatePanel
          title="Loading admin session"
          description="Checking saved login and access level."
        />
      </div>
    );
  }

  if (!isAuthenticated && !isLoginPage) {
    return null;
  }

  if (isLoginPage) {
    return <main>{children}</main>;
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="content">{children}</main>
    </div>
  );
}
