#!/usr/bin/env python3
"""
test_system.py - Test if the system is working
"""

import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        from src.utils.config_manager import ConfigManager
        print("✅ Config manager import successful")
        
        config = ConfigManager()
        print("✅ Config manager initialization successful")
        
        from src.utils.visualizer import Visualizer
        print("✅ Visualizer import successful")
        
        try:
            from gui.main_window import run_gui_app
            print("✅ GUI components import successful")
            gui_available = True
        except ImportError as e:
            print(f"⚠️ GUI not available: {e}")
            gui_available = False
        
        return gui_available
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 Vehicle Detection System - System Test")
    print("=" * 50)
    
    gui_available = test_imports()
    
    if gui_available:
        print("\n🎉 All systems working! Starting GUI...")
        from src.gui.main_window import run_gui_app
        run_gui_app()
    else:
        print("\n❌ System test failed")
        print("Install missing dependencies:")
        print("pip install PySide6 PyYAML opencv-python numpy")

if __name__ == "__main__":
    main()
