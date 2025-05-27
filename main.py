#!/usr/bin/env python3
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
        from src.utils.config_manager import ConfigManager
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
