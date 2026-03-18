export type UserRole = "USER" | "ADMIN" | "MODERATOR";
export type UserStatus = "ACTIVE" | "REVIEW" | "SUSPENDED";
export type AdminAppRole = "ADMIN" | "MODERATOR";

export type AdminUser = {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  isEmailVerified: boolean;
  ecoPoints: number;
  streakDays: number;
  postsCount: number;
  createdAt: string;
  status: UserStatus;
};

export type UserFilters = {
  role?: UserRole | "ALL";
  status?: UserStatus | "ALL";
  search?: string;
};

export type UpdateAdminUserPayload = {
  role: UserRole;
  status: UserStatus;
  adminNote: string;
};

export type UserMetrics = {
  totalUsers: number;
  adminCount: number;
  needsReview: number;
  verifiedCount: number;
};

export type EcoCategory = {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
};

export type CategoryFilters = {
  search?: string;
};

export type UpdateCategoryPayload = {
  name: string;
  description: string;
  color: string;
  icon: string;
};

export type CategoryMetrics = {
  totalCategories: number;
  uniqueColors: number;
  iconCount: number;
};

export type Habit = {
  id: string;
  title: string;
  category: string;
  points: number;
  co2Value: number;
  waterValue: number;
  energyValue: number;
};

export type HabitFilters = {
  search?: string;
  category?: string | "ALL";
};

export type UpdateHabitPayload = {
  title: string;
  category: string;
  points: number;
  co2Value: number;
  waterValue: number;
  energyValue: number;
};

export type HabitMetrics = {
  totalHabits: number;
  totalPoints: number;
  categoriesUsed: number;
};

export type Achievement = {
  id: string;
  title: string;
  description: string;
  icon: string;
  targetValue: number;
  rewardPoints: number;
};

export type AchievementFilters = {
  search?: string;
};

export type UpdateAchievementPayload = {
  title: string;
  description: string;
  icon: string;
  targetValue: number;
  rewardPoints: number;
};

export type AchievementMetrics = {
  totalAchievements: number;
  totalRewardPoints: number;
  maxTargetValue: number;
};

export type CommunityPost = {
  id: string;
  author: string;
  content: string;
  visibility: "PUBLIC" | "FOLLOWERS" | "PRIVATE";
  state: "Published" | "Flagged" | "Needs review" | "Hidden";
  reportsCount: number;
  createdAt: string;
};

export type PostFilters = {
  search?: string;
  state?: CommunityPost["state"] | "ALL";
  visibility?: CommunityPost["visibility"] | "ALL";
};

export type UpdatePostPayload = {
  visibility: CommunityPost["visibility"];
  state: CommunityPost["state"];
  moderatorNote: string;
};

export type PostMetrics = {
  totalPosts: number;
  flaggedPosts: number;
  hiddenPosts: number;
  totalReports: number;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type AuthAdmin = {
  id: string;
  email: string;
  username: string;
  role: AdminAppRole;
};

export type AuthSession = {
  token: string;
  user: AuthAdmin;
};
