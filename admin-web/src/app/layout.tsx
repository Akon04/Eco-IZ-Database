import type { Metadata } from "next";

import { AppFrame } from "@/components/app-frame";
import { AuthProvider } from "@/components/auth-provider";
import { AppQueryProvider } from "@/components/query-provider";
import { ToastProvider } from "@/components/toast-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "ECOIZ Admin",
  description: "Admin panel for ECOIZ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppQueryProvider>
          <ToastProvider>
            <AuthProvider>
              <AppFrame>{children}</AppFrame>
            </AuthProvider>
          </ToastProvider>
        </AppQueryProvider>
      </body>
    </html>
  );
}
