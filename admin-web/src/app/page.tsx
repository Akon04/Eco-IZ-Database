import { DashboardWorkspace } from "@/components/dashboard/dashboard-workspace";
import { PageHeader } from "@/components/page-header";
import { getAchievementMetrics, listAchievements } from "@/lib/api/achievements";
import { getCategoryMetrics } from "@/lib/api/categories";
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
  ] = await Promise.all([
    getAdminUserMetrics(),
    getHabitMetrics(),
    getAchievementMetrics(),
    getPostMetrics(),
    getCategoryMetrics(),
    listPosts(),
    listAdminUsers(),
    listAchievements(),
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
