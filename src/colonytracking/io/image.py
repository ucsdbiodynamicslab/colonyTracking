"""Image I/O module for loading and saving microscopy images."""

import os
from pathlib import Path
from typing import Union, List, Tuple
import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageLoader:
    """Load microscopy images in various formats."""
    
    SUPPORTED_FORMATS = ('.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp')
    
    @staticmethod
    def load(filepath: Union[str, Path]) -> np.ndarray:
        """Load image from file."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Image file not found: {filepath}")
        
        # Handle TIFF files specially (preserve data type)
        if filepath.suffix.lower() in ('.tif', '.tiff'):
            try:
                img = Image.open(filepath)
                img_array = np.array(img)
                logger.debug(f"Loaded TIFF image: {filepath.name}, shape={img_array.shape}, dtype={img_array.dtype}")
                return img_array
            except Exception as e:
                logger.warning(f"PIL failed for TIFF, trying OpenCV: {e}")
                # Fallback to OpenCV
                img = cv2.imread(str(filepath), cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
                if img is None:
                    raise ValueError(f"Failed to load TIFF image: {filepath}")
                return img
        
        # Use OpenCV for other formats
        img = cv2.imread(str(filepath))
        if img is None:
            raise ValueError(f"Failed to load image: {filepath}")
        
        # OpenCV loads in BGR, convert to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        logger.debug(f"Loaded image: {filepath.name}, shape={img.shape}")
        return img
    
    @staticmethod
    def load_sequence(directory: Union[str, Path], 
                     pattern: str = '*',
                     sort: bool = True) -> List[np.ndarray]:
        """Load all images from a directory matching pattern."""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all image files
        images = []
        filepaths = []
        
        for ext in ImageLoader.SUPPORTED_FORMATS:
            filepaths.extend(directory.glob(f"{pattern}{ext}"))
            filepaths.extend(directory.glob(f"{pattern}{ext.upper()}"))
        
        if sort:
            filepaths = sorted(set(filepaths))
        else:
            filepaths = list(set(filepaths))
        
        logger.info(f"Found {len(filepaths)} images in {directory}")
        
        for filepath in filepaths:
            try:
                img = ImageLoader.load(filepath)
                images.append(img)
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")
        
        return images
    
    @staticmethod
    def save(image: np.ndarray, filepath: Union[str, Path]) -> None:
        """Save image to file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Use PIL for preservation of data types
        pil_img = Image.fromarray(image)
        pil_img.save(filepath)
        logger.debug(f"Saved image: {filepath}")


class ImageConverter:
    """Image format conversion utilities."""
    
    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale."""
        if image.ndim == 2:
            # Already grayscale
            return image
        elif image.ndim == 3 and image.shape[2] == 3:
            # RGB to grayscale using standard weights
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.ndim == 3 and image.shape[2] == 4:
            # RGBA to grayscale
            rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        else:
            raise ValueError(f"Cannot convert image with shape {image.shape} to grayscale")
    
    @staticmethod
    def to_rgb(image: np.ndarray) -> np.ndarray:
        """Convert image to RGB."""
        if image.ndim == 3 and image.shape[2] == 3:
            # Already RGB
            return image
        elif image.ndim == 2:
            # Grayscale to RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            raise ValueError(f"Cannot convert image with shape {image.shape} to RGB")
    
    @staticmethod
    def to_uint8(image: np.ndarray) -> np.ndarray:
        """Convert image to uint8 (0-255)."""
        if image.dtype == np.uint8:
            return image
        
        # Normalize to 0-1 range first, then to 0-255
        if image.dtype in (np.float32, np.float64):
            if image.min() >= 0 and image.max() <= 1:
                return (image * 255).astype(np.uint8)
            else:
                # Normalize min-max to 0-1
                img_min = image.min()
                img_max = image.max()
                if img_max > img_min:
                    normalized = (image - img_min) / (img_max - img_min)
                    return (normalized * 255).astype(np.uint8)
                else:
                    return np.zeros_like(image, dtype=np.uint8)
        else:
            # Integer types, use OpenCV's conversion
            return cv2.convertScaleAbs(image)
    
    @staticmethod
    def normalize(image: np.ndarray, method: str = 'minmax') -> np.ndarray:
        """Normalize image intensities."""
        if method == 'minmax':
            img_min = image.min()
            img_max = image.max()
            if img_max > img_min:
                return (image - img_min) / (img_max - img_min)
            else:
                return np.zeros_like(image, dtype=np.float32)
        elif method == 'z':
            mean = image.mean()
            std = image.std()
            if std > 0:
                return (image - mean) / std
            else:
                return np.zeros_like(image, dtype=np.float32)
        else:
            raise ValueError(f"Unknown normalization method: {method}")


class ImageResizer:
    """Image resizing utilities."""
    
    @staticmethod
    def resize(image: np.ndarray, max_dimension: int, 
               interpolation: str = 'area') -> Tuple[np.ndarray, float]:
        """Resize image if any dimension exceeds max_dimension."""
        height, width = image.shape[:2]
        max_size = max(height, width)
        
        if max_size <= max_dimension:
            return image, 1.0
        
        scale_factor = max_dimension / max_size
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)
        
        # Select interpolation
        interp_map = {
            'area': cv2.INTER_AREA,
            'linear': cv2.INTER_LINEAR,
            'cubic': cv2.INTER_CUBIC,
        }
        interp = interp_map.get(interpolation, cv2.INTER_AREA)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=interp)
        logger.debug(f"Resized image from {(height, width)} to {(new_height, new_width)}, scale={scale_factor:.3f}")
        
        return resized, scale_factor
