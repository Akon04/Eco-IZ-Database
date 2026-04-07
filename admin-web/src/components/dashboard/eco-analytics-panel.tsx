"use client";

import type { EcoAnalytics } from "@/lib/types";

type EcoAnalyticsPanelProps = {
  analytics: EcoAnalytics;
};

const categoryPalette: Record<string, { tone: string; accent: string }> = {
  "Транспорт": { tone: "#FFE7CB", accent: "#D97C18" },
  "Вода": { tone: "#D9F0FF", accent: "#2E97E6" },
  "Пластик": { tone: "#D8F7F2", accent: "#26B9B0" },
  "Отходы": { tone: "#E3F8D9", accent: "#55B83D" },
  "Энергия": { tone: "#FFF0BF", accent: "#D8A10D" },
};

export function EcoAnalyticsPanel({ analytics }: EcoAnalyticsPanelProps) {
  const maxCount = Math.max(...analytics.categoryBreakdown.map((item) => item.count), 1);

  return (
    <section className="grid eco-analytics-layout" style={{ marginTop: 16 }}>
      <article className="card">
        <div className="section-head">
          <div>
            <h2 className="section-title">Эко-аналитика</h2>
            <p className="muted">Как пользователи используют eco-каталог и какие категории доминируют.</p>
          </div>
        </div>

        <div className="eco-bars">
          {analytics.categoryBreakdown.map((item) => {
            const palette = categoryPalette[item.category] ?? {
              tone: "var(--surface-alt)",
              accent: "var(--accent-strong)",
            };

            return (
              <div key={item.category} className="eco-bar-card">
                <div className="eco-bar-head">
                  <span
                    className="eco-dot"
                    style={{ background: palette.accent, boxShadow: `0 0 0 8px ${palette.tone}` }}
                  />
                  <div>
                    <strong>{item.category}</strong>
                    <p className="muted">
                      {item.count} активностей · {item.co2Saved.toFixed(1)} кг CO2
                    </p>
                  </div>
                </div>
                <div className="eco-bar-track">
                  <div
                    className="eco-bar-fill"
                    style={{
                      width: `${(item.count / maxCount) * 100}%`,
                      background: `linear-gradient(90deg, ${palette.accent}, ${palette.tone})`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </article>

      <div className="grid" style={{ gap: 16 }}>
        <section className="grid grid-three">
          <article className="card eco-kpi-card">
            <p className="muted">Самая популярная категория</p>
            <p className="metric" style={{ fontSize: 30 }}>{analytics.topCategory || "Нет данных"}</p>
            <p className="muted">Лидирует по числу записанных активностей.</p>
          </article>
          <article className="card eco-kpi-card">
            <p className="muted">Своя активность</p>
            <p className="metric">{analytics.customActivitiesCount}</p>
            <p className="muted">Сколько раз пользователи выбрали custom-сценарий.</p>
          </article>
          <article className="card eco-kpi-card">
            <p className="muted">Средний CO2 / активность</p>
            <p className="metric">{analytics.averageCo2PerActivity.toFixed(2)}</p>
            <p className="muted">Среднее eco-влияние на одну активность.</p>
          </article>
        </section>

        <article className="card">
          <h3 className="section-title">Топ пользователи по активностям</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Пользователь</th>
                  <th>Активностей</th>
                  <th>Eco баллы</th>
                  <th>CO2</th>
                </tr>
              </thead>
              <tbody>
                {analytics.topUsersByActivity.map((user) => (
                  <tr key={user.userId}>
                    <td>{user.username}</td>
                    <td>{user.activitiesCount}</td>
                    <td>{user.ecoPoints}</td>
                    <td>{user.co2Saved.toFixed(1)} кг</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>
    </section>
  );
}
