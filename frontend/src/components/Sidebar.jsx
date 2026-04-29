import { anomalyLabels, rangeOptions } from "../constants/dashboard";

function ParameterSelector({ parameters, selectedParams, onToggleParameter }) {
  return (
    <section className="panel">
      <h2>Choose sensors</h2>
      <p>Pick the telemetry sources you want to compare.</p>
      <div className="chip-grid">
        {parameters.map((parameter) => {
          const selected = selectedParams.includes(parameter);
          return (
            <button
              key={parameter}
              type="button"
              className={`chip ${selected ? "selected" : ""}`}
              onClick={() => onToggleParameter(parameter)}
            >
              {parameter}
            </button>
          );
        })}
      </div>
    </section>
  );
}

function StatisticSelector({ statistics, selectedStatistic, onChange }) {
  return (
    <section className="panel">
      <h2>What should the chart show?</h2>
      <p>Use a simpler statistic like average or latest reading for easier reading.</p>
      <select
        className="field"
        value={selectedStatistic}
        onChange={(event) => onChange(event.target.value)}
      >
        {statistics.map((statistic) => (
          <option key={statistic} value={statistic}>
            {statistic.replace("value_", "").replaceAll("_", " ")}
          </option>
        ))}
      </select>
    </section>
  );
}

function TimeWindowSelector({ maxWindowDays, rangeDays, onChange }) {
  return (
    <section className="panel">
      <h2>Time window</h2>
      <p>Shorter windows are easier to read and better for storytelling.</p>
      <div className="range-grid">
        {rangeOptions
          .filter((option) => option <= maxWindowDays)
          .map((option) => (
            <button
              key={option}
              type="button"
              className={`range-pill ${rangeDays === option ? "active" : ""}`}
              onClick={() => onChange(option)}
            >
              Last {option} day{option > 1 ? "s" : ""}
            </button>
          ))}
      </div>
    </section>
  );
}

function AlertLayerSelector({ anomalyFilters, onToggleFilter }) {
  return (
    <section className="panel">
      <h2>Alert layers</h2>
      <p>These labels are written for non-technical users.</p>
      <div className="toggle-list">
        {Object.entries(anomalyLabels).map(([key, label]) => (
          <label key={key} className="toggle-row">
            <input
              type="checkbox"
              checked={anomalyFilters[key]}
              onChange={() => onToggleFilter(key)}
            />
            <span>{label}</span>
          </label>
        ))}
      </div>
    </section>
  );
}

function NormalizeToggle({ normalize, onToggle }) {
  return (
    <section className="panel">
      <div className="switch-row">
        <div>
          <h2>Normalize for comparison</h2>
          <p>Recommended when sensors operate on different scales.</p>
        </div>
        <button
          type="button"
          className={`switch ${normalize ? "on" : ""}`}
          onClick={onToggle}
        >
          <span />
        </button>
      </div>
    </section>
  );
}

export function Sidebar({
  dataset,
  selectedParams,
  selectedStatistic,
  rangeDays,
  anomalyFilters,
  normalize,
  onToggleParameter,
  onChangeStatistic,
  onChangeRange,
  onToggleFilter,
  onToggleNormalize,
}) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <span className="brand-kicker">SatPulse</span>
        <h1>Mission telemetry made easier to understand.</h1>
        <p>
          A lighter, clearer dashboard for reviewing unusual sensor behavior
          without forcing users to think like data scientists.
        </p>
      </div>

      <ParameterSelector
        parameters={dataset.parameters}
        selectedParams={selectedParams}
        onToggleParameter={onToggleParameter}
      />
      <StatisticSelector
        statistics={dataset.statistics}
        selectedStatistic={selectedStatistic}
        onChange={onChangeStatistic}
      />
      <TimeWindowSelector
        maxWindowDays={dataset.windowDays}
        rangeDays={rangeDays}
        onChange={onChangeRange}
      />
      <AlertLayerSelector
        anomalyFilters={anomalyFilters}
        onToggleFilter={onToggleFilter}
      />
      <NormalizeToggle normalize={normalize} onToggle={onToggleNormalize} />
    </aside>
  );
}
