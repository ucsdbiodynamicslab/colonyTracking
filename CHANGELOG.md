# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-22

### Added

- Initial Python implementation of Colony Tracking System
- `ColonyDetector` class for initial colony detection from image pairs
- `ColonyTracker` class for temporal tracking across frame sequences
- `GrowthAnalysis` class for computing colony growth metrics
- `PlotGenerator` class for visualization (area, diameter, normalized growth, emergence times)
- `ImageLoader`, `ImageConverter`, `ImageResizer` utilities for image I/O
- Core image processing algorithms: blob detection, circularity filtering, ROI masking
- Configuration system with customizable parameters
- Comprehensive unit tests
- Full API documentation and usage examples
- GUI launcher with PyQt6 (placeholder for future GUI development)
- Modern Python packaging with pyproject.toml

### Features

- Automatic colony detection using image subtraction and blob analysis
- Multi-stage filtering: separation, circularity, area, edge removal
- Temporal tracking using nearest-neighbor distance matching
- Light intensity correction for uneven illumination
- Growth metric calculation (area, diameter, normalized growth, emergence time)
- Publication-quality visualization with matplotlib
- Batch processing support
- Comprehensive logging throughout
- Type hints for better IDE support

### Documentation

- README with quick start guide
- API reference with all classes and methods
- Usage examples covering common scenarios
- Development guidelines for contributors
- Design document from original MATLAB implementation

### Performance

- Efficient blob detection using scikit-image regionprops
- Optional image resizing for large images
- Vectorized operations using NumPy

## Future Enhancements

- [ ] Complete PyQt6 GUI implementation
- [ ] Kalman filtering for improved tracking
- [ ] Hungarian algorithm for multi-object assignment
- [ ] Adaptive thresholding for varying image conditions
- [ ] Parallel frame processing
- [ ] Machine learning-based circularity filtering
- [ ] Advanced visualization (3D growth surfaces, animations)
- [ ] Export to HDF5, SQLite for large datasets
- [ ] REST API for integration with other tools
- [ ] Jupyter notebook integration
- [ ] Real-time processing capabilities

