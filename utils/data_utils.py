from datetime import datetime  # Import datetime
from typing import Set, Dict, Any, List  # Added for type hinting
import csv
# Removed duplicate import csv

from models.resource import CareResource


def is_duplicate_resource(resource_identifier: str, seen_resource_identifiers: Set[str]) -> bool:  # Renamed parameter
    return resource_identifier in seen_resource_identifiers


def is_complete_resource(resource: Dict[str, Any], required_keys: List[str]) -> bool:  # Added type hints
    return all(key in resource and resource[key] is not None for key in required_keys)  # Also check for None


def save_resources_to_csv(resources: List[Dict[str, Any]], filename: str):  # Added type hint
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
