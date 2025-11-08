import time
import requests
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class TrafficDataGenerator:
    """Generate realistic mock traffic data"""

    def __init__(self):
        self.location_ids = [1, 2, 3, 4, 5]
        self.colors = ['white', 'black', 'silver', 'gray', 'red', 'blue', 'brown', 'green', 'yellow']
        self.color_probabilities = [0.24, 0.22, 0.16, 0.14, 0.10, 0.08, 0.03, 0.02, 0.01]

    def generate_event(self) -> Dict[str, Any]:
        """Generate a single traffic event"""
        now = datetime.now()
        hour = now.hour

        # Simulate rush hour patterns
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            # Rush hour
            vehicle_count = random.randint(40, 100)
            avg_speed = random.gauss(25, 8)  # Slower during rush hour
            density_score = random.uniform(0.7, 1.0)
        elif 22 <= hour or hour <= 5:
            # Night time
            vehicle_count = random.randint(5, 20)
            avg_speed = random.gauss(50, 10)
            density_score = random.uniform(0.1, 0.3)
        else:
            # Normal hours
            vehicle_count = random.randint(20, 60)
            avg_speed = random.gauss(40, 12)
            density_score = random.uniform(0.4, 0.7)

        # Ensure speed is positive
        avg_speed = max(5, avg_speed)
        min_speed = max(5, avg_speed - random.uniform(5, 15))
        max_speed = avg_speed + random.uniform(10, 25)

        # Generate color distribution
        color_counts = {}
        remaining = vehicle_count
        for color, prob in zip(self.colors, self.color_probabilities):
            if remaining <= 0:
                break
            count = int(vehicle_count * prob * random.uniform(0.8, 1.2))
            count = min(count, remaining)
            if count > 0:
                color_counts[color] = count
                remaining -= count

        # Generate inter-arrival statistics
        mean_interval = 3600 / vehicle_count if vehicle_count > 0 else 60
        inter_arrival_stats = {
            'mean': mean_interval,
            'std': mean_interval * 0.4,
            'min': max(0.5, mean_interval * 0.2),
            'max': mean_interval * 2.5
        }

        # Occasionally inject anomalies for testing
        if random.random() < 0.05:  # 5% chance of anomaly
            anomaly_type = random.choice(['high_speed', 'low_speed', 'high_density', 'low_density'])

            if anomaly_type == 'high_speed':
                avg_speed *= 1.8
                max_speed *= 2.0
            elif anomaly_type == 'low_speed':
                avg_speed *= 0.3
                min_speed *= 0.2
            elif anomaly_type == 'high_density':
                vehicle_count = int(vehicle_count * 2.5)
                density_score = min(1.0, density_score * 1.5)
            elif anomaly_type == 'low_density':
                vehicle_count = max(1, int(vehicle_count * 0.3))
                density_score *= 0.3

        return {
            'timestamp': now.isoformat(),
            'location_id': random.choice(self.location_ids),
            'vehicle_count': int(vehicle_count),
            'avg_speed': round(avg_speed, 2),
            'min_speed': round(min_speed, 2),
            'max_speed': round(max_speed, 2),
            'color_counts': color_counts,
            'inter_arrival_stats': inter_arrival_stats,
            'traffic_density_score': round(density_score, 3),
            'raw_features': {
                'weather': random.choice(['clear', 'rainy', 'cloudy']),
                'visibility': random.choice(['good', 'moderate', 'poor'])
            }
        }


class TrafficPublisher:
    """Publish traffic events to backend API"""

    def __init__(self, backend_url: str, interval: int):
        self.backend_url = backend_url.rstrip('/')
        self.interval = interval
        self.generator = TrafficDataGenerator()
        self.max_retries = 3
        self.retry_delay = 2

    def publish_event(self, event: Dict[str, Any]) -> bool:
        """Publish a single event to the backend"""
        endpoint = f"{self.backend_url}/ingest/traffic"

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    endpoint,
                    json=event,
                    timeout=5
                )

                if response.status_code == 201:
                    print(f"✓ Published event: location={event['location_id']}, vehicles={event['vehicle_count']}, speed={event['avg_speed']:.1f}")
                    return True
                else:
                    print(f"✗ Failed to publish event: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))

            except requests.exceptions.RequestException as e:
                print(f"✗ Connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))

        return False

    def run(self):
        """Main loop to generate and publish events"""
        print(f"Starting traffic event publisher...")
        print(f"Backend URL: {self.backend_url}")
        print(f"Publish interval: {self.interval} seconds")
        print()

        while True:
            event = self.generator.generate_event()
            self.publish_event(event)
            time.sleep(self.interval)


if __name__ == '__main__':
    backend_host = os.getenv('BACKEND_HOST', 'backend')
    backend_port = os.getenv('BACKEND_PORT', '3000')
    backend_url = f"http://{backend_host}:{backend_port}"

    interval = int(os.getenv('PUBLISH_INTERVAL', '10'))

    publisher = TrafficPublisher(backend_url, interval)

    # Wait for backend to be ready
    print("Waiting for backend to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{backend_url}/health", timeout=2)
            if response.status_code == 200:
                print("Backend is ready!")
                break
        except:
            pass
        time.sleep(2)
    else:
        print("Warning: Backend health check failed, but continuing anyway...")

    publisher.run()
