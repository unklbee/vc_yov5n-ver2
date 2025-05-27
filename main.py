# Entry Point and Essential Utilities

## Main Entry Point (`main.py`)

#!/usr/bin/env python3
"""
Vehicle Detection System - Optimized Entry Point
"""
import sys
import os
import argparse
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []

    # Core dependencies
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")

    # GUI dependencies (optional)
    gui_available = True
    try:
        import PySide6
    except ImportError:
        gui_available = False
        print("⚠️ PySide6 not available - GUI mode disabled")

    if missing:
        print("❌ Missing required dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False, False

    return True, gui_available

def run_gui_mode(config_path: str = None):
    """Run GUI mode"""
    try:
        from gui.app import run_app
        print("🚀 Starting GUI mode...")
        run_app(config_path)
    except ImportError as e:
        print(f"❌ GUI mode not available: {e}")
        print("Install PySide6: pip install PySide6")
        return False
    except Exception as e:
        print(f"❌ GUI error: {e}")
        return False
    return True

def run_cli_mode(args):
    """Run CLI mode"""
    try:
        from src.cli.cli_interface import run_cli
        print("🚀 Starting CLI mode...")
        return run_cli(args)
    except Exception as e:
        print(f"❌ CLI error: {e}")
        return False

def run_test_mode():
    """Run simple test mode"""
    print("🧪 Running test mode...")

    try:
        # Test configuration
        from src.utils.config import ConfigManager
        config_manager = ConfigManager()
        print("✅ Configuration manager working")

        # Test video source
        from src.utils.video_source import VideoSource
        print("✅ Video source module working")

        # Test detector (mock)
        from src.core.detector import VehicleDetector
        detector = VehicleDetector("dummy_model.xml", {"device": "CPU"})
        print("✅ Detector module working")

        print("\n🎉 All core components are working!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Vehicle Detection System - Optimized Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run GUI mode
  %(prog)s --mode cli --source 0     # Run CLI with webcam
  %(prog)s --mode cli --source video.mp4  # Run CLI with video file
  %(prog)s --test                    # Run test mode
        """
    )

    parser.add_argument(
        "--mode",
        choices=["gui", "cli"],
        default="gui",
        help="Application mode (default: gui)"
    )

    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Configuration file path (default: config/default.yaml)"
    )

    parser.add_argument(
        "--source",
        help="Video source (file path, camera ID, or RTSP URL)"
    )

    parser.add_argument(
        "--model",
        help="Model file path (overrides config)"
    )

    parser.add_argument(
        "--device",
        choices=["CPU", "GPU"],
        help="Processing device (overrides config)"
    )

    parser.add_argument(
        "--output",
        help="Output video file path (CLI mode only)"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test mode to check components"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Print header
    print("🚗 Vehicle Detection System - Optimized Edition")
    print("=" * 55)

    # Test mode
    if args.test:
        success = run_test_mode()
        sys.exit(0 if success else 1)

    # Check dependencies
    deps_ok, gui_available = check_dependencies()
    if not deps_ok:
        sys.exit(1)

    # Force CLI mode if GUI not available
    if args.mode == "gui" and not gui_available:
        print("⚠️ GUI not available, switching to CLI mode")
        args.mode = "cli"
        if not args.source:
            print("❌ CLI mode requires --source argument")
            sys.exit(1)

    # Run application
    try:
        if args.mode == "gui":
            success = run_gui_mode(args.config)
        else:
            success = run_cli_mode(args)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()