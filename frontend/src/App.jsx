import { useDeferredValue, useEffect, useMemo, useState } from "react";

import { InsightPanel } from "./components/InsightPanel";
import { MetricCards } from "./components/MetricCards";
import { ReliabilityChart } from "./components/ReliabilityChart";
import { SensorChart } from "./components/SensorChart";
import { Sidebar } from "./components/Sidebar";
import { SummaryHeader } from "./components/SummaryHeader";
import { defaultAnomalyFilters } from "./constants/dashboard";
import { useDashboardData } from "./hooks/useDashboardData";
import {
  buildAnomalyPoints,
  buildErrorPoints,
  getRecordsForRange,
  normalizeRecords,
  summarizeRecords,
} from "./utils/dashboardData";

function App() {
  const { dataset, loading, error } = useDashboardData();
  const [selectedParams, setSelectedParams] = useState([]);
  const [selectedStatistic, setSelectedStatistic] = useState("");
  const [rangeDays, setRangeDays] = useState(7);
  const [normalize, setNormalize] = useState(true);
  const [anomalyFilters, setAnomalyFilters] = useState(defaultAnomalyFilters);

  useEffect(() => {
    if (!dataset) {
      return;
    }

    setSelectedParams(dataset.parameters.slice(0, 2));
    setSelectedStatistic(dataset.defaultStatistic);
    setRangeDays(dataset.defaultRangeDays);
  }, [dataset]);

  const filteredRecords = useMemo(() => {
    return getRecordsForRange(dataset, rangeDays);
  }, [dataset, rangeDays]);

  const deferredRecords = useDeferredValue(filteredRecords);

  const metricKeys = useMemo(
    () => selectedParams.map((parameter) => `${parameter}_${selectedStatistic}`),
    [selectedParams, selectedStatistic],
  );

  const chartRecords = useMemo(() => {
    if (!deferredRecords.length) {
      return [];
    }

    return normalize
      ? normalizeRecords(deferredRecords, metricKeys)
      : deferredRecords;
  }, [deferredRecords, metricKeys, normalize]);

  const enabledAnomalies = useMemo(
    () =>
      Object.entries(anomalyFilters)
        .filter(([, enabled]) => enabled)
        .map(([key]) => key),
    [anomalyFilters],
  );

  const anomalyPoints = useMemo(
    () =>
      buildAnomalyPoints(
        chartRecords,
        selectedParams,
        selectedStatistic,
        enabledAnomalies,
      ),
    [chartRecords, enabledAnomalies, selectedParams, selectedStatistic],
  );

  const errorPoints = useMemo(
    () => buildErrorPoints(deferredRecords),
    [deferredRecords],
  );

  const summary = useMemo(() => {
    return summarizeRecords(deferredRecords);
  }, [deferredRecords]);

  if (loading) {
    return <div className="state-card">Loading dashboard data...</div>;
  }

  if (error) {
    return <div className="state-card error">{error}</div>;
  }

  const toggleParameter = (parameter) => {
    setSelectedParams((current) =>
      current.includes(parameter)
        ? current.filter((item) => item !== parameter)
        : [...current, parameter],
    );
  };

  const toggleFilter = (key) => {
    setAnomalyFilters((current) => ({
      ...current,
      [key]: !current[key],
    }));
  };

  return (
    <div className="page-shell">
      <Sidebar
        dataset={dataset}
        selectedParams={selectedParams}
        selectedStatistic={selectedStatistic}
        rangeDays={rangeDays}
        anomalyFilters={anomalyFilters}
        normalize={normalize}
        onToggleParameter={toggleParameter}
        onChangeStatistic={setSelectedStatistic}
        onChangeRange={setRangeDays}
        onToggleFilter={toggleFilter}
        onToggleNormalize={() => setNormalize((current) => !current)}
      />

      <main className="main-content">
        <SummaryHeader records={deferredRecords} summary={summary} />
        <MetricCards summary={summary} />
        <SensorChart
          records={chartRecords}
          selectedParams={selectedParams}
          selectedStatistic={selectedStatistic}
          enabledAnomalies={enabledAnomalies}
          anomalyPoints={anomalyPoints}
          normalize={normalize}
        />

        <section className="two-column">
          <ReliabilityChart records={deferredRecords} errorPoints={errorPoints} />
          <InsightPanel summary={summary} />
        </section>
      </main>
    </div>
  );
}

export default App;
