import React from 'react';
import './KPICards.css';

function KPICards({ summary }) {
  const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return typeof num === 'number' ? num.toLocaleString() : num;
  };

  const formatSpeed = (speed) => {
    if (speed === null || speed === undefined) return 'N/A';
    return `${parseFloat(speed).toFixed(1)} km/h`;
  };

  return (
    <div className="kpi-cards">
      <div className="kpi-card">
        <h3>Total Events</h3>
        <div className="kpi-value">{formatNumber(summary.event_count)}</div>
      </div>

      <div className="kpi-card">
        <h3>Total Vehicles</h3>
        <div className="kpi-value">{formatNumber(summary.total_vehicles)}</div>
      </div>

      <div className="kpi-card">
        <h3>Average Speed</h3>
        <div className="kpi-value">{formatSpeed(summary.average_speed)}</div>
      </div>

      <div className="kpi-card">
        <h3>Anomalies Detected</h3>
        <div className="kpi-value anomaly-count">{formatNumber(summary.anomaly_count)}</div>
      </div>
    </div>
  );
}

export default KPICards;
