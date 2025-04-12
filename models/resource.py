# models/resource.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from models.other_models import TagType

class TimeSlot(BaseModel):
    from_time: str = Field(
        ...,
        alias="from",
        description='Start time in format "h:mm AM/PM" (e.g., "10:00 AM").',
    )
    to_time: str = Field(
        ...,
        alias="to",
        description='End time in format "h:mm AM/PM" (e.g., "11:00 AM").',
    )
    days: List[Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]] = Field(
        ..., description='List of days for this time slot (e.g., ["Mon", "Wed"]).'
    )


class CareResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Core Identifiers
    provider_name: Optional[str] = Field(
        None, description="The official name of the resource or service provider."
    )
    resource_name: str = Field(
        ..., description="The official name of the resource or service."
    )
    resource_category: Optional[str] = Field(
        None,
        description="Expanded category (e.g., Home Care Assistance, Legal Aid, Support Group).",
    )
    resource_subcategory: Optional[str] = Field(
        None, description="Subcategory for more specific grouping."
    )
    tags: Optional[List[TagType]] = Field(
        None,
        description="Predefined tags for filtering and search. Choose from: education, preparation, early_stages, middle_stages, late_stages, early_onset, health, end_of_life, difficult_conversations, legal, financial, long_term_care, social_support, shared_stories, safety, health_insurance, insurance, mental_health, self_care, burnout, care_coordination, symptom_management, behavior_management, dementia_symptoms, daily_care_activities, tips_advice, home_care, adult_day_care, training.",
    )

    # Location Information
    location: Optional[Literal["Virtual", "In-person", "At Home", "Telephone"]] = Field(
        None,
        description="Delivery location type (Virtual, In-person, At Home, Telephone).",
    )
    location_city: Optional[str] = Field(
        None, description="City where the resource is based, if applicable."
    )
    location_state: Optional[str] = Field(
        None, description="State where the resource is based, if applicable."
    )
    location_country: Optional[str] = Field(
        None, description="Country where the resource is based, if applicable."
    )
    zip_code: Optional[str] = Field(
        None, description="Zip code for location-based services, if applicable."
    )

    # Contact Info
    contact_phone: Optional[str] = Field(None, description="Contact phone number.")
    contact_email: Optional[str] = Field(None, description="Contact email address.")
    website: Optional[str] = Field(
        None, description="Primary website for the resource."
    )

    # Descriptive Info
    description: Optional[str] = Field(
        None, description="Brief summary of the resource or service."
    )
    time_slots: Optional[List[TimeSlot]] = Field(
        None, description="Structured list of time slots for service availability."
    )
    time_zone: Optional[str] = Field(
        None, description='Time zone abbreviation (e.g., "EST", "CST", "AKST").'
    )
    age_range: Optional[str] = Field(
        None, description="Target age group (e.g., '18+', '65 and older')."
    )
    target_audience: Optional[List[str]] = Field(
        None,
        description="Intended users (e.g., caregivers, people with dementia, professionals).",
    )

    cost_details: Optional[
        Literal[
            "Free or low-cost",
            "Available with an out-of-pocket fee",
            "Covered by some insurance",
        ]
    ] = Field(None, description="Cost information for the service.")

    eligibility_criteria: Optional[str] = Field(
        None,
        description="Requirements to access this resource (e.g., must be a caregiver).",
    )
    languages: Optional[List[str]] = Field(
        None, description="Languages offered (e.g., ['English', 'Spanish'])."
    )
    accessibility_features: Optional[List[str]] = Field(
        None,
        description="Accessibility info (e.g., ['Wheelchair accessible', 'Transportation provided']).",
    )
    resource_format: Optional[str] = Field(
        None, description="Delivery format (e.g., 'In-person', 'Virtual', 'Hybrid')."
    )

    dementia_types: Optional[
        List[
            Literal[
                "Alzheimer's Disease",
                "Vascular Dementia",
                "Lewy Body Dementia",
                "Frontotemporal Dementia",
                "Mixed Dementia",
                "Parkinson's Disease",
            ]
        ]
    ] = Field(None, description="Dementia types supported by this resource.")

    service_option: Optional[Literal["Live", "Asynchronous", "Zip code"]] = Field(
        None, description="Service option (Live, Asynchronous, Zip code)."
    )

    # Provenance & Metadata
    source_last_updated: Optional[str] = Field(
        None, description="Last updated date on the source website (if available)."
    )
    source_url: Optional[str] = Field(
        None, description="Exact URL this resource was extracted from."
    )
    source_origin: Optional[str] = Field(
        None,
        description="Root domain the resource was sourced from (e.g., 'wearehfc.org').",
    )

    # Internal Tracking
    date_added_to_db: Optional[datetime] = Field(
        None, description="When this resource was first added to our database."
    )
    date_last_reviewed: Optional[datetime] = Field(
        None,
        description="When this resource was last reviewed or updated in our system.",
    )


class CareResourceforLLM(BaseModel):
    # Core Identifiers
    provider_name: Optional[str] = Field(
        None, description="The official name of the resource or service provider."
    )
    resource_name: str = Field(
        ..., description="The official name of the resource or service."
    )
    resource_category: Optional[str] = Field(
        None, description="Expanded category (e.g., Home Care Assistance, Legal Aid, Support Group)."
    )
    resource_subcategory: Optional[str] = Field(
        None, description="Subcategory for more specific grouping."
    )
    tags: Optional[List[TagType]] = Field(
        None, description="Predefined tags for filtering and search."
    )

    # Location Information
    location: Optional[Literal["Virtual", "In-person", "At Home", "Telephone"]] = Field(
        None, description="Delivery location type (Virtual, In-person, At Home, Telephone)."
    )
    location_city: Optional[str] = Field(None)
    location_state: Optional[str] = Field(None)
    location_country: Optional[str] = Field(None)
    zip_code: Optional[str] = Field(None)

    # Contact Info
    contact_phone: Optional[str] = Field(None)
    contact_email: Optional[str] = Field(None)
    website: Optional[str] = Field(None)

    # Descriptive Info
    description: Optional[str] = Field(None)
    time_slots: Optional[List[TimeSlot]] = Field(None)
    time_zone: Optional[str] = Field(None)
    age_range: Optional[str] = Field(None)
    target_audience: Optional[List[str]] = Field(None)
    cost_details: Optional[
        Literal[
            "Free or low-cost",
            "Available with an out-of-pocket fee",
            "Covered by some insurance",
        ]
    ] = Field(None)
    eligibility_criteria: Optional[str] = Field(None)
    languages: Optional[List[str]] = Field(None)
    accessibility_features: Optional[List[str]] = Field(None)
    resource_format: Optional[str] = Field(None)
    dementia_types: Optional[
        List[
            Literal[
                "Alzheimer's Disease",
                "Vascular Dementia",
                "Lewy Body Dementia",
                "Frontotemporal Dementia",
                "Mixed Dementia",
                "Parkinson's Disease",
            ]
        ]
    ] = Field(None)
    service_option: Optional[Literal["Live", "Asynchronous", "Zip code"]] = Field(None)


class CareResources(BaseModel):
    """
    A collection of CareResource objects.
    """
    resources: List[CareResource] = Field(
        default_factory=list,
        description="List of CareResource objects."
    )


class CareResourcesforLLM(BaseModel):
    """
    A collection of CareResource objects.
    """
    resources: List[CareResourceforLLM] = Field(
        default_factory=list,
        description="List of CareResource objects."
    )

class TagOutput(BaseModel):
    tag: TagType