"""
Drone-optimized configuration file.

This configuration is tuned for real-time processing on Raspberry Pi 4/5
with focus on obstacle detection rather than detailed motion analysis.
"""


class DroneOptimizedConfig:
    """
    Configuration optimized for drone operation with Raspberry Pi.
    
    Key differences from default config:
    - Smaller grid for faster processing
    - Larger search steps for speed
    - Disabled recursive subdivision
    - Reduced visualization overhead
    - Frame skipping for real-time operation
    """
    
    # ============================================================================
    # HARDWARE SETTINGS
    # ============================================================================
    
    # Camera configuration
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Processing resolution (images downscaled to this before processing)
    # Smaller = faster processing, less detail
    PROCESSING_WIDTH = 416  # or 320 for even faster
    PROCESSING_HEIGHT = 416  # or 320 for even faster
    
    # ============================================================================
    # MOTION DETECTION SETTINGS (Simplified for speed)
    # ============================================================================
    
    # Grid subdivision - REDUCED from default 5x5
    GRID_ROWS = 3  # Was 5 - fewer sections = faster processing
    GRID_COLS = 3  # Was 5
    
    # Motion detection
    SEARCH_STEP_SIZE = 2  # Was 1 - larger steps = faster but less precise
    MOTION_THRESHOLD = 0.3  # Minimum motion strength to consider significant
    
    # Recursive analysis - DISABLED for drone use
    MAX_RECURSIVE_DEPTH = 0  # Was 2 - recursion too slow for real-time
    RECURSIVE_SUBDIVISION_FACTOR = 2
    
    # Border sections
    EXCLUDE_BORDER_SECTIONS = True  # Skip edge sections
    
    # ============================================================================
    # REAL-TIME PROCESSING SETTINGS
    # ============================================================================
    
    # Frame processing
    FRAME_SKIP = 2  # Process every 2nd frame (15 FPS from 30 FPS camera)
    # FRAME_SKIP = 3  # Use 3 for even more speed (10 FPS)
    MAX_FRAMES = None  # Process all frames
    SKIP_FRAMES = 0  # Don't skip initial frames
    
    # Performance limits
    MAX_PROCESSING_TIME_MS = 50  # Maximum 50ms per frame (20 FPS target)
    
    # ============================================================================
    # VISUALIZATION SETTINGS (Minimal for performance)
    # ============================================================================
    
    # Disable heavy visualization features
    SHOW_MOTION_VECTORS = False  # Arrows are slow to draw
    SHOW_GRID_LINES = False  # Lines add overhead
    COLOR_CODE_MOTION = False  # Color coding adds computation
    SHOW_COMPASS = False  # Compass legend takes space and time
    SHOW_OVERALL_DIRECTION = True  # Keep this - useful for navigation
    
    VECTOR_SCALE = 3.0
    
    # ============================================================================
    # OBSTACLE DETECTION SETTINGS
    # ============================================================================
    
    # Depth-based obstacle detection (for RealSense camera)
    DANGER_DISTANCE_METERS = 3.0  # Red alert if obstacle within 3m
    WARNING_DISTANCE_METERS = 5.0  # Yellow warning if within 5m
    MIN_OBSTACLE_SIZE_PIXELS = 100  # Minimum size to consider as obstacle
    
    # Zone configuration (divide view into left/center/right)
    ENABLE_ZONE_DETECTION = True
    NUM_HORIZONTAL_ZONES = 3  # Left, center, right
    
    # ============================================================================
    # SAFETY SETTINGS
    # ============================================================================
    
    # Watchdog timers
    MAX_FRAME_AGE_MS = 200  # Alert if frame is older than 200ms
    MAX_NO_FRAME_TIME_MS = 1000  # Alert if no new frame for 1 second
    
    # Failsafe behavior
    EMERGENCY_STOP_ON_CRITICAL_OBSTACLE = False  # Let flight controller handle
    ALERT_ON_SLOW_PROCESSING = True  # Warn if processing too slow
    
    # ============================================================================
    # DIRECTION DEFINITIONS (Same as original)
    # ============================================================================
    
    # 8 directional offsets (dx, dy)
    DIRECTIONS = [
        (0, -1),   # North
        (1, -1),   # Northeast
        (1, 0),    # East
        (1, 1),    # Southeast
        (0, 1),    # South
        (-1, 1),   # Southwest
        (-1, 0),   # West
        (-1, -1)   # Northwest
    ]
    
    DIRECTION_NAMES = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    DIRECTION_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]  # degrees
    
    # ============================================================================
    # DATA LOGGING SETTINGS
    # ============================================================================
    
    # Flight data logging
    ENABLE_LOGGING = True
    LOG_DIRECTORY = "/home/pi/flight_logs"  # Or SD card mount point
    LOG_OBSTACLES = True
    LOG_MOTION_DATA = True
    LOG_CAMERA_FRAMES = False  # Set True to save frames (uses lots of space)
    LOG_DEPTH_DATA = True
    
    # ============================================================================
    # 3D MAPPING SETTINGS
    # ============================================================================
    
    # SLAM/Mapping configuration
    ENABLE_3D_MAPPING = False  # Disable for obstacle detection only mode
    MAPPING_BACKEND = 'simple'  # 'simple', 'rtabmap', 'orbslam'
    MAPPING_RESOLUTION = 0.05  # 5cm voxel size
    MAX_MAP_SIZE_MB = 500  # Limit map size
    
    # ============================================================================
    # COMMUNICATION SETTINGS
    # ============================================================================
    
    # MAVLink connection for flight controller
    MAVLINK_CONNECTION = '/dev/ttyACM0'  # Or 'udp:127.0.0.1:14550' for SITL
    MAVLINK_BAUD = 57600
    
    # Ground station communication
    ENABLE_TELEMETRY = True
    TELEMETRY_PORT = 14551  # UDP port for ground station
    SEND_VIDEO_STREAM = False  # Warning: bandwidth intensive
    
    # ============================================================================
    # PERFORMANCE PROFILING
    # ============================================================================
    
    ENABLE_PROFILING = True  # Measure timing of each component
    PRINT_TIMING_EVERY_N_FRAMES = 30  # Print stats every 30 frames
    
    @classmethod
    def summary(cls):
        """Print configuration summary."""
        print("=" * 70)
        print("DRONE OPTIMIZED CONFIGURATION")
        print("=" * 70)
        print(f"Camera: {cls.CAMERA_WIDTH}x{cls.CAMERA_HEIGHT} @ {cls.CAMERA_FPS} FPS")
        print(f"Processing: {cls.PROCESSING_WIDTH}x{cls.PROCESSING_HEIGHT}")
        print(f"Grid: {cls.GRID_ROWS}x{cls.GRID_COLS}")
        print(f"Search step: {cls.SEARCH_STEP_SIZE} pixels")
        print(f"Recursive depth: {cls.MAX_RECURSIVE_DEPTH}")
        print(f"Frame skip: {cls.FRAME_SKIP} (effective FPS: {cls.CAMERA_FPS//cls.FRAME_SKIP})")
        print(f"Danger distance: {cls.DANGER_DISTANCE_METERS}m")
        print(f"Warning distance: {cls.WARNING_DISTANCE_METERS}m")
        print(f"3D Mapping: {'Enabled' if cls.ENABLE_3D_MAPPING else 'Disabled'}")
        print(f"Visualization: Minimal (performance mode)")
        print("=" * 70)


class GroundStationConfig(DroneOptimizedConfig):
    """
    Configuration for ground station testing (more visualization, less speed focus).
    Inherits from DroneOptimizedConfig but enables more features for debugging.
    """
    
    # Enable visualization for testing
    SHOW_MOTION_VECTORS = True
    SHOW_GRID_LINES = True
    COLOR_CODE_MOTION = True
    SHOW_COMPASS = True
    
    # No frame skipping for testing
    FRAME_SKIP = 1
    
    # Enable frame saving for analysis
    LOG_CAMERA_FRAMES = True
    
    # Enable detailed profiling
    PRINT_TIMING_EVERY_N_FRAMES = 10


class SimulationConfig(DroneOptimizedConfig):
    """
    Configuration for SITL (Software In The Loop) simulation testing.
    """
    
    # Simulation connection
    MAVLINK_CONNECTION = 'udp:127.0.0.1:14550'
    
    # Enable all logging for analysis
    LOG_CAMERA_FRAMES = True
    ENABLE_PROFILING = True
    
    # Can use higher quality since simulation PC is more powerful
    PROCESSING_WIDTH = 640
    PROCESSING_HEIGHT = 480
    FRAME_SKIP = 1


# ============================================================================
# PERFORMANCE COMPARISON
# ============================================================================

class ConfigComparison:
    """Compare original config vs drone-optimized config."""
    
    @staticmethod
    def print_comparison():
        """Print side-by-side comparison."""
        print("\n" + "=" * 90)
        print("CONFIGURATION COMPARISON")
        print("=" * 90)
        print(f"{'Parameter':<30} {'Original':<25} {'Drone Optimized':<25}")
        print("-" * 90)
        
        # Import original config for comparison
        try:
            from config import Config as OriginalConfig
            
            comparisons = [
                ('GRID_ROWS', OriginalConfig.GRID_ROWS, DroneOptimizedConfig.GRID_ROWS),
                ('GRID_COLS', OriginalConfig.GRID_COLS, DroneOptimizedConfig.GRID_COLS),
                ('SEARCH_STEP_SIZE', OriginalConfig.SEARCH_STEP_SIZE, DroneOptimizedConfig.SEARCH_STEP_SIZE),
                ('MAX_RECURSIVE_DEPTH', OriginalConfig.MAX_RECURSIVE_DEPTH, DroneOptimizedConfig.MAX_RECURSIVE_DEPTH),
                ('FRAME_SKIP', OriginalConfig.FRAME_SKIP, DroneOptimizedConfig.FRAME_SKIP),
                ('SHOW_MOTION_VECTORS', OriginalConfig.SHOW_MOTION_VECTORS, DroneOptimizedConfig.SHOW_MOTION_VECTORS),
            ]
            
            for param, original, optimized in comparisons:
                change = "✓ Same" if original == optimized else "→ Changed"
                print(f"{param:<30} {str(original):<25} {str(optimized):<25} {change}")
            
            # Calculate speedup estimate
            sections_original = (OriginalConfig.GRID_ROWS - 2) * (OriginalConfig.GRID_COLS - 2)
            sections_optimized = (DroneOptimizedConfig.GRID_ROWS - 2) * (DroneOptimizedConfig.GRID_COLS - 2)
            
            speedup = sections_original / sections_optimized
            speedup *= (DroneOptimizedConfig.SEARCH_STEP_SIZE / OriginalConfig.SEARCH_STEP_SIZE)
            speedup *= DroneOptimizedConfig.FRAME_SKIP
            
            print("-" * 90)
            print(f"Estimated speedup: {speedup:.1f}x faster")
            print(f"Sections to analyze: {sections_original} → {sections_optimized}")
            print("=" * 90 + "\n")
            
        except ImportError:
            print("Could not import original config for comparison")


if __name__ == "__main__":
    # Print configuration summary
    DroneOptimizedConfig.summary()
    
    # Print comparison
    ConfigComparison.print_comparison()
    
    print("\nConfiguration profiles available:")
    print("  - DroneOptimizedConfig: For real-time flight")
    print("  - GroundStationConfig: For testing/development")
    print("  - SimulationConfig: For SITL simulation")
