import cv2
import numpy as np
from config import Config
from typing import List, Tuple, Optional
import colorsys

class MotionSection:
    def __init__(self, x: int, y: int, width: int, height: int, depth: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.motion_angle = 0
        self.motion_strength = 0
        self.best_direction = None
        self.subsections = []

class VideoMotionAnalyzer:
    def __init__(self):
        self.config = Config()

    def load_video(self, video_path: str) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        return cap

    def create_grid_sections(self, frame_height: int, frame_width: int, depth: int = 0) -> List[MotionSection]:
        sections = []
        rows = self.config.GRID_ROWS
        cols = self.config.GRID_COLS

        section_height = frame_height // rows
        section_width = frame_width // cols

        # Determine row and column ranges
        if self.config.EXCLUDE_BORDER_SECTIONS and depth == 0:
            # Skip first and last rows/columns for border sections
            row_start, row_end = 1, rows - 1
            col_start, col_end = 1, cols - 1
        else:
            row_start, row_end = 0, rows
            col_start, col_end = 0, cols

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                x = col * section_width
                y = row * section_height
                # Ensure we don't go out of bounds
                width = min(section_width, frame_width - x)
                height = min(section_height, frame_height - y)

                section = MotionSection(x, y, width, height, depth)
                sections.append(section)

        return sections

    def extract_section(self, frame: np.ndarray, section: MotionSection) -> np.ndarray:
        return frame[section.y:section.y + section.height,
                    section.x:section.x + section.width]

    def template_match_score(self, template: np.ndarray, target: np.ndarray) -> float:
        if template.shape != target.shape:
            return 0.0

        # Normalize both images to reduce lighting effects
        template_norm = cv2.normalize(template, None, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        target_norm = cv2.normalize(target, None, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)

        # Use normalized cross-correlation
        result = cv2.matchTemplate(template_norm, target_norm, cv2.TM_CCOEFF_NORMED)
        return result[0, 0] if result.size > 0 else 0.0

    def find_best_motion_direction(self, prev_section: np.ndarray, curr_frame: np.ndarray,
                                 section: MotionSection) -> Tuple[int, float]:
        best_score = -1
        best_direction = 0

        for i, (dx, dy) in enumerate(self.config.DIRECTIONS):
            # Calculate new position
            new_x = section.x + dx * self.config.SEARCH_STEP_SIZE
            new_y = section.y + dy * self.config.SEARCH_STEP_SIZE

            # Check bounds
            if (new_x < 0 or new_y < 0 or
                new_x + section.width >= curr_frame.shape[1] or
                new_y + section.height >= curr_frame.shape[0]):
                continue

            # Extract candidate section
            candidate = curr_frame[new_y:new_y + section.height,
                                new_x:new_x + section.width]

            # Calculate similarity
            score = self.template_match_score(prev_section, candidate)

            if score > best_score:
                best_score = score
                best_direction = i

        return best_direction, best_score

    def create_recursive_subsections(self, section: MotionSection) -> List[MotionSection]:
        if section.depth >= self.config.MAX_RECURSIVE_DEPTH:
            return []

        subsections = []
        factor = self.config.RECURSIVE_SUBDIVISION_FACTOR
        sub_width = section.width // factor
        sub_height = section.height // factor

        for row in range(factor):
            for col in range(factor):
                sub_x = section.x + col * sub_width
                sub_y = section.y + row * sub_height

                # Ensure we don't go out of bounds
                actual_width = min(sub_width, section.width - col * sub_width)
                actual_height = min(sub_height, section.height - row * sub_height)

                if actual_width > 10 and actual_height > 10:  # Minimum size check
                    subsection = MotionSection(sub_x, sub_y, actual_width, actual_height, section.depth + 1)
                    subsections.append(subsection)

        return subsections

    def analyze_motion_recursive(self, prev_frame: np.ndarray, curr_frame: np.ndarray,
                               sections: List[MotionSection]) -> List[MotionSection]:
        analyzed_sections = []

        for section in sections:
            # Extract section from previous frame
            prev_section = self.extract_section(prev_frame, section)

            # Find best motion direction
            best_dir, score = self.find_best_motion_direction(prev_section, curr_frame, section)

            # Store results
            section.best_direction = best_dir
            section.motion_angle = self.config.DIRECTION_ANGLES[best_dir]
            section.motion_strength = score

            analyzed_sections.append(section)

            # Recursive analysis if motion is significant
            if (score > self.config.MOTION_THRESHOLD and
                section.depth < self.config.MAX_RECURSIVE_DEPTH):

                subsections = self.create_recursive_subsections(section)
                if subsections:
                    analyzed_subsections = self.analyze_motion_recursive(prev_frame, curr_frame, subsections)
                    section.subsections = analyzed_subsections

        return analyzed_sections

    def angle_to_color(self, angle: float, strength: float) -> Tuple[int, int, int]:
        # Convert angle to hue (0-360 degrees -> 0-1)
        hue = angle / 360.0
        # Use strength as saturation
        saturation = min(strength * 2, 1.0)  # Scale up for visibility
        value = 0.8  # Keep brightness constant

        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return tuple(int(c * 255) for c in rgb)

    def draw_motion_visualization(self, frame: np.ndarray, sections: List[MotionSection]) -> np.ndarray:
        vis_frame = frame.copy()

        def draw_sections_recursive(sections: List[MotionSection]):
            for section in sections:
                if self.config.COLOR_CODE_MOTION:
                    # Color-code the section based on motion
                    color = self.angle_to_color(section.motion_angle, section.motion_strength)

                    # Draw filled rectangle with transparency
                    overlay = vis_frame.copy()
                    cv2.rectangle(overlay,
                                (section.x, section.y),
                                (section.x + section.width, section.y + section.height),
                                color, -1)
                    cv2.addWeighted(vis_frame, 0.7, overlay, 0.3, 0, vis_frame)

                if self.config.SHOW_GRID_LINES:
                    # Draw section boundaries
                    cv2.rectangle(vis_frame,
                                (section.x, section.y),
                                (section.x + section.width, section.y + section.height),
                                (255, 255, 255), 1)

                if self.config.SHOW_MOTION_VECTORS and section.motion_strength > 0.1:
                    # Draw motion vector
                    center_x = section.x + section.width // 2
                    center_y = section.y + section.height // 2

                    angle_rad = np.radians(section.motion_angle)
                    vector_length = section.motion_strength * self.config.VECTOR_SCALE * 20

                    end_x = int(center_x + vector_length * np.sin(angle_rad))
                    end_y = int(center_y - vector_length * np.cos(angle_rad))  # Negative for screen coordinates

                    cv2.arrowedLine(vis_frame, (center_x, center_y), (end_x, end_y),
                                  (0, 255, 255), 2, tipLength=0.3)

                # Recursively draw subsections
                if section.subsections:
                    draw_sections_recursive(section.subsections)

        draw_sections_recursive(sections)
        return vis_frame

    def create_motion_legend(self) -> np.ndarray:
        legend_size = 200
        legend = np.zeros((legend_size, legend_size, 3), dtype=np.uint8)

        # Draw color wheel for motion directions
        center = legend_size // 2
        for angle in range(0, 360, 10):
            color = self.angle_to_color(angle, 1.0)
            angle_rad = np.radians(angle)

            # Draw line from center outward
            end_x = int(center + (center - 20) * np.sin(angle_rad))
            end_y = int(center - (center - 20) * np.cos(angle_rad))

            cv2.line(legend, (center, center), (end_x, end_y), color, 3)

        # Add direction labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(legend, 'N', (center - 5, 15), font, 0.5, (255, 255, 255), 1)
        cv2.putText(legend, 'E', (legend_size - 15, center + 5), font, 0.5, (255, 255, 255), 1)
        cv2.putText(legend, 'S', (center - 5, legend_size - 5), font, 0.5, (255, 255, 255), 1)
        cv2.putText(legend, 'W', (5, center + 5), font, 0.5, (255, 255, 255), 1)

        return legend

    def calculate_overall_movement(self, sections: List[MotionSection]) -> Tuple[float, float]:
        """Calculate overall movement direction and strength from all sections."""
        total_x = 0
        total_y = 0
        total_strength = 0

        def process_sections(sections_list):
            nonlocal total_x, total_y, total_strength
            for section in sections_list:
                if section.motion_strength > 0.1:  # Only consider significant motion
                    angle_rad = np.radians(section.motion_angle)
                    # Weight by section area and motion strength
                    weight = section.width * section.height * section.motion_strength

                    total_x += weight * np.sin(angle_rad)
                    total_y += -weight * np.cos(angle_rad)  # Negative for screen coordinates
                    total_strength += weight

                # Process subsections recursively
                if section.subsections:
                    process_sections(section.subsections)

        process_sections(sections)

        if total_strength > 0:
            avg_x = total_x / total_strength
            avg_y = total_y / total_strength

            # Calculate overall angle and strength
            overall_angle = np.degrees(np.arctan2(avg_x, -avg_y)) % 360
            overall_strength = min(np.sqrt(avg_x**2 + avg_y**2), 1.0)

            return overall_angle, overall_strength

        return 0, 0

    def draw_overall_direction_gauge(self, frame: np.ndarray, overall_angle: float, overall_strength: float) -> np.ndarray:
        """Draw overall movement direction gauge on the frame."""
        gauge_size = 80
        margin = 20

        # Position gauge in top-right corner
        gauge_x = frame.shape[1] - gauge_size - margin
        gauge_y = margin

        # Create gauge background
        center_x = gauge_x + gauge_size // 2
        center_y = gauge_y + gauge_size // 2

        # Draw outer circle
        cv2.circle(frame, (center_x, center_y), gauge_size // 2, (100, 100, 100), 2)

        # Draw cardinal direction markers
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        font_color = (200, 200, 200)

        # North
        cv2.putText(frame, 'N', (center_x - 5, gauge_y + 10), font, font_scale, font_color, 1)
        # East
        cv2.putText(frame, 'E', (gauge_x + gauge_size - 10, center_y + 3), font, font_scale, font_color, 1)
        # South
        cv2.putText(frame, 'S', (center_x - 5, gauge_y + gauge_size - 5), font, font_scale, font_color, 1)
        # West
        cv2.putText(frame, 'W', (gauge_x + 5, center_y + 3), font, font_scale, font_color, 1)

        # Draw overall movement vector if there's significant motion
        if overall_strength > 0.05:
            angle_rad = np.radians(overall_angle)
            vector_length = (gauge_size // 2 - 10) * min(overall_strength * 3, 1.0)

            end_x = int(center_x + vector_length * np.sin(angle_rad))
            end_y = int(center_y - vector_length * np.cos(angle_rad))

            # Draw arrow
            cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y),
                          (0, 255, 0), 3, tipLength=0.4)

            # Add text showing direction
            direction_text = f"{overall_angle:.0f}°"
            text_x = gauge_x
            text_y = gauge_y + gauge_size + 15
            cv2.putText(frame, direction_text, (text_x, text_y), font, 0.4, (0, 255, 0), 1)

        return frame

    def process_video(self, video_path: str, output_path: Optional[str] = None):
        cap = self.load_video(video_path)

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"Processing video: {width}x{height} @ {fps}fps, {total_frames} frames")

        # Calculate output dimensions based on compass visibility
        output_width = width + (200 if self.config.SHOW_COMPASS else 0)

        # Setup output video if specified
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (output_width, height))

        # Create motion legend if needed
        legend = self.create_motion_legend() if self.config.SHOW_COMPASS else None

        # Initialize
        prev_frame = None
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Skip initial frames if configured
            if frame_count <= self.config.SKIP_FRAMES:
                continue

            # Stop if max frames reached (after skipping)
            processed_frames = frame_count - self.config.SKIP_FRAMES
            if self.config.MAX_FRAMES and processed_frames > self.config.MAX_FRAMES:
                break

            # Skip frames if configured
            if frame_count % self.config.FRAME_SKIP != 0:
                continue

            # Convert to grayscale for motion analysis
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Create grid sections
                sections = self.create_grid_sections(height, width)

                # Analyze motion
                analyzed_sections = self.analyze_motion_recursive(prev_frame, gray_frame, sections)

                # Create visualization
                vis_frame = self.draw_motion_visualization(frame, analyzed_sections)

                # Add overall direction gauge if enabled
                if self.config.SHOW_OVERALL_DIRECTION:
                    overall_angle, overall_strength = self.calculate_overall_movement(analyzed_sections)
                    vis_frame = self.draw_overall_direction_gauge(vis_frame, overall_angle, overall_strength)

                # Combine with legend if enabled
                if self.config.SHOW_COMPASS and legend is not None:
                    legend_resized = cv2.resize(legend, (200, height))
                    combined_frame = np.hstack([vis_frame, legend_resized])
                else:
                    combined_frame = vis_frame

                # Display
                cv2.imshow('Motion Analysis', combined_frame)

                # Save if output specified
                if output_path:
                    out.write(combined_frame)

                # Print progress
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {progress:.1f}%")

            prev_frame = gray_frame

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        if output_path:
            out.release()
        cv2.destroyAllWindows()

        print("Video processing complete!")