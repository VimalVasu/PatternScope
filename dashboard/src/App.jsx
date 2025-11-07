import React, { useState, useEffect } from 'react';
import DateRangeSelector from './components/DateRangeSelector';
import KPICards from './components/KPICards';
import TimeSeriesChart from './components/TimeSeriesChart';
import TrendSuggestions from './components/TrendSuggestions';
import * as api from './services/api';
import './App.css';

function App() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    end: new Date().toISOString().slice(0, 16)
  });

  const [summary, setSummary] = useState(null);
  const [timeseries, setTimeseries] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [summaryData, timeseriesData, suggestionsData] = await Promise.all([
        api.getDashboardSummary(dateRange.start, dateRange.end),
        api.getDashboardTimeseries(dateRange.start, dateRange.end),
        api.getTrendSuggestions(dateRange.start, dateRange.end)
      ]);

      setSummary(summaryData);
      setTimeseries(timeseriesData.timeseries || []);
      setSuggestions(suggestionsData.suggestions || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDateRangeChange = (newRange) => {
    setDateRange(newRange);
  };

  const handleRefresh = () => {
    fetchData();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>PatternScope Dashboard</h1>
        <p>Traffic Monitoring & Anomaly Detection</p>
      </header>

      <div className="container">
        <DateRangeSelector
          dateRange={dateRange}
          onChange={handleDateRangeChange}
          onRefresh={handleRefresh}
          loading={loading}
        />

        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}

        {loading && <div className="loading">Loading...</div>}

        {!loading && summary && (
          <>
            <KPICards summary={summary} />
            <TimeSeriesChart data={timeseries} />
            <TrendSuggestions suggestions={suggestions} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
