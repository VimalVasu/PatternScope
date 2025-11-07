import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './TimeSeriesChart.css';

function TimeSeriesChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <h2>Vehicle Count Over Time</h2>
        <div className="no-data">No data available for the selected period</div>
      </div>
    );
  }

  // Format data for chart
  const chartData = data.map(item => ({
    time: new Date(item.time_bucket).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }),
    vehicles: parseInt(item.vehicle_count) || 0,
    speed: parseFloat(item.avg_speed) || 0
  }));

  return (
    <div className="chart-container">
      <h2>Vehicle Count Over Time</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis yAxisId="left" label={{ value: 'Vehicles', angle: -90, position: 'insideLeft' }} />
          <YAxis yAxisId="right" orientation="right" label={{ value: 'Speed (km/h)', angle: 90, position: 'insideRight' }} />
          <Tooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="vehicles"
            stroke="#8884d8"
            strokeWidth={2}
            name="Vehicle Count"
            dot={{ r: 3 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="speed"
            stroke="#82ca9d"
            strokeWidth={2}
            name="Avg Speed"
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TimeSeriesChart;
