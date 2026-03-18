import { PageHeader } from "@/components/page-header";
import { UsersWorkspace } from "@/components/users/users-workspace";
import { getAdminUserMetrics, listAdminUsers } from "@/lib/api/users";

export default async function UsersPage() {
  const [users, metrics] = await Promise.all([
    listAdminUsers(),
    getAdminUserMetrics(),
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
