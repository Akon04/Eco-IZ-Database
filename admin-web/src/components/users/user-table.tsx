import type { AdminUser, UserFilters, UserRole, UserStatus } from "@/lib/types";

type UserTableProps = {
  users: AdminUser[];
  selectedUserId: string;
  filters: UserFilters;
  onSelect: (userId: string) => void;
  onFilterChange: (filters: UserFilters) => void;
};

const roleOptions: Array<UserRole | "ALL"> = ["ALL", "ADMIN", "MODERATOR", "USER"];
const statusOptions: Array<UserStatus | "ALL"> = [
  "ALL",
  "ACTIVE",
  "REVIEW",
  "SUSPENDED",
];

export function UserTable({
  users,
  selectedUserId,
  filters,
  onSelect,
  onFilterChange,
}: UserTableProps) {
  return (
    <article className="card">
      <div className="section-head">
        <div>
          <h2 className="section-title">User directory</h2>
          <p className="muted">
            Prepared for `GET /admin/users` and `PATCH /admin/users/:id`.
          </p>
        </div>
        <div className="toolbar">
          <label className="inline-field">
            <span className="sr-only">Search users</span>
            <input
              value={filters.search ?? ""}
              onChange={(event) =>
                onFilterChange({ ...filters, search: event.target.value })
              }
              placeholder="Search username or email"
            />
          </label>
          <label className="inline-field">
            <span className="sr-only">Role filter</span>
            <select
              value={filters.role ?? "ALL"}
              onChange={(event) =>
                onFilterChange({
                  ...filters,
                  role: event.target.value as UserRole | "ALL",
                })
              }
            >
              {roleOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="inline-field">
            <span className="sr-only">Status filter</span>
            <select
              value={filters.status ?? "ALL"}
              onChange={(event) =>
                onFilterChange({
                  ...filters,
                  status: event.target.value as UserStatus | "ALL",
                })
              }
            >
              {statusOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
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
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Eco points</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className={selectedUserId === user.id ? "table-row-active" : ""}
                onClick={() => onSelect(user.id)}
              >
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  <span className="pill">{user.role}</span>
                </td>
                <td>
                  <span className="pill">{user.status}</span>
                </td>
                <td>{user.ecoPoints}</td>
                <td>{user.createdAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
