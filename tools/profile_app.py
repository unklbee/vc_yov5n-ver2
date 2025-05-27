## 6. Profile Script (`tools/profile_app.py`)

#!/usr/bin/env python3
"""
Application profiling tool
"""
import sys
import cProfile
import pstats
import io
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def profile_detection():
    """Profile detection performance"""
    from src.core.detector import VehicleDetector
    from src.utils.config import ConfigManager
    import numpy as np

    print("🔍 Profiling detection performance...")

    # Create detector
    config_manager = ConfigManager()
    config = config_manager.get_detection_dict()
    detector = VehicleDetector(config['model_path'], config)

    # Create test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def run_detection():
        for _ in range(50):
            detector.detect(frame)

    # Profile
    profiler = cProfile.Profile()
    profiler.enable()
    run_detection()
    profiler.disable()

    # Print results
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions

    print(s.getvalue())

    # Save profile data
    profiler.dump_stats('detection_profile.prof')
    print("📊 Profile saved to detection_profile.prof")

def profile_gui():
    """Profile GUI performance"""
    print("🖥️ Profiling GUI performance...")

    from src.gui.app import run_app

    def run_gui_simulation():
        # Simulate GUI operations
        pass

    # Profile GUI operations
    profiler = cProfile.Profile()
    profiler.enable()
    run_gui_simulation()
    profiler.disable()

    # Save results
    profiler.dump_stats('gui_profile.prof')
    print("📊 GUI profile saved to gui_profile.prof")

def analyze_profile(profile_file: str):
    """Analyze existing profile file"""
    print(f"📈 Analyzing profile: {profile_file}")

    stats = pstats.Stats(profile_file)

    print("\n⏱️ Top functions by cumulative time:")
    stats.sort_stats('cumulative').print_stats(15)

    print("\n🔥 Top functions by own time:")
    stats.sort_stats('tottime').print_stats(15)

    print("\n📞 Most called functions:")
    stats.sort_stats('ncalls').print_stats(15)

def main():
    """Main profiling function"""
    import argparse

    parser = argparse.ArgumentParser(description="Application Profiling Tool")
    parser.add_argument("--detection", action="store_true", help="Profile detection")
    parser.add_argument("--gui", action="store_true", help="Profile GUI")
    parser.add_argument("--analyze", help="Analyze existing profile file")

    args = parser.parse_args()

    try:
        if args.analyze:
            analyze_profile(args.analyze)
        elif args.detection:
            profile_detection()
        elif args.gui:
            profile_gui()
        else:
            print("Please specify --detection, --gui, or --analyze")

    except Exception as e:
        print(f"❌ Profiling error: {e}")

if __name__ == "__main__":
    main()