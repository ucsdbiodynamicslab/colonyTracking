"""
Colony detection module implementing initial blob detection and filtering.

Performs image preprocessing, binary thresholding, blob detection, and
multi-stage filtering to identify bacterial colonies.
"""

import numpy as np
from typing import List, Tuple, Optional
import logging
from dataclasses import dataclass

from colonytracking import config
from colonytracking.data import Colony, ColonyMeasurement, DetectionResult
from colonytracking.io.image import ImageConverter, ImageResizer
from colonytracking.processing.core import (
    BlobDetector,
    CircleMask,
    ImageDifference,
    IntensityCorrection,
)

logger = logging.getLogger(__name__)


class ColonyDetector:
    """Detect colonies in initial image pair."""
    
    def __init__(self, config_dict: Optional[dict] = None):
        """
        Initialize detector with configuration.
        
        Parameters
        ----------
        config_dict : dict, optional
            Configuration overrides. Keys:
            - separation: minimum colony separation (pixels)
            - min_area: minimum area for detection
            - circularity_range: (min, max) acceptable circularity
            - difference_threshold: binary image threshold
        """
        self.config = config.DEFAULT_DETECTOR_CONFIG.copy()
        if config_dict:
            self.config.update(config_dict)
        
        self.separation = self.config['separation']
        self.min_area = self.config['min_area']
        self.circularity_range = self.config['circularity_range']
        self.difference_threshold = self.config['difference_threshold']
        
        logger.info(f"Initialized ColonyDetector with separation={self.separation}, min_area={self.min_area}")
    
    def detect(self, background_image: np.ndarray, colony_image: np.ndarray,
              roi_radius: Optional[float] = None,
              roi_center: Optional[Tuple[float, float]] = None,
              correction_point: Optional[Tuple[int, int]] = None) -> DetectionResult:
        """
        Detect colonies in image pair.
        
        Parameters
        ----------
        background_image : np.ndarray
            Reference/background image without colonies
        colony_image : np.ndarray
            Image with colonies present
        roi_radius : float, optional
            Circular ROI radius (default from config)
        roi_center : Tuple[float, float], optional
            ROI center (x, y). If None, uses image center
        correction_point : Tuple[int, int], optional
            (y, x) point for light intensity correction.
            If None, no correction is performed.
            
        Returns
        -------
        DetectionResult
            Detected colonies and metadata
        """
        # Set defaults
        if roi_radius is None:
            roi_radius = config.ROI_RADIUS
        
        logger.info(f"Starting colony detection. Background shape: {background_image.shape}, Colony shape: {colony_image.shape}")
        
        # Phase 1: Image preprocessing
        logger.debug("Phase 1: Image preprocessing")
        bg_processed = self._preprocess_image(background_image)
        col_processed = self._preprocess_image(colony_image)
        
        # Phase 2: Light intensity correction
        if correction_point is not None:
            logger.debug(f"Phase 2: Applying light intensity correction at point {correction_point}")
            col_processed = IntensityCorrection.correct_intensity(
                col_processed, bg_processed, correction_point, 
                window=config.INTENSITY_CORRECTION_WINDOW
            )
        else:
            logger.debug("Phase 2: Skipping light intensity correction (no point provided)")
        
        # Phase 3: Generate ROI mask
        logger.debug(f"Phase 3: Creating ROI mask with radius={roi_radius}")
        if roi_center is None:
            roi_center = (col_processed.shape[1] / 2, col_processed.shape[0] / 2)
        
        roi_mask = CircleMask.create_circular_mask(col_processed.shape, roi_radius, roi_center)
        
        # Phase 4: Binary image generation
        logger.debug("Phase 4: Creating binary difference image")
        binary_image = ImageDifference.compute_difference(
            bg_processed, col_processed, 
            threshold=self.difference_threshold
        )
        binary_image = binary_image & roi_mask  # Apply ROI mask
        
        # Phase 5: Initial blob detection
        logger.debug("Phase 5: Detecting blobs")
        blobs = BlobDetector.detect_blobs(binary_image)
        initial_count = len(blobs)
        
        # Phase 6: Separation filtering
        logger.debug(f"Phase 6: Filtering by separation (threshold={self.separation}px)")
        blobs = self._filter_by_separation(blobs)
        after_separation = len(blobs)
        logger.info(f"After separation filtering: {after_separation}/{initial_count} blobs")
        
        # Phase 7: Circularity filtering
        logger.debug(f"Phase 7: Filtering by circularity {self.circularity_range}")
        blobs = BlobDetector.filter_by_circularity(blobs, *self.circularity_range)
        
        # Phase 8: Area filtering
        logger.debug(f"Phase 8: Filtering by area (min={self.min_area}px)")
        blobs = BlobDetector.filter_by_area(blobs, self.min_area)
        after_filtering = len(blobs)
        logger.info(f"After filtering: {after_filtering} blobs remaining")
        
        # Phase 9: Remove edge-touching blobs
        logger.debug("Phase 9: Removing edge-touching blobs")
        blobs = self._remove_edge_touching_blobs(blobs, roi_mask)
        final_count = len(blobs)
        logger.info(f"After edge removal: {final_count} blobs remaining")
        
        # Convert blobs to Colony objects
        colonies = self._blobs_to_colonies(blobs)
        
        # Create result
        result = DetectionResult(
            colonies=colonies,
            binary_image=binary_image,
            intensity_correction_point=correction_point if correction_point else (0, 0),
            num_detected=initial_count,
            num_after_filtering=final_count,
            roi_mask=roi_mask,
        )
        
        logger.info(f"Detection complete: {len(colonies)} colonies detected")
        return result
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image: convert to grayscale and optionally resize."""
        # Convert to grayscale
        if image.ndim == 3:
            gray = ImageConverter.to_grayscale(image)
        else:
            gray = image
        
        # Resize if necessary
        if gray.shape[0] > config.RESIZE_THRESHOLD or gray.shape[1] > config.RESIZE_THRESHOLD:
            gray, _ = ImageResizer.resize(gray, config.RESIZE_THRESHOLD)
        
        return gray
    
    def _filter_by_separation(self, blobs: List[dict]) -> List[dict]:
        """
        Filter merged blobs using separation distance.
        
        Removes colonies that are too close together (merged detections).
        """
        filtered = []
        
        for blob in blobs:
            # Skip small blobs in separation filter
            if blob['area'] < config.MIN_COLONY_AREA_SEPARATION:
                filtered.append(blob)
                continue
            
            # Check distance to other large blobs
            is_valid = True
            for other_blob in blobs:
                if other_blob['area'] < config.MIN_COLONY_AREA_SEPARATION:
                    continue
                if blob == other_blob:
                    continue
                
                # Calculate inter-center distance
                dist_centers = np.linalg.norm(blob['centroid'] - other_blob['centroid'])
                
                # Calculate minimum distance (edge to edge)
                r1 = blob['major_axis_length'] / 2
                r2 = other_blob['major_axis_length'] / 2
                min_dist = dist_centers - r1 - r2
                
                # If too close, mark as invalid
                if min_dist < self.separation:
                    is_valid = False
                    break
            
            if is_valid:
                filtered.append(blob)
        
        return filtered
    
    def _remove_edge_touching_blobs(self, blobs: List[dict], roi_mask: np.ndarray) -> List[dict]:
        """Remove colonies touching the ROI boundary."""
        filtered = []
        
        # Find edge pixels of ROI
        edge_mask = roi_mask.copy()
        inner_mask = roi_mask.copy()
        
        # Erode to find interior
        from scipy import ndimage
        inner_mask = ndimage.binary_erosion(inner_mask, iterations=5)
        edge_pixels = edge_mask & ~inner_mask
        
        for blob in blobs:
            pixels = blob['pixel_list']
            
            # Check if any pixels are on edge
            on_edge = False
            for x, y in pixels:
                x, y = int(x), int(y)
                if 0 <= y < edge_mask.shape[0] and 0 <= x < edge_mask.shape[1]:
                    if edge_pixels[y, x]:
                        on_edge = True
                        break
            
            if not on_edge:
                filtered.append(blob)
        
        return filtered
    
    def _blobs_to_colonies(self, blobs: List[dict]) -> List[Colony]:
        """Convert blob detections to Colony objects."""
        colonies = []
        
        for i, blob in enumerate(blobs):
            colony = Colony(colony_id=i + 1)
            
            # Create initial measurement
            diameter = 2 * np.sqrt(blob['area'] / np.pi)
            measurement = ColonyMeasurement(
                area=float(blob['area']),
                diameter=float(diameter),
                centroid=tuple(blob['centroid']),
                pixel_list=blob['pixel_list'],
                timestamp=0,
            )
            
            colony.measurements.append(measurement)
            colony.emergence_frame = 0
            
            colonies.append(colony)
        
        return colonies
