import type { Achievement, AchievementFilters } from "@/lib/types";

type AchievementTableProps = {
  achievements: Achievement[];
  selectedAchievementId: string;
  filters: AchievementFilters;
  onSelect: (achievementId: string) => void;
  onFilterChange: (filters: AchievementFilters) => void;
};

export function AchievementTable({
  achievements,
  selectedAchievementId,
  filters,
  onSelect,
  onFilterChange,
}: AchievementTableProps) {
  return (
    <article className="card">
      <div className="section-head">
        <div>
          <h2 className="section-title">Achievement directory</h2>
          <p className="muted">
            Prepared for `GET /admin/achievements` and `PATCH /admin/achievements/:id`.
          </p>
        </div>
        <label className="inline-field inline-field-wide">
          <span className="sr-only">Search achievements</span>
          <input
            value={filters.search ?? ""}
            onChange={(event) =>
              onFilterChange({ ...filters, search: event.target.value })
            }
            placeholder="Search title, description, or icon"
          />
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Icon</th>
              <th>Target</th>
              <th>Reward</th>
            </tr>
          </thead>
          <tbody>
            {achievements.map((achievement) => (
              <tr
                key={achievement.id}
                className={
                  selectedAchievementId === achievement.id
                    ? "table-row-active"
                    : ""
                }
                onClick={() => onSelect(achievement.id)}
              >
                <td>{achievement.title}</td>
                <td>{achievement.icon}</td>
                <td>{achievement.targetValue}</td>
                <td>{achievement.rewardPoints}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
