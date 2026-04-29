import { formatLongDate } from "../utils/formatters";

export function SummaryHeader({ records, summary }) {
  return (
    <section className="hero">
      <div>
        <span className="eyebrow">Telemetry review summary</span>
        <h2>{summary.headline}</h2>
        <p>
          Data shown from {formatLongDate(records[0]?.timestamp)} to{" "}
          {formatLongDate(records.at(-1)?.timestamp)}.
        </p>
      </div>
      <div className="hero-badge">
        {summary.finalAlerts > 0 ? "Needs attention" : "Stable period"}
      </div>
    </section>
  );
}
