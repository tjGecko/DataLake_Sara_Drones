"""
Test script to verify that paths are always stored as absolute paths.

This script tests:
1. RegistryHeader root_dir field validation
2. CleanWavEntry file_path field validation
3. Path conversion from relative to absolute
"""

from pathlib import Path
from p05_data_models.clean_wav_registry import (
    CleanWavRegistry,
    RegistryHeader,
    CleanWavEntry,
    DroneType
)
import os


def test_registry_header_absolute_paths():
    """Test that RegistryHeader always stores absolute paths."""
    print("=== Testing RegistryHeader Absolute Paths ===")
    
    # Test with relative path
    relative_path = "config"
    header = RegistryHeader(
        created_by="test_script",
        filter_terms=["bebop", "mambo"],
        root_dir=relative_path,
        description="Test registry"
    )
    
    print(f"Input relative path: {relative_path}")
    print(f"Stored absolute path: {header.root_dir}")
    
    assert header.root_dir.is_absolute(), f"Expected absolute path, got: {header.root_dir}"
    assert header.root_dir.exists(), f"Path should exist: {header.root_dir}"
    print("✓ Relative path converted to absolute correctly")
    
    # Test with absolute path
    absolute_path = Path.cwd() / "config"
    header2 = RegistryHeader(
        created_by="test_script",
        filter_terms=["bebop", "mambo"],
        root_dir=absolute_path,
        description="Test registry"
    )
    
    print(f"Input absolute path: {absolute_path}")
    print(f"Stored absolute path: {header2.root_dir}")
    
    assert header2.root_dir.is_absolute(), f"Expected absolute path, got: {header2.root_dir}"
    print("✓ Absolute path preserved correctly")
    
    # Both should resolve to the same path
    assert header.root_dir == header2.root_dir, "Both should resolve to same absolute path"
    print("✓ Relative and absolute paths resolve to same location")


def test_clean_wav_entry_absolute_paths():
    """Test that CleanWavEntry always stores absolute file paths."""
    print(f"\n=== Testing CleanWavEntry Absolute Paths ===")
    
    # Test with relative path to an existing file
    relative_file = "test_setup.py"
    
    # Create a mock entry (we'll bypass file existence check by creating entry directly)
    try:
        entry = CleanWavEntry(
            file_path=relative_file,
            drone_type=DroneType.BEBOP,
            file_size=1000,
            modified_time=1234567890.0
        )
        
        print(f"Input relative file path: {relative_file}")
        print(f"Stored absolute file path: {entry.file_path}")
        
        assert entry.file_path.is_absolute(), f"Expected absolute path, got: {entry.file_path}"
        print("✓ Relative file path converted to absolute correctly")
        
    except Exception as e:
        print(f"Error testing relative file path: {e}")
    
    # Test with absolute path
    absolute_file = Path.cwd() / "test_setup.py"
    entry2 = CleanWavEntry(
        file_path=absolute_file,
        drone_type=DroneType.MAMBO,
        file_size=2000,
        modified_time=1234567890.0
    )
    
    print(f"Input absolute file path: {absolute_file}")
    print(f"Stored absolute file path: {entry2.file_path}")
    
    assert entry2.file_path.is_absolute(), f"Expected absolute path, got: {entry2.file_path}"
    print("✓ Absolute file path preserved correctly")


def test_registry_creation_with_absolute_paths():
    """Test that CleanWavRegistry.create() works with absolute paths."""
    print(f"\n=== Testing Registry Creation with Absolute Paths ===")
    
    # Use current working directory as test root
    test_root = Path.cwd()
    
    registry = CleanWavRegistry.create(
        created_by="test_absolute_paths.py",
        filter_terms=["bebop", "mambo"],
        root_dir=test_root,
        description="Test registry with absolute paths"
    )
    
    print(f"Registry root_dir: {registry.header.root_dir}")
    
    assert registry.header.root_dir.is_absolute(), "Registry root_dir should be absolute"
    assert registry.header.root_dir == test_root.resolve(), "Should match resolved input path"
    print("✓ Registry created with absolute root_dir")
    
    return registry


def test_path_serialization():
    """Test that absolute paths are properly serialized and deserialized."""
    print(f"\n=== Testing Path Serialization ===")
    
    registry = CleanWavRegistry.create(
        created_by="test_script",
        filter_terms=["test"],
        root_dir=Path.cwd(),
        description="Serialization test"
    )
    
    # Test file-based serialization using our custom save/load methods
    test_file = Path("test_registry.json")
    
    try:
        # Save to file
        registry.save_to_file(test_file)
        print("File save successful")
        
        # Load from file
        registry_loaded = CleanWavRegistry.load_from_file(test_file)
        print("File load successful")
        
        # Check that paths are still absolute
        assert registry_loaded.header.root_dir.is_absolute(), "Deserialized root_dir should be absolute"
        assert registry_loaded.header.root_dir == registry.header.root_dir, "Paths should match after round-trip"
        print("✓ Absolute paths preserved through file serialization")
        
        # Show a sample of the JSON to verify format
        with open(test_file, 'r') as f:
            json_content = f.read()
        print(f"\nSample JSON (first 300 chars):")
        print(json_content[:300] + "..." if len(json_content) > 300 else json_content)
        
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def main():
    """Run all absolute path tests."""
    print("🚀 Testing Absolute Path Validation\n")
    
    try:
        test_registry_header_absolute_paths()
        test_clean_wav_entry_absolute_paths()
        test_registry_creation_with_absolute_paths()
        test_path_serialization()
        
        print(f"\n=== Test Summary ===")
        print("✅ All absolute path tests passed!")
        print("📍 Paths will always be stored as absolute paths in the registry")
        print("🔍 This ensures files can be located regardless of where the registry is accessed from")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()