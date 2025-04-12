import os
import pickle
import gzip
from typing import Set, Dict, Any, List
import csv
from datetime import datetime
from pydantic import BaseModel
from models.resource import CareResource, CareResources
from config import REQUIRED_KEYS

def is_duplicate_resource(resource_identifier: str, seen_resource_identifiers: Set[str]) -> bool:  # Renamed parameter
    dupe = resource_identifier in seen_resource_identifiers
    if not dupe:
        # print(f"✅ New resource: {resource_identifier}")
        pass
    return dupe

def is_missing_too_many_fields(resource: CareResource) -> bool:
    should_haves = ['location_state', 'description', 'time_slots', 'age_range', 'target_audience', 'cost_details', 'eligibility_criteria', 'resource_format', 'languages', 'accessibility_features']
    val_present = 0
    for key in should_haves:
        value = getattr(resource, key)
        if value and len(value) > 0:
            val_present += 1
    return val_present / len(should_haves) * 1.0 < .5

def is_complete_resource(resource: BaseModel, required_keys: List[str] = REQUIRED_KEYS) -> bool:  # Added type hints
    for key in required_keys:
        value = getattr(resource, key, None)  # Get attribute, default to None if missing
        if not value or value == "":  # Check for None or empty string
            # Optionally, log or handle missing keys:
            # print(f"❌ Resource missing or empty value for key '{key}': {resource}")
            return False  # Return False immediately if a key is missing or empty
    return True  # All keys are present and have non-empty values


def save_resource_to_gzipped_pickle(resource: Any, filename: str, data_dir: str = 'data'):
    """Saves a list of resource dictionaries to a gzipped pickle file."""

    os.makedirs(data_dir, exist_ok=True)

    # Ensure the filename ends with .pkl.gz
    if not filename.endswith(".pkl.gz"):
        filename += ".pkl.gz"

    full_output_path = os.path.join(data_dir, filename)

    with gzip.open(full_output_path, "wb") as f:
        pickle.dump(resource, f, protocol=pickle.HIGHEST_PROTOCOL)

def save_resources_to_csv(resources: List[Dict[str, Any]], filename: str):
    if not resources:
        print("No resources to save.")
        return

    # Use field names from the  model
    fieldnames = CareResource.model_fields.keys()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        # Ensure datetime objects are formatted as strings for CSV
        formatted_resources = []
        for resource in resources:
            formatted_resource = {}
            for key, value in resource.items():
                if isinstance(value, datetime):
                    formatted_resource[key] = value.isoformat()
                elif isinstance(value, list):
                    # Convert list to a simple string representation for CSV # Fixed comment indentation
                    formatted_resource[key] = ', '.join(map(str, value))
                else:
                    formatted_resource[key] = value
            formatted_resources.append(formatted_resource)
        writer.writerows(formatted_resources)
    print(f"Saved {len(resources)} resources to '{filename}'.")  # Fixed typo: resource -> resources