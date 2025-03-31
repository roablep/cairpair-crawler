from datetime import datetime  # Import datetime
from typing import Set, Dict, Any, List  # Added for type hinting
import csv
# Removed duplicate import csv

from models.resource import CareResource


def is_duplicate_resource(resource_identifier: str, seen_resource_identifiers: Set[str]) -> bool:  # Renamed parameter
    dupe = resource_identifier in seen_resource_identifiers
    if not dupe:
        # print(f"✅ New resource: {resource_identifier}")
        pass
    return dupe


def is_complete_resource(resource: Dict[str, Any], required_keys: List[str]) -> bool:  # Added type hints
    yes = all(key in resource and resource[key] is not None for key in required_keys)  # Also check for None
    if not yes:
        # print(f"❌ Resource missing keys: {resource}")
        pass
    return yes


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
