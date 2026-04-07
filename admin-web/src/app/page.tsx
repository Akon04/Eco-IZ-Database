import { DashboardWorkspace } from "@/components/dashboard/dashboard-workspace";
import { PageHeader } from "@/components/page-header";
import { getAchievementMetrics, listAchievements } from "@/lib/api/achievements";
import { getEcoAnalytics } from "@/lib/api/dashboard";
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
    ecoAnalytics,
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
        getEcoAnalytics(),
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
          needsReviewPosts: 0,
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
        Promise.resolve({
          categoryBreakdown: [],
          topCategory: "",
          customActivitiesCount: 0,
          averageCo2PerActivity: 0,
          topUsersByActivity: [],
        }),
      ]);

  return (
    <>
      <PageHeader
        title="Панель"
        description="Общий обзор платформы, модерации и эко-активности."
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
        initialEcoAnalytics={ecoAnalytics}
      />
    </>
  );
}
