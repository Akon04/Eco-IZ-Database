"use client";

import { useDeferredValue, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { HabitDetailPanel } from "@/components/habits/habit-detail-panel";
import { HabitMetricsCards } from "@/components/habits/habit-metrics";
import { HabitTable } from "@/components/habits/habit-table";
import { StatePanel } from "@/components/state-panel";
import { getHabitMetrics, listHabits } from "@/lib/api/habits";
import { queryKeys } from "@/lib/query-keys";
import type { Habit, HabitFilters, HabitMetrics } from "@/lib/types";

type HabitsWorkspaceProps = {
  initialHabits: Habit[];
  metrics: HabitMetrics;
};

export function HabitsWorkspace({
  initialHabits,
  metrics,
}: HabitsWorkspaceProps) {
  const [filters, setFilters] = useState<HabitFilters>({
    search: "",
    category: "ALL",
  });
  const [selectedHabitId, setSelectedHabitId] = useState(
    initialHabits[0]?.id ?? "",
  );
  const deferredSearch = useDeferredValue(filters.search ?? "");
  const queryFilters = useMemo(
    () => ({ ...filters, search: deferredSearch }),
    [deferredSearch, filters],
  );
  const filtersKey = JSON.stringify(queryFilters);

  const habitsQuery = useQuery({
    queryKey: queryKeys.habits.list(filtersKey),
    queryFn: () => listHabits(queryFilters),
    initialData: initialHabits,
  });

  const metricsQuery = useQuery({
    queryKey: queryKeys.habits.metrics,
    queryFn: getHabitMetrics,
    initialData: metrics,
  });

  const filteredHabits = habitsQuery.data;

  const categoryOptions = useMemo(() => {
    return Array.from(new Set(filteredHabits.map((habit) => habit.category))).sort();
  }, [filteredHabits]);

  const selectedHabit =
    filteredHabits.find((habit: Habit) => habit.id === selectedHabitId) ??
    filteredHabits[0];

  return (
    <>
      <HabitMetricsCards metrics={metricsQuery.data} />

      <section className="split" style={{ marginTop: 16 }}>
        <HabitTable
          habits={filteredHabits}
          selectedHabitId={selectedHabit?.id ?? ""}
          filters={filters}
          categoryOptions={categoryOptions}
          onSelect={setSelectedHabitId}
          onFilterChange={setFilters}
        />
        {selectedHabit ? (
          <HabitDetailPanel
            habit={selectedHabit}
            categoryOptions={categoryOptions}
          />
        ) : habitsQuery.isLoading ? (
          <StatePanel
            title="Loading habits"
            description="Refreshing the current habit catalog and eco values."
          />
        ) : habitsQuery.isError ? (
          <StatePanel
            title="Failed to load habits"
            description="The habit catalog could not be loaded. Try refreshing the page."
            tone="error"
          />
        ) : (
          <StatePanel
            title="No habits found"
            description="Clear the search or reset the category filter to browse the full habit catalog."
            tone="warning"
          />
        )}
      </section>
    </>
  );
}
