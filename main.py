import sys
import argparse
from motion_analyzer import VideoMotionAnalyzer
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Video Motion Analyzer')
    parser.add_argument('input_video', help='Path to input video file')
    parser.add_argument('-o', '--output', help='Path to output video file (optional)')
    parser.add_argument('--grid-size', type=int, nargs=2, metavar=('ROWS', 'COLS'),
                       help='Grid size (rows cols), default: 16 16')
    parser.add_argument('--step-size', type=int, metavar='PIXELS',
                       help='Search step size in pixels, default: 5')
    parser.add_argument('--max-depth', type=int, metavar='DEPTH',
                       help='Maximum recursive depth, default: 2')
    parser.add_argument('--motion-threshold', type=float, metavar='THRESHOLD',
                       help='Motion threshold for recursion, default: 0.1')
    parser.add_argument('--max-frames', type=int, metavar='N',
                       help='Process only first N frames (default: all frames)')
    parser.add_argument('--skip-frames', type=int, metavar='N',
                       help='Skip first N frames before processing (default: 0)')

    args = parser.parse_args()

    # Update configuration if arguments provided
    if args.grid_size:
        Config.GRID_ROWS, Config.GRID_COLS = args.grid_size
    if args.step_size:
        Config.SEARCH_STEP_SIZE = args.step_size
    if args.max_depth:
        Config.MAX_RECURSIVE_DEPTH = args.max_depth
    if args.motion_threshold:
        Config.MOTION_THRESHOLD = args.motion_threshold
    if args.max_frames:
        Config.MAX_FRAMES = args.max_frames
    if args.skip_frames:
        Config.SKIP_FRAMES = args.skip_frames

    print("Video Motion Analyzer")
    print("=" * 50)
    print(f"Grid Size: {Config.GRID_ROWS}x{Config.GRID_COLS}")
    print(f"Search Step Size: {Config.SEARCH_STEP_SIZE} pixels")
    print(f"Max Recursive Depth: {Config.MAX_RECURSIVE_DEPTH}")
    print(f"Motion Threshold: {Config.MOTION_THRESHOLD}")
    print(f"Max Frames: {Config.MAX_FRAMES if Config.MAX_FRAMES else 'All'}")
    print(f"Skip Frames: {Config.SKIP_FRAMES}")
    print("=" * 50)

    try:
        analyzer = VideoMotionAnalyzer()
        analyzer.process_video(args.input_video, args.output)
    except Exception as e:
        print(f"Error processing video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()