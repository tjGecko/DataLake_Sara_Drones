# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is the **Sara Al-Emadi Drones** project, focusing on drone detection using acoustic simulation techniques. The project appears to involve Variational Autoencoders (VAE) based on the related codebase name. This is currently an early-stage project with minimal code structure.

## Development Environment

### Virtual Environment Setup
```powershell
# Activate the virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# For Command Prompt
.\.venv\Scripts\activate.bat

# Install dependencies (when requirements file is created)
python -m pip install -r requirements.txt
```

### Python Environment
- Uses Python virtual environment (`.venv/`)
- Current Python version: 3.13 (based on virtual environment structure)
- Package manager: pip

## Project Structure

```
01_Sara_Al-Emadi_Drones/
├── .env                    # Environment variables (update paths here)
├── .gitignore              # Git ignore rules
├── .venv/                  # Python virtual environment
├── config/                 # Configuration files
│   └── training_data.yaml  # Main configuration file
├── output/                 # Generated output files
├── p05_data_models/        # Data models package
│   ├── __init__.py         # Package exports
│   └── clean_wav_registry.py  # WAV file registry models
├── requirements.txt        # Python dependencies
├── example_usage.py        # Example of drone type correction
├── scan_wav_files.py       # Main WAV file processing script
├── test_setup.py           # Setup verification script
└── WARP.md                 # This file
```

## Development Commands

### Initial Setup
```powershell
# Install all dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Verify setup is working
.\.venv\Scripts\python.exe test_setup.py
```

### Environment Management
```powershell
# Create virtual environment (if needed)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install new packages
python -m pip install <package_name>

# Update requirements file
python -m pip freeze > requirements.txt
```

### Main Processing Commands
```powershell
# Process WAV files and create registry
.\.venv\Scripts\python.exe scan_wav_files.py

# Test drone type correction functionality
.\.venv\Scripts\python.exe example_usage.py
```

### Configuration

**Before first use:**
1. Update `.env` file with your local paths
2. Update `config/training_data.yaml` with your drone audio dataset path:
   ```yaml
   data_lake:
     root_dir: "C:/path/to/your/DroneAudioDataset/Binary_Drone_Audio/yes_drone/"
   ```

**Environment Variables (in .env):**
- `TRAINING_DATA_CONFIG`: Path to YAML configuration file
- `CLEAN_WAV_REGISTRY_OUTPUT`: Path for output JSON registry
- `DATA_ROOT_OVERRIDE`: (Optional) Override data root directory

### Testing (When Tests Are Added)
```powershell
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_<module>.py

# Run tests with verbose output
python -m pytest -v
```

### Code Quality (When Configured)
```powershell
# Format code
python -m black .

# Lint code
python -m flake8

# Type checking
python -m mypy .
```

## Architecture Notes

### Current Implementation
- `p05_data_models/clean_wav_registry.py`: Core data models with Pydantic validation
  - `DroneType` enum with corrected names (BEBOP, MAMBO)
  - `CleanWavEntry` for individual WAV file metadata
  - `CleanWavRegistry` for managing collections of WAV files
  - Automatic correction of legacy misspellings ("membo" → "mambo")
- `scan_wav_files.py`: Main script for processing WAV file datasets
  - Environment variable configuration
  - YAML configuration file support
  - Recursive WAV file discovery with filtering
  - Automatic drone type detection and correction
- `config/training_data.yaml`: Central configuration file
  - Data paths, processing parameters, filter terms
  - Easy to modify for different environments

### Key Features
- **Legacy Data Correction**: Automatically fixes "membo" misspelling to "mambo"
- **Environment-Based Configuration**: Uses .env files for path management
- **Comprehensive Validation**: Pydantic models ensure data integrity
- **Cross-Platform Paths**: Works with Windows and Unix path formats

### Future Development Areas
- Acoustic signal processing modules (using librosa, scipy)
- VAE model implementation for drone detection
- Data preprocessing and feature extraction pipelines
- Training and inference scripts
- Model evaluation and metrics

## Git Workflow

The project uses Git for version control. The repository is currently in initial state with no commits yet.

```powershell
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# View changes
git diff
```

## Notes for Future Development

1. **Dependencies**: No external dependencies are currently installed. Consider adding common packages for acoustic processing (librosa, scipy, numpy) and machine learning (torch/tensorflow, scikit-learn).

2. **Project Structure**: The current structure is minimal. As the project grows, consider organizing into logical modules such as:
   - `data/` - Data processing and loading
   - `models/` - VAE and other model implementations  
   - `training/` - Training scripts and utilities
   - `evaluation/` - Metrics and evaluation tools
   - `preprocessing/` - Audio preprocessing pipelines

3. **Configuration**: Consider adding configuration management (JSON/YAML configs or environment variables) for model parameters, file paths, and training settings.

4. **Testing**: Establish testing framework early with unit tests for data processing functions and model components.