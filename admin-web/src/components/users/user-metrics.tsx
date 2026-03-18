import { MetricCards } from "@/components/metric-cards";
import type { UserMetrics } from "@/lib/types";

type UserMetricsProps = {
  metrics: UserMetrics;
};

export function UserMetricsCards({ metrics }: UserMetricsProps) {
  const cards = [
    {
      label: "Total users",
      value: metrics.totalUsers,
      note: "Current mock directory size",
    },
    {
      label: "Admins",
      value: metrics.adminCount,
      note: "Users with full access",
    },
    {
      label: "Needs review",
      value: metrics.needsReview,
      note: "Accounts that require moderation",
    },
    {
      label: "Verified email",
      value: metrics.verifiedCount,
      note: "Ready for secure admin actions",
    },
  ];

  return <MetricCards items={cards} columns="four" />;
}
