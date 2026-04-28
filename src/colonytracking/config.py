"""
Configuration module for Colony Tracking System.

Defines all hard-coded parameters and default settings.
"""

# ============================================================================
# IMAGE PROCESSING PARAMETERS
# ============================================================================

# Binary image generation threshold
# Colonies are darker than background; differences > DIFFERENCE_THRESHOLD
# are marked as candidate colony pixels
DIFFERENCE_THRESHOLD = 20

# Display optimization: resize images larger than this for performance
RESIZE_THRESHOLD = 1500

# ============================================================================
# COLONY DETECTION PARAMETERS
# ============================================================================

# Minimum area (pixels) for separation filter
# Blobs smaller than this are not considered in separation filtering
MIN_COLONY_AREA_SEPARATION = 1000

# Minimum area (pixels) for initial blob detection
MIN_COLONY_AREA_DETECTION = 100

# Circularity range: acceptable ratio of major axis to minor axis
# Value ~1.0 = circular, >1.0 = elongated
# Range (0.9, 1.1) means ±10% tolerance from perfect circle
CIRCULARITY_MIN = 0.9
CIRCULARITY_MAX = 1.1

# ============================================================================
# COLONY TRACKING PARAMETERS
# ============================================================================

# Distance threshold (pixels) for temporal matching
# Colonies matched if centroid distance between frames < this value
TRACKING_DISTANCE_THRESHOLD = 15

# Minimum area for tracking (prevents tracking noise)
MIN_TRACKING_AREA = 100

# ============================================================================
# REGION OF INTEREST (ROI) PARAMETERS
# ============================================================================

# Petri dish circular ROI parameters
ROI_RADIUS = 3000  # pixels
ROI_CENTER = None  # If None, uses image center

# Angular resolution for ROI mask generation (degrees)
# Lower = more points = smoother circle
ROI_ANGULAR_RESOLUTION = 1

# ============================================================================
# LIGHT CORRECTION PARAMETERS
# ============================================================================

# Size of region (pixels) around user-selected point for intensity correction
# Uses ±INTENSITY_CORRECTION_WINDOW from click point
INTENSITY_CORRECTION_WINDOW = 25

# ============================================================================
# VISUALIZATION PARAMETERS
# ============================================================================

# Colormap for differentiating colonies
COLORMAP_NAME = 'jet'

# Line width for circle overlays (pixels)
CIRCLE_LINE_WIDTH = 2

# Figure DPI for matplotlib
FIGURE_DPI = 100

# ============================================================================
# FILE I/O PARAMETERS
# ============================================================================

# Supported image formats
SUPPORTED_FORMATS = ('.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp')

# Output format for figures
OUTPUT_FIGURE_FORMAT = 'jpg'

# ============================================================================
# TIME PARAMETERS
# ============================================================================

# Assumed time interval between images (minutes)
# Used for labeling time axis in plots
TIME_INTERVAL_MINUTES = 30

# ============================================================================
# PERFORMANCE PARAMETERS
# ============================================================================

# Use threading for long-running operations
USE_THREADING = False

# Maximum number of parallel workers
MAX_WORKERS = 4

# ============================================================================
# ADVANCED PARAMETERS
# ============================================================================

# Morphological operations for cleaning binary images
USE_MORPHOLOGICAL_CLEANUP = False

# Gaussian blur sigma for pre-processing (set to 0 to disable)
GAUSSIAN_SIGMA = 0.0

# Adaptive thresholding (if True, uses local adaptive threshold instead of global)
USE_ADAPTIVE_THRESHOLD = False

# ============================================================================
# DEFAULT COLONY DETECTION CONFIGURATION
# ============================================================================

DEFAULT_DETECTOR_CONFIG = {
    'separation': 50,
    'min_area': MIN_COLONY_AREA_SEPARATION,
    'circularity_range': (CIRCULARITY_MIN, CIRCULARITY_MAX),
    'difference_threshold': DIFFERENCE_THRESHOLD,
    'resize_threshold': RESIZE_THRESHOLD,
}

# ============================================================================
# DEFAULT TRACKER CONFIGURATION
# ============================================================================

DEFAULT_TRACKER_CONFIG = {
    'distance_threshold': TRACKING_DISTANCE_THRESHOLD,
    'min_area': MIN_TRACKING_AREA,
    'difference_threshold': DIFFERENCE_THRESHOLD,
}

# ============================================================================
# DEFAULT ROI CONFIGURATION
# ============================================================================

DEFAULT_ROI_CONFIG = {
    'radius': ROI_RADIUS,
    'center': ROI_CENTER,
    'angular_resolution': ROI_ANGULAR_RESOLUTION,
}
