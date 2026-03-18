import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import { mockAchievements } from "@/lib/mocks";
import type {
  Achievement,
  AchievementFilters,
  AchievementMetrics,
  UpdateAchievementPayload,
} from "@/lib/types";

export async function listAchievements(
  filters: AchievementFilters = {},
): Promise<Achievement[]> {
  if (!isMockMode()) {
    const params = new URLSearchParams();
    if (filters.search?.trim()) params.set("search", filters.search.trim());

    return apiRequest<Achievement[]>(
      `/admin/achievements${params.size ? `?${params.toString()}` : ""}`,
    );
  }

  await wait(70);

  const query = filters.search?.trim().toLowerCase();
  return mockAchievements.filter((achievement) => {
    if (!query) return true;

    return (
      achievement.title.toLowerCase().includes(query) ||
      achievement.description.toLowerCase().includes(query) ||
      achievement.icon.toLowerCase().includes(query)
    );
  });
}

export async function getAchievementMetrics(): Promise<AchievementMetrics> {
  if (!isMockMode()) {
    return apiRequest<AchievementMetrics>("/admin/achievements/metrics");
  }

  await wait(40);

  return {
    totalAchievements: mockAchievements.length,
    totalRewardPoints: mockAchievements.reduce(
      (sum, achievement) => sum + achievement.rewardPoints,
      0,
    ),
    maxTargetValue: Math.max(...mockAchievements.map((item) => item.targetValue)),
  };
}

export async function updateAchievement(
  achievementId: string,
  payload: UpdateAchievementPayload,
): Promise<Achievement> {
  if (!isMockMode()) {
    return apiRequest<Achievement>(`/admin/achievements/${achievementId}`, {
      method: "PATCH",
      body: payload,
    });
  }

  await wait(120);

  const achievement = mockAchievements.find((item) => item.id === achievementId);
  if (!achievement) {
    throw new Error("Achievement not found");
  }

  return {
    ...achievement,
    ...payload,
  };
}
