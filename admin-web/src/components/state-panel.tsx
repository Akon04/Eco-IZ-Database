type StatePanelProps = {
  title: string;
  description: string;
  tone?: "neutral" | "warning" | "error";
};

export function StatePanel({
  title,
  description,
  tone = "neutral",
}: StatePanelProps) {
  return (
    <article className={`card state-panel state-panel-${tone}`}>
      <p className="state-kicker">
        {tone === "error" ? "Issue" : tone === "warning" ? "Attention" : "State"}
      </p>
      <h2 className="section-title">{title}</h2>
      <p className="muted">{description}</p>
    </article>
  );
}
