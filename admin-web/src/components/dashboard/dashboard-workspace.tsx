"use client";

import { useQuery } from "@tanstack/react-query";

import { MetricCards } from "@/components/metric-cards";
import { StatePanel } from "@/components/state-panel";
import { getAchievementMetrics, listAchievements } from "@/lib/api/achievements";
import { getCategoryMetrics } from "@/lib/api/categories";
import { isMockMode } from "@/lib/config";
import { getHabitMetrics } from "@/lib/api/habits";
import { getPostMetrics, listPosts } from "@/lib/api/posts";
import { queryKeys } from "@/lib/query-keys";
import { getAdminUserMetrics, listAdminUsers } from "@/lib/api/users";
import type {
  Achievement,
  AchievementMetrics,
  CommunityPost,
  PostMetrics,
  UserMetrics,
} from "@/lib/types";

type DashboardWorkspaceProps = {
  initialUserMetrics: UserMetrics;
  initialHabitMetrics: {
    totalHabits: number;
    totalPoints: number;
    categoriesUsed: number;
  };
  initialAchievementMetrics: AchievementMetrics;
  initialPostMetrics: PostMetrics;
  initialCategoryMetrics: {
    totalCategories: number;
    uniqueColors: number;
    iconCount: number;
  };
  initialPosts: CommunityPost[];
  initialUsers: Array<{
    id: string;
    username: string;
    email: string;
    role: "USER" | "ADMIN" | "MODERATOR";
    isEmailVerified: boolean;
    ecoPoints: number;
    streakDays: number;
    postsCount: number;
    createdAt: string;
    status: "ACTIVE" | "REVIEW" | "SUSPENDED";
  }>;
  initialAchievements: Achievement[];
};

export function DashboardWorkspace({
  initialUserMetrics,
  initialHabitMetrics,
  initialAchievementMetrics,
  initialPostMetrics,
  initialCategoryMetrics,
  initialPosts,
  initialUsers,
  initialAchievements,
}: DashboardWorkspaceProps) {
  const userMetricsQuery = useQuery({
    queryKey: queryKeys.users.metrics,
    queryFn: getAdminUserMetrics,
    initialData: initialUserMetrics,
  });

  const habitMetricsQuery = useQuery({
    queryKey: queryKeys.habits.metrics,
    queryFn: getHabitMetrics,
    initialData: initialHabitMetrics,
  });

  const achievementMetricsQuery = useQuery({
    queryKey: queryKeys.achievements.metrics,
    queryFn: getAchievementMetrics,
    initialData: initialAchievementMetrics,
  });

  const postMetricsQuery = useQuery({
    queryKey: queryKeys.posts.metrics,
    queryFn: getPostMetrics,
    initialData: initialPostMetrics,
  });

  const categoryMetricsQuery = useQuery({
    queryKey: queryKeys.categories.metrics,
    queryFn: getCategoryMetrics,
    initialData: initialCategoryMetrics,
  });

  const postsQuery = useQuery({
    queryKey: queryKeys.posts.list("dashboard"),
    queryFn: () => listPosts(),
    initialData: initialPosts,
    placeholderData: (previousData) => previousData,
  });

  const usersQuery = useQuery({
    queryKey: queryKeys.users.list("dashboard"),
    queryFn: () => listAdminUsers(),
    initialData: initialUsers,
    placeholderData: (previousData) => previousData,
  });

  const achievementsQuery = useQuery({
    queryKey: queryKeys.achievements.list("dashboard"),
    queryFn: () => listAchievements(),
    initialData: initialAchievements,
    placeholderData: (previousData) => previousData,
  });

  const hasError =
    userMetricsQuery.isError ||
    habitMetricsQuery.isError ||
    achievementMetricsQuery.isError ||
    postMetricsQuery.isError ||
    categoryMetricsQuery.isError ||
    postsQuery.isError ||
    usersQuery.isError ||
    achievementsQuery.isError;

  if (hasError) {
    return (
      <StatePanel
        title="Failed to load dashboard"
        description="Some dashboard datasets could not be loaded. Try refreshing the page."
        tone="error"
      />
    );
  }

  const userMetrics = userMetricsQuery.data;
  const habitMetrics = habitMetricsQuery.data;
  const achievementMetrics = achievementMetricsQuery.data;
  const postMetrics = postMetricsQuery.data;
  const categoryMetrics = categoryMetricsQuery.data;
  const posts = postsQuery.data;
  const users = usersQuery.data;
  const achievements = achievementsQuery.data;

  const isBootstrappingLiveDashboard =
    !isMockMode() &&
    (userMetricsQuery.isFetching ||
      habitMetricsQuery.isFetching ||
      achievementMetricsQuery.isFetching ||
      postMetricsQuery.isFetching ||
      categoryMetricsQuery.isFetching ||
      postsQuery.isFetching ||
      usersQuery.isFetching ||
      achievementsQuery.isFetching) &&
    userMetrics.totalUsers === 0 &&
    habitMetrics.totalHabits === 0 &&
    achievementMetrics.totalAchievements === 0 &&
    postMetrics.totalPosts === 0 &&
    categoryMetrics.totalCategories === 0 &&
    posts.length === 0 &&
    users.length === 0 &&
    achievements.length === 0;

  if (isBootstrappingLiveDashboard) {
    return (
      <StatePanel
        title="Loading dashboard"
        description="Fetching live admin metrics, catalog data, and moderation state."
      />
    );
  }

  const topMetrics = [
    {
      label: "Registered users",
      value: String(userMetrics.totalUsers),
      note: `${userMetrics.verifiedCount} verified, ${userMetrics.needsReview} need review`,
    },
    {
      label: "Habit catalog",
      value: String(habitMetrics.totalHabits),
      note: `${habitMetrics.categoriesUsed} categories, ${habitMetrics.totalPoints} total points`,
    },
    {
      label: "Posts to review",
      value: String(
        postMetrics.flaggedPosts + users.filter((u) => u.status === "REVIEW").length,
      ),
      note: `${postMetrics.flaggedPosts} flagged posts, ${postMetrics.totalReports} total reports`,
    },
    {
      label: "Achievements",
      value: String(achievementMetrics.totalAchievements),
      note: `${achievementMetrics.totalRewardPoints} reward points across catalog`,
    },
  ];

  const moderationQueue = posts
    .filter((post) => post.state === "Flagged" || post.state === "Needs review")
    .map((post) => ({
      label: `Post by ${post.author}`,
      status: post.state,
      owner: "Moderator",
    }));

  const operationsQueue = [
    {
      label: "User accounts pending review",
      status: `${userMetrics.needsReview} pending`,
      owner: "Admin",
    },
    {
      label: "Category catalog status",
      status: `${categoryMetrics.totalCategories} active`,
      owner: "Content",
    },
    {
      label: "Achievement catalog status",
      status: `${achievements.length} configured`,
      owner: "Product",
    },
  ];

  const recentItems = [
    `${postMetrics.flaggedPosts} posts are currently flagged for moderation`,
    `${userMetrics.adminCount} admins and moderators have elevated access`,
    `${habitMetrics.totalHabits} habits are available in the catalog`,
    `${achievementMetrics.maxTargetValue} is the current highest achievement target`,
  ];

  return (
    <>
      <MetricCards items={topMetrics} columns="four" />

      <section className="split" style={{ marginTop: 16 }}>
        <article className="card">
          <h2 className="section-title">Priority Today</h2>
          <p className="muted">
            Start with moderation, then review admin-controlled catalog changes
            across habits, categories, and achievements.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Queue</th>
                  <th>Status</th>
                  <th>Owner</th>
                </tr>
              </thead>
              <tbody>
                {[...moderationQueue, ...operationsQueue].map((item) => (
                  <tr key={`${item.label}-${item.status}`}>
                    <td>{item.label}</td>
                    <td>
                      <span className="pill">{item.status}</span>
                    </td>
                    <td>{item.owner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="card">
          <h2 className="section-title">Operational snapshot</h2>
          <div className="grid">
            {recentItems.map((item) => (
              <div key={item} className="card" style={{ padding: 14 }}>
                {item}
              </div>
            ))}
          </div>
        </article>
      </section>
    </>
  );
}
