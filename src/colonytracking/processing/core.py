"""
Core image processing utilities for Colony Tracking System.

Low-level image operations including line drawing, mask generation,
binary image operations, and blob detection.
"""

import numpy as np
from typing import Tuple, List, Optional
import logging
from scipy import ndimage
from skimage import measure, morphology
import cv2

logger = logging.getLogger(__name__)


class LineDrawer:
    """Bresenham line rasterization."""
    
    @staticmethod
    def draw_line(image: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                  intensity: int = 255) -> np.ndarray:
        """Draw line on image using Bresenham's algorithm."""
        image = image.copy()
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                image[y, x] = intensity
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return image


class CircleMask:
    """Generate circular region of interest masks."""
    
    @staticmethod
    def create_circular_mask(image_shape: Tuple[int, int],
                            radius: float,
                            center: Optional[Tuple[float, float]] = None) -> np.ndarray:
        """Create circular ROI mask."""
        height, width = image_shape
        
        if center is None:
            center = (width / 2.0, height / 2.0)
        
        mask_img = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask_img, (int(center[0]), int(center[1])), int(radius), 1, -1)
        mask = mask_img.astype(bool)
        
        logger.debug(f"Created circular mask: radius={radius}, center={center}, shape={image_shape}")
        return mask


class BlobDetector:
    """Connected component analysis for blob detection."""
    
    @staticmethod
    def detect_blobs(binary_image: np.ndarray) -> List[dict]:
        """Detect connected components (blobs) in binary image."""
        labeled_image = measure.label(binary_image, connectivity=2)
        properties = measure.regionprops(labeled_image)
        
        blobs = []
        for prop in properties:
            blob = {
                'area': prop.area,
                'centroid': np.array(prop.centroid[::-1]),
                'pixel_list': np.array(prop.coords[:, ::-1]),
                'major_axis_length': prop.major_axis_length,
                'minor_axis_length': prop.minor_axis_length,
                'eccentricity': prop.eccentricity,
                'solidity': prop.solidity,
                'label': prop.label,
            }
            blobs.append(blob)
        
        logger.debug(f"Detected {len(blobs)} blobs in image")
        return blobs
    
    @staticmethod
    def filter_by_area(blobs: List[dict], min_area: float, max_area: Optional[float] = None) -> List[dict]:
        """Filter blobs by area."""
        filtered = [b for b in blobs if b['area'] >= min_area]
        if max_area is not None:
            filtered = [b for b in filtered if b['area'] <= max_area]
        logger.debug(f"Filtered to {len(filtered)} blobs by area ({min_area}-{max_area})")
        return filtered
    
    @staticmethod
    def filter_by_circularity(blobs: List[dict], min_circularity: float = 0.9,
                             max_circularity: float = 1.1) -> List[dict]:
        """Filter blobs by circularity (ratio of major to minor axis)."""
        filtered = []
        for blob in blobs:
            if blob['minor_axis_length'] > 0:
                circularity = blob['major_axis_length'] / blob['minor_axis_length']
                if min_circularity <= circularity <= max_circularity:
                    filtered.append(blob)
        
        logger.debug(f"Filtered to {len(filtered)} blobs by circularity ({min_circularity}-{max_circularity})")
        return filtered


class ImageDifference:
    """Image difference operations for colony detection."""
    
    @staticmethod
    def compute_difference(image1: np.ndarray, image2: np.ndarray,
                          threshold: int = 20) -> np.ndarray:
        """Compute binary difference image."""
        from colonytracking.io.image import ImageConverter
        
        gray1 = ImageConverter.to_grayscale(image1)
        gray2 = ImageConverter.to_grayscale(image2)
        
        gray1 = gray1.astype(np.int32)
        gray2 = gray2.astype(np.int32)
        
        diff = gray1 - gray2
        binary = diff > threshold
        
        logger.debug(f"Computed difference image with threshold={threshold}, detected {binary.sum()} pixels")
        return binary


class IntensityCorrection:
    """Light intensity correction utilities."""
    
    @staticmethod
    def get_mean_intensity_region(image: np.ndarray, center: Tuple[int, int],
                                 window: int = 25) -> float:
        """Calculate mean intensity in region around center."""
        from colonytracking.io.image import ImageConverter
        
        if image.ndim == 3:
            image = ImageConverter.to_grayscale(image)
        
        y, x = center
        y1 = max(0, y - window)
        y2 = min(image.shape[0], y + window + 1)
        x1 = max(0, x - window)
        x2 = min(image.shape[1], x + window + 1)
        
        region = image[y1:y2, x1:x2]
        return float(region.mean())
    
    @staticmethod
    def correct_intensity(image: np.ndarray, reference_image: np.ndarray,
                         correction_point: Tuple[int, int],
                         window: int = 25) -> np.ndarray:
        """Apply light intensity correction."""
        from colonytracking.io.image import ImageConverter
        
        is_rgb = image.ndim == 3
        if is_rgb:
            gray = ImageConverter.to_grayscale(image)
        else:
            gray = image.copy()
        
        ref_gray = ImageConverter.to_grayscale(reference_image)
        
        mean_ref = IntensityCorrection.get_mean_intensity_region(ref_gray, correction_point, window)
        mean_current = IntensityCorrection.get_mean_intensity_region(gray, correction_point, window)
        
        correction_offset = mean_ref - mean_current
        
        if gray.dtype == np.uint8:
            corrected = np.clip(gray.astype(np.int32) + correction_offset, 0, 255).astype(np.uint8)
        else:
            corrected = gray + correction_offset
        
        if is_rgb:
            return ImageConverter.to_rgb(corrected)
        else:
            return corrected


class BinaryMorphology:
    """Binary image morphological operations."""
    
    @staticmethod
    def clean_binary_image(binary_image: np.ndarray,
                          remove_small_objects: bool = True,
                          min_size: int = 100,
                          fill_holes: bool = False) -> np.ndarray:
        """Clean binary image using morphological operations."""
        result = binary_image.copy()
        
        if remove_small_objects:
            result = morphology.remove_small_objects(result, min_size=min_size)
        
        if fill_holes:
            result = ndimage.binary_fill_holes(result)
        
        return result
