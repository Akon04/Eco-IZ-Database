import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import type { EcoAnalytics } from "@/lib/types";

const mockEcoAnalytics: EcoAnalytics = {
  categoryBreakdown: [
    { category: "Транспорт", count: 12, co2Saved: 8.4 },
    { category: "Вода", count: 7, co2Saved: 1.2 },
    { category: "Пластик", count: 9, co2Saved: 2.1 },
    { category: "Отходы", count: 5, co2Saved: 1.7 },
    { category: "Энергия", count: 6, co2Saved: 3.3 },
  ],
  topCategory: "Транспорт",
  customActivitiesCount: 4,
  averageCo2PerActivity: 0.72,
  topUsersByActivity: [
    { userId: "user-1", username: "akniyet", activitiesCount: 14, ecoPoints: 220, co2Saved: 7.4 },
    { userId: "user-2", username: "akerke", activitiesCount: 11, ecoPoints: 180, co2Saved: 5.1 },
    { userId: "user-3", username: "nurdana", activitiesCount: 9, ecoPoints: 146, co2Saved: 4.3 },
  ],
};

export async function getEcoAnalytics(): Promise<EcoAnalytics> {
  if (!isMockMode()) {
    return apiRequest<EcoAnalytics>("/admin/dashboard/eco-analytics");
  }

  await wait(60);
  return mockEcoAnalytics;
}
