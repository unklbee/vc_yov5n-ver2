#!/usr/bin/env python3
"""
quick_setup.py
Quick setup script untuk Vehicle Detection System
"""

import os
import sys
from pathlib import Path
import yaml

def create_directories():
    """Create necessary directories"""
    directories = [
        "src/core",
        "src/gui/widgets",
        "src/gui/dialogs",
        "src/gui/styles",
        "src/cli",
        "src/utils",
        "config",
        "models",
        "data/counts",
        "tests"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_init_files():
    """Create __init__.py files"""
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/gui/__init__.py",
        "src/gui/widgets/__init__.py",
        "src/gui/dialogs/__init__.py",
        "src/gui/styles/__init__.py",
        "src/cli/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py"
    ]

    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")

def create_default_config():
    """Create default configuration"""
    config = {
        'detection': {
            'model_path': 'models/yolov5n-416.xml',
            'device': 'CPU',
            'input_shape': [416, 416],
            'conf_threshold': 0.25,
            'nms_threshold': 0.5,
            'frame_skip': 2
        },
        'tracker': {
            'max_age': 1,
            'min_hits': 3,
            'iou_threshold': 0.3,
            'trail_length': 30
        },
        'api': {
            'enabled': False,
            'endpoint': '',
            'api_key': '',
            'send_interval': 60,
            'timeout': 30
        },
        'data_storage': {
            'enabled': True,
            'save_interval': 300,
            'output_directory': 'data/counts',
            'format': 'json'
        },
        'ui': {
            'window_title': 'Vehicle Detection System',
            'default_width': 1200,
            'default_height': 800,
            'theme': 'dark'
        }
    }

    config_file = Path("config/default.yaml")
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print(f"✅ Created configuration: {config_file}")

def create_simple_main():
    """Create a simple main.py for testing"""
    main_content = '''#!/usr/bin/env python3
"""
Simple main.py for testing
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🚗 Vehicle Detection System")
    print("Setting up...")
    
    try:
        # Test config manager
        from utils.config_manager import ConfigManager
        config_manager = ConfigManager("config/default.yaml")
        print(f"✅ Config loaded successfully")
        print(f"   Model path: {config_manager.config.detection.model_path}")
        print(f"   Device: {config_manager.config.detection.device}")
        
        # Test GUI import
        try:
            from gui.main_window import run_gui_app
            print("✅ GUI components available")
            print("   Starting GUI...")
            run_gui_app()
        except ImportError as e:
            print(f"⚠️ GUI not available: {e}")
            print("   Install PySide6: pip install PySide6")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    with open("main.py", 'w', encoding='utf-8') as f:
        f.write(main_content)

    print("✅ Created simple main.py")

def create_requirements():
    """Create requirements.txt"""
    requirements = """# Core dependencies
opencv-python>=4.5.0
numpy>=1.21.0
openvino>=2022.1.0

# Configuration management
PyYAML>=6.0
dataclasses; python_version<"3.7"

# Data handling and API
requests>=2.25.0
pandas>=1.3.0

# GUI dependencies - PySide6
PySide6>=6.4.0

# Development dependencies (optional)
# Install with: pip install -e .[dev]
pytest>=6.0.0
black>=21.0.0
flake8>=3.9.0
mypy>=0.910
"""

    with open("requirements.txt", 'w', encoding='utf-8') as f:
        f.write(requirements)

    print("✅ Created requirements.txt")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'),
        ('PyYAML', 'yaml'),
        ('requests', 'requests'),
        ('PySide6', 'PySide6')
    ]

    missing_packages = []
    available_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            available_packages.append(package_name)
        except ImportError:
            missing_packages.append(package_name)

    print("\n📦 Package Status:")
    for package in available_packages:
        print(f"✅ {package}")

    for package in missing_packages:
        print(f"❌ {package} (not installed)")

    if missing_packages:
        print(f"\n⚠️ Missing packages. Install with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n🎉 All required packages are installed!")
        return True

def main():
    """Main setup function"""
    print("🚀 Vehicle Detection System - Quick Setup")
    print("=" * 50)

    # Step 1: Create directories
    print("\n📁 Creating directories...")
    create_directories()

    # Step 2: Create __init__.py files
    print("\n📄 Creating __init__.py files...")
    create_init_files()

    # Step 3: Create configuration
    print("\n⚙️ Creating default configuration...")
    create_default_config()

    # Step 4: Create main.py
    print("\n🐍 Creating main.py...")
    create_simple_main()

    # Step 5: Create requirements.txt
    print("\n📋 Creating requirements.txt...")
    create_requirements()

    # Step 6: Check dependencies
    print("\n🔍 Checking dependencies...")
    deps_ok = check_dependencies()

    print("\n" + "=" * 50)
    print("✅ Quick setup completed!")
    print("\n📋 Next steps:")
    print("1. Copy the artifact code files to their respective locations")
    print("2. Install missing dependencies if any")
    print("3. Add your YOLO model files to the models/ directory")
    print("4. Run: python main.py")

    if not deps_ok:
        print("\n⚠️ Install missing dependencies first!")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()