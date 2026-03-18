"use client";

import { useEffect } from "react";

import { StatePanel } from "@/components/state-panel";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="auth-shell">
      <div className="grid" style={{ width: "min(100%, 560px)" }}>
        <StatePanel
          title="Something went wrong"
          description="The admin workspace failed to render this page. Try loading it again."
          tone="error"
        />
        <button type="button" className="primary-button" onClick={reset}>
          Try again
        </button>
      </div>
    </div>
  );
}
