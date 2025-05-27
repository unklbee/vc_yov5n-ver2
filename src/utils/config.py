"""
Complete src/utils/config.py - Configuration Manager
"""

import yaml
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

@dataclass
class DetectionConfig:
    """Detection configuration"""
    model_path: str = "models/yolov5n-416.xml"
    device: str = "CPU"
    input_shape: Tuple[int, int] = (416, 416)
    conf_threshold: float = 0.25
    nms_threshold: float = 0.5
    frame_skip: int = 2

@dataclass
class UIConfig:
    """UI configuration"""
    window_width: int = 1200
    window_height: int = 800
    theme: str = "dark"
    auto_save: bool = True

@dataclass
class StorageConfig:
    """Storage configuration"""
    enabled: bool = True
    save_interval: int = 300
    output_dir: str = "data/counts"
    format: str = "json"

@dataclass
class AppConfig:
    """Main application configuration"""
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)

class ConfigManager:
    """Configuration manager with validation and auto-save"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/default.yaml")
        self.config = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                return self._dict_to_config(data)
            except Exception as e:
                print(f"Config loading failed: {e}, using defaults")

        return AppConfig()

    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to config object"""
        config = AppConfig()

        if 'detection' in data:
            config.detection = DetectionConfig(**data['detection'])
        if 'ui' in data:
            config.ui = UIConfig(**data['ui'])
        if 'storage' in data:
            config.storage = StorageConfig(**data['storage'])

        return config

    def save(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(asdict(self.config), f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Config saving failed: {e}")

    def update_detection(self, **kwargs):
        """Update detection configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.detection, key):
                setattr(self.config.detection, key, value)

        if self.config.ui.auto_save:
            self.save()

    def get_detection_dict(self) -> Dict[str, Any]:
        """Get detection config as dictionary"""
        return asdict(self.config.detection)