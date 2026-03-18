import type { CommunityPost, PostFilters } from "@/lib/types";

type PostTableProps = {
  posts: CommunityPost[];
  selectedPostId: string;
  filters: PostFilters;
  onSelect: (postId: string) => void;
  onFilterChange: (filters: PostFilters) => void;
};

const stateOptions: Array<CommunityPost["state"] | "ALL"> = [
  "ALL",
  "Published",
  "Flagged",
  "Needs review",
  "Hidden",
];

const visibilityOptions: Array<CommunityPost["visibility"] | "ALL"> = [
  "ALL",
  "PUBLIC",
  "FOLLOWERS",
  "PRIVATE",
];

export function PostTable({
  posts,
  selectedPostId,
  filters,
  onSelect,
  onFilterChange,
}: PostTableProps) {
  return (
    <article className="card">
      <div className="section-head">
        <div>
          <h2 className="section-title">Moderation queue</h2>
          <p className="muted">
            Prepared for `GET /admin/posts` and `PATCH /admin/posts/:id`.
          </p>
        </div>
        <div className="toolbar">
          <label className="inline-field inline-field-wide">
            <span className="sr-only">Search posts</span>
            <input
              value={filters.search ?? ""}
              onChange={(event) =>
                onFilterChange({ ...filters, search: event.target.value })
              }
              placeholder="Search author or content"
            />
          </label>
          <label className="inline-field">
            <span className="sr-only">State filter</span>
            <select
              value={filters.state ?? "ALL"}
              onChange={(event) =>
                onFilterChange({
                  ...filters,
                  state: event.target.value as CommunityPost["state"] | "ALL",
                })
              }
            >
              {stateOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="inline-field">
            <span className="sr-only">Visibility filter</span>
            <select
              value={filters.visibility ?? "ALL"}
              onChange={(event) =>
                onFilterChange({
                  ...filters,
                  visibility: event.target.value as
                    | CommunityPost["visibility"]
                    | "ALL",
                })
              }
            >
              {visibilityOptions.map((option) => (
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
              <th>Author</th>
              <th>Visibility</th>
              <th>Status</th>
              <th>Reports</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {posts.map((post) => (
              <tr
                key={post.id}
                className={selectedPostId === post.id ? "table-row-active" : ""}
                onClick={() => onSelect(post.id)}
              >
                <td>{post.author}</td>
                <td>{post.visibility}</td>
                <td>
                  <span className="pill">{post.state}</span>
                </td>
                <td>{post.reportsCount}</td>
                <td>{post.createdAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}
