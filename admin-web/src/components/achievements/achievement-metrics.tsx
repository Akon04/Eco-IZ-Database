import { MetricCards } from "@/components/metric-cards";
import type { AchievementMetrics } from "@/lib/types";

type AchievementMetricsProps = {
  metrics: AchievementMetrics;
};

export function AchievementMetricsCards({
  metrics,
}: AchievementMetricsProps) {
  const cards = [
    {
      label: "Total achievements",
      value: metrics.totalAchievements,
      note: "Current milestone catalog",
    },
    {
      label: "Reward points",
      value: metrics.totalRewardPoints,
      note: "Combined reward budget in mock data",
    },
    {
      label: "Max target",
      value: metrics.maxTargetValue,
      note: "Highest completion threshold",
    },
  ];

  return <MetricCards items={cards} columns="three" />;
}
