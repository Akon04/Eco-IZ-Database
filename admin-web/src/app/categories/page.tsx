import { PageHeader } from "@/components/page-header";
import { CategoriesWorkspace } from "@/components/categories/categories-workspace";
import { getCategoryMetrics, listCategories } from "@/lib/api/categories";
import { isMockMode } from "@/lib/config";

export default async function CategoriesPage() {
  const [categories, metrics] = isMockMode()
    ? await Promise.all([listCategories(), getCategoryMetrics()])
    : await Promise.all([
        Promise.resolve([]),
        Promise.resolve({
          totalCategories: 0,
          uniqueColors: 0,
          iconCount: 0,
        }),
      ]);

  return (
    <>
      <PageHeader
        title="Categories"
        description="Maintain eco categories used by habits and analytics."
      />
      <CategoriesWorkspace initialCategories={categories} metrics={metrics} />
    </>
  );
}
