class Config:
    # Grid subdivision settings
    GRID_ROWS = 5
    GRID_COLS = 5

    # Motion detection settings
    SEARCH_STEP_SIZE = 1  # pixels to move in each direction
    MOTION_THRESHOLD = 0.3  # minimum motion strength to trigger recursion

    # Recursive analysis settings
    MAX_RECURSIVE_DEPTH = 2
    RECURSIVE_SUBDIVISION_FACTOR = 2  # divide each section into 2x2 subsections

    # Visualization settings
    SHOW_MOTION_VECTORS = False
    SHOW_GRID_LINES = True
    COLOR_CODE_MOTION = True
    VECTOR_SCALE = 3.0  # scale factor for motion vector display
    SHOW_COMPASS = False  # show direction compass legend
    SHOW_OVERALL_DIRECTION = True  # show overall camera movement gauge

    # Video processing
    FRAME_SKIP = 1  # process every nth frame (1 = all frames)
    MAX_FRAMES = None  # process only first n frames (None = all frames)
    SKIP_FRAMES = 0  # skip first n frames before processing
    EXCLUDE_BORDER_SECTIONS = True  # skip first/last rows and columns

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