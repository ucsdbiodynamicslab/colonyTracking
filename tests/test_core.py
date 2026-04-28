"""
Unit tests for Colony Tracking System.

Basic tests for core functionality. Run with: pytest tests/
"""

import pytest
import numpy as np
from pathlib import Path

# Import modules under test
from colonytracking.data import Colony, ColonyMeasurement
from colonytracking.processing.core import BlobDetector, CircleMask, ImageDifference
from colonytracking.processing.detector import ColonyDetector
from colonytracking.analysis import GrowthAnalysis


class TestColonyDataStructure:
    """Test colony data structures."""
    
    def test_colony_creation(self):
        """Test creating a colony object."""
        colony = Colony(colony_id=1)
        assert colony.colony_id == 1
        assert len(colony.measurements) == 0
        assert colony.emergence_frame == -1
    
    def test_colony_measurement_append(self):
        """Test appending measurements to colony."""
        colony = Colony(colony_id=1)
        
        measurement = ColonyMeasurement(
            area=100.0,
            diameter=11.28,
            centroid=(50.0, 50.0),
            pixel_list=np.array([[50, 50]]),
            timestamp=0
        )
        colony.append_measurement(measurement)
        
        assert len(colony.measurements) == 1
        assert colony.get_last_measurement().area == 100.0
    
    def test_colony_get_arrays(self):
        """Test retrieving measurements as arrays."""
        colony = Colony(colony_id=1)
        
        for i in range(5):
            measurement = ColonyMeasurement(
                area=100.0 + i * 10,
                diameter=11.28 + i,
                centroid=(50.0 + i, 50.0 + i),
                pixel_list=np.array([[50 + i, 50 + i]]),
                timestamp=i
            )
            colony.append_measurement(measurement)
        
        areas = colony.get_areas()
        assert len(areas) == 5
        assert areas[0] == 100.0
        assert areas[-1] == 140.0


class TestBlobDetection:
    """Test blob detection utilities."""
    
    def test_detect_single_blob(self):
        """Test detecting a single blob."""
        # Create simple binary image with one blob
        binary_image = np.zeros((100, 100), dtype=bool)
        binary_image[40:60, 40:60] = True
        
        blobs = BlobDetector.detect_blobs(binary_image)
        
        assert len(blobs) == 1
        assert blobs[0]['area'] == 400  # 20x20
        assert 39 < blobs[0]['centroid'][0] < 61  # x coordinate
        assert 39 < blobs[0]['centroid'][1] < 61  # y coordinate
    
    def test_filter_by_area(self):
        """Test filtering blobs by area."""
        # Create two blobs
        binary_image = np.zeros((100, 100), dtype=bool)
        binary_image[10:20, 10:20] = True  # Small blob (100 px)
        binary_image[40:60, 40:60] = True  # Large blob (400 px)
        
        blobs = BlobDetector.detect_blobs(binary_image)
        assert len(blobs) == 2
        
        # Filter to keep only large blobs
        filtered = BlobDetector.filter_by_area(blobs, min_area=200)
        assert len(filtered) == 1
        assert filtered[0]['area'] > 200


class TestCircleMask:
    """Test circular mask generation."""
    
    def test_create_circular_mask(self):
        """Test creating a circular ROI mask."""
        image_shape = (100, 100)
        radius = 30
        center = (50, 50)
        
        mask = CircleMask.create_circular_mask(image_shape, radius, center)
        
        assert mask.shape == image_shape
        assert mask.dtype == bool
        
        # Center should be True
        assert mask[50, 50] == True
        
        # Far corner should be False
        assert mask[0, 0] == False
        
        # Count non-zero pixels (should be roughly pi*r^2)
        area = mask.sum()
        expected_area = np.pi * radius ** 2
        assert 0.8 * expected_area < area < 1.2 * expected_area


class TestGrowthAnalysis:
    """Test growth analysis functions."""
    
    def test_compute_emergence_times(self):
        """Test emergence time detection."""
        # Create colonies with different emergence patterns
        colonies = []
        
        for col_id in [1, 2, 3]:
            colony = Colony(colony_id=col_id)
            
            # First measurements below threshold
            for i in range(3):
                measurement = ColonyMeasurement(
                    area=500.0,
                    diameter=25.0,
                    centroid=(50.0, 50.0),
                    pixel_list=np.array([[50, 50]]),
                    timestamp=i
                )
                colony.append_measurement(measurement)
            
            # Then above threshold
            for i in range(3, 6):
                measurement = ColonyMeasurement(
                    area=1500.0,
                    diameter=44.0,
                    centroid=(50.0, 50.0),
                    pixel_list=np.array([[50, 50]]),
                    timestamp=i
                )
                colony.append_measurement(measurement)
            
            colonies.append(colony)
        
        emergence_times = GrowthAnalysis.compute_emergence_times(colonies)
        
        assert len(emergence_times) == 3
        for col_id in [1, 2, 3]:
            assert emergence_times[col_id] == 3


class TestImageDifference:
    """Test image difference computation."""
    
    def test_compute_difference(self):
        """Test binary image difference."""
        # Create two images with different intensities
        img1 = np.full((100, 100), 100, dtype=np.uint8)  # Background
        img2 = img1.copy()
        img2[40:60, 40:60] = 50  # Darker region (colonies)
        
        binary = ImageDifference.compute_difference(img1, img2, threshold=20)
        
        assert binary.dtype == bool
        # Binary should have True in the region where difference > 20
        assert binary[50, 50] == True
        # And False elsewhere
        assert binary[10, 10] == False


@pytest.mark.parametrize("num_frames", [3, 5, 10])
def test_detector_initialization(num_frames):
    """Test detector initialization with different parameters."""
    detector = ColonyDetector({
        'separation': 50,
        'min_area': 1000,
    })
    
    assert detector.separation == 50
    assert detector.min_area == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
