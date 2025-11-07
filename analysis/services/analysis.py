import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from datetime import datetime
from typing import Optional, List, Dict, Any

from services.db import Database


class AnalysisService:
    def __init__(self):
        self.db = Database()

    async def run_analysis(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        methods: List[str] = None
    ) -> Dict[str, Any]:
        """Run anomaly detection analysis"""

        # Fetch data
        start_str = start.isoformat() if start else None
        end_str = end.isoformat() if end else None
        df = self.db.fetch_traffic_events(start_str, end_str)

        if df.empty:
            return {
                'success': True,
                'anomalies_detected': 0,
                'message': 'No traffic events found in the specified period'
            }

        # Detect anomalies using specified methods
        anomalies = []
        methods = methods or ['zscore', 'iqr', 'isolation_forest']

        if 'zscore' in methods:
            anomalies.extend(self._detect_zscore(df))

        if 'iqr' in methods:
            anomalies.extend(self._detect_iqr(df))

        if 'isolation_forest' in methods:
            anomalies.extend(self._detect_isolation_forest(df))

        if 'lof' in methods:
            anomalies.extend(self._detect_lof(df))

        # Remove duplicates (same event detected by multiple methods)
        unique_anomalies = self._deduplicate_anomalies(anomalies)

        # Store anomalies in database
        if unique_anomalies:
            self.db.insert_anomalies(unique_anomalies)

        return {
            'success': True,
            'anomalies_detected': len(unique_anomalies),
            'anomaly_details': unique_anomalies,
            'period': {
                'start': start_str,
                'end': end_str
            },
            'methods_used': methods
        }

    def _detect_zscore(self, df: pd.DataFrame, threshold: float = 3.0) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method"""
        anomalies = []

        for metric in ['vehicle_count', 'avg_speed', 'traffic_density_score']:
            if metric not in df.columns or df[metric].isna().all():
                continue

            # Calculate z-scores
            mean = df[metric].mean()
            std = df[metric].std()

            if std == 0:
                continue

            z_scores = np.abs((df[metric] - mean) / std)

            # Find anomalies
            anomaly_indices = z_scores > threshold

            for idx in df[anomaly_indices].index:
                anomalies.append({
                    'traffic_event_id': int(df.loc[idx, 'id']),
                    'anomaly_type': 'zscore',
                    'confidence_score': min(float(z_scores[idx]) / threshold, 1.0),
                    'affected_metrics': [metric],
                    'description': f'{metric} value {df.loc[idx, metric]} is {z_scores[idx]:.2f} standard deviations from mean'
                })

        return anomalies

    def _detect_iqr(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Interquartile Range (IQR) method"""
        anomalies = []

        for metric in ['vehicle_count', 'avg_speed', 'traffic_density_score']:
            if metric not in df.columns or df[metric].isna().all():
                continue

            Q1 = df[metric].quantile(0.25)
            Q3 = df[metric].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Find anomalies
            anomaly_indices = (df[metric] < lower_bound) | (df[metric] > upper_bound)

            for idx in df[anomaly_indices].index:
                value = df.loc[idx, metric]
                distance = max(abs(value - lower_bound), abs(value - upper_bound))
                confidence = min(distance / (IQR * 1.5), 1.0) if IQR > 0 else 0.5

                anomalies.append({
                    'traffic_event_id': int(df.loc[idx, 'id']),
                    'anomaly_type': 'iqr',
                    'confidence_score': float(confidence),
                    'affected_metrics': [metric],
                    'description': f'{metric} value {value} is outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]'
                })

        return anomalies

    def _detect_isolation_forest(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []

        # Select numeric features
        features = ['vehicle_count', 'avg_speed', 'traffic_density_score']
        feature_cols = [col for col in features if col in df.columns and not df[col].isna().all()]

        if not feature_cols:
            return anomalies

        # Prepare data
        X = df[feature_cols].fillna(df[feature_cols].mean())

        if len(X) < 10:  # Need minimum samples
            return anomalies

        # Train Isolation Forest
        clf = IsolationForest(contamination=0.1, random_state=42)
        predictions = clf.fit_predict(X)
        scores = clf.score_samples(X)

        # Find anomalies (prediction == -1)
        anomaly_indices = predictions == -1

        for idx in df[anomaly_indices].index:
            anomalies.append({
                'traffic_event_id': int(df.loc[idx, 'id']),
                'anomaly_type': 'isolation_forest',
                'confidence_score': float(1.0 - (scores[idx] + 0.5)),  # Normalize score
                'affected_metrics': feature_cols,
                'description': f'Anomaly detected using Isolation Forest on features: {", ".join(feature_cols)}'
            })

        return anomalies

    def _detect_lof(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Local Outlier Factor"""
        anomalies = []

        # Select numeric features
        features = ['vehicle_count', 'avg_speed', 'traffic_density_score']
        feature_cols = [col for col in features if col in df.columns and not df[col].isna().all()]

        if not feature_cols:
            return anomalies

        # Prepare data
        X = df[feature_cols].fillna(df[feature_cols].mean())

        if len(X) < 10:  # Need minimum samples
            return anomalies

        # Train LOF
        clf = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
        predictions = clf.fit_predict(X)
        scores = clf.negative_outlier_factor_

        # Find anomalies (prediction == -1)
        anomaly_indices = predictions == -1

        for idx in df[anomaly_indices].index:
            anomalies.append({
                'traffic_event_id': int(df.loc[idx, 'id']),
                'anomaly_type': 'lof',
                'confidence_score': float(min(abs(scores[idx]), 1.0)),
                'affected_metrics': feature_cols,
                'description': f'Local outlier detected on features: {", ".join(feature_cols)}'
            })

        return anomalies

    def _deduplicate_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate anomalies for the same traffic event"""
        seen = {}

        for anomaly in anomalies:
            event_id = anomaly['traffic_event_id']

            if event_id not in seen or anomaly['confidence_score'] > seen[event_id]['confidence_score']:
                seen[event_id] = anomaly

        return list(seen.values())
