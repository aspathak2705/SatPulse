export function formatShortDate(value) {
  return new Intl.DateTimeFormat("en-IN", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export function formatLongDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatInteger(value) {
  return new Intl.NumberFormat("en-IN").format(value);
}

export function formatPercent(value) {
  return `${value.toFixed(2)}%`;
}

export function formatChartNumber(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  const absolute = Math.abs(value);
  if (absolute >= 1000) {
    return new Intl.NumberFormat("en-IN", {
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);
  }

  if (absolute > 0 && absolute < 0.01) {
    return value.toExponential(2);
  }

  return value.toFixed(2);
}
