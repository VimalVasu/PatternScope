import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from services.db import Database


class OllamaClient:
    """Client for interacting with Ollama LLM service"""

    def __init__(self, url: str, model: str):
        self.url = url.rstrip('/')
        self.model = model
        self.timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
        self.db = Database()

    async def generate_trend_suggestions(
        self,
        anomalies: List[Dict[str, Any]],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Generate human-readable trend suggestions from anomalies"""

        if not anomalies:
            return []

        # Prepare prompt
        prompt = self._build_prompt(anomalies, start, end)

        try:
            # Call Ollama API
            suggestion_text = await self._call_ollama(prompt)

            # Store suggestion in database
            suggestion = {
                'time_period_start': start.isoformat() if start else None,
                'time_period_end': end.isoformat() if end else None,
                'suggestion_type': 'anomaly_summary',
                'confidence_level': 0.8,
                'description': suggestion_text,
                'related_anomalies': [a['traffic_event_id'] for a in anomalies[:10]]  # Limit to 10
            }

            suggestion_id = self.db.insert_trend_suggestion(suggestion)
            suggestion['id'] = suggestion_id

            return [suggestion]

        except Exception as e:
            print(f"Error generating trend suggestions: {e}")
            # Return a fallback suggestion
            return [{
                'time_period_start': start.isoformat() if start else None,
                'time_period_end': end.isoformat() if end else None,
                'suggestion_type': 'anomaly_summary',
                'confidence_level': 0.5,
                'description': f'Detected {len(anomalies)} anomalies in traffic patterns. Manual review recommended.',
                'related_anomalies': [a['traffic_event_id'] for a in anomalies[:10]]
            }]

    def _build_prompt(
        self,
        anomalies: List[Dict[str, Any]],
        start: Optional[datetime],
        end: Optional[datetime]
    ) -> str:
        """Build prompt for LLM"""

        period = ""
        if start and end:
            period = f"from {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}"
        elif start:
            period = f"since {start.strftime('%Y-%m-%d %H:%M')}"

        # Group anomalies by type
        by_type = {}
        for anomaly in anomalies:
            atype = anomaly['anomaly_type']
            if atype not in by_type:
                by_type[atype] = []
            by_type[atype].append(anomaly)

        anomaly_summary = "\n".join([
            f"- {len(items)} anomalies detected using {atype} method"
            for atype, items in by_type.items()
        ])

        prompt = f"""Analyze the following traffic anomalies {period} and provide actionable insights:

{anomaly_summary}

Total anomalies detected: {len(anomalies)}

Based on these anomalies, provide 3-5 bullet-point suggestions for traffic management. Focus on:
1. Potential causes of the anomalies
2. Safety concerns
3. Recommended actions

Keep each bullet point concise (1-2 sentences).
"""

        return prompt

    async def _call_ollama(self, prompt: str) -> str:
        """Make API call to Ollama"""

        endpoint = f"{self.url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get('response', 'No suggestions generated')


class MockLLMClient:
    """Mock LLM client for testing"""

    def __init__(self):
        self.db = Database()

    async def generate_trend_suggestions(
        self,
        anomalies: List[Dict[str, Any]],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Generate mock trend suggestions"""

        suggestions_text = f"""Based on the analysis of {len(anomalies)} traffic anomalies:

• Unusual traffic patterns detected - consider investigating potential incidents or events
• Speed variations suggest possible congestion or road conditions requiring attention
• Monitor these patterns for recurring issues during similar time periods
• Consider adjusting traffic signal timing if anomalies persist
• Review footage or sensor data for the affected time periods
"""

        suggestion = {
            'time_period_start': start.isoformat() if start else None,
            'time_period_end': end.isoformat() if end else None,
            'suggestion_type': 'anomaly_summary',
            'confidence_level': 0.8,
            'description': suggestions_text,
            'related_anomalies': [a['traffic_event_id'] for a in anomalies[:10]]
        }

        suggestion_id = self.db.insert_trend_suggestion(suggestion)
        suggestion['id'] = suggestion_id

        return [suggestion]
