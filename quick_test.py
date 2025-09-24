import os
import sys
from test_optimizer import MotionTestOptimizer

def main():
    # Check if video file exists
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]

    if not video_files:
        print("No video files found in current directory.")
        print("Please place a video file in the video_motion_analyzer folder.")
        print("Usage: python quick_test.py [video_file.mp4]")
        return

    # Use provided video or first found video
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = video_files[0]
        print(f"Using video file: {video_path}")

    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return

    print("Running motion detection parameter optimization...")
    print(f"Testing upward camera movement from frame 1100-1160")
    print("Looking for optimal settings for South direction detection (180°)")

    optimizer = MotionTestOptimizer(video_path)
    best_config = optimizer.run_parameter_tests()

    if best_config and 'error' not in best_config:
        print("\n" + "="*50)
        print("RECOMMENDED CONFIGURATION:")
        print("="*50)
        config_params = best_config['config']
        print(f"GRID_ROWS = {config_params['GRID_ROWS']}")
        print(f"GRID_COLS = {config_params['GRID_COLS']}")
        print(f"SEARCH_STEP_SIZE = {config_params['SEARCH_STEP_SIZE']}")
        print(f"MOTION_THRESHOLD = {config_params['MOTION_THRESHOLD']}")
        print(f"MAX_RECURSIVE_DEPTH = {config_params['MAX_RECURSIVE_DEPTH']}")
        print(f"\nOverall Score: {best_config['overall_score']:.1f}/100")
        print(f"Average angle detected: {best_config['avg_angle']:.1f}° (should be ~180° for upward cam)")

if __name__ == "__main__":
    main()