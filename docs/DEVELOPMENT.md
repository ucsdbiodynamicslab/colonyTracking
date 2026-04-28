## Development Guidelines

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/biodynamics/colonytracking.git
cd colonytracking

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

---

### Code Style

Use Black for code formatting:

```bash
black src/colonytracking tests/
```

Use flake8 for linting:

```bash
flake8 src/colonytracking tests/ --max-line-length=100
```

---

### Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=colonytracking --cov-report=html

# Run specific test file
pytest tests/test_core.py -v

# Run tests matching pattern
pytest tests/ -k "test_blob" -v
```

---

### Type Checking

Run mypy for static type checking:

```bash
mypy src/colonytracking
```

---

### Project Structure

```
colonytracking/
├── src/colonytracking/          # Main package
│   ├── __init__.py              # Package init, exports main classes
│   ├── config.py                # Configuration parameters
│   │
│   ├── data/                    # Data structures
│   │   ├── __init__.py
│   │   └── structures.py        # Colony, Measurement classes
│   │
│   ├── io/                      # Image I/O
│   │   ├── __init__.py
│   │   └── image.py             # ImageLoader, ImageConverter, ImageResizer
│   │
│   ├── processing/              # Image processing
│   │   ├── __init__.py
│   │   ├── core.py              # Core utilities (blob detection, etc.)
│   │   ├── detector.py          # ColonyDetector class
│   │   └── tracker.py           # ColonyTracker class
│   │
│   ├── analysis/                # Analysis and visualization
│   │   ├── __init__.py
│   │   ├── growth.py            # GrowthAnalysis class
│   │   └── visualization.py     # PlotGenerator class
│   │
│   └── gui/                     # GUI application
│       ├── __init__.py
│       └── main.py              # Main GUI window
│
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_core.py             # Core algorithm tests
│   ├── test_detector.py         # Detection tests
│   ├── test_tracker.py          # Tracking tests
│   └── test_integration.py      # Integration tests
│
├── docs/                        # Documentation
│   ├── API.md                   # API reference
│   ├── USAGE.md                 # Usage examples
│   └── DEVELOPMENT.md           # Development guidelines
│
├── pyproject.toml              # Modern Python packaging
├── requirements.txt            # Package dependencies
├── setup.py                    # Setup for pip install -e .
├── README.md                   # Main documentation
├── DESIGN_DOCUMENT.md          # Original architecture
└── .gitignore
```

---

### Adding New Features

1. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Implement feature** with proper:
   - Type hints
   - Docstrings
   - Error handling
   - Logging

3. **Add tests**:
   - Unit tests in `tests/`
   - Run full test suite: `pytest tests/ -v`

4. **Update documentation**:
   - Add API documentation if adding public classes
   - Update README if changing user-facing behavior
   - Add example to USAGE.md for new features

5. **Submit pull request** with:
   - Clear description of changes
   - Passing tests
   - Formatted code (black, flake8)
   - Updated documentation

---

### Common Tasks

#### Adding a new processing algorithm

1. Add core utility class to `processing/core.py`:
   ```python
   class MyNewAlgorithm:
       @staticmethod
       def process(image, parameter):
           # Implementation
           return result
   ```

2. Export in `processing/__init__.py`:
   ```python
   from .core import MyNewAlgorithm
   __all__ = [..., 'MyNewAlgorithm']
   ```

3. Write tests in `tests/`:
   ```python
   def test_my_new_algorithm():
       result = MyNewAlgorithm.process(test_image, param)
       assert result is not None
   ```

---

#### Adding a new visualization

1. Add method to `PlotGenerator` in `analysis/visualization.py`:
   ```python
   @staticmethod
   def plot_my_metric(colonies, save_path=None):
       # Implementation using matplotlib
       return fig, ax
   ```

2. Document in `docs/API.md`

3. Add example to `docs/USAGE.md`

---

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now debug messages will be printed
```

Use Python debugger:

```python
import pdb

# Set breakpoint
pdb.set_trace()

# Or use Python 3.7+ syntax
breakpoint()
```

---

### Performance Optimization

Profile code:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
detector.detect(background, colony)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

### Documentation

Build Sphinx documentation:

```bash
cd docs/
sphinx-build -b html . _build/html
# Open _build/html/index.html
```

---

### Continuous Integration

GitHub Actions workflows (`.github/workflows/`) automatically run:
- Tests on push/PR
- Code formatting checks
- Type checking
- Coverage reports

---

### Release Checklist

Before releasing a new version:

- [ ] Update version in `pyproject.toml` and `__init__.py`
- [ ] Update CHANGELOG
- [ ] Run full test suite
- [ ] Check code coverage (>80%)
- [ ] Verify documentation is current
- [ ] Create GitHub release with tag

Then:

```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

