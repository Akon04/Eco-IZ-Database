import { DashboardWorkspace } from "@/components/dashboard/dashboard-workspace";
import { PageHeader } from "@/components/page-header";
import { getAchievementMetrics, listAchievements } from "@/lib/api/achievements";
import { getCategoryMetrics } from "@/lib/api/categories";
import { isMockMode } from "@/lib/config";
import { getHabitMetrics } from "@/lib/api/habits";
import { getPostMetrics, listPosts } from "@/lib/api/posts";
import { getAdminUserMetrics, listAdminUsers } from "@/lib/api/users";

export default async function DashboardPage() {
  const [
    userMetrics,
    habitMetrics,
    achievementMetrics,
    postMetrics,
    categoryMetrics,
    posts,
    users,
    achievements,
  ] = isMockMode()
    ? await Promise.all([
        getAdminUserMetrics(),
        getHabitMetrics(),
        getAchievementMetrics(),
        getPostMetrics(),
        getCategoryMetrics(),
        listPosts(),
        listAdminUsers(),
        listAchievements(),
      ])
    : await Promise.all([
        Promise.resolve({
          totalUsers: 0,
          adminCount: 0,
          needsReview: 0,
          verifiedCount: 0,
        }),
        Promise.resolve({
          totalHabits: 0,
          totalPoints: 0,
          categoriesUsed: 0,
        }),
        Promise.resolve({
          totalAchievements: 0,
          totalRewardPoints: 0,
          maxTargetValue: 0,
        }),
        Promise.resolve({
          totalPosts: 0,
          flaggedPosts: 0,
          hiddenPosts: 0,
          totalReports: 0,
        }),
        Promise.resolve({
          totalCategories: 0,
          uniqueColors: 0,
          iconCount: 0,
        }),
        Promise.resolve([]),
        Promise.resolve([]),
        Promise.resolve([]),
      ]);

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Overview of platform health, moderation queue, and eco activity."
      />
      <DashboardWorkspace
        initialUserMetrics={userMetrics}
        initialHabitMetrics={habitMetrics}
        initialAchievementMetrics={achievementMetrics}
        initialPostMetrics={postMetrics}
        initialCategoryMetrics={categoryMetrics}
        initialPosts={posts}
        initialUsers={users}
        initialAchievements={achievements}
      />
    </>
  );
}
