"""
Script to scan and filter WAV files based on configuration.

This script:
1. Loads environment variables for configuration paths
2. Loads a YAML configuration file containing a root directory path
3. Scans for WAV files within that directory and its subdirectories
4. Filters files to only include those containing drone-related terms in their names
5. Creates a structured registry with metadata and file information
6. Saves the registry to a JSON file

The script automatically corrects legacy misspellings (e.g., "membo" -> "mambo").
"""

import os
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
import warnings

from dotenv import load_dotenv
from p05_data_models.clean_wav_registry import (
    CleanWavRegistry,
    DroneType,
    normalize_drone_type
)


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load and parse the YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        dict: Parsed configuration
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If there's an error parsing the YAML
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    return config


def find_wav_files(root_dir: Path, filter_terms: List[str] = None) -> List[Path]:
    """
    Recursively find WAV files in the specified directory, optionally filtered by terms.
    
    Args:
        root_dir: Root directory to search in
        filter_terms: List of substrings to filter filenames by (case-insensitive).
                     If None or empty, no filtering is applied.
        
    Returns:
        List of Path objects for each matching WAV file found
    """
    if not root_dir.exists():
        raise FileNotFoundError(f"Root directory not found: {root_dir}")
    
    print(f"Searching for WAV files in: {root_dir}")
    
    # Get all WAV files (case-insensitive search)
    wav_files = []
    for pattern in ['*.wav', '*.WAV']:
        wav_files.extend(root_dir.rglob(pattern))
    
    print(f"Found {len(wav_files)} total WAV files")
    
    # Apply filters if any terms are provided
    if filter_terms:
        filter_terms = [term.lower() for term in filter_terms]
        filtered_files = [
            f for f in wav_files
            if any(term in str(f).lower() for term in filter_terms)
        ]
        print(f"After filtering for terms {filter_terms}: {len(filtered_files)} files")
        return filtered_files
        
    return wav_files


def determine_drone_type(file_path: Path) -> DroneType:
    """
    Determine the drone type based on the file path.
    
    This function uses the normalize_drone_type function to handle
    legacy misspellings like "membo" -> "mambo".
    """
    file_str = str(file_path).lower()
    
    if 'bebop' in file_str:
        return DroneType.BEBOP
    elif 'membo' in file_str or 'mambo' in file_str:
        # This will automatically correct "membo" to "mambo"
        detected_name = 'membo' if 'membo' in file_str else 'mambo'
        return normalize_drone_type(detected_name)
    else:
        # Default to BEBOP if no clear match (shouldn't happen with proper filtering)
        print(f"Warning: Could not determine drone type for {file_path}, defaulting to BEBOP")
        return DroneType.BEBOP


def main():
    """Main function to execute the script."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get configuration paths from environment variables
        config_path = Path(os.getenv('TRAINING_DATA_CONFIG', 'config/training_data.yaml'))
        output_path = Path(os.getenv('CLEAN_WAV_REGISTRY_OUTPUT', 'output/clean_wav_registry.json'))
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Assert the config file exists
        if not config_path.exists():
            print(f"""
Configuration file not found at: {config_path}

Please ensure you have:
1. Created the config file at the expected location
2. Set the TRAINING_DATA_CONFIG environment variable (optional)
3. Updated the paths in your .env file

Current working directory: {Path.cwd()}
            """)
            sys.exit(1)
        
        script_name = str(Path(__file__).resolve())
        
        # Load configuration
        print(f"Loading configuration from: {config_path}")
        config = load_config(config_path)
        
        # Get root directory from config (with optional override from environment)
        data_root_override = os.getenv('DATA_ROOT_OVERRIDE')
        if data_root_override:
            root_dir = Path(data_root_override).expanduser()
            print(f"Using DATA_ROOT_OVERRIDE: {root_dir}")
        else:
            root_dir = Path(config['data_lake']['root_dir']).expanduser()
        
        # Get filter terms from config
        filter_terms = config.get('wav_filtering', {}).get('filter_terms', ['bebop', 'mambo'])
        
        print(f"Root directory: {root_dir}")
        print(f"Filtering for files containing: {', '.join(filter_terms)}")
        
        # Check if root directory exists
        if not root_dir.exists():
            print(f"""
Root directory not found: {root_dir}

Please:
1. Update the 'root_dir' path in {config_path}
2. Or set the DATA_ROOT_OVERRIDE environment variable
3. Ensure the directory contains the drone audio dataset

Refer to: {config.get('data_lake', {}).get('root_dir_info', 'No info available')}
            """)
            sys.exit(1)
        
        # Find and filter WAV files
        wav_files = find_wav_files(root_dir, filter_terms)
        
        if not wav_files:
            print(f"""
No WAV files found matching the filter criteria.

Search location: {root_dir}
Filter terms: {filter_terms}
            
Please verify:
1. The root directory path is correct
2. The directory contains WAV files with the expected naming patterns
3. The filter terms match your file naming convention
            """)
            return
        
        # Create registry
        registry = CleanWavRegistry.create(
            created_by=script_name,
            filter_terms=filter_terms,
            root_dir=root_dir,
            description=f"Registry of clean WAV files for {config.get('project_info', {}).get('name', 'drone detection')}"
        )
        
        # Add files to registry
        print(f"\nProcessing {len(wav_files)} WAV files...")
        processed_count = 0
        error_count = 0
        
        # Capture warnings for drone type corrections
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            for file_path in wav_files:
                try:
                    drone_type = determine_drone_type(file_path)
                    registry.add_entry(file_path, drone_type)
                    processed_count += 1
                except Exception as e:
                    print(f"Warning: Could not add {file_path}: {e}")
                    error_count += 1
            
            # Show any drone type corrections that were made
            corrections = [warn for warn in w if "Correcting legacy drone type" in str(warn.message)]
            if corrections:
                print(f"\nDrone type corrections made: {len(corrections)}")
                for correction in corrections[:5]:  # Show first 5 corrections
                    print(f"  {correction.message}")
                if len(corrections) > 5:
                    print(f"  ... and {len(corrections) - 5} more corrections")
        
        # Print summary
        print(f"\nProcessing complete:")
        print(f"- Successfully processed: {processed_count} files")
        if error_count > 0:
            print(f"- Errors encountered: {error_count} files")
        
        print(f"\nRegistry summary:")
        for drone_type, count in registry.count_by_drone_type.items():
            print(f"- {drone_type.value.upper()}: {count} files")
        
        # Save registry
        registry.save_to_file(output_path)
        print(f"\nSaved registry to: {output_path}")
        
        # Show sample of files (first 3 of each type)
        print(f"\nSample files:")
        samples = {}
        for entry in registry.entries:
            if entry.drone_type not in samples:
                samples[entry.drone_type] = []
            if len(samples[entry.drone_type]) < 3:
                try:
                    rel_path = entry.file_path.relative_to(root_dir)
                    samples[entry.drone_type].append(rel_path)
                except ValueError:
                    # If relative_to fails, use the filename
                    samples[entry.drone_type].append(entry.file_path.name)
        
        for drone_type, files in samples.items():
            print(f"\n{drone_type.value.upper()} samples:")
            for file_path in files:
                print(f"  - {file_path}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
