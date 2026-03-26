import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import { mockHabits } from "@/lib/mocks";
import type {
  Habit,
  HabitFilters,
  HabitMetrics,
  UpdateHabitPayload,
} from "@/lib/types";

export async function listHabits(
  filters: HabitFilters = {},
): Promise<Habit[]> {
  if (!isMockMode()) {
    const params = new URLSearchParams();
    if (filters.search?.trim()) params.set("search", filters.search.trim());
    if (filters.category && filters.category !== "ALL") {
      params.set("category", filters.category.trim());
    }

    return apiRequest<Habit[]>(
      `/admin/habits${params.size ? `?${params.toString()}` : ""}`,
    );
  }

  await wait(70);

  const query = filters.search?.trim().toLowerCase();
  return mockHabits.filter((habit) => {
    const matchesSearch =
      !query ||
      habit.title.toLowerCase().includes(query) ||
      habit.category.toLowerCase().includes(query);
    const matchesCategory =
      !filters.category ||
      filters.category === "ALL" ||
      habit.category === filters.category;

    return matchesSearch && matchesCategory;
  });
}

export async function getHabitMetrics(): Promise<HabitMetrics> {
  if (!isMockMode()) {
    return apiRequest<HabitMetrics>("/admin/habits/metrics");
  }

  await wait(40);

  return {
    totalHabits: mockHabits.length,
    totalPoints: mockHabits.reduce((sum, habit) => sum + habit.points, 0),
    categoriesUsed: new Set(mockHabits.map((habit) => habit.category)).size,
  };
}

export async function updateHabit(
  habitId: string,
  payload: UpdateHabitPayload,
): Promise<Habit> {
  if (!isMockMode()) {
    return apiRequest<Habit>(`/admin/habits/${habitId}`, {
      method: "PATCH",
      body: payload,
    });
  }

  await wait(120);

  const habit = mockHabits.find((item) => item.id === habitId);
  if (!habit) {
    throw new Error("Habit not found");
  }

  return {
    ...habit,
    ...payload,
  };
}
