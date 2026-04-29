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
  formatChartNumber,
  formatLongDate,
  formatShortDate,
} from "../utils/formatters";

export function ReliabilityChart({ records, errorPoints }) {
  return (
    <article className="content-card">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Reliability view</span>
          <h3>How unusual was the behavior?</h3>
        </div>
        <p>
          When the blue line rises above the gold guide line, the model is less
          comfortable with what it sees.
        </p>
      </div>
      <div className="chart-shell compact">
        <ResponsiveContainer width="100%" height={300}>
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
            <YAxis stroke="#6b7c93" tickFormatter={formatChartNumber} />
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
            <Line
              type="monotone"
              dataKey="error"
              name="Model unfamiliarity"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="threshold"
              name="Expected range"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={false}
              isAnimationActive={false}
            />
            <Scatter
              name="Combined alerts"
              data={errorPoints}
              dataKey="value"
              fill="#ef4444"
              shape="circle"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}
