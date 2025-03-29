import csv

from models.resource import CareResource


def is_duplicate_resource(resource_name: str, seen_names: set) -> bool:
    return resource_name in seen_names


def is_complete_resource(resource: dict, required_keys: list) -> bool:
    return all(key in resource for key in required_keys)


def save_resources_to_csv(resources: list, filename: str):
    if not resources:
        print("No resources to save.")
        return

    # Use field names from the  model
    fieldnames = CareResource.model_fields.keys()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resources)
    print(f"Saved {len(resources)} resource to '{filename}'.")
