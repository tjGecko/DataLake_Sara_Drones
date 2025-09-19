"""
Data model for the clean WAV file registry.

This module defines the data structure for tracking clean WAV files,
including their paths, drone types, and metadata about the registry creation.
Includes automatic correction of misspelled drone names from legacy data.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union
import warnings

from pydantic import BaseModel, Field, field_validator, ConfigDict


class DroneType(str, Enum):
    """Supported drone types in the registry."""
    BEBOP = "bebop"
    MAMBO = "mambo"  # Corrected from "membo"


# Legacy name mapping for backward compatibility
LEGACY_DRONE_NAME_MAPPING = {
    "membo": DroneType.MAMBO,  # Correct the misspelling
    "mambo": DroneType.MAMBO,  # Already correct
    "bebop": DroneType.BEBOP,  # Already correct
}


def normalize_drone_type(value: Union[str, DroneType]) -> DroneType:
    """
    Normalize drone type, correcting legacy misspellings.
    
    Args:
        value: Raw drone type value that may contain legacy misspellings
        
    Returns:
        Corrected DroneType enum value
        
    Raises:
        ValueError: If the drone type is not recognized
    """
    if isinstance(value, DroneType):
        return value
    
    # Convert to lowercase for case-insensitive matching
    normalized_value = value.lower().strip()
    
    if normalized_value in LEGACY_DRONE_NAME_MAPPING:
        corrected_type = LEGACY_DRONE_NAME_MAPPING[normalized_value]
        
        # Warn if we're correcting a legacy misspelling
        if normalized_value == "membo":
            warnings.warn(
                f"Correcting legacy drone type '{value}' to '{corrected_type.value}'. "
                "The original dataset contained a misspelling.",
                UserWarning,
                stacklevel=3
            )
        
        return corrected_type
    
    # Try direct enum lookup as fallback
    try:
        return DroneType(normalized_value)
    except ValueError:
        raise ValueError(
            f"Unknown drone type: '{value}'. "
            f"Supported types: {list(LEGACY_DRONE_NAME_MAPPING.keys())}"
        )


class CleanWavEntry(BaseModel):
    """Represents a single entry in the clean WAV registry."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    file_path: Path = Field(..., description="Absolute path to the WAV file")
    drone_type: DroneType = Field(..., description="Type of drone in the recording")
    file_size: int = Field(..., description="Size of the file in bytes")
    modified_time: float = Field(..., description="Last modified timestamp of the file")
    snr_db: float = Field(default=20.0, description="Signal-to-noise ratio in decibels")
    
    @field_validator('file_path', mode='before')
    @classmethod
    def validate_file_path(cls, v):
        """Ensure file_path is always an absolute path for future reference."""
        if isinstance(v, str):
            path = Path(v)
        elif isinstance(v, Path):
            path = v
        else:
            raise ValueError(f"file_path must be a string or Path object, got {type(v)}")
        
        # Convert to absolute path and resolve any symbolic links
        absolute_path = path.expanduser().resolve()
        
        return absolute_path
    
    @field_validator('drone_type', mode='before')
    @classmethod
    def validate_drone_type(cls, v):
        """Validate and normalize drone type, correcting legacy misspellings."""
        return normalize_drone_type(v)


class RegistryHeader(BaseModel):
    """Metadata about the registry creation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    created_by: str = Field(..., description="Script that generated this registry")
    created_at: datetime = Field(default_factory=datetime.now, description="When the registry was created")
    description: str = Field(default="Clean WAV file registry", description="Purpose of this registry")
    filter_terms: List[str] = Field(..., description="Terms used to filter the WAV files")
    root_dir: Path = Field(..., description="Absolute root directory path for reference")
    
    @field_validator('root_dir', mode='before')
    @classmethod
    def validate_root_dir(cls, v):
        """Ensure root_dir is always an absolute path for future reference."""
        if isinstance(v, str):
            path = Path(v)
        elif isinstance(v, Path):
            path = v
        else:
            raise ValueError(f"root_dir must be a string or Path object, got {type(v)}")
        
        # Convert to absolute path and resolve any symbolic links
        absolute_path = path.expanduser().resolve()
        
        return absolute_path


class CleanWavRegistry(BaseModel):
    """Container for clean WAV file registry with metadata."""
    header: RegistryHeader
    entries: List[CleanWavEntry] = Field(default_factory=list, description="List of WAV file entries")

    @property
    def count_by_drone_type(self) -> dict[DroneType, int]:
        """Count entries by drone type."""
        from collections import defaultdict
        counts = defaultdict(int)
        for entry in self.entries:
            counts[entry.drone_type] += 1
        return dict(counts)

    def add_entry(self, file_path: Path, drone_type: Union[str, DroneType]) -> None:
        """
        Add a new entry to the registry.
        
        Args:
            file_path: Path to the WAV file
            drone_type: Type of drone (will be normalized to correct any misspellings)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"WAV file not found: {file_path}")
            
        # Normalize drone type to handle legacy misspellings
        normalized_drone_type = normalize_drone_type(drone_type)
        
        stat = file_path.stat()
        self.entries.append(CleanWavEntry(
            file_path=file_path,
            drone_type=normalized_drone_type,
            file_size=stat.st_size,
            modified_time=stat.st_mtime
        ))

    @classmethod
    def create(
        cls,
        created_by: str,
        filter_terms: List[str],
        root_dir: Path,
        description: str = "Clean WAV file registry"
    ) -> 'CleanWavRegistry':
        """Create a new registry with the given metadata."""
        return cls(
            header=RegistryHeader(
                created_by=created_by,
                filter_terms=filter_terms,
                root_dir=root_dir,
                description=description
            )
        )

    def save_to_file(self, file_path: Path) -> None:
        """Save the registry to a JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            # Convert Path objects to strings for JSON serialization
            data = self.model_dump(mode='json')
            # Convert Path objects in the dumped data
            data['header']['root_dir'] = str(self.header.root_dir)
            for entry in data['entries']:
                entry['file_path'] = str(Path(entry['file_path']))
            
            import json
            f.write(json.dumps(data, indent=2))

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'CleanWavRegistry':
        """Load a registry from a JSON file."""
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # The field validators will automatically convert string paths back to Path objects
        return cls.model_validate(data)

    def get_legacy_entries_corrected(self) -> int:
        """
        Get count of entries that had their drone types corrected from legacy names.
        This is useful for reporting how many corrections were made.
        """
        # This would require tracking corrections during validation,
        # but serves as a placeholder for potential future enhancement
        return 0

    def validate_all_entries(self) -> List[str]:
        """
        Validate all entries and return list of any validation warnings.
        
        Returns:
            List of warning messages for any issues found
        """
        warnings_list = []
        
        for i, entry in enumerate(self.entries):
            # Check if file still exists
            if not entry.file_path.exists():
                warnings_list.append(f"Entry {i}: File no longer exists: {entry.file_path}")
            
            # Check for reasonable file size (at least 1KB)
            if entry.file_size < 1024:
                warnings_list.append(f"Entry {i}: Suspiciously small file size: {entry.file_size} bytes")
        
        return warnings_list