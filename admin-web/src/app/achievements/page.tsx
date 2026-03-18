import { PageHeader } from "@/components/page-header";
import { AchievementsWorkspace } from "@/components/achievements/achievements-workspace";
import {
  getAchievementMetrics,
  listAchievements,
} from "@/lib/api/achievements";

export default async function AchievementsPage() {
  const [achievements, metrics] = await Promise.all([
    listAchievements(),
    getAchievementMetrics(),
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
