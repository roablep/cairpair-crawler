# models/resource.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CareResource(BaseModel):
    # Core Identifiers
    provider_name: Optional[str] = Field(
        None, description="The official name of the resource or service provider."
    )
    resource_name: Optional[str] = Field(
        None, description="The official name of the resource or service."
    )
    resource_type: Optional[str] = Field(
        None,
        description="Expanded category (e.g., Home Care Assistance, Legal Aid, Support Group).",
    )

    # Location Information
    location_city: Optional[str] = Field(
        None, description="City where the resource is based, if applicable."
    )
    location_state: Optional[str] = Field(
        None, description="State where the resource is based, if applicable."
    )
    location_country: Optional[str] = Field(
        None, description="Country where the resource is based, if applicable."
    )

    # Contact Info
    contact_phone: Optional[str] = Field(None, description="Contact phone number.")
    contact_email: Optional[str] = Field(None, description="Contact email address.")
    website: Optional[str] = Field(None, description="Primary website for the resource.")

    # Descriptive Info
    description: Optional[str] = Field(
        None, description="Brief summary of the resource or service."
    )
    schedule_details: Optional[str] = Field(
        None,
        description="Information on schedule, dates, times, or frequency (e.g., 'Meets Tuesdays 2-4 PM', 'Monthly')."
    )
    age_range: Optional[str] = Field(
        None, description="Target age group (e.g., '18+', '65 and older')."
    )
    target_audience: Optional[List[str]] = Field(
        None, description="Intended users (e.g., caregivers, people with dementia, professionals)."
    )
    cost_details: Optional[str] = Field(
        None, description="Cost info (e.g., 'Free', 'Sliding scale', 'Insurance accepted')."
    )
    eligibility_criteria: Optional[str] = Field(
        None, description="Requirements to access this resource (e.g., must be a caregiver)."
    )
    languages: Optional[List[str]] = Field(
        None, description="Languages offered (e.g., ['English', 'Spanish'])."
    )
    accessibility_features: Optional[List[str]] = Field(
        None,
        description="Accessibility info (e.g., ['Wheelchair accessible', 'Transportation provided'])."
    )
    resource_format: Optional[str] = Field(
        None, description="Delivery format (e.g., 'In-person', 'Virtual', 'Hybrid')."
    )

    # Provenance & Metadata
    source_last_updated: Optional[str] = Field(
        None, description="Last updated date on the source website (if available)."
    )
    source_url: Optional[str] = Field(
        None, description="Exact URL this resource was extracted from."
    )
    source_origin: Optional[str] = Field(
        None, description="Root domain the resource was sourced from (e.g., 'wearehfc.org')."
    )

    # Internal Tracking (not expected from LLM extraction)
    date_added_to_db: Optional[datetime] = Field(
        None, description="When this resource was first added to our database."
    )
    date_last_reviewed: Optional[datetime] = Field(
        None, description="When this resource was last reviewed or updated in our system."
    )

class CareResources(BaseModel):
    """
    A collection of CareResource objects.
    """
    resources: List[CareResource] = Field(
        default_factory=list,
        description="List of CareResource objects."
    )

class ResourceProvider(BaseModel):
    """
    A provider of resources, including the name and a list of resources.
    """

    provider_name: Optional[str] = Field(
        None, description="The official name of the resource or service provider."
    )
    resource_type: Optional[str] = Field(
        None,
        description="Expanded category (e.g., Home Care Assistance, Legal Aid, Support Group).",
    )

    # Location Information
    location_city: Optional[str] = Field(
        None, description="City where the resource is based, if applicable."
    )
    location_state: Optional[str] = Field(
        None, description="State where the resource is based, if applicable."
    )
    location_country: Optional[str] = Field(
        None, description="Country where the resource is based, if applicable."
    )
    
    # Contact Info
    contact_phone: Optional[str] = Field(None, description="Contact phone number.")
    contact_email: Optional[str] = Field(None, description="Contact email address.")
    website: Optional[str] = Field(None, description="Primary website for the resource.")
