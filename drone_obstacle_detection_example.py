"""
Example implementation for drone obstacle detection using RealSense camera.

This is a proof-of-concept showing how to adapt the MotionExtraction project
for real-time obstacle detection on a drone.

Requirements:
- Raspberry Pi 4B/5 (8GB recommended)
- Intel RealSense D435i or D455 depth camera
- pyrealsense2 library installed
"""

import cv2
import numpy as np
import pyrealsense2 as rs
from typing import Tuple, List, Optional
import time


class DroneConfig:
    """Optimized configuration for drone operation."""
    # Real-time processing settings
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Processing resolution (downscale for speed)
    PROCESS_WIDTH = 416
    PROCESS_HEIGHT = 416
    
    # Motion detection (simplified from original)
    GRID_ROWS = 3
    GRID_COLS = 3
    FRAME_SKIP = 2  # Process every 2nd frame
    
    # Obstacle detection
    DANGER_DISTANCE = 3.0  # meters
    WARNING_DISTANCE = 5.0  # meters
    MIN_OBSTACLE_SIZE = 100  # pixels
    
    # Safety
    MAX_PROCESSING_TIME = 0.05  # 50ms max per frame (20 FPS)


class ObstacleDetector:
    """
    Simple obstacle detector using depth camera.
    Detects obstacles in the flight path based on depth information.
    """
    
    def __init__(self, config: DroneConfig):
        self.config = config
        
        # Initialize RealSense pipeline
        self.pipeline = rs.pipeline()
        self.rs_config = rs.config()
        
        # Enable streams
        self.rs_config.enable_stream(
            rs.stream.depth,
            config.CAMERA_WIDTH,
            config.CAMERA_HEIGHT,
            rs.format.z16,
            config.CAMERA_FPS
        )
        self.rs_config.enable_stream(
            rs.stream.color,
            config.CAMERA_WIDTH,
            config.CAMERA_HEIGHT,
            rs.format.bgr8,
            config.CAMERA_FPS
        )
        
        # Start streaming
        self.pipeline.start(self.rs_config)
        
        # Get depth scale
        depth_sensor = self.pipeline.get_active_profile().get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        
        print(f"RealSense camera initialized: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.CAMERA_FPS}fps")
        print(f"Depth scale: {self.depth_scale}")
        
    def get_frames(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get color and depth frames from camera.
        
        Returns:
            Tuple of (color_image, depth_image) or (None, None) if failed
        """
        try:
            # Wait for frames
            frames = self.pipeline.wait_for_frames(timeout_ms=1000)
            
            # Get color and depth frames
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            
            if not depth_frame or not color_frame:
                return None, None
            
            # Convert to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            
            return color_image, depth_image
            
        except Exception as e:
            print(f"Error getting frames: {e}")
            return None, None
    
    def detect_obstacles(self, depth_image: np.ndarray) -> dict:
        """
        Detect obstacles in depth image.
        
        Args:
            depth_image: Depth image from RealSense camera (in mm)
            
        Returns:
            Dictionary containing obstacle information:
            - has_obstacle: bool
            - danger_zone: bool (obstacle within danger distance)
            - warning_zone: bool (obstacle within warning distance)
            - closest_distance: float (meters)
            - obstacle_regions: list of (x, y, width, height)
        """
        start_time = time.time()
        
        # Convert depth to meters
        depth_meters = depth_image * self.depth_scale
        
        # Find pixels closer than warning distance
        warning_mask = (depth_meters > 0.1) & (depth_meters < self.config.WARNING_DISTANCE)
        danger_mask = (depth_meters > 0.1) & (depth_meters < self.config.DANGER_DISTANCE)
        
        # Count pixels in each zone
        warning_count = np.sum(warning_mask)
        danger_count = np.sum(danger_mask)
        
        # Find closest obstacle
        valid_depths = depth_meters[depth_meters > 0.1]
        closest_distance = np.min(valid_depths) if len(valid_depths) > 0 else float('inf')
        
        # Divide image into zones (left, center, right)
        height, width = depth_image.shape
        left_zone = danger_mask[:, :width//3]
        center_zone = danger_mask[:, width//3:2*width//3]
        right_zone = danger_mask[:, 2*width//3:]
        
        result = {
            'has_obstacle': warning_count > self.config.MIN_OBSTACLE_SIZE,
            'danger_zone': danger_count > self.config.MIN_OBSTACLE_SIZE,
            'warning_zone': warning_count > self.config.MIN_OBSTACLE_SIZE,
            'closest_distance': closest_distance,
            'left_blocked': np.sum(left_zone) > self.config.MIN_OBSTACLE_SIZE,
            'center_blocked': np.sum(center_zone) > self.config.MIN_OBSTACLE_SIZE,
            'right_blocked': np.sum(right_zone) > self.config.MIN_OBSTACLE_SIZE,
            'processing_time': time.time() - start_time
        }
        
        return result
    
    def visualize_obstacles(self, color_image: np.ndarray, 
                          depth_image: np.ndarray, 
                          obstacle_info: dict) -> np.ndarray:
        """
        Create visualization overlay showing obstacles.
        
        Args:
            color_image: RGB image
            depth_image: Depth image
            obstacle_info: Result from detect_obstacles()
            
        Returns:
            Image with obstacle visualization
        """
        vis_image = color_image.copy()
        
        # Create depth colormap
        depth_meters = depth_image * self.depth_scale
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03),
            cv2.COLORMAP_JET
        )
        
        # Overlay warning/danger zones
        height, width = depth_image.shape
        
        # Draw zone lines
        cv2.line(vis_image, (width//3, 0), (width//3, height), (255, 255, 255), 1)
        cv2.line(vis_image, (2*width//3, 0), (2*width//3, height), (255, 255, 255), 1)
        
        # Color zones based on obstacles
        alpha = 0.3
        overlay = vis_image.copy()
        
        if obstacle_info['left_blocked']:
            cv2.rectangle(overlay, (0, 0), (width//3, height), (0, 0, 255), -1)
        if obstacle_info['center_blocked']:
            cv2.rectangle(overlay, (width//3, 0), (2*width//3, height), (0, 0, 255), -1)
        if obstacle_info['right_blocked']:
            cv2.rectangle(overlay, (2*width//3, 0), (width, height), (0, 0, 255), -1)
            
        vis_image = cv2.addWeighted(overlay, alpha, vis_image, 1 - alpha, 0)
        
        # Add status text
        status_color = (0, 255, 0)  # Green
        if obstacle_info['warning_zone']:
            status_color = (0, 255, 255)  # Yellow
        if obstacle_info['danger_zone']:
            status_color = (0, 0, 255)  # Red
            
        status_text = "CLEAR"
        if obstacle_info['warning_zone']:
            status_text = "WARNING"
        if obstacle_info['danger_zone']:
            status_text = "DANGER"
            
        cv2.putText(vis_image, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        cv2.putText(vis_image, f"Distance: {obstacle_info['closest_distance']:.2f}m", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.putText(vis_image, f"FPS: {1.0/obstacle_info['processing_time']:.1f}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Combine color and depth views
        depth_colormap = cv2.resize(depth_colormap, (width//2, height//2))
        depth_colormap_padded = np.zeros_like(vis_image)
        depth_colormap_padded[:height//2, :width//2] = depth_colormap
        
        return vis_image
    
    def cleanup(self):
        """Stop the camera pipeline."""
        self.pipeline.stop()
        print("Camera stopped")


def main():
    """
    Example usage of the obstacle detector.
    This demonstrates real-time obstacle detection suitable for drone operation.
    """
    print("=" * 60)
    print("Drone Obstacle Detection - Example Implementation")
    print("=" * 60)
    print()
    print("This example shows real-time obstacle detection using")
    print("Intel RealSense depth camera optimized for drone use.")
    print()
    print("Controls:")
    print("  'q' - Quit")
    print("  's' - Save screenshot")
    print()
    
    # Initialize
    config = DroneConfig()
    detector = ObstacleDetector(config)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Get frames from camera
            color_image, depth_image = detector.get_frames()
            
            if color_image is None or depth_image is None:
                print("Failed to get frames")
                break
            
            # Process only every Nth frame for performance
            if frame_count % config.FRAME_SKIP == 0:
                # Detect obstacles
                obstacle_info = detector.detect_obstacles(depth_image)
                
                # Check if processing is too slow
                if obstacle_info['processing_time'] > config.MAX_PROCESSING_TIME:
                    print(f"Warning: Processing too slow ({obstacle_info['processing_time']*1000:.1f}ms)")
                
                # Print alerts
                if obstacle_info['danger_zone']:
                    print(f"⚠️  DANGER! Obstacle at {obstacle_info['closest_distance']:.2f}m")
                elif obstacle_info['warning_zone']:
                    print(f"⚡ Warning: Obstacle at {obstacle_info['closest_distance']:.2f}m")
                
                # Create visualization
                vis_image = detector.visualize_obstacles(color_image, depth_image, obstacle_info)
                
                # Display
                cv2.imshow('Drone Obstacle Detection', vis_image)
            
            frame_count += 1
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"obstacle_detection_{int(time.time())}.png"
                cv2.imwrite(filename, vis_image)
                print(f"Screenshot saved: {filename}")
            
            # Print stats every 5 seconds
            if frame_count % (config.CAMERA_FPS * 5) == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"Running... {frame_count} frames, {fps:.1f} FPS average")
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        # Cleanup
        detector.cleanup()
        cv2.destroyAllWindows()
        
        # Print summary
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        print()
        print("=" * 60)
        print("Summary:")
        print(f"Total frames: {frame_count}")
        print(f"Total time: {elapsed:.1f}s")
        print(f"Average FPS: {fps:.1f}")
        print("=" * 60)


if __name__ == "__main__":
    main()
