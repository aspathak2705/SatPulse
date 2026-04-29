export function normalizeRecords(records, keys) {
  const bounds = keys.reduce((accumulator, key) => {
    const values = records
      .map((record) => record[key])
      .filter((value) => typeof value === "number" && !Number.isNaN(value));

    const minimum = Math.min(...values);
    const maximum = Math.max(...values);

    return {
      ...accumulator,
      [key]: { minimum, spread: maximum - minimum },
    };
  }, {});

  return records.map((record) => {
    const next = { ...record };
    keys.forEach((key) => {
      const { minimum, spread } = bounds[key];
      next[key] = spread === 0 ? 0.5 : (record[key] - minimum) / spread;
    });
    return next;
  });
}

export function buildAnomalyPoints(records, selectedParams, statistic, anomalyKeys) {
  return anomalyKeys.flatMap((anomalyKey) =>
    selectedParams.flatMap((parameter) => {
      const metricKey = `${parameter}_${statistic}`;
      return records
        .filter((record) => record[anomalyKey])
        .map((record) => ({
          timestamp: record.timestamp,
          value: record[metricKey],
          anomalyKey,
          parameter,
        }));
    }),
  );
}

export function buildErrorPoints(records) {
  return records
    .filter((record) => record.finalAnomaly)
    .map((record) => ({
      timestamp: record.timestamp,
      value: record.error,
    }));
}

export function friendlyHeadline(totalAlerts) {
  if (totalAlerts === 0) {
    return "Everything looks steady in the selected period.";
  }

  if (totalAlerts < 10) {
    return "Only a few unusual moments need attention.";
  }

  return "Several unusual patterns were detected and may need review.";
}

export function summarizeRecords(records) {
  const totalPoints = records.length;
  const finalAlerts = records.filter((record) => record.finalAnomaly).length;
  const lstmAlerts = records.filter((record) => record.lstmAnomaly).length;
  const isoAlerts = records.filter((record) => record.isoAnomaly).length;
  const anomalyRate = totalPoints ? (finalAlerts / totalPoints) * 100 : 0;

  return {
    totalPoints,
    finalAlerts,
    lstmAlerts,
    isoAlerts,
    anomalyRate,
    headline: friendlyHeadline(finalAlerts),
  };
}

export function getRecordsForRange(dataset, rangeDays) {
  if (!dataset?.records?.length) {
    return [];
  }

  const latest = new Date(dataset.records.at(-1).timestamp);
  const startTime = latest.getTime() - rangeDays * 24 * 60 * 60 * 1000;

  return dataset.records.filter(
    (record) => new Date(record.timestamp).getTime() >= startTime,
  );
}
