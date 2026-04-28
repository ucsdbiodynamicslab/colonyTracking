## API Reference

### Core Classes

#### `ColonyDetector`

Initial colony detection from image pair.

**Usage:**
```python
from colonytracking import ColonyDetector

detector = ColonyDetector({
    'separation': 50,  # Minimum distance between colonies (pixels)
    'min_area': 1000,  # Minimum colony area
    'circularity_range': (0.9, 1.1),
})

result = detector.detect(
    background_image,
    colony_image,
    roi_radius=3000,
    correction_point=(400, 400)  # (y, x) for light correction
)

print(f"Detected {len(result.colonies)} colonies")
```

**Parameters:**
- `config_dict`: Dictionary with detection parameters
  - `separation`: Minimum pixel distance between colony centroids
  - `min_area`: Minimum area threshold
  - `circularity_range`: (min, max) acceptable circularity values

**Methods:**
- `detect(background_image, colony_image, ...)`: Detect colonies in an image pair
  - Returns: `DetectionResult` with detected colonies

---

#### `ColonyTracker`

Temporal tracking across multiple frames.

**Usage:**
```python
from colonytracking import ColonyTracker

tracker = ColonyTracker({
    'distance_threshold': 15,  # Max pixels for matching
    'min_area': 100,
})

# Track through multiple frames
for frame in frame_sequence:
    result = tracker.track_frame(
        colonies,          # From previous frame
        frame,             # Current frame image
        reference_frame,   # Background/first image
        roi_mask,          # Circular ROI mask
        correction_point   # For light correction
    )
    print(f"Matched {result.matched_count}, Lost {result.lost_count}")
```

**Methods:**
- `track_frame(colonies, current_frame, reference_frame, ...)`: Track colonies in single frame
- `track_sequence(colonies, frames, reference_frame, ...)`: Track through entire sequence

---

#### `Colony`

Data structure for individual colony with temporal tracking data.

**Attributes:**
- `colony_id`: Unique identifier
- `measurements`: List of `ColonyMeasurement` objects across timepoints
- `emergence_frame`: Frame index when colony first detected

**Methods:**
- `get_areas()`: Get area values for all timepoints
- `get_diameters()`: Get diameter values for all timepoints
- `get_centroids()`: Get (x, y) positions for all timepoints
- `get_normalized_growth()`: Get diameter normalized by emergence diameter
- `append_measurement(measurement)`: Add measurement at next timepoint
- `get_last_measurement()`: Get most recent measurement

---

#### `GrowthAnalysis`

Compute colony growth metrics.

**Usage:**
```python
from colonytracking import GrowthAnalysis

# Analyze colony set
result = GrowthAnalysis.analyze(colonies)

print("Emergence times:", result.emergence_times)
print("Growth rates:", result.growth_rates)
print("Final sizes:", result.final_sizes)
```

**Methods:**
- `compute_emergence_times(colonies)`: Determine emergence frame for each colony
- `compute_growth_rates(colonies)`: Calculate growth rate (pixels/frame)
- `compute_final_sizes(colonies)`: Get final diameter for each colony
- `analyze(colonies)`: Perform complete analysis

---

#### `PlotGenerator`

Generate publication-quality plots.

**Usage:**
```python
from colonytracking import PlotGenerator

# Plot area over time
fig, ax = PlotGenerator.plot_area_vs_time(
    colonies,
    time_interval_minutes=30,
    save_path='area_plot.jpg'
)

# Plot normalized growth
fig, ax = PlotGenerator.plot_normalized_growth(colonies)

# Plot emergence times
fig, ax = PlotGenerator.plot_emergence_times(colonies)
```

**Methods:**
- `plot_area_vs_time(colonies, ...)`: Time series of colony areas
- `plot_diameter_vs_time(colonies, ...)`: Time series of colony diameters
- `plot_normalized_growth(colonies, ...)`: Growth curves normalized by emergence
- `plot_emergence_times(colonies, ...)`: Bar chart of emergence times

---

### Utility Classes

#### `ImageLoader`

Load and manage image files.

```python
from colonytracking.io import ImageLoader

# Load single image
img = ImageLoader.load('image.tif')

# Load image sequence
images = ImageLoader.load_sequence('/path/to/images/')

# Save image
ImageLoader.save(processed_image, 'output.tif')
```

---

#### `ImageConverter`

Convert between image formats.

```python
from colonytracking.io import ImageConverter

# Convert RGB to grayscale
gray = ImageConverter.to_grayscale(rgb_image)

# Convert grayscale to RGB
rgb = ImageConverter.to_rgb(gray_image)

# Normalize intensities
normalized = ImageConverter.normalize(image, method='minmax')
```

---

### Data Structures

#### `ColonyMeasurement`

Single measurement at one timepoint.

```python
from colonytracking.data import ColonyMeasurement

measurement = ColonyMeasurement(
    area=1500.0,          # Pixel count
    diameter=43.75,       # Calculated diameter
    centroid=(100.5, 200.3),  # Center coordinates
    pixel_list=np.array([...]),  # All pixels
    timestamp=0           # Frame index
)
```

---

#### `DetectionResult`

Result of initial colony detection.

```python
from colonytracking.data import DetectionResult

result = detector.detect(...)

print(f"Colonies: {len(result.colonies)}")
print(f"Initial detections: {result.num_detected}")
print(f"After filtering: {result.num_after_filtering}")
```

---

#### `TrackingResult`

Result of tracking one frame.

```python
result = tracker.track_frame(...)

print(f"Matched: {result.matched_count}")
print(f"Lost: {result.lost_count}")
print(f"Frame: {result.frame_number}")
```

---

### Configuration

All parameters can be customized via `colonytracking.config`:

```python
import colonytracking.config as config

# View defaults
print(config.DIFFERENCE_THRESHOLD)           # 20
print(config.TRACKING_DISTANCE_THRESHOLD)    # 15
print(config.ROI_RADIUS)                     # 3000
print(config.INTENSITY_CORRECTION_WINDOW)    # 25

# All configurable parameters:
# - DIFFERENCE_THRESHOLD
# - MIN_COLONY_AREA_SEPARATION
# - MIN_TRACKING_AREA
# - CIRCULARITY_MIN / CIRCULARITY_MAX
# - TRACKING_DISTANCE_THRESHOLD
# - ROI_RADIUS, ROI_CENTER
# - INTENSITY_CORRECTION_WINDOW
# - TIME_INTERVAL_MINUTES
# And many more...
```

---

## Error Handling

Common issues and solutions:

### Empty detection
- Check image contrast (colonies should be darker than background)
- Adjust `DIFFERENCE_THRESHOLD` in config
- Verify ROI settings
- Check intensity correction point selection

### False positives
- Increase `MIN_COLONY_AREA` threshold
- Tighten `CIRCULARITY_RANGE`
- Increase colony `separation` distance

### Tracking loss
- Reduce `TRACKING_DISTANCE_THRESHOLD`
- Check for colony merging/overlapping
- Verify imaging consistency

