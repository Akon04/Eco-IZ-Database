"use client";

import { useDeferredValue, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { AchievementDetailPanel } from "@/components/achievements/achievement-detail-panel";
import { AchievementMetricsCards } from "@/components/achievements/achievement-metrics";
import { AchievementTable } from "@/components/achievements/achievement-table";
import { StatePanel } from "@/components/state-panel";
import {
  getAchievementMetrics,
  listAchievements,
} from "@/lib/api/achievements";
import { queryKeys } from "@/lib/query-keys";
import type {
  Achievement,
  AchievementFilters,
  AchievementMetrics,
} from "@/lib/types";

type AchievementsWorkspaceProps = {
  initialAchievements: Achievement[];
  metrics: AchievementMetrics;
};

export function AchievementsWorkspace({
  initialAchievements,
  metrics,
}: AchievementsWorkspaceProps) {
  const [filters, setFilters] = useState<AchievementFilters>({ search: "" });
  const [selectedAchievementId, setSelectedAchievementId] = useState(
    initialAchievements[0]?.id ?? "",
  );
  const deferredSearch = useDeferredValue(filters.search ?? "");
  const queryFilters = useMemo(
    () => ({ ...filters, search: deferredSearch }),
    [deferredSearch, filters],
  );
  const filtersKey = JSON.stringify(queryFilters);

  const achievementsQuery = useQuery({
    queryKey: queryKeys.achievements.list(filtersKey),
    queryFn: () => listAchievements(queryFilters),
    initialData: initialAchievements,
    placeholderData: (previousData) => previousData,
  });

  const metricsQuery = useQuery({
    queryKey: queryKeys.achievements.metrics,
    queryFn: getAchievementMetrics,
    initialData: metrics,
  });

  const filteredAchievements = achievementsQuery.data;

  const selectedAchievement =
    filteredAchievements.find(
      (item: Achievement) => item.id === selectedAchievementId,
    ) ??
    filteredAchievements[0];

  return (
    <>
      <AchievementMetricsCards metrics={metricsQuery.data} />

      <section className="split" style={{ marginTop: 16 }}>
        <AchievementTable
          achievements={filteredAchievements}
          selectedAchievementId={selectedAchievement?.id ?? ""}
          filters={filters}
          onSelect={setSelectedAchievementId}
          onFilterChange={setFilters}
        />
        {selectedAchievement ? (
          <AchievementDetailPanel achievement={selectedAchievement} />
        ) : achievementsQuery.isLoading || achievementsQuery.isFetching ? (
          <StatePanel
            title="Loading achievements"
            description="Refreshing milestone configuration and applying your search."
          />
        ) : achievementsQuery.isError ? (
          <StatePanel
            title="Failed to load achievements"
            description="The achievement directory could not be loaded. Try refreshing the page."
            tone="error"
          />
        ) : (
          <StatePanel
            title="No achievements found"
            description="Clear the search term to return to the configured achievement catalog."
            tone="warning"
          />
        )}
      </section>
    </>
  );
}
