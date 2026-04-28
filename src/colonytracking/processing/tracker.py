"""
Colony tracking module implementing temporal tracking across frames.

Performs frame-to-frame matching using nearest-neighbor distance-based
association to follow individual colonies through time.
"""

import numpy as np
from typing import List, Optional
import logging

from colonytracking import config
from colonytracking.data import Colony, ColonyMeasurement, TrackingResult
from colonytracking.io.image import ImageConverter
from colonytracking.processing.core import (
    BlobDetector,
    CircleMask,
    ImageDifference,
    IntensityCorrection,
)

logger = logging.getLogger(__name__)


class ColonyTracker:
    """Track colonies across multiple time frames."""
    
    def __init__(self, config_dict: Optional[dict] = None):
        """
        Initialize tracker with configuration.
        
        Parameters
        ----------
        config_dict : dict, optional
            Configuration overrides. Keys:
            - distance_threshold: max pixels for matching (default 15)
            - min_area: minimum area for tracking
            - difference_threshold: binary image threshold
        """
        self.config = config.DEFAULT_TRACKER_CONFIG.copy()
        if config_dict:
            self.config.update(config_dict)
        
        self.distance_threshold = self.config['distance_threshold']
        self.min_area = self.config['min_area']
        self.difference_threshold = self.config['difference_threshold']
        
        logger.info(f"Initialized ColonyTracker with distance_threshold={self.distance_threshold}px")
    
    def track_frame(self, colonies: List[Colony], current_frame: np.ndarray,
                   reference_frame: np.ndarray,
                   roi_mask: np.ndarray,
                   correction_point: Optional[tuple] = None,
                   frame_number: int = -1) -> TrackingResult:
        """
        Track colonies in a new frame.
        
        Parameters
        ----------
        colonies : List[Colony]
            Colonies from previous frame (will be updated in-place)
        current_frame : np.ndarray
            Current frame image
        reference_frame : np.ndarray
            Reference/background image
        roi_mask : np.ndarray
            Circular ROI mask
        correction_point : tuple, optional
            (y, x) point for light intensity correction
        frame_number : int, optional
            Frame index (for logging)
            
        Returns
        -------
        TrackingResult
            Tracking results and statistics
        """
        logger.debug(f"Tracking frame {frame_number}: {len(colonies)} existing colonies")
        
        # Phase 1: Prepare current frame
        logger.debug("Phase 1: Preparing current frame")
        current_frame = ImageConverter.to_grayscale(current_frame)
        reference_frame = ImageConverter.to_grayscale(reference_frame)
        
        # Phase 2: Apply intensity correction
        if correction_point is not None:
            logger.debug(f"Phase 2: Applying light intensity correction")
            current_frame = IntensityCorrection.correct_intensity(
                current_frame, reference_frame, correction_point,
                window=config.INTENSITY_CORRECTION_WINDOW
            )
        else:
            logger.debug("Phase 2: Skipping intensity correction")
        
        # Phase 3: Create binary image
        # Note: In tracking, diff is inverted: (orig - current) not (current - orig)
        logger.debug("Phase 3: Creating binary difference image")
        binary_image = ImageDifference.compute_difference(
            reference_frame, current_frame,
            threshold=self.difference_threshold
        )
        binary_image = binary_image & roi_mask
        
        # Phase 4: Detect blobs in current frame
        logger.debug("Phase 4: Detecting blobs in current frame")
        blobs = BlobDetector.detect_blobs(binary_image)
        blobs = BlobDetector.filter_by_area(blobs, self.min_area)
        logger.debug(f"Detected {len(blobs)} blobs in current frame")
        
        # Phase 5: Temporal matching
        logger.debug("Phase 5: Performing temporal matching")
        matched_count = 0
        lost_count = 0
        
        for colony in colonies:
            # Get previous centroid
            last_measurement = colony.get_last_measurement()
            if last_measurement is None:
                continue
            
            prev_centroid = np.array(last_measurement.centroid)
            
            # Calculate distance to all current blobs
            if len(blobs) == 0:
                # No blobs detected - colony lost
                measurement = ColonyMeasurement(
                    area=0.0,
                    diameter=0.0,
                    centroid=tuple(prev_centroid),
                    pixel_list=np.empty((0, 2)),
                    timestamp=len(colony.measurements),
                )
                colony.measurements.append(measurement)
                lost_count += 1
                continue
            
            distances = []
            for blob in blobs:
                dist = np.linalg.norm(blob['centroid'] - prev_centroid)
                distances.append(dist)
            
            min_dist_idx = np.argmin(distances)
            min_dist = distances[min_dist_idx]
            
            # Decision logic
            if min_dist > self.distance_threshold:
                # Colony not found - record lost
                logger.debug(f"Colony {colony.colony_id} lost (min distance {min_dist:.1f} > {self.distance_threshold})")
                measurement = ColonyMeasurement(
                    area=0.0,
                    diameter=0.0,
                    centroid=tuple(prev_centroid),
                    pixel_list=np.empty((0, 2)),
                    timestamp=len(colony.measurements),
                )
                colony.measurements.append(measurement)
                lost_count += 1
            else:
                # Colony found - update with new measurements
                logger.debug(f"Colony {colony.colony_id} matched (distance {min_dist:.1f}px)")
                blob = blobs[min_dist_idx]
                
                diameter = 2 * np.sqrt(blob['area'] / np.pi)
                measurement = ColonyMeasurement(
                    area=float(blob['area']),
                    diameter=float(diameter),
                    centroid=tuple(blob['centroid']),
                    pixel_list=blob['pixel_list'],
                    timestamp=len(colony.measurements),
                )
                colony.measurements.append(measurement)
                matched_count += 1
        
        # Create tracking result
        result = TrackingResult(
            colonies=colonies,
            frame_number=frame_number,
            matched_count=matched_count,
            lost_count=lost_count,
            new_count=0,  # No new colonies expected after initial detection
        )
        
        logger.info(f"Frame {frame_number}: matched={matched_count}, lost={lost_count}")
        return result
    
    def track_sequence(self, colonies: List[Colony], frames: List[np.ndarray],
                      reference_frame: np.ndarray, roi_mask: np.ndarray,
                      correction_point: Optional[tuple] = None) -> List[TrackingResult]:
        """
        Track colonies through entire frame sequence.
        
        Parameters
        ----------
        colonies : List[Colony]
            Initial colonies from detection
        frames : List[np.ndarray]
            Sequence of frames (starting from frame 3)
        reference_frame : np.ndarray
            Reference/background frame
        roi_mask : np.ndarray
            Circular ROI mask
        correction_point : tuple, optional
            Light correction point
            
        Returns
        -------
        List[TrackingResult]
            Tracking results for each frame
        """
        results = []
        
        for frame_idx, frame in enumerate(frames, start=3):
            logger.info(f"Processing frame {frame_idx}/{len(frames) + 2}")
            result = self.track_frame(
                colonies, frame, reference_frame, roi_mask,
                correction_point=correction_point,
                frame_number=frame_idx
            )
            results.append(result)
        
        return results
