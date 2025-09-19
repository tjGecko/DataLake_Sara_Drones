"""
Test script to verify the project setup and configuration loading.

This script tests:
1. Environment variable loading
2. Configuration file parsing
3. Data model imports
4. Drone type correction functionality

Run this script to verify your setup is working correctly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

def test_environment_variables():
    """Test that environment variables are loaded correctly."""
    print("=== Testing Environment Variables ===")
    
    load_dotenv()
    
    config_path = os.getenv('TRAINING_DATA_CONFIG', 'config/training_data.yaml')
    output_path = os.getenv('CLEAN_WAV_REGISTRY_OUTPUT', 'output/clean_wav_registry.json')
    
    print(f"✓ TRAINING_DATA_CONFIG: {config_path}")
    print(f"✓ CLEAN_WAV_REGISTRY_OUTPUT: {output_path}")
    
    return config_path, output_path


def test_config_loading(config_path):
    """Test configuration file loading."""
    print(f"\n=== Testing Configuration Loading ===")
    
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return None
    
    print(f"✓ Configuration file exists: {config_file}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✓ Configuration file loaded successfully")
        
        # Check key sections
        sections_to_check = ['data_lake', 'training_data_creation', 'wav_filtering']
        for section in sections_to_check:
            if section in config:
                print(f"✓ Section '{section}' found")
            else:
                print(f"⚠️  Section '{section}' missing")
        
        # Show some config values
        if 'data_lake' in config:
            root_dir = config['data_lake'].get('root_dir', 'Not specified')
            print(f"  Root directory: {root_dir}")
        
        if 'wav_filtering' in config:
            filter_terms = config['wav_filtering'].get('filter_terms', [])
            print(f"  Filter terms: {filter_terms}")
        
        return config
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None


def test_data_models():
    """Test that data models can be imported and used."""
    print(f"\n=== Testing Data Models ===")
    
    try:
        from p05_data_models.clean_wav_registry import (
            CleanWavRegistry,
            DroneType,
            normalize_drone_type
        )
        print("✓ Data models imported successfully")
        
        # Test drone type correction
        test_cases = ["membo", "mambo", "bebop", "MEMBO"]
        print("  Testing drone type corrections:")
        
        for test_case in test_cases:
            try:
                corrected = normalize_drone_type(test_case)
                print(f"    '{test_case}' -> {corrected.value}")
            except Exception as e:
                print(f"    '{test_case}' -> ERROR: {e}")
        
        # Test registry creation
        registry = CleanWavRegistry.create(
            created_by="test_setup.py",
            filter_terms=["bebop", "mambo"],
            root_dir=Path("C:/temp/test"),
            description="Test registry"
        )
        print("✓ Registry creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with data models: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available."""
    print(f"\n=== Testing Dependencies ===")
    
    dependencies = [
        ("pydantic", "Pydantic"),
        ("yaml", "PyYAML"),
        ("dotenv", "python-dotenv")
    ]
    
    all_good = True
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {display_name} available")
        except ImportError:
            print(f"❌ {display_name} not available")
            all_good = False
    
    return all_good


def main():
    """Run all tests."""
    print("🚀 Testing Sara Al-Emadi Drones Project Setup\n")
    
    # Test dependencies first
    deps_ok = test_dependencies()
    
    # Test environment variables
    config_path, output_path = test_environment_variables()
    
    # Test configuration loading
    config = test_config_loading(config_path)
    
    # Test data models
    models_ok = test_data_models()
    
    # Summary
    print(f"\n=== Test Summary ===")
    
    if deps_ok:
        print("✓ Dependencies: All required packages available")
    else:
        print("❌ Dependencies: Some packages missing")
    
    if config is not None:
        print("✓ Configuration: Successfully loaded")
    else:
        print("❌ Configuration: Failed to load")
    
    if models_ok:
        print("✓ Data Models: Working correctly")
    else:
        print("❌ Data Models: Issues detected")
    
    if deps_ok and config is not None and models_ok:
        print("\n🎉 All tests passed! Your setup is ready.")
        print(f"You can now run: python scan_wav_files.py")
        print(f"(Make sure to update the root_dir in {config_path} first)")
    else:
        print("\n⚠️  Some issues detected. Please fix the errors above.")


if __name__ == "__main__":
    main()