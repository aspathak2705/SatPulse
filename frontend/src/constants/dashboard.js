export const anomalyLabels = {
  lstmAnomaly: "AI pattern alert",
  isoAnomaly: "Outlier alert",
  finalAnomaly: "Combined alert",
};

export const anomalyColors = {
  lstmAnomaly: "#f59e0b",
  isoAnomaly: "#0ea5e9",
  finalAnomaly: "#ef4444",
};

export const chartPalette = ["#2563eb", "#10b981", "#8b5cf6", "#f97316"];

export const rangeOptions = [1, 3, 7, 14, 30];

export const defaultAnomalyFilters = {
  lstmAnomaly: false,
  isoAnomaly: false,
  finalAnomaly: true,
};

export const explanationItems = [
  {
    label: "What are combined alerts?",
    value:
      "These are moments where the system believes the telemetry deserves human review.",
  },
  {
    label: "Why normalize the lines?",
    value:
      "Normalization puts sensors on the same 0-1 scale so non-technical users can compare movement patterns easily.",
  },
  {
    label: "How should I read the error chart?",
    value:
      "When the blue line rises above the gold guide line, the system is seeing behavior that looks less familiar than usual.",
  },
];
