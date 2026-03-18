import type { CategoryFilters, EcoCategory } from "@/lib/types";

type CategoryTableProps = {
  categories: EcoCategory[];
  selectedCategoryId: string;
  filters: CategoryFilters;
  onSelect: (categoryId: string) => void;
  onFilterChange: (filters: CategoryFilters) => void;
};

export function CategoryTable({
  categories,
  selectedCategoryId,
  filters,
  onSelect,
  onFilterChange,
}: CategoryTableProps) {
  return (
    <article className="card">
      <div className="section-head">
        <div>
          <h2 className="section-title">Category directory</h2>
          <p className="muted">
            Prepared for `GET /admin/categories` and `PATCH /admin/categories/:id`.
          </p>
        </div>
        <label className="inline-field inline-field-wide">
          <span className="sr-only">Search categories</span>
          <input
            value={filters.search ?? ""}
            onChange={(event) =>
              onFilterChange({ ...filters, search: event.target.value })
            }
            placeholder="Search name, description, or icon"
          />
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Color</th>
              <th>Icon</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category) => (
              <tr
                key={category.id}
                className={
                  selectedCategoryId === category.id ? "table-row-active" : ""
                }
                onClick={() => onSelect(category.id)}
              >
                <td>{category.name}</td>
                <td>{category.description}</td>
                <td>
                  <span className="pill">{category.color}</span>
                </td>
                <td>{category.icon}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
