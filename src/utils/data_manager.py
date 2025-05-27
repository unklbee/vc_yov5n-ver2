"""
src/utils/data_manager.py
Data storage and API management
"""

import json
import csv
import os
import requests
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class CountData:
    """Vehicle count data structure"""
    timestamp: str
    vehicle_counts: Dict[str, Dict[str, int]]
    total_count: int
    fps: float
    line_statistics: List[Dict]


class DataManager:
    """Manages data storage and API communication"""

    def __init__(self, config: Dict[str, Any]):
        self.storage_config = config.get('data_storage', {})
        self.api_config = config.get('api', {})

        self.output_dir = self.storage_config.get('output_directory', 'data/counts')
        self.save_interval = self.storage_config.get('save_interval', 300)
        self.format = self.storage_config.get('format', 'json')

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Data buffer
        self.data_buffer = []
        self.last_save_time = time.time()
        self.last_api_send_time = time.time()

        # API settings
        self.api_enabled = self.api_config.get('enabled', False)
        self.api_endpoint = self.api_config.get('endpoint', '')
        self.api_key = self.api_config.get('api_key', '')
        self.api_interval = self.api_config.get('send_interval', 60)
        self.api_timeout = self.api_config.get('timeout', 30)

        # Background thread for periodic tasks
        self.running = True
        self.background_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.background_thread.start()

    def add_count_data(self, vehicle_counts: Dict, fps: float, line_statistics: List[Dict]):
        """Add new count data to buffer"""
        timestamp = datetime.now().isoformat()
        total_count = sum(sum(counts.values()) for counts in vehicle_counts.values())

        count_data = CountData(
            timestamp=timestamp,
            vehicle_counts=vehicle_counts,
            total_count=total_count,
            fps=fps,
            line_statistics=line_statistics
        )

        self.data_buffer.append(count_data)

        # Check if it's time to save
        current_time = time.time()
        if current_time - self.last_save_time >= self.save_interval:
            self._save_data()
            self.last_save_time = current_time

        # Check if it's time to send API data
        if (self.api_enabled and current_time - self.last_api_send_time >= self.api_interval):
            self._send_api_data(count_data)
            self.last_api_send_time = current_time

    def _save_data(self):
        """Save buffered data to file"""
        if not self.data_buffer:
            return

        try:
            if self.storage_config.get('enabled', True):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                if self.format in ['json', 'both']:
                    self._save_json(timestamp)

                if self.format in ['csv', 'both']:
                    self._save_csv(timestamp)

                print(f"✅ Data saved: {len(self.data_buffer)} records")

            # Clear buffer after saving
            self.data_buffer = []

        except Exception as e:
            print(f"❌ Error saving data: {e}")

    def _save_json(self, timestamp: str):
        """Save data as JSON"""
        filename = f"vehicle_counts_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        data = {
            'metadata': {
                'saved_at': datetime.now().isoformat(),
                'record_count': len(self.data_buffer),
                'interval_seconds': self.save_interval
            },
            'records': [
                {
                    'timestamp': record.timestamp,
                    'vehicle_counts': record.vehicle_counts,
                    'total_count': record.total_count,
                    'fps': record.fps,
                    'line_statistics': record.line_statistics
                }
                for record in self.data_buffer
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_csv(self, timestamp: str):
        """Save data as CSV"""
        filename = f"vehicle_counts_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            header = ['timestamp', 'total_count', 'fps', 'car_up', 'car_down',
                      'motorcycle_up', 'motorcycle_down', 'bus_up', 'bus_down',
                      'truck_up', 'truck_down', 'lines_crossed']
            writer.writerow(header)

            # Write data
            for record in self.data_buffer:
                row = [
                    record.timestamp,
                    record.total_count,
                    record.fps,
                    record.vehicle_counts.get('car', {}).get('up', 0),
                    record.vehicle_counts.get('car', {}).get('down', 0),
                    record.vehicle_counts.get('motorcycle', {}).get('up', 0),
                    record.vehicle_counts.get('motorcycle', {}).get('down', 0),
                    record.vehicle_counts.get('bus', {}).get('up', 0),
                    record.vehicle_counts.get('bus', {}).get('down', 0),
                    record.vehicle_counts.get('truck', {}).get('up', 0),
                    record.vehicle_counts.get('truck', {}).get('down', 0),
                    len(record.line_statistics)
                ]
                writer.writerow(row)

    def _send_api_data(self, count_data: CountData):
        """Send data to API endpoint"""
        if not self.api_endpoint:
            return

        try:
            payload = {
                'timestamp': count_data.timestamp,
                'vehicle_counts': count_data.vehicle_counts,
                'total_count': count_data.total_count,
                'fps': count_data.fps,
                'line_statistics': count_data.line_statistics
            }

            headers = {
                'Content-Type': 'application/json'
            }

            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                timeout=self.api_timeout
            )

            if response.status_code == 200:
                print(f"✅ Data sent to API successfully")
            else:
                print(f"❌ API error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Error sending data to API: {e}")

    def _background_worker(self):
        """Background worker for periodic tasks"""
        while self.running:
            try:
                time.sleep(30)  # Check every 30 seconds

                # Force save if buffer is getting large
                if len(self.data_buffer) > 100:
                    self._save_data()

            except Exception as e:
                print(f"❌ Background worker error: {e}")

    def force_save(self):
        """Force save current buffer"""
        self._save_data()

    def get_statistics(self) -> Dict[str, Any]:
        """Get data manager statistics"""
        return {
            'buffer_size': len(self.data_buffer),
            'last_save_time': datetime.fromtimestamp(self.last_save_time).isoformat(),
            'api_enabled': self.api_enabled,
            'storage_enabled': self.storage_config.get('enabled', True),
            'output_directory': self.output_dir
        }

    def stop(self):
        """Stop background processes and save remaining data"""
        self.running = False
        if hasattr(self, 'background_thread'):
            self.background_thread.join(timeout=5)
        self.force_save()


class APITester:
    """Test API endpoint connectivity"""

    @staticmethod
    def test_connection(endpoint: str, api_key: str = "", timeout: int = 10) -> Dict[str, Any]:
        """Test API endpoint connection"""
        try:
            headers = {'Content-Type': 'application/json'}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            # Test with minimal payload
            test_payload = {
                'test': True,
                'timestamp': datetime.now().isoformat()
            }

            response = requests.post(
                endpoint,
                json=test_payload,
                headers=headers,
                timeout=timeout
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'message': f"Connection successful: {response.status_code}"
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Connection timeout',
                'message': f"Request timed out after {timeout} seconds"
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection error',
                'message': "Could not connect to the endpoint"
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Unknown error',
                'message': str(e)
            }