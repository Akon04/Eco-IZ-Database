import type { Habit, HabitFilters } from "@/lib/types";

type HabitTableProps = {
  habits: Habit[];
  selectedHabitId: string;
  filters: HabitFilters;
  categoryOptions: string[];
  onSelect: (habitId: string) => void;
  onFilterChange: (filters: HabitFilters) => void;
};

export function HabitTable({
  habits,
  selectedHabitId,
  filters,
  categoryOptions,
  onSelect,
  onFilterChange,
}: HabitTableProps) {
  return (
    <article className="card">
      <div className="section-head">
        <div>
          <h2 className="section-title">Habit catalog</h2>
          <p className="muted">
            Prepared for `GET /admin/habits` and `PATCH /admin/habits/:id`.
          </p>
        </div>
        <div className="toolbar">
          <label className="inline-field inline-field-wide">
            <span className="sr-only">Search habits</span>
            <input
              value={filters.search ?? ""}
              onChange={(event) =>
                onFilterChange({ ...filters, search: event.target.value })
              }
              placeholder="Search title or category"
            />
          </label>
          <label className="inline-field">
            <span className="sr-only">Category filter</span>
            <select
              value={filters.category ?? "ALL"}
              onChange={(event) =>
                onFilterChange({
                  ...filters,
                  category: event.target.value,
                })
              }
            >
              <option value="ALL">ALL</option>
              {categoryOptions.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Category</th>
              <th>Points</th>
              <th>CO2</th>
              <th>Water</th>
              <th>Energy</th>
            </tr>
          </thead>
          <tbody>
            {habits.map((habit) => (
              <tr
                key={habit.id}
                className={selectedHabitId === habit.id ? "table-row-active" : ""}
                onClick={() => onSelect(habit.id)}
              >
                <td>{habit.title}</td>
                <td>{habit.category}</td>
                <td>{habit.points}</td>
                <td>{habit.co2Value}</td>
                <td>{habit.waterValue}</td>
                <td>{habit.energyValue}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
