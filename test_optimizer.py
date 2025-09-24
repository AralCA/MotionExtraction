import cv2
import numpy as np
from motion_analyzer import VideoMotionAnalyzer
from config import Config
import json
import time
from typing import Dict, List, Tuple

class MotionTestOptimizer:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.test_results = []

    def test_configuration(self, config_params: Dict, test_name: str) -> Dict:
        """Test a specific configuration and return results."""
        print(f"\n=== Testing: {test_name} ===")

        # Apply configuration
        for param, value in config_params.items():
            setattr(Config, param, value)

        # Display current config
        print(f"Grid: {Config.GRID_ROWS}x{Config.GRID_COLS}")
        print(f"Search Step: {Config.SEARCH_STEP_SIZE}")
        print(f"Motion Threshold: {Config.MOTION_THRESHOLD}")
        print(f"Max Depth: {Config.MAX_RECURSIVE_DEPTH}")

        analyzer = VideoMotionAnalyzer()

        # Capture results
        motion_data = []
        overall_directions = []
        processing_times = []

        cap = analyzer.load_video(self.video_path)

        # Skip to our test section
        for _ in range(Config.SKIP_FRAMES):
            cap.read()

        prev_frame = None
        frame_count = 0

        while frame_count < Config.MAX_FRAMES:
            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                height, width = gray_frame.shape
                sections = analyzer.create_grid_sections(height, width)

                # Analyze motion
                analyzed_sections = analyzer.analyze_motion_recursive(prev_frame, gray_frame, sections)

                # Calculate overall movement
                overall_angle, overall_strength = analyzer.calculate_overall_movement(analyzed_sections)
                overall_directions.append((overall_angle, overall_strength))

                # Collect detailed motion data
                section_data = []
                for section in analyzed_sections:
                    section_data.append({
                        'angle': section.motion_angle,
                        'strength': section.motion_strength,
                        'area': section.width * section.height
                    })
                motion_data.append(section_data)

            prev_frame = gray_frame
            processing_times.append(time.time() - start_time)

        cap.release()

        # Analyze results
        results = self.analyze_test_results(motion_data, overall_directions, processing_times, test_name)
        results['config'] = config_params.copy()

        self.test_results.append(results)
        return results

    def analyze_test_results(self, motion_data: List, overall_directions: List,
                           processing_times: List, test_name: str) -> Dict:
        """Analyze the test results for accuracy and stability."""

        if not overall_directions:
            return {'error': 'No motion data collected'}

        # Extract angles and strengths
        angles = [d[0] for d in overall_directions if d[1] > 0.1]  # Only significant motion
        strengths = [d[1] for d in overall_directions if d[1] > 0.1]

        if not angles:
            return {
                'test_name': test_name,
                'error': 'No significant motion detected',
                'avg_processing_time': np.mean(processing_times) * 1000,
                'frames_processed': len(motion_data)
            }

        # For upward camera motion, video content moves down (South = 180°)
        # Convert angles to be relative to South (180°) for easier analysis
        normalized_angles = []
        for angle in angles:
            # Calculate distance from South (180°)
            distance_from_south = min(abs(angle - 180), abs((angle + 180) % 360 - 180))
            normalized_angles.append(distance_from_south)

        results = {
            'test_name': test_name,
            'frames_processed': len(motion_data),
            'significant_motion_frames': len(angles),
            'avg_processing_time_ms': np.mean(processing_times) * 1000,

            # Accuracy metrics (how close to South/180° direction)
            'avg_deviation_from_south': np.mean(normalized_angles),
            'std_deviation_from_south': np.std(normalized_angles),
            'max_deviation_from_south': np.max(normalized_angles),

            # Stability metrics
            'angle_stability': np.std(angles),  # Lower is more stable
            'strength_consistency': np.std(strengths),  # Lower is more consistent
            'avg_strength': np.mean(strengths),

            # Direction analysis
            'raw_angles': angles[:10],  # First 10 for inspection
            'avg_angle': np.mean(angles),
            'angle_range': np.max(angles) - np.min(angles),
        }

        # Calculate accuracy score (lower deviation from South = higher accuracy)
        accuracy_score = max(0, 100 - results['avg_deviation_from_south'] * 2)

        # Calculate stability score (lower standard deviation = higher stability)
        stability_score = max(0, 100 - results['angle_stability'] * 0.5)

        # Overall score
        results['accuracy_score'] = accuracy_score
        results['stability_score'] = stability_score
        results['overall_score'] = (accuracy_score + stability_score) / 2

        # Print results
        print(f"Frames with significant motion: {results['significant_motion_frames']}/{results['frames_processed']}")
        print(f"Average angle: {results['avg_angle']:.1f}°")
        print(f"Deviation from South: {results['avg_deviation_from_south']:.1f}° ± {results['std_deviation_from_south']:.1f}°")
        print(f"Angle stability (std): {results['angle_stability']:.1f}°")
        print(f"Average strength: {results['avg_strength']:.3f}")
        print(f"Processing time: {results['avg_processing_time_ms']:.1f} ms/frame")
        print(f"Accuracy score: {results['accuracy_score']:.1f}/100")
        print(f"Stability score: {results['stability_score']:.1f}/100")
        print(f"OVERALL SCORE: {results['overall_score']:.1f}/100")

        return results

    def run_parameter_tests(self):
        """Run tests with different parameter combinations."""

        # Test configurations for upward camera movement
        test_configs = [
            {
                'name': 'Baseline (Current Settings)',
                'params': {
                    'GRID_ROWS': 5, 'GRID_COLS': 5,
                    'SEARCH_STEP_SIZE': 1,
                    'MOTION_THRESHOLD': 5,
                    'MAX_RECURSIVE_DEPTH': 1
                }
            },
            {
                'name': 'Higher Resolution Grid',
                'params': {
                    'GRID_ROWS': 8, 'GRID_COLS': 8,
                    'SEARCH_STEP_SIZE': 1,
                    'MOTION_THRESHOLD': 5,
                    'MAX_RECURSIVE_DEPTH': 1
                }
            },
            {
                'name': 'Larger Search Step',
                'params': {
                    'GRID_ROWS': 5, 'GRID_COLS': 5,
                    'SEARCH_STEP_SIZE': 3,
                    'MOTION_THRESHOLD': 5,
                    'MAX_RECURSIVE_DEPTH': 1
                }
            },
            {
                'name': 'Lower Motion Threshold',
                'params': {
                    'GRID_ROWS': 5, 'GRID_COLS': 5,
                    'SEARCH_STEP_SIZE': 1,
                    'MOTION_THRESHOLD': 0.2,
                    'MAX_RECURSIVE_DEPTH': 1
                }
            },
            {
                'name': 'With Recursion',
                'params': {
                    'GRID_ROWS': 5, 'GRID_COLS': 5,
                    'SEARCH_STEP_SIZE': 1,
                    'MOTION_THRESHOLD': 0.3,
                    'MAX_RECURSIVE_DEPTH': 2
                }
            },
            {
                'name': 'Coarser Grid + Larger Steps',
                'params': {
                    'GRID_ROWS': 3, 'GRID_COLS': 3,
                    'SEARCH_STEP_SIZE': 5,
                    'MOTION_THRESHOLD': 5,
                    'MAX_RECURSIVE_DEPTH': 1
                }
            },
            {
                'name': 'Fine Grid + Small Steps',
                'params': {
                    'GRID_ROWS': 10, 'GRID_COLS': 10,
                    'SEARCH_STEP_SIZE': 1,
                    'MOTION_THRESHOLD': 5,
                    'MAX_RECURSIVE_DEPTH': 0
                }
            }
        ]

        print("Starting parameter optimization tests...")
        print("Expected motion: Upward camera movement (North direction ~0°)")
        print("=" * 60)

        for config in test_configs:
            try:
                self.test_configuration(config['params'], config['name'])
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"Error in test '{config['name']}': {e}")
                continue

        # Sort results by overall score
        self.test_results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)

        print("\n" + "=" * 60)
        print("FINAL RESULTS SUMMARY")
        print("=" * 60)

        for i, result in enumerate(self.test_results[:5], 1):
            if 'error' not in result:
                print(f"{i}. {result['test_name']}")
                print(f"   Overall Score: {result['overall_score']:.1f}")
                print(f"   Accuracy: {result['accuracy_score']:.1f}, Stability: {result['stability_score']:.1f}")
                print(f"   Avg Angle: {result['avg_angle']:.1f}°, Deviation: {result['avg_deviation_from_south']:.1f}°")
                print(f"   Config: {result['config']}")
                print()

        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)

        print("Detailed results saved to 'test_results.json'")

        return self.test_results[0] if self.test_results else None

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python test_optimizer.py <video_path>")
        sys.exit(1)

    optimizer = MotionTestOptimizer(sys.argv[1])
    best_config = optimizer.run_parameter_tests()

    if best_config:
        print(f"\nBest configuration: {best_config['test_name']}")
        print(f"Apply these settings to config.py: {best_config['config']}")