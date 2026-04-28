"""
Colony Tracking System - Image analysis tool for bacterial colony detection and tracking.

Main package initialization.
"""

__version__ = "1.0.0"
__author__ = "Biodynamics Team"
__email__ = "info@biodynamics.com"

# Import key classes for convenient access
from colonytracking.data import Colony, ColonyMeasurement, DetectionResult, TrackingResult, AnalysisResult
from colonytracking.processing.detector import ColonyDetector
from colonytracking.processing.tracker import ColonyTracker
from colonytracking.analysis import GrowthAnalysis, PlotGenerator
from colonytracking.io import ImageLoader, ImageConverter, ImageResizer

__all__ = [
    'Colony',
    'ColonyMeasurement',
    'DetectionResult',
    'TrackingResult',
    'AnalysisResult',
    'ColonyDetector',
    'ColonyTracker',
    'GrowthAnalysis',
    'PlotGenerator',
    'ImageLoader',
    'ImageConverter',
    'ImageResizer',
]
