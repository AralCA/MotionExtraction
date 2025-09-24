# Video Motion Analyzer

A Python tool that analyzes motion in videos by comparing consecutive frames and extracting motion angles using 8-directional search with recursive subdivision.

## Features

- **8-Directional Motion Detection**: Searches in N, NE, E, SE, S, SW, W, NW directions
- **Configurable Grid Subdivision**: Divide frames into customizable grid sections
- **Recursive Analysis**: Subdivide sections with significant motion for finer detail
- **Color-Coded Visualization**: Motion angles displayed using HSV color mapping
- **Real-time Processing**: View results while processing (or save to file)
- **Flexible Configuration**: Easily adjust all parameters

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python main.py input_video.mp4
```

### Save Output Video
```bash
python main.py input_video.mp4 -o output_with_motion.mp4
```

### Custom Parameters
```bash
python main.py input_video.mp4 --grid-size 8 8 --step-size 10 --max-depth 3
```

### Command Line Options

- `--grid-size ROWS COLS`: Grid subdivision (default: 16x16)
- `--step-size PIXELS`: Search step size in pixels (default: 5)
- `--max-depth DEPTH`: Maximum recursive depth (default: 2)
- `--motion-threshold THRESHOLD`: Motion threshold for recursion (default: 0.1)

## How It Works

1. **Frame Processing**: Extracts consecutive frames and converts to grayscale
2. **Grid Creation**: Divides each frame into a configurable grid
3. **Motion Search**: For each grid section, searches in 8 directions to find best match
4. **Recursive Subdivision**: Sections with high motion are subdivided for finer analysis
5. **Visualization**: Results displayed with color-coded motion angles

## Visualization

- **Color Coding**: Hue represents motion angle (0-360°), saturation represents motion strength
- **Motion Vectors**: Yellow arrows show motion direction and magnitude
- **Grid Lines**: White lines show section boundaries
- **Legend**: Color wheel on the right shows angle-to-color mapping

## Configuration

Edit `config.py` to customize:

```python
GRID_ROWS = 16              # Grid height
GRID_COLS = 16              # Grid width
SEARCH_STEP_SIZE = 5        # Pixel step for directional search
MAX_RECURSIVE_DEPTH = 2     # Levels of subdivision
MOTION_THRESHOLD = 0.1      # Minimum motion for recursion
```

## Controls

- Press 'q' to quit during playback
- Window shows real-time analysis results

## Output

- Live visualization window with motion analysis
- Optional output video file with embedded analysis
- Console progress updates