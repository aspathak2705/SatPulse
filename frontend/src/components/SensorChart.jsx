import {
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  anomalyColors,
  anomalyLabels,
  chartPalette,
} from "../constants/dashboard";
import {
  formatChartNumber,
  formatLongDate,
  formatShortDate,
} from "../utils/formatters";

export function SensorChart({
  records,
  selectedParams,
  selectedStatistic,
  enabledAnomalies,
  anomalyPoints,
  normalize,
}) {
  return (
    <section className="content-card">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Main view</span>
          <h3>Sensor comparison over time</h3>
        </div>
        <p>
          Red markers show the alert layers you selected. Keeping the window
          shorter makes the story much easier to follow.
        </p>
      </div>

      <div className="chart-shell">
        <ResponsiveContainer width="100%" height={360}>
          <ComposedChart
            data={records}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <CartesianGrid stroke="#d8e2f1" strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatShortDate}
              stroke="#6b7c93"
              minTickGap={24}
            />
            <YAxis
              stroke="#6b7c93"
              tickFormatter={formatChartNumber}
              domain={normalize ? [0, 1] : ["auto", "auto"]}
              label={{
                value: normalize ? "Normalized scale" : "Telemetry value",
                angle: -90,
                position: "insideLeft",
                style: { fill: "#6b7c93" },
              }}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "18px",
                border: "1px solid #d8e2f1",
                background: "#ffffff",
                boxShadow: "0 16px 40px rgba(37, 99, 235, 0.12)",
              }}
              labelFormatter={formatLongDate}
              formatter={(value, name) => [formatChartNumber(value), name]}
            />
            <Legend />
            {selectedParams.map((parameter, index) => {
              const dataKey = `${parameter}_${selectedStatistic}`;
              return (
                <Line
                  key={dataKey}
                  type="monotone"
                  dataKey={dataKey}
                  name={parameter}
                  stroke={chartPalette[index % chartPalette.length]}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              );
            })}
            {enabledAnomalies.map((anomalyKey) => (
              <Scatter
                key={anomalyKey}
                name={anomalyLabels[anomalyKey]}
                data={anomalyPoints.filter(
                  (point) => point.anomalyKey === anomalyKey,
                )}
                dataKey="value"
                fill={anomalyColors[anomalyKey]}
                shape="circle"
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
