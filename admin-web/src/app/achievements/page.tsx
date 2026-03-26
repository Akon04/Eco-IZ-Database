import { PageHeader } from "@/components/page-header";
import { AchievementsWorkspace } from "@/components/achievements/achievements-workspace";
import {
  getAchievementMetrics,
  listAchievements,
} from "@/lib/api/achievements";
import { isMockMode } from "@/lib/config";

export default async function AchievementsPage() {
  const [achievements, metrics] = isMockMode()
    ? await Promise.all([listAchievements(), getAchievementMetrics()])
    : await Promise.all([
        Promise.resolve([]),
        Promise.resolve({
          totalAchievements: 0,
          totalRewardPoints: 0,
          maxTargetValue: 0,
        }),
      ]);

  return (
    <>
      <PageHeader
        title="Achievements"
        description="Configure milestones, target values, and reward points."
      />
      <AchievementsWorkspace
        initialAchievements={achievements}
        metrics={metrics}
      />
    </>
  );
}
