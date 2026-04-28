## Usage Examples

### Example 1: Basic Colony Detection and Tracking

```python
from colonytracking import ColonyDetector, ColonyTracker, ImageLoader, GrowthAnalysis, PlotGenerator
import numpy as np

# Load images
loader = ImageLoader()
images = loader.load_sequence('/path/to/images/')

# Detect colonies in first image pair
detector = ColonyDetector({'separation': 50})
detection_result = detector.detect(images[0], images[1], correction_point=(400, 400))
colonies = detection_result.colonies

print(f"Detected {len(colonies)} colonies")

# Track through remaining frames
tracker = ColonyTracker()
for i, frame in enumerate(images[2:], start=2):
    tracking_result = tracker.track_frame(
        colonies,
        frame,
        images[0],  # Reference frame
        detection_result.roi_mask,
        correction_point=(400, 400)
    )
    print(f"Frame {i+1}: matched={tracking_result.matched_count}, lost={tracking_result.lost_count}")

# Analyze results
analysis = GrowthAnalysis.analyze(colonies)

print("\n=== Analysis Results ===")
for col_id, emergence_time in analysis.emergence_times.items():
    print(f"Colony {col_id}: emerged at frame {emergence_time}, growth rate = {analysis.growth_rates[col_id]:.3f} px/frame")

# Generate visualizations
PlotGenerator.plot_area_vs_time(colonies, save_path='area_plot.jpg')
PlotGenerator.plot_diameter_vs_time(colonies, save_path='diameter_plot.jpg')
PlotGenerator.plot_normalized_growth(colonies, save_path='growth_plot.jpg')
PlotGenerator.plot_emergence_times(colonies, save_path='emergence_plot.jpg')
```

---

### Example 2: Batch Processing

```python
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

# Process multiple image sets
image_directories = [
    '/data/experiment_1',
    '/data/experiment_2',
    '/data/experiment_3',
]

detector_config = {
    'separation': 50,
    'min_area': 1000,
}

all_results = {}

for image_dir in image_directories:
    images = ImageLoader.load_sequence(image_dir, sort=True)
    
    detector = ColonyDetector(detector_config)
    detection_result = detector.detect(images[0], images[1])
    colonies = detection_result.colonies
    
    tracker = ColonyTracker()
    for frame in images[2:]:
        tracker.track_frame(colonies, frame, images[0], detection_result.roi_mask)
    
    analysis = GrowthAnalysis.analyze(colonies)
    all_results[image_dir] = analysis
    
    print(f"{image_dir}: Detected {len(colonies)} colonies")

# Combine results
print(f"\nTotal experiments: {len(all_results)}")
```

---

### Example 3: Custom Detection Parameters

```python
# Customize detector behavior
custom_config = {
    'separation': 100,              # Stricter separation
    'min_area': 500,                # Lower minimum area
    'circularity_range': (0.85, 1.15),  # Looser circularity
    'difference_threshold': 25,     # Higher threshold for binary image
}

detector = ColonyDetector(custom_config)
result = detector.detect(background, colonies)

# Filter results manually if needed
large_colonies = [c for c in result.colonies if c.get_last_measurement().area > 5000]
print(f"Large colonies (>5000 px²): {len(large_colonies)}")
```

---

### Example 4: Interactive Visualization

```python
import matplotlib.pyplot as plt

detector = ColonyDetector()
result = detector.detect(background_img, colony_img)

# Display detected colonies on image
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Show original image
ax1.imshow(colony_img, cmap='gray')
ax1.set_title('Original Image')

# Show binary image with detected colonies
ax2.imshow(result.binary_image, cmap='gray')
ax2.set_title(f'Detected Colonies ({len(result.colonies)})')

# Overlay centroids
for i, colony in enumerate(result.colonies):
    measurement = colony.get_last_measurement()
    x, y = measurement.centroid
    ax2.plot(x, y, 'r*', markersize=15)
    ax2.text(x, y+20, str(i+1), color='red', fontsize=10)

plt.tight_layout()
plt.show()
```

---

### Example 5: Growth Rate Analysis

```python
from colonytracking import GrowthAnalysis
import numpy as np

analysis = GrowthAnalysis.analyze(colonies)

# Find fastest growing colony
fastest_id = max(analysis.growth_rates, key=analysis.growth_rates.get)
fastest_rate = analysis.growth_rates[fastest_id]

print(f"Fastest growing colony: Colony {fastest_id} ({fastest_rate:.3f} px/frame)")

# Find slowest growing
slowest_id = min(analysis.growth_rates, key=analysis.growth_rates.get)
slowest_rate = analysis.growth_rates[slowest_id]

print(f"Slowest growing colony: Colony {slowest_id} ({slowest_rate:.3f} px/frame)")

# Calculate average growth statistics
growth_rates = list(analysis.growth_rates.values())
print(f"\nGrowth statistics:")
print(f"  Mean: {np.mean(growth_rates):.3f} px/frame")
print(f"  Std Dev: {np.std(growth_rates):.3f} px/frame")
print(f"  Min: {np.min(growth_rates):.3f} px/frame")
print(f"  Max: {np.max(growth_rates):.3f} px/frame")
```

---

### Example 6: Export Results

```python
import pandas as pd

# Create results dataframe
results_data = []

for colony in colonies:
    diameters = colony.get_diameters()
    areas = colony.get_areas()
    
    for t, (d, a) in enumerate(zip(diameters, areas)):
        results_data.append({
            'colony_id': colony.colony_id,
            'timepoint': t,
            'diameter_px': d,
            'area_px2': a,
            'emergence_frame': colony.emergence_frame,
        })

df = pd.DataFrame(results_data)

# Save to CSV
df.to_csv('colony_measurements.csv', index=False)

# Summary statistics
summary = df.groupby('colony_id').agg({
    'area_px2': ['min', 'max', 'mean'],
    'diameter_px': ['min', 'max', 'mean'],
})

summary.to_csv('colony_summary.csv')
```

---

## Command Line Usage

```bash
# Launch GUI
colonytracking

# Run detection on single image set (future enhancement)
python -m colonytracking detect /path/to/images/ --separation 50 --output results.json

# Batch process (future enhancement)
python -m colonytracking batch /data/*/images/ --config config.yaml
```

