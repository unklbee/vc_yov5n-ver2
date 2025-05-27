"""
src/utils/config_manager.py
Configuration management system
"""

import yaml
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DetectionConfig:
    """Detection configuration"""
    model_path: str = "models/yolov5n-416.xml"
    device: str = "CPU"
    input_shape: tuple = (416, 416)
    conf_threshold: float = 0.25
    nms_threshold: float = 0.5
    frame_skip: int = 2


@dataclass
class TrackerConfig:
    """Tracker configuration"""
    max_age: int = 1
    min_hits: int = 3
    iou_threshold: float = 0.3
    trail_length: int = 30


@dataclass
class APIConfig:
    """API configuration"""
    enabled: bool = False
    endpoint: str = ""
    api_key: str = ""
    send_interval: int = 60  # seconds
    timeout: int = 30


@dataclass
class DataStorageConfig:
    """Data storage configuration"""
    enabled: bool = True
    save_interval: int = 300  # seconds
    output_directory: str = "data/counts"
    format: str = "json"  # json, csv, both


@dataclass
class UIConfig:
    """UI configuration"""
    window_title: str = "Vehicle Detection System"
    default_width: int = 1200
    default_height: int = 800
    theme: str = "light"


@dataclass
class SystemConfig:
    """Complete system configuration"""
    detection: DetectionConfig
    tracker: TrackerConfig
    api: APIConfig
    data_storage: DataStorageConfig
    ui: UIConfig


class ConfigManager:
    """Configuration manager"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/default.yaml"
        self.config = self._load_default_config()

        if os.path.exists(self.config_path):
            self.load_config(self.config_path)

    def _load_default_config(self) -> SystemConfig:
        """Load default configuration"""
        return SystemConfig(
            detection=DetectionConfig(),
            tracker=TrackerConfig(),
            api=APIConfig(),
            data_storage=DataStorageConfig(),
            ui=UIConfig()
        )

    def load_config(self, config_path: str) -> bool:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            self._update_config_from_dict(data)
            self.config_path = config_path
            print(f"✅ Configuration loaded from {config_path}")
            return True

        except Exception as e:
            print(f"❌ Error loading config from {config_path}: {e}")
            return False

    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save configuration to file"""
        path = config_path or self.config_path

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            config_dict = asdict(self.config)

            with open(path, 'w', encoding='utf-8') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)

            print(f"✅ Configuration saved to {path}")
            return True

        except Exception as e:
            print(f"❌ Error saving config to {path}: {e}")
            return False

    def _update_config_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        if 'detection' in data:
            detection_data = data['detection']
            self.config.detection = DetectionConfig(**{
                k: v for k, v in detection_data.items()
                if k in DetectionConfig.__annotations__
            })

        if 'tracker' in data:
            tracker_data = data['tracker']
            self.config.tracker = TrackerConfig(**{
                k: v for k, v in tracker_data.items()
                if k in TrackerConfig.__annotations__
            })

        if 'api' in data:
            api_data = data['api']
            self.config.api = APIConfig(**{
                k: v for k, v in api_data.items()
                if k in APIConfig.__annotations__
            })

        if 'data_storage' in data:
            storage_data = data['data_storage']
            self.config.data_storage = DataStorageConfig(**{
                k: v for k, v in storage_data.items()
                if k in DataStorageConfig.__annotations__
            })

        if 'ui' in data:
            ui_data = data['ui']
            self.config.ui = UIConfig(**{
                k: v for k, v in ui_data.items()
                if k in UIConfig.__annotations__
            })

    def get_detection_config(self) -> Dict[str, Any]:
        """Get detection configuration as dict"""
        return asdict(self.config.detection)

    def get_tracker_config(self) -> Dict[str, Any]:
        """Get tracker configuration as dict"""
        return asdict(self.config.tracker)

    def update_detection_config(self, **kwargs):
        """Update detection configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.detection, key):
                setattr(self.config.detection, key, value)

    def update_api_config(self, **kwargs):
        """Update API configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.api, key):
                setattr(self.config.api, key, value)

    def update_storage_config(self, **kwargs):
        """Update storage configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.data_storage, key):
                setattr(self.config.data_storage, key, value)