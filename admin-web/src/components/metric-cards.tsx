type MetricCardItem = {
  label: string;
  value: string | number;
  note: string;
};

type MetricCardsProps = {
  items: MetricCardItem[];
  columns?: "three" | "four";
};

export function MetricCards({
  items,
  columns = "four",
}: MetricCardsProps) {
  return (
    <section className={`grid ${columns === "three" ? "grid-three" : "cards"}`}>
      {items.map((item) => (
        <article key={item.label} className="card">
          <p className="muted">{item.label}</p>
          <p className="metric">{item.value}</p>
          <p className="muted">{item.note}</p>
        </article>
      ))}
    </section>
  );
}
