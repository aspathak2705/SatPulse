import { formatInteger, formatPercent } from "../utils/formatters";

export function MetricCards({ summary }) {
  return (
    <section className="card-grid">
      <article className="metric-card">
        <span>Records reviewed</span>
        <strong>{formatInteger(summary.totalPoints)}</strong>
        <p>Telemetry snapshots included in the selected window.</p>
      </article>
      <article className="metric-card">
        <span>Unusual moments</span>
        <strong>{formatInteger(summary.finalAlerts)}</strong>
        <p>Combined alerts worth a quick human check.</p>
      </article>
      <article className="metric-card">
        <span>Alert rate</span>
        <strong>{formatPercent(summary.anomalyRate)}</strong>
        <p>The share of records that looked unusual.</p>
      </article>
    </section>
  );
}
