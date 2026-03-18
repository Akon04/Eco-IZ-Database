import { StatePanel } from "@/components/state-panel";

export default function Loading() {
  return (
    <div className="auth-shell">
      <StatePanel
        title="Loading admin workspace"
        description="Preparing dashboard data and restoring the current session."
      />
    </div>
  );
}
