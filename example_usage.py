"""
Example usage of the CleanWavRegistry with drone type correction.

This script demonstrates how legacy misspelled drone names are automatically
corrected when creating registry entries.
"""

from pathlib import Path
from p05_data_models.clean_wav_registry import (
    CleanWavRegistry, 
    DroneType, 
    normalize_drone_type
)
import warnings


def demonstrate_drone_type_correction():
    """Demonstrate the drone type correction functionality."""
    print("=== Drone Type Correction Demo ===\n")
    
    # Test the normalization function directly
    print("1. Testing normalize_drone_type function:")
    test_values = ["membo", "MEMBO", "mambo", "MAMBO", "bebop", "BEBOP"]
    
    for value in test_values:
        try:
            corrected = normalize_drone_type(value)
            print(f"   '{value}' -> {corrected.value}")
        except Exception as e:
            print(f"   '{value}' -> ERROR: {e}")
    
    print("\n2. Testing with registry creation:")
    
    # Create a registry
    registry = CleanWavRegistry.create(
        created_by="example_usage.py",
        filter_terms=["clean", "drone"],
        root_dir=Path("C:/example/audio/data"),
        description="Example registry showing drone type correction"
    )
    
    # Capture warnings to show when corrections are made
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # This would normally add real WAV files, but for demo we'll skip the file check
        print("   Adding entries with legacy 'membo' name...")
        
        # Note: In real usage, you'd have actual WAV files
        # For demo purposes, we'll create a mock entry directly
        from p05_data_models.clean_wav_registry import CleanWavEntry
        import time
        
        # Create mock entries with the legacy misspelled name
        mock_entries = [
            {
                "file_path": Path("C:/example/audio/data/drone1_membo.wav"),
                "drone_type": "membo",  # Legacy misspelling
                "file_size": 1024000,
                "modified_time": time.time()
            },
            {
                "file_path": Path("C:/example/audio/data/drone2_mambo.wav"),
                "drone_type": "mambo",  # Correct spelling
                "file_size": 1024000,
                "modified_time": time.time()
            }
        ]
        
        # Add entries (this will trigger the correction)
        for entry_data in mock_entries:
            entry = CleanWavEntry(**entry_data)
            registry.entries.append(entry)
        
        # Show any warnings that were generated
        if w:
            print("   Warnings generated:")
            for warning in w:
                print(f"     {warning.message}")
        else:
            print("   No warnings (all names were already correct)")
    
    print("\n3. Final registry contents:")
    counts = registry.count_by_drone_type
    for drone_type, count in counts.items():
        print(f"   {drone_type.value}: {count} entries")
    
    print(f"\n4. All entries now use correct drone types:")
    for i, entry in enumerate(registry.entries):
        print(f"   Entry {i}: {entry.file_path.name} -> {entry.drone_type.value}")


if __name__ == "__main__":
    demonstrate_drone_type_correction()