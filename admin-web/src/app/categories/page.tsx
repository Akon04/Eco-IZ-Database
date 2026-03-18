import { PageHeader } from "@/components/page-header";
import { CategoriesWorkspace } from "@/components/categories/categories-workspace";
import { getCategoryMetrics, listCategories } from "@/lib/api/categories";

export default async function CategoriesPage() {
  const [categories, metrics] = await Promise.all([
    listCategories(),
    getCategoryMetrics(),
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
