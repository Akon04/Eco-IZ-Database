import { PageHeader } from "@/components/page-header";
import { UsersWorkspace } from "@/components/users/users-workspace";
import { getAdminUserMetrics, listAdminUsers } from "@/lib/api/users";
import { isMockMode } from "@/lib/config";

export default async function UsersPage() {
  const [users, metrics] = isMockMode()
    ? await Promise.all([listAdminUsers(), getAdminUserMetrics()])
    : await Promise.all([
        Promise.resolve([]),
        Promise.resolve({
          totalUsers: 0,
          adminCount: 0,
          needsReview: 0,
          verifiedCount: 0,
        }),
      ]);

  return (
    <>
      <PageHeader
        title="Users"
        description="Manage admin roles, moderation access, and account status."
      />
      <UsersWorkspace initialUsers={users} metrics={metrics} />
    </>
  );
}
