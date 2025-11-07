import React from 'react';
import './TrendSuggestions.css';

function TrendSuggestions({ suggestions }) {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="suggestions-container">
        <h2>Trend Suggestions</h2>
        <div className="no-suggestions">No trend suggestions available</div>
      </div>
    );
  }

  return (
    <div className="suggestions-container">
      <h2>Trend Suggestions</h2>
      <div className="suggestions-list">
        {suggestions.map((suggestion, index) => (
          <div key={suggestion.id || index} className="suggestion-card">
            <div className="suggestion-header">
              <span className="suggestion-type">{suggestion.suggestion_type || 'Analysis'}</span>
              {suggestion.confidence_level && (
                <span className="confidence-badge">
                  {(suggestion.confidence_level * 100).toFixed(0)}% confidence
                </span>
              )}
            </div>

            <div className="suggestion-description">
              {suggestion.description.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>

            <div className="suggestion-footer">
              <small>
                Generated: {new Date(suggestion.created_at).toLocaleString()}
              </small>
              {suggestion.related_anomalies && suggestion.related_anomalies.length > 0 && (
                <small>
                  Related to {suggestion.related_anomalies.length} anomal{suggestion.related_anomalies.length === 1 ? 'y' : 'ies'}
                </small>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TrendSuggestions;
