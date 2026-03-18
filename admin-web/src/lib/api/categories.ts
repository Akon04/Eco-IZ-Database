import { apiRequest } from "@/lib/api/client";
import { wait } from "@/lib/api/helpers";
import { isMockMode } from "@/lib/config";
import { mockCategories } from "@/lib/mocks";
import type {
  CategoryFilters,
  CategoryMetrics,
  EcoCategory,
  UpdateCategoryPayload,
} from "@/lib/types";

export async function listCategories(
  filters: CategoryFilters = {},
): Promise<EcoCategory[]> {
  if (!isMockMode()) {
    const params = new URLSearchParams();
    if (filters.search?.trim()) params.set("search", filters.search.trim());

    return apiRequest<EcoCategory[]>(
      `/admin/categories${params.size ? `?${params.toString()}` : ""}`,
    );
  }

  await wait(70);

  const query = filters.search?.trim().toLowerCase();
  return mockCategories.filter((category) => {
    if (!query) return true;

    return (
      category.name.toLowerCase().includes(query) ||
      category.description.toLowerCase().includes(query) ||
      category.icon.toLowerCase().includes(query)
    );
  });
}

export async function getCategoryMetrics(): Promise<CategoryMetrics> {
  if (!isMockMode()) {
    return apiRequest<CategoryMetrics>("/admin/categories/metrics");
  }

  await wait(40);

  return {
    totalCategories: mockCategories.length,
    uniqueColors: new Set(mockCategories.map((category) => category.color)).size,
    iconCount: new Set(mockCategories.map((category) => category.icon)).size,
  };
}

export async function updateCategory(
  categoryId: string,
  payload: UpdateCategoryPayload,
): Promise<EcoCategory> {
  if (!isMockMode()) {
    return apiRequest<EcoCategory>(`/admin/categories/${categoryId}`, {
      method: "PATCH",
      body: payload,
    });
  }

  await wait(120);

  const category = mockCategories.find((item) => item.id === categoryId);
  if (!category) {
    throw new Error("Category not found");
  }

  return {
    ...category,
    ...payload,
  };
}
