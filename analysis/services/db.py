import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional, List, Dict, Any
import pandas as pd


class Database:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'db'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'patternscope'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }

    def get_connection(self):
        return psycopg2.connect(**self.connection_params)

    def fetch_traffic_events(self, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """Fetch traffic events as pandas DataFrame"""
        conn = self.get_connection()
        try:
            query = """
                SELECT
                    id, timestamp, location_id, vehicle_count,
                    avg_speed, min_speed, max_speed,
                    traffic_density_score
                FROM traffic_events
            """

            conditions = []
            params = []

            if start:
                conditions.append("timestamp >= %s")
                params.append(start)

            if end:
                conditions.append("timestamp <= %s")
                params.append(end)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp"

            df = pd.read_sql_query(query, conn, params=params if params else None)
            return df

        finally:
            conn.close()

    def insert_anomalies(self, anomalies: List[Dict[str, Any]]) -> int:
        """Insert detected anomalies into the database"""
        if not anomalies:
            return 0

        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            query = """
                INSERT INTO anomalies (
                    traffic_event_id, anomaly_type, confidence_score,
                    affected_metrics, description
                ) VALUES (%s, %s, %s, %s, %s)
            """

            for anomaly in anomalies:
                cursor.execute(query, (
                    anomaly['traffic_event_id'],
                    anomaly['anomaly_type'],
                    anomaly['confidence_score'],
                    psycopg2.extras.Json(anomaly['affected_metrics']),
                    anomaly['description']
                ))

            conn.commit()
            return len(anomalies)

        finally:
            conn.close()

    def insert_trend_suggestion(self, suggestion: Dict[str, Any]) -> int:
        """Insert trend suggestion into the database"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            query = """
                INSERT INTO trend_suggestions (
                    time_period_start, time_period_end, suggestion_type,
                    confidence_level, description, related_anomalies
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            cursor.execute(query, (
                suggestion['time_period_start'],
                suggestion['time_period_end'],
                suggestion['suggestion_type'],
                suggestion['confidence_level'],
                suggestion['description'],
                suggestion.get('related_anomalies', [])
            ))

            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else 0

        finally:
            conn.close()
