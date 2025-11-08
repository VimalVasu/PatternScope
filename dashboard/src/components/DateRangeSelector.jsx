import React from 'react';
import './DateRangeSelector.css';

function DateRangeSelector({ dateRange, onChange, onRefresh, loading }) {
  const handleStartChange = (e) => {
    onChange({ ...dateRange, start: e.target.value });
  };

  const handleEndChange = (e) => {
    onChange({ ...dateRange, end: e.target.value });
  };

  return (
    <div className="date-range-selector">
      <div className="date-input-group">
        <label>
          Start:
          <input
            type="datetime-local"
            value={dateRange.start}
            onChange={handleStartChange}
            disabled={loading}
          />
        </label>

        <label>
          End:
          <input
            type="datetime-local"
            value={dateRange.end}
            onChange={handleEndChange}
            disabled={loading}
          />
        </label>
      </div>

      <button
        className="refresh-button"
        onClick={onRefresh}
        disabled={loading}
      >
        {loading ? 'Loading...' : 'Refresh'}
      </button>
    </div>
  );
}

export default DateRangeSelector;
