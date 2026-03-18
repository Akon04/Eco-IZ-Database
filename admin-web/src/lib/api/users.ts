import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import { mockUsers } from "@/lib/mocks";
import type {
  AdminUser,
  UpdateAdminUserPayload,
  UserFilters,
  UserMetrics,
} from "@/lib/types";

export async function listAdminUsers(
  filters: UserFilters = {},
): Promise<AdminUser[]> {
  if (!isMockMode()) {
    const params = new URLSearchParams();
    if (filters.role && filters.role !== "ALL") params.set("role", filters.role);
    if (filters.status && filters.status !== "ALL") {
      params.set("status", filters.status);
    }
    if (filters.search?.trim()) params.set("search", filters.search.trim());

    return apiRequest<AdminUser[]>(
      `/admin/users${params.size ? `?${params.toString()}` : ""}`,
    );
  }

  await wait(80);

  return mockUsers.filter((user) => {
    const matchesRole =
      !filters.role || filters.role === "ALL" || user.role === filters.role;
    const matchesStatus =
      !filters.status ||
      filters.status === "ALL" ||
      user.status === filters.status;
    const query = filters.search?.trim().toLowerCase();
    const matchesSearch =
      !query ||
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query);

    return matchesRole && matchesStatus && matchesSearch;
  });
}

export async function getAdminUserMetrics(): Promise<UserMetrics> {
  if (!isMockMode()) {
    return apiRequest<UserMetrics>("/admin/users/metrics");
  }

  await wait(40);

  return {
    totalUsers: mockUsers.length,
    adminCount: mockUsers.filter((user) => user.role === "ADMIN").length,
    needsReview: mockUsers.filter((user) => user.status === "REVIEW").length,
    verifiedCount: mockUsers.filter((user) => user.isEmailVerified).length,
  };
}

export async function updateAdminUser(
  userId: string,
  payload: UpdateAdminUserPayload,
): Promise<AdminUser> {
  if (!isMockMode()) {
    return apiRequest<AdminUser>(`/admin/users/${userId}`, {
      method: "PATCH",
      body: payload,
    });
  }

  await wait(120);

  const user = mockUsers.find((item) => item.id === userId);
  if (!user) {
    throw new Error("User not found");
  }

  return {
    ...user,
    role: payload.role,
    status: payload.status,
  };
}
