"""
Data structures for Colony Tracking System.

Defines dataclasses for storing colony detection and tracking results.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np


@dataclass
class ColonyMeasurement:
    """Single timepoint measurement for a colony."""
    
    area: float
    """Pixel count of colony region"""
    
    diameter: float
    """Diameter calculated as 2*sqrt(area/π)"""
    
    centroid: Tuple[float, float]
    """[x, y] center of mass coordinates"""
    
    pixel_list: np.ndarray = field(default_factory=lambda: np.empty((0, 2)))
    """Array of [x, y] pixel coordinates belonging to colony"""
    
    timestamp: int = 0
    """Frame number or time index"""


@dataclass
class Colony:
    """Complete temporal tracking data for a single detected colony."""
    
    colony_id: int
    """Unique identifier for this colony"""
    
    measurements: List[ColonyMeasurement] = field(default_factory=list)
    """List of measurements across all timepoints"""
    
    emergence_frame: int = -1
    """Frame index when colony first detected (>0 threshold)"""
    
    def get_areas(self) -> np.ndarray:
        """Get area measurements across all timepoints."""
        return np.array([m.area for m in self.measurements])
    
    def get_diameters(self) -> np.ndarray:
        """Get diameter measurements across all timepoints."""
        return np.array([m.diameter for m in self.measurements])
    
    def get_centroids(self) -> np.ndarray:
        """Get centroid positions across all timepoints."""
        return np.array([m.centroid for m in self.measurements])
    
    def get_normalized_growth(self) -> np.ndarray:
        """Get diameter normalized by emergence frame diameter."""
        diameters = self.get_diameters()
        if self.emergence_frame >= 0 and self.emergence_frame < len(diameters):
            emergence_diameter = diameters[self.emergence_frame]
            if emergence_diameter > 0:
                return diameters / emergence_diameter
        return np.ones_like(diameters)
    
    def append_measurement(self, measurement: ColonyMeasurement) -> None:
        """Add a measurement at next timepoint."""
        measurement.timestamp = len(self.measurements)
        self.measurements.append(measurement)
    
    def get_last_measurement(self) -> ColonyMeasurement:
        """Get most recent measurement."""
        if self.measurements:
            return self.measurements[-1]
        return None


@dataclass
class DetectionResult:
    """Result from colony detection phase."""
    
    colonies: List[Colony] = field(default_factory=list)
    """List of detected colonies"""
    
    binary_image: np.ndarray = field(default_factory=lambda: np.empty((0, 0), dtype=bool))
    """Final binary image showing colony regions"""
    
    intensity_correction_point: Tuple[int, int] = (0, 0)
    """[row, col] of user-selected light correction reference"""
    
    num_detected: int = 0
    """Total number of colonies detected"""
    
    num_after_filtering: int = 0
    """Number of colonies after all filtering stages"""
    
    roi_mask: np.ndarray = field(default_factory=lambda: np.empty((0, 0), dtype=bool))
    """ROI mask applied during detection"""


@dataclass
class TrackingResult:
    """Result from temporal tracking phase."""
    
    colonies: List[Colony] = field(default_factory=list)
    """List of colonies with temporal tracking data"""
    
    frame_number: int = 0
    """Current frame number being processed"""
    
    matched_count: int = 0
    """Number of colonies matched to previous frame"""
    
    lost_count: int = 0
    """Number of colonies lost in this frame"""
    
    new_count: int = 0
    """Number of new colonies appearing in this frame (should be 0 after frame 2)"""


@dataclass
class AnalysisResult:
    """Results from growth analysis."""
    
    colonies: List[Colony] = field(default_factory=list)
    """Colony data with computed metrics"""
    
    emergence_times: dict = field(default_factory=dict)
    """Mapping of colony_id -> emergence frame"""
    
    growth_rates: dict = field(default_factory=dict)
    """Mapping of colony_id -> growth rate (pixels/frame or similar)"""
    
    final_sizes: dict = field(default_factory=dict)
    """Mapping of colony_id -> final measurement"""
