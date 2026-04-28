# Colony Tracking System - Design Document

**Version**: 1.0  
**Date**: April 22, 2026  
**Purpose**: Complete architectural and functional specification for clean-room rewrite in alternative language

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Structures](#data-structures)
5. [Algorithms](#algorithms)
6. [User Workflows](#user-workflows)
7. [GUI Specification](#gui-specification)
8. [API Reference](#api-reference)
9. [Implementation Notes](#implementation-notes)

---

## System Overview

### Purpose
The Colony Tracking System is an image analysis application designed to:
- Detect bacterial colonies that emerge between time-lapse microscopy images
- Track individual colonies across multiple time points
- Measure colony growth metrics (area, diameter, growth rate)
- Provide interactive manual validation and selection of detected colonies

### Domain Context
- **Input**: Time-lapse sequence of microscopy images showing bacterial growth on a petri dish
- **Processing**: Image subtraction, blob detection, circularity filtering, spatial tracking
- **Output**: Colony measurements (area, diameter, growth trajectories) and visualization
- **User Interaction**: Interactive GUI for parameter tuning and manual validation

### Target Use Case
Bacterial growth studies where:
- Images are captured at regular intervals (e.g., 30-minute intervals)
- Colonies emerge gradually from a background
- Multiple colonies need individual tracking
- User validation is critical for accuracy

---

## Architecture

### System Layer Diagram
```
┌─────────────────────────────────────┐
│    GUI Application Layer            │
│  (bacteriaTrackerGUI)              │
├─────────────────────────────────────┤
│    Processing Pipeline              │
│  • Colony Detection                 │
│  • Colony Tracking                  │
│  • Growth Analysis                  │
├─────────────────────────────────────┤
│    Image Processing Core            │
│  • Image I/O                        │
│  • Pixel-level operations           │
│  • Region analysis (regionprops)    │
│  • Binary image operations          │
├─────────────────────────────────────┤
│    Utility Functions                │
│  • Circle drawing                   │
│  • Mask generation                  │
│  • Line drawing (Bresenham)         │
└─────────────────────────────────────┘
```

### Design Patterns

1. **State Management**: Application state maintained in GUI handles structure
2. **Functional Decomposition**: Large operations split into focused sub-functions
3. **Image Processing Pipeline**: Sequential image transformations with intermediate visualization
4. **Interactive Validation**: User-driven filtering through ginput (mouse click selection)

---

## Core Components

### 1. Main GUI Application (bacteriaTrackerGUI)

**File**: `bacteriaTrackerGUI.m` + `bacteriaTrackerGUI.fig`

**Responsibility**: 
- User interface for entire application
- File selection and management
- Orchestration of processing pipeline
- Results visualization and analysis

**Key Functions**:
- `selectFiles_Callback`: File selection dialog
- `pushbutton_selectcoloniessub_Callback`: Trigger initial colony detection
- `pushbutton_area_Callback`: Plot area vs. time
- `pushbutton_diameter_Callback`: Plot diameter vs. time
- `pushbutton_normgrowth_Callback`: Plot normalized growth rate
- `pushbutton_emergence_Callback`: Plot emergence time

**State Variables** (stored in handles structure):
- `handles.files`: Selected image file list (cell array of strings)
- `handles.path`: Directory path of selected files
- `handles.colonies`: Main data structure containing detected colonies
- `handles.groupNum`: Group/batch number (user input)
- `handles.seperation`: Minimum separation distance between colonies (pixels)
- `handles.lower`: Growth rate lower threshold (default 0.5)
- `handles.upper`: Growth rate upper threshold (default 1.1)

**Critical Dependencies**:
- `colonySelectorSub()`: Initial colony detection
- `colonyTrackerSub()`: Time-based tracking
- `circleMask()`: Region of interest mask generation
- `circle()`: Visualization of detected colonies

---

### 2. Colony Selector Sub-function (colonySelectorSub)

**File**: `colonySelectorSub.m`

**Input Parameters**:
- `img1` (matrix): Background image without colonies
- `img2` (matrix): Image with colonies present
- `mask` (logical matrix): Circular ROI mask
- `dia` (scalar): Minimum separation distance between colony centroids (pixels)

**Output Parameters**:
- `result` (struct array): Detected colonies with fields:
  - `Area`: Pixel count of colony
  - `Diameter`: Calculated as $\sqrt{\text{Area}/\pi} \times 2$ (assuming circular)
  - `PixelList`: Cell containing [x, y] coordinates of colony pixels
  - `Centroid`: Cell containing [x, y] centroid coordinates
- `image` (logical matrix): Binary image of final colony locations
- `colorPoint` (vector): [row, col] used for light intensity correction

**Algorithm Overview**:

#### Phase 1: Image Preprocessing
1. Convert RGB to grayscale (if necessary)
2. Resize for display if dimensions exceed 1500×1500 pixels
3. **Light Intensity Correction**:
   - User clicks on a reference point in the image
   - Extract 50×50 pixel region around click (±25 pixels)
   - Calculate mean intensity in original and current images
   - Adjust current image: `grayImg = grayImg + (aveColorNow - aveColorOrig)`

#### Phase 2: Binary Image Generation
1. Create difference image: `binImg = (grayImg - grayImg2) > 20`
   - Threshold of 20 is hard-coded; colonies are darker than background
   - Values exceed 20 indicate colony presence
2. Apply ROI mask: `binImg = binImg & mask`

#### Phase 3: Initial Blob Detection
1. Use `regionprops()` to extract blob properties:
   - `Centroid`: (x, y) center of mass
   - `Area`: Pixel count
   - `PixelList`: All pixel coordinates [x, y]
   - `MajorAxisLength`: Longest ellipse axis
   - `MinorAxisLength`: Shortest ellipse axis
2. Calculate diameter for each blob: `Diameter = sqrt(Area/π) * 2`

#### Phase 4: Separation Filtering
- **Purpose**: Remove colonies that are too close together (merged detections)
- **Logic**: For each blob with Area > 1000:
  - Calculate distance to all other blobs
  - Distance = (distance between centroids) - (Diameter₁/2) - (Diameter₂/2)
  - If distance < `dia` parameter: mark blob as invalid
- **Result**: Blobs marked invalid have PixelList set to empty

#### Phase 5: Circularity Filtering
- **Circularity Metric**: `circularity = MajorAxisLength / MinorAxisLength`
  - Value = 1: perfect circle
  - Value > 1: elongated ellipse
- **Filter Criteria**:
  - Keep only blobs with: `0.9 < circularity < 1.1` (±10% tolerance)
  - AND `Area > 1000` (hard-coded threshold)

#### Phase 6: ROI Edge Removal
- Purpose: Eliminate colonies touching the circular ROI boundary
- Match current blobs against original blobs using centroid comparison
- Keep only blobs with exact centroid matches to original set

#### Phase 7: Interactive Manual Deselection
1. Display binary image overlaid with detected colonies
2. User clicks on colonies to exclude (using `ginput()`)
3. For each click:
   - Find nearest colony to click location
   - Remove that colony from result
   - Update centroid visualization
   - Prompt for next click
4. Loop until user clicks outside image or issues empty input

**Output Format**:
```
result(i).Area = scalar (pixel count)
result(i).Diameter = scalar (pixels)
result(i).PixelList = cell array containing [x, y] coordinate matrix
result(i).Centroid = cell array containing [x, y] vector
```

---

### 3. Colony Tracker Sub-function (colonyTrackerSub)

**File**: `colonyTrackerSub.m`

**Input Parameters**:
- `prev` (struct array): Previous timepoint's colonies (contains Area, Centroid, PixelList, Diameter as cell arrays with temporal dimension)
- `img` (matrix): Current image
- `orig` (matrix): First/reference image from sequence
- `mask` (logical matrix): Circular ROI mask
- `colorPoint` (vector): Reference point for light correction [row, col]

**Output Parameters**:
- `prev` (struct array): Updated with measurements from current timepoint

**Algorithm Overview**:

#### Phase 1: Image Preparation
1. Convert to grayscale if RGB
2. Apply light intensity correction (same as colonySelectorSub):
   - Extract reference region at `colorPoint`
   - Calculate intensity difference
   - Adjust current image accordingly

#### Phase 2: Binary Image Creation
1. Compute difference: `binImg = (grayImg2 - grayImg) > 20`
   - Note: grayImg2 is the original, grayImg is current
   - Inverted compared to colonySelectorSub
2. Apply mask: `binImg = binImg & mask`

#### Phase 3: Blob Detection and Filtering
1. Extract regionprops with Area, Centroid, PixelList
2. Filter: Keep only blobs with `Area > 100`
3. Create L array containing filtered blobs

#### Phase 4: Temporal Matching
- **Goal**: Associate each previous colony with current frame's blobs

For each previous colony `j`:
1. Get previous centroid: `center = cell2mat(prev(j).Centroid)`
2. Calculate distance to all current blobs:
   ```
   dist(i) = sqrt((L(i).Centroid(1) - center(1))² + 
                  (L(i).Centroid(2) - center(2))²)
   ```
3. Decision logic:
   - If `min(dist) > 15`: Colony not found (lost or merged)
     - Append dummy values: Area=0, Centroid=(previous), Diameter=0
   - If `min(dist) ≤ 15`: Colony found
     - Find blob index with minimum distance
     - Append actual measurements to previous colony's temporal arrays

#### Phase 5: Temporal Array Extension
- Each measurement field is maintained as an array (grows with each frame):
  - `prev(j).Area` → append current frame's area
  - `prev(j).Centroid` → append current frame's centroid (as cell)
  - `prev(j).PixelList` → append current frame's pixel list (as cell)
  - `prev(j).Diameter` → append current frame's diameter

**Critical Notes**:
- Previous colonies are never removed; gap frames recorded with zero area
- Temporal data stored as cell arrays of increasing length
- No prediction/Kalman filtering; simple nearest-neighbor matching
- Distance threshold of 15 pixels is hard-coded

---

### 4. Utility: Circle Mask Generation (circleMask)

**File**: `circleMask.m`

**Input Parameters**:
- `img` (matrix): Reference image (for size determination only)
- `rad` (scalar): Circle radius in pixels
- `center` (vector): [x, y] center coordinates
- `deg` (scalar): Angular resolution in degrees (e.g., 1 = 360 points, 3 = 120 points)

**Output Parameters**:
- `mask` (logical matrix): Binary mask with same size as input image; circle=true, background=false

**Algorithm**:
1. Create false-initialized logical matrix same size as img
2. Calculate circle perimeter points:
   - For each angle from `deg` to 360 by step `deg`:
     - Convert to radians: `angle = 2π/360 × degrees`
     - Calculate point: `x = center(1) + rad × cos(angle)`
     - Calculate point: `y = center(2) + rad × sin(angle)`
     - Clamp to image bounds
3. Draw lines between consecutive perimeter points using `pixelLine()`
4. Fill interior using `imfill()` with 'holes' option

**Purpose**: Define region of interest to exclude artifacts outside petri dish

---

### 5. Utility: Pixel Line Drawing (pixelLine)

**File**: `pixelLine.m`

**Input Parameters**:
- `x0, y0` (scalars): Starting point
- `x1, y1` (scalars): Ending point
- `grayimg` (matrix): Image to draw on (uint8)
- `intensity` (scalar): Pixel value to write

**Output Parameters**:
- `grayimg` (matrix): Modified image with line drawn

**Algorithm**: Bresenham's line algorithm
1. Calculate absolute differences: `dx = |x1-x0|`, `dy = |y1-y0|`
2. Determine step direction: `sx = sign(x1-x0)`, `sy = sign(y1-y0)`
3. Initialize error: `err = dx - dy`
4. Iterate from start to end:
   - Set pixel at current position to intensity
   - Calculate `e2 = 2 × err`
   - If `e2 > -dy`: step x, update error
   - If `e2 < dx`: step y, update error
5. Continue until reaching endpoint

**Purpose**: Efficient integer-only line rasterization for mask generation

---

### 6. Utility: Circle Drawing (circle)

**File**: `circle.m`

**Input Parameters**:
- `x, y` (scalars): Circle center
- `r` (scalar): Circle radius
- `color` (vector): RGB color [r, g, b]

**Output**: Plots circle outline on current figure

**Algorithm**:
1. Generate angle array: `ang = 0 : 0.01 : 2π`
2. Calculate perimeter points:
   ```
   xp = r × cos(ang)
   yp = r × sin(ang)
   ```
3. Plot points: `plot(x + xp, y + yp, 'color', color)`

**Purpose**: Visualization overlay for colony detection results

---

## Data Structures

### Colony Result Structure

**Primary data structure** representing a single detected colony:

```
result(i).Area              % scalar: pixel count at each timepoint (or cell array for multi-frame)
result(i).Diameter          % scalar or array: calculated as 2*sqrt(Area/π)
result(i).PixelList         % cell: {[x1 y1; x2 y2; ...]} pixel coordinates
result(i).Centroid          % cell: {[x y]} center of mass coordinates
```

**Initial Detection** (from `colonySelectorSub`):
- Single timepoint measurement
- Each field is scalar or cell
- Example: `result(1).Area = 1500` (pixels)

**After Tracking** (from `colonyTrackerSub`):
- Temporal accumulation
- Fields become cell arrays of growing length
- Example: 
  ```
  result(1).Area = [1500, 1650, 1800, ...]  (frame 1, 2, 3, ...)
  result(1).Centroid = {[100, 200], [101, 201], [102, 202], ...}
  ```

### GUI Handles Structure

```
handles.files           % cell array: filenames
handles.path            % string: directory path
handles.colonies        % struct array: detected colonies (result from processing)
handles.groupNum        % scalar: user-specified group identifier
handles.seperation      % scalar: minimum colony separation (pixels)
handles.lower           % scalar: growth rate lower threshold (default 0.5)
handles.upper           % scalar: growth rate upper threshold (default 1.1)
handles.output          % handle: reference to main GUI window
```

---

## Algorithms

### Image Difference and Colony Detection

**Principle**: Colonies are darker than background due to bacterial density

1. **Grayscale Conversion**: RGB → single-channel intensity
2. **Light Correction**: Account for uneven illumination
   - Use user-selected reference point
   - Measure intensity difference in reference region
   - Apply global offset to current image
3. **Subtraction**: Compute difference image
   - `diff = background - current` (original image minus current)
   - In colonySelectorSub: `(grayImg - grayImg2) > 20`
   - Threshold 20 chosen empirically
4. **Binary Thresholding**: Any difference > 20 becomes candidate colony pixel
5. **Morphological Filtering**:
   - ROI mask application (exclude outside petri dish)
   - Size filtering (Area > 1000)
   - Circularity filtering (0.9 < MajorAxis/MinorAxis < 1.1)
   - Separation filtering (minimum distance between centroids)

### Temporal Tracking

**Nearest Neighbor Matching**:
- No prediction, no filtering
- Frame-to-frame distance calculation
- Distance threshold = 15 pixels
- Lost colonies recorded with zero area (not removed)

**Advantages**: Simple, deterministic, handles merging/splitting events by stopping track
**Disadvantages**: Cannot recover from occlusion, no trajectory smoothing

### Growth Measurement

**Metrics**:
1. **Area**: Raw pixel count per frame
2. **Diameter**: Assuming circular geometry: $D = 2\sqrt{\frac{\text{Area}}{\pi}}$
3. **Normalized Growth**: Ratio of diameter at frame $i$ to diameter at emergence

---

## User Workflows

### Workflow 1: Initial Colony Detection

**Preconditions**: User has image sequence loaded

**Steps**:
1. User clicks "Select Colonies" button
2. System:
   - Loads first image (background reference)
   - Loads second image (with colonies)
   - Generates circular ROI mask (hardcoded radius 3000, center = image center)
   - Prompts user to click on well-lit region for intensity correction
3. User clicks on image area with uniform lighting
4. System:
   - Creates binary difference image
   - Detects blobs using regionprops
   - Filters by separation (from GUI input field)
   - Filters by circularity
   - Filters by size
   - Removes edge-touching colonies
5. System displays colony circles on image with numbers (1, 2, 3, ...)
6. User can click on colonies to deselect erroneous detections
7. Process repeats until user stops clicking
8. Results saved in `handles.colonies`

**Key User Inputs**:
- `handles.seperation`: Minimum pixel distance between colony centers

**Output**: Array of colony structures with initial measurements

---

### Workflow 2: Colony Tracking

**Preconditions**: Initial colonies detected, image sequence available

**Steps**:
1. For each image frame (starting frame 3):
   - Call `colonyTrackerSub()` with:
     - Previous colony data
     - Current frame image
     - First (reference) image
     - Circular ROI mask
     - Light correction reference point
2. System:
   - Corrects light intensity in current frame
   - Creates binary difference image
   - Detects blobs (Area > 100)
   - Matches to previous colonies (distance < 15 pixels)
   - Appends measurements to each colony's temporal arrays
3. Repeat for all remaining frames
4. Final result: Each colony has growth trajectory across all timepoints

---

### Workflow 3: Analysis and Visualization

**Available Analysis Views**:

1. **Area vs. Time**: Plot area measurements for each colony
   - Y-axis: Area (pixels)
   - X-axis: Time (frames, labeled as "30 min" intervals)
   - Color-coded per colony using `jet()` colormap

2. **Diameter vs. Time**: Plot diameter measurements
   - Y-axis: Diameter (pixels)
   - X-axis: Time (frames)

3. **Normalized Growth**: Plot growth rate
   - Calculation: `Diameter(t) / Diameter(t_emerge)`
   - Typically shows sigmoid growth curve

4. **Emergence Time**: Bar chart of when colonies first detected

All plots use consistent colony-wise coloring for cross-reference.

---

## GUI Specification

### Layout Components

**Input Controls**:
- **Group Number** (edit field): User-specified batch identifier
- **Separation Distance** (edit field): Minimum colony separation in pixels
- **Select Files** (button): `uigetfile()` dialog for multiselect

**Processing Controls**:
- **Select Colonies** (button): Trigger initial detection workflow
  - Calls `colonySelectorSub()` with loaded images
  - Prompts for intensity correction point
  - Allows manual deselection
  - Saves results to `handles.colonies`

**Analysis Controls** (enabled after colony selection):
- **Plot Area** (button): Time-series area visualization
- **Plot Diameter** (button): Time-series diameter visualization
- **Plot Normalized Growth** (button): Growth rate visualization
- **Plot Emergence** (button): Emergence time bar chart

**Display Area**:
- Image display showing:
  - Colony circles with center points
  - Colony numbers as text labels
  - Color-coded by colony index

### File Organization

**Output Directory Structure**:
```
<input_directory>/
├── figures/
│   ├── selectedColonies_<separation>.jpg
│   └── selectedColonies_<separation>.fig
├── <image1>_presentation
│   └── video frames (avi/mp4)
└── <image1>_presentation1
    └── growth animation frames (avi/mp4)
```

---

## API Reference

### colonySelectorSub

```
[ result, image, colorPoint ] = colonySelectorSub( img1, img2, mask, dia )

INPUT:
  img1      - MxNx3 (RGB) or MxN (grayscale) matrix: background image
  img2      - MxNx3 (RGB) or MxN (grayscale) matrix: image with colonies
  mask      - MxN logical matrix: circular ROI mask
  dia       - scalar: minimum separation between colonies (pixels)

OUTPUT:
  result    - 1xP struct array:
              result(i).Area         - scalar
              result(i).Diameter     - scalar
              result(i).PixelList    - {[x y] matrix}
              result(i).Centroid     - {[x y] vector}
  image     - MxN logical matrix: final binary colony image
  colorPoint - [row col] vector: user-selected reference point
```

### colonyTrackerSub

```
[ prev ] = colonyTrackerSub( prev, img, orig, mask, colorPoint )

INPUT:
  prev      - struct array: previous timepoint colonies (see colonySelectorSub output)
  img       - MxN matrix: current timepoint image
  orig      - MxN matrix: reference (first) image
  mask      - MxN logical matrix: circular ROI mask
  colorPoint - [row col] vector: light correction reference point

OUTPUT:
  prev      - struct array: MODIFIED IN-PLACE with appended measurements
              prev(i).Area(end+1)     = current area
              prev(i).Centroid(end+1) = {current centroid}
              prev(i).PixelList(end+1) = {current pixels}
              prev(i).Diameter(end+1) = current diameter
```

### circleMask

```
[ mask ] = circleMask( img, rad, center, deg )

INPUT:
  img     - reference image for size
  rad     - scalar: circle radius
  center  - [x y] vector: circle center
  deg     - scalar: angular resolution in degrees

OUTPUT:
  mask    - MxN logical matrix: true inside circle, false outside
```

### circle

```
circle(x, y, r, color)

INPUT:
  x, y  - scalars: circle center
  r     - scalar: radius
  color - [R G B] vector: color for line plot
```

### pixelLine

```
[ grayimg ] = pixelLine( x0, y0, x1, y1, grayimg, intensity )

INPUT:
  x0, y0      - scalars: start point
  x1, y1      - scalars: end point
  grayimg     - matrix: image to draw on
  intensity   - scalar: pixel value to write

OUTPUT:
  grayimg     - modified image with line drawn
```

---

## Implementation Notes

### Hard-Coded Parameters

| Parameter | Value | Location | Purpose |
|-----------|-------|----------|---------|
| Resize threshold | 1500×1500 | colonySelectorSub | Display optimization |
| Difference threshold | 20 | colonySelectorSub, colonyTrackerSub | Binary image generation |
| Area minimum (phase 4) | 1000 pixels | colonySelectorSub | Separation filter |
| Circularity range | 0.9–1.1 | colonySelectorSub | Circular shape filter |
| Area minimum (tracking) | 100 pixels | colonyTrackerSub | Blob noise filter |
| Distance threshold | 15 pixels | colonyTrackerSub | Temporal matching |
| ROI radius | 3000 pixels | bacteriaTrackerGUI | Petri dish edge |
| ROI center | Image center | bacteriaTrackerGUI | Petri dish centering |
| Intensity correction window | ±25 pixels | colonySelectorSub, colonyTrackerSub | Light reference region |

### Data Flow

```
User Input
    ↓
[File Selection]
    ↓
Read Image Pair (img1, img2)
    ↓
[User selects intensity correction point]
    ↓
colonySelectorSub()
    ├─ Binary diff image
    ├─ Blob detection
    ├─ Multi-stage filtering
    └─ Interactive deselection
    ↓
[Result: Colony array at frame 2]
    ↓
For Frame 3..N:
  colonyTrackerSub()
    ├─ Load frame
    ├─ Detect blobs
    ├─ Match to previous
    └─ Append measurements
    ↓
[Result: Temporal colony data]
    ↓
User clicks analysis button (area/diameter/growth/emergence)
    ↓
Generate visualization
    ↓
Display plot
```

### Critical Implementation Considerations

1. **Cell Array Handling**: Centroids and PixelLists stored as cells for heterogeneous data (mixed scalar and matrix)

2. **Index Conversion**: MATLAB uses 1-based indexing; column-major order
   - `regionprops` returns (row, col) which is (y, x) in image coordinates
   - Be careful when converting to/from typical x-y notation

3. **Memory Management**: Large image sequences can consume significant memory
   - Resizing for display is optimization
   - PixelList storage for every colony at every frame

4. **User Interaction Blocking**: `ginput()` blocks execution until input received
   - Loop in manual deselection phase continues until empty click

5. **Error Handling**: Minimal in original code
   - Should add checks for:
     - Empty file selection
     - Non-existent files
     - Insufficient image frames
     - Invalid region of interest

### Timing and Intervals

- Assumption: Images captured at **30-minute intervals**
- Time axis labels use this interval
- No absolute timestamps; purely relative frame counting
- Frame 1 is reference (background only)
- Colonies first detected in frame 2
- Tracking proceeds from frame 3 onwards

### Visualization Details

**Figure Windows** created during processing:
1. Display image for intensity point selection
2. Binary difference image ("original")
3. Separation filter result ("close things gone")
4. Circularity filter result ("circular and small things gone")
5. ROI mask applied ("mask applied")
6. Edge elimination result ("blobs on edge eliminated")
7. Final deselection interface with color-coded colonies
8. Final result with numbered colonies and circles

Each figure is interactive and user can interact with next step.

**Colors**: 
- Used: `jet()` colormap for colony differentiation
- Provides maximum visual separation across spectrum

---

## Migration Guide for Rewrite

### Key Decisions to Make

1. **Image Library**: 
   - Original uses MATLAB's Image Processing Toolbox
   - Alternatives: OpenCV (C++/Python), PIL/Pillow (Python), scikit-image (Python)

2. **GUI Framework**:
   - Original uses MATLAB's built-in `guide` and uicontrol
   - Alternatives: Qt, GTK, Tkinter (Python), WPF (C#)

3. **Data Structure**:
   - Original uses struct arrays with cell arrays for flexibility
   - Modern equivalent: Classes/dataclasses with lists or numpy arrays

4. **Processing Model**:
   - Maintain state in application object vs. passing through function calls
   - Consider immutable data vs. in-place modification (colonyTrackerSub modifies input)

5. **Parameter Configuration**:
   - Hard-coded values should become configurable constants
   - Consider configuration file or ini/yaml format

### Recommended Refactoring Opportunities

1. **Parameterize Hard-Coded Values**: Create configuration structure
2. **Add Error Handling**: Validate inputs, handle edge cases
3. **Improve Temporal Tracking**: Consider Kalman filtering or Hungarian algorithm for multi-object matching
4. **Add Progress Indication**: Long image sequences may require status bars
5. **Performance Optimization**: 
   - Vectorize loops where possible
   - Consider parallel frame processing
   - Implement adaptive thresholds instead of fixed values
6. **Test Coverage**: Original has no explicit unit tests
7. **Documentation**: Add docstrings and inline comments

### Validation Checkpoints

When reimplementing, verify against original:
1. Initial blob detection matches on first image pair
2. Circularity filtering removes same blobs
3. Separation filtering produces identical results
4. Temporal tracking follows same correspondence logic
5. Growth measurements (area, diameter) match exactly
6. Visualization displays in same color order

---

## Appendix: Mathematical Formulas

### Colony Diameter Calculation
$$D = 2\sqrt{\frac{A}{\pi}}$$
Where:
- D = Diameter (pixels)
- A = Area (pixels²)
- Assumes circular geometry

### Circularity Metric
$$C = \frac{\text{MajorAxisLength}}{\text{MinorAxisLength}}$$
Where:
- C ≈ 1: circular blob
- C > 1: elongated blob
- Valid range accepted: 0.9 < C < 1.1

### Spatial Distance (2D)
$$\text{dist} = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$
Used for colony-to-colony separation and temporal matching.

### Centroid Calculation
$$\text{Centroid}_x = \frac{\sum_{i} x_i}{n}, \quad \text{Centroid}_y = \frac{\sum_{i} y_i}{n}$$
Where n = number of pixels in blob, calculated by regionprops.

---

**Document Complete**

This design document provides sufficient detail for implementing an equivalent system in any programming language with image processing capabilities. All algorithms, data structures, workflows, and parameters are explicitly specified.

