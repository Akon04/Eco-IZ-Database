import { MetricCards } from "@/components/metric-cards";
import type { CategoryMetrics } from "@/lib/types";

type CategoryMetricsProps = {
  metrics: CategoryMetrics;
};

export function CategoryMetricsCards({ metrics }: CategoryMetricsProps) {
  const cards = [
    {
      label: "Total categories",
      value: metrics.totalCategories,
      note: "Current eco catalog sections",
    },
    {
      label: "Unique colors",
      value: metrics.uniqueColors,
      note: "Used for visual classification",
    },
    {
      label: "Active icons",
      value: metrics.iconCount,
      note: "Icon labels in the current mock set",
    },
  ];

  return <MetricCards items={cards} columns="three" />;
}
