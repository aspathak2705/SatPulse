import { explanationItems } from "../constants/dashboard";
import { formatInteger, formatPercent } from "../utils/formatters";

export function InsightPanel({ summary }) {
  return (
    <article className="content-card info-stack">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Plain-language summary</span>
          <h3>What should a non-technical user take away?</h3>
        </div>
      </div>

      <div className="insight-list">
        <div className="insight-item">
          <strong>{formatInteger(summary.lstmAlerts)}</strong>
          <span>pattern alerts detected by the sequence model</span>
        </div>
        <div className="insight-item">
          <strong>{formatInteger(summary.isoAlerts)}</strong>
          <span>outlier alerts detected by the statistical scan</span>
        </div>
        <div className="insight-item">
          <strong>{formatPercent(summary.anomalyRate)}</strong>
          <span>of the selected data looked unusual overall</span>
        </div>
      </div>

      <div className="explanation-list">
        {explanationItems.map((item) => (
          <article key={item.label} className="explanation-card">
            <h4>{item.label}</h4>
            <p>{item.value}</p>
          </article>
        ))}
      </div>
    </article>
  );
}
