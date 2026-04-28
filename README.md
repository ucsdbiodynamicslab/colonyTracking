# Colony Tracking System

A Python image analysis application for detecting, tracking, and measuring bacterial colonies in time-lapse microscopy images.

## Features

- **Automatic Colony Detection**: Identifies bacterial colonies from microscopy images using image subtraction and blob detection
- **Temporal Tracking**: Follows individual colonies across multiple time points
- **Growth Analysis**: Measures colony growth metrics (area, diameter, growth rates)
- **Interactive Validation**: GUI-based manual selection and deselection of detected colonies
- **Visualization**: Real-time plotting and analysis of colony growth trajectories

## Requirements

- Python 3.9 or higher
- See `requirements.txt` for full dependency list

## Installation

### From source

```bash
git clone https://github.com/biodynamics/colonytracking.git
cd colonytracking
pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
```

### GUI support (optional)

```bash
pip install -e ".[gui]"
```

## Quick Start

### Running the GUI Application

```bash
colonytracking
```

Or from Python:

```python
from colonytracking.gui.main import main
main()
```

### Using the Library

```python
from colonytracking.processing.detector import ColonyDetector
from colonytracking.processing.tracker import ColonyTracker
from colonytracking.io.image import ImageLoader
import numpy as np

# Load images
loader = ImageLoader()
background_img = loader.load('background.tif')
colony_img = loader.load('colonies_t0.tif')

# Detect colonies
detector = ColonyDetector(separation=50)
colonies = detector.detect(background_img, colony_img)

# Track colonies across frames
tracker = ColonyTracker(distance_threshold=15)
for i, frame_path in enumerate(frame_paths[1:], start=1):
    frame = loader.load(frame_path)
    tracker.track_frame(frame, background_img)
```

## Project Structure

```
colonytracking/
├── src/colonytracking/
│   ├── __init__.py
│   ├── config.py                 # Configuration and constants
│   ├── io/
│   │   ├── __init__.py
│   │   └── image.py              # Image I/O operations
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── core.py               # Core image processing utilities
│   │   ├── detector.py           # Colony detection algorithm
│   │   └── tracker.py            # Temporal tracking algorithm
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── growth.py             # Growth metric calculations
│   │   └── visualization.py      # Plotting and visualization
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main.py               # Main GUI application window
│   │   ├── widgets.py            # Custom Qt widgets
│   │   └── dialogs.py            # Dialog windows
│   └── data/
│       ├── __init__.py
│       └── structures.py         # Data classes and structures
├── tests/
│   ├── __init__.py
│   ├── test_detector.py
│   ├── test_tracker.py
│   ├── test_processing.py
│   └── test_integration.py
├── docs/
│   ├── API.md
│   ├── USAGE.md
│   └── DEVELOPMENT.md
├── pyproject.toml
├── requirements.txt
├── README.md
└── DESIGN_DOCUMENT.md
```

## Usage Guide

### Workflow 1: Initial Colony Detection

1. Launch the application: `colonytracking`
2. Click "Select Files" and choose your microscopy image sequence
3. Click "Select Colonies" to detect colonies in the initial image pair
4. Click on a well-lit region for intensity correction
5. Review detected colonies (displayed with circles and numbers)
6. Click colonies to deselect erroneous detections
7. Results are automatically tracked across all frames

### Workflow 2: Analysis

After colonies are detected and tracked, generate analysis plots:
- **Plot Area**: View area growth over time for each colony
- **Plot Diameter**: View diameter changes across timepoints
- **Plot Normalized Growth**: Visualize normalized growth trajectories
- **Plot Emergence**: Bar chart showing colony emergence times

### Workflow 3: Batch Processing

For processing multiple image sets programmatically:

```python
from colonytracking.processing import ColonyAnalyzer

analyzer = ColonyAnalyzer(config={
    'separation': 50,
    'min_area': 100,
    'circularity_range': (0.9, 1.1)
})

results = analyzer.process_directory('/path/to/images/')
analyzer.export_results(results, format='csv')
```

## Configuration

Default parameters are defined in `src/colonytracking/config.py`:

```python
DIFFERENCE_THRESHOLD = 20          # Binary image threshold
MIN_COLONY_AREA = 1000             # Minimum pixels for separation filter
MIN_TRACKING_AREA = 100            # Minimum pixels for tracking
CIRCULARITY_RANGE = (0.9, 1.1)    # Acceptable circularity range
TRACKING_DISTANCE_THRESHOLD = 15   # Pixels for temporal matching
ROI_RADIUS = 3000                  # Petri dish radius in pixels
INTENSITY_CORRECTION_WINDOW = 25   # Pixels for light correction
```

These can be overridden when creating detector/tracker instances.

## Algorithm Overview

### Colony Detection

1. **Image Preprocessing**: RGB to grayscale conversion, optional resizing
2. **Light Correction**: User-selected reference point for intensity normalization
3. **Binary Image**: Threshold difference image to identify candidate colonies
4. **Blob Detection**: Extract connected components with area and circularity metrics
5. **Filtering**: Remove merged colonies, non-circular blobs, and edge-touching regions
6. **Interactive Validation**: Manual deselection via mouse clicks

### Temporal Tracking

1. **Frame-to-Frame Matching**: Nearest-neighbor association between frames
2. **Distance-Based Linking**: Colonies matched if centroid distance < threshold
3. **Temporal Accumulation**: Measurements appended to colony track
4. **Gap Handling**: Lost colonies recorded with zero-area frames (tracks preserved)

### Growth Metrics

- **Area**: Raw pixel count per frame
- **Diameter**: Calculated assuming circular geometry: $D = 2\sqrt{A/\pi}$
- **Normalized Growth**: Ratio of current diameter to emergence diameter
- **Growth Rate**: Temporal derivative of diameter or area

## Performance Notes

- Processing speed depends on image resolution and number of colonies
- Large image sequences (>100 frames) may require several seconds per frame
- GUI remains responsive with background processing (future: threading)
- Memory usage scales with image resolution and temporal history

## Development

### Running Tests

```bash
pytest tests/
pytest tests/ -v --cov=colonytracking
```

### Code Quality

```bash
black src/colonytracking tests/
flake8 src/colonytracking tests/
mypy src/colonytracking
```

### Building Documentation

```bash
cd docs/
sphinx-build -b html . _build/html
```

## Troubleshooting

### Issue: Colonies not detected
- Check image contrast: bright background, dark colonies
- Adjust `DIFFERENCE_THRESHOLD` in config
- Verify circular ROI mask settings
- Confirm intensity correction point selection

### Issue: False positive detections
- Increase `MIN_COLONY_AREA` threshold
- Tighten `CIRCULARITY_RANGE` parameter
- Increase colony `separation` distance

### Issue: Tracking loss
- Reduce `TRACKING_DISTANCE_THRESHOLD` (stricter matching)
- Check for overlapping/merging colonies
- Verify consistent imaging conditions between frames

## License

MIT License - See LICENSE file for details

## Citation

If you use this software in your research, please cite:

```bibtex
@software{colonytracking2026,
  title={Colony Tracking System},
  author={Biodynamics Team},
  year={2026},
  url={https://github.com/biodynamics/colonytracking}
}
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

For detailed API documentation, see [API.md](docs/API.md)  
For usage examples, see [USAGE.md](docs/USAGE.md)  
For development guidelines, see [DEVELOPMENT.md](docs/DEVELOPMENT.md)
