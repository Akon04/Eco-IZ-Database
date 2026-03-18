import { MetricCards } from "@/components/metric-cards";
import type { PostMetrics } from "@/lib/types";

type PostMetricsProps = {
  metrics: PostMetrics;
};

export function PostMetricsCards({ metrics }: PostMetricsProps) {
  const cards = [
    {
      label: "Total posts",
      value: metrics.totalPosts,
      note: "Current moderation scope",
    },
    {
      label: "Flagged",
      value: metrics.flaggedPosts,
      note: "Need moderator attention first",
    },
    {
      label: "Hidden",
      value: metrics.hiddenPosts,
      note: "Already restricted from public view",
    },
    {
      label: "Reports",
      value: metrics.totalReports,
      note: "Total report count across current posts",
    },
  ];

  return <MetricCards items={cards} columns="four" />;
}
