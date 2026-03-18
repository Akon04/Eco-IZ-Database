import { PageHeader } from "@/components/page-header";
import { HabitsWorkspace } from "@/components/habits/habits-workspace";
import { getHabitMetrics, listHabits } from "@/lib/api/habits";

export default async function HabitsPage() {
  const [habits, metrics] = await Promise.all([
    listHabits(),
    getHabitMetrics(),
  ]);

  return (
    <>
      <PageHeader
        title="Habits"
        description="Edit the habit catalog, points, and eco impact values."
      />
      <HabitsWorkspace initialHabits={habits} metrics={metrics} />
    </>
  );
}
