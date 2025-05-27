## 2. Memory Manager (`src/utils/memory.py`)

"""
Memory management and optimization utilities
"""
import gc
import psutil
import threading
import time
from typing import Dict, Any, Optional

class MemoryManager:
    """Memory management and optimization"""

    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.monitoring = True

        # Start memory monitoring
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()

    def _monitor_memory(self):
        """Background memory monitoring"""
        while self.monitoring:
            try:
                memory = psutil.virtual_memory()

                if memory.percent > self.max_memory_percent:
                    print(f"⚠️ High memory usage: {memory.percent:.1f}%")
                    self.cleanup_memory()

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                print(f"Memory monitoring error: {e}")

    def cleanup_memory(self):
        """Force memory cleanup"""
        print("🧹 Cleaning up memory...")

        # Force garbage collection
        collected = gc.collect()
        print(f"   Collected {collected} objects")

        # Get memory info after cleanup
        memory = psutil.virtual_memory()
        print(f"   Memory usage: {memory.percent:.1f}%")

    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        memory = psutil.virtual_memory()

        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'percentage': memory.percent,
            'status': 'critical' if memory.percent > 90 else
            'warning' if memory.percent > 80 else 'normal'
        }

    def stop(self):
        """Stop memory monitoring"""
        self.monitoring = False