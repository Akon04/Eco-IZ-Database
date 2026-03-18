import { MetricCards } from "@/components/metric-cards";
import type { HabitMetrics } from "@/lib/types";

type HabitMetricsProps = {
  metrics: HabitMetrics;
};

export function HabitMetricsCards({ metrics }: HabitMetricsProps) {
  const cards = [
    {
      label: "Total habits",
      value: metrics.totalHabits,
      note: "Current catalog size",
    },
    {
      label: "Total points",
      value: metrics.totalPoints,
      note: "Points across the current mock catalog",
    },
    {
      label: "Categories used",
      value: metrics.categoriesUsed,
      note: "Habit distribution across eco domains",
    },
  ];

  return <MetricCards items={cards} columns="three" />;
}
