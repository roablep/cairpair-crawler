# models/resource.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from models.other_models import TagType

class TimeSlot(BaseModel):
    from_time: str = Field(
        ...,
        alias="from",
        description='Start time, including AM/PM. Look for patterns like "10:00 AM", "2 PM". Format: "h:mm AM/PM".',
    )
    to_time: str = Field(
        ...,
        alias="to",
        description='End time, including AM/PM. Look for patterns like "11:30 AM", "5pm". Format: "h:mm AM/PM".',
    )
    days: List[Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]] = Field(
        ...,
        description='List of specific days this time slot applies to. Look for "Tuesdays and Thursdays", "M-F", "3rd Wednesday of the month". Use ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].'
    )


class CareResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Core Identifiers
    provider_name: Optional[str] = Field(None)
    resource_name: str = Field(...)
    resource_category: Optional[str] = Field(None)
    resource_subcategory: Optional[str] = Field(None)
    tags: Optional[List[TagType]] = Field(None)

    # Location Information
    location: Optional[Literal["Virtual", "In-person", "At Home", "Telephone"]] = Field(None)
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
        None,
        description="The official name of the overarching organization or company offering the service. Look for logos, page headers/footers, 'About Us', or copyright statements."
    )
    resource_name: str = Field(
        ...,
        description="The specific, official name of the program, service, support group, workshop, or event being described. Often a prominent heading or title."
    )
    resource_category: Optional[str] = Field(
        None,
        description="General type of service (e.g., Home Care Assistance, Legal Aid, Support Group). Look for descriptive keywords like 'support group', 'respite care', 'legal services'. This may be classified later."
    )
    resource_subcategory: Optional[str] = Field(
        None,
        description="Subcategory for more specific grouping within the main category. This may be classified later."
    )
    tags: Optional[List[TagType]] = Field(
        None,
        description="Predefined tags for filtering. Look for keywords related to dementia stages (early, middle, late), challenges (behavior management, legal planning), or focus areas (safety, self-care, insurance). Choose from the predefined list: education, preparation, early_stages, middle_stages, late_stages, early_onset, health, end_of_life, difficult_conversations, legal, financial, long_term_care, social_support, shared_stories, safety, health_insurance, insurance, mental_health, self_care, burnout, care_coordination, symptom_management, behavior_management, dementia_symptoms, daily_care_activities, tips_advice, home_care, adult_day_care, training."
    )

    # Location Information
    location: Optional[Literal["Virtual", "In-person", "At Home", "Telephone"]] = Field(
        None,
        description="How the service is delivered. Look for terms like 'online', 'virtual', 'webinar', 'Zoom', 'in-person', 'at our center', 'we come to you', 'in-home visit', 'over the phone', 'helpline'."
    )
    location_city: Optional[str] = Field(
        None,
        description="City where the service is delivered or the service area, if 'In-person' or 'At Home'. Check contact sections, footers, 'Locations'."
    )
    location_state: Optional[str] = Field(
        None,
        description="State (e.g., 'CA', 'New York') where the service is delivered or the service area, if 'In-person' or 'At Home'."
    )
    location_country: Optional[str] = Field(
        None,
        description="Country where the service is based, if applicable (e.g., 'USA', 'Canada')."
    )
    zip_code: Optional[str] = Field(
        None,
        description="Zip code for the service location or service area, if 'In-person' or 'At Home'."
    )

    # Contact Info
    contact_phone: Optional[str] = Field(
        None,
        description="Primary contact phone number for *this specific resource*. Prioritize numbers labeled 'Information', 'Registration', 'Helpline', 'Intake' over general reception numbers."
    )
    contact_email: Optional[str] = Field(
        None,
        description="Primary contact email address for *this resource*. Prefer specific program emails (e.g., supportgroup@...) over generic 'info@...' or 'contact@...' if available."
    )
    website: Optional[str] = Field(
        None,
        description="The *most direct URL* for this specific resource. Could be the current page URL or a link labeled 'Learn More', 'Details', 'Program Page', 'Register Here'."
    )

    # Descriptive Info
    description: Optional[str] = Field(
        None,
        description="Brief summary of *what the resource does*, *who it helps*, and *key activities/purpose*. Focus on concrete details, summarize longer text, avoid generic marketing fluff."
    )
    time_slots: Optional[List[TimeSlot]] = Field(
        None,
        description="Structured list of schedules, meeting times, or operating hours. Look for patterns like 'Meets every Tuesday 10:00 AM - 11:30 AM', 'Open M-F 9am-5pm'. Requires extracting start time, end time, and specific days for each slot."
    )
    time_zone: Optional[str] = Field(
        None,
        description='Time zone abbreviation if explicitly mentioned with the time slots (e.g., "EST", "PST", "Central Time", "ET"). Extract only if stated.'
    )
    age_range: Optional[str] = Field(
        None,
        description="Target age group if specified (e.g., '18+', '65 and older', 'seniors 60+'). Look for 'age group', 'older adults'."
    )
    target_audience: Optional[List[str]] = Field(
        None,
        description="Intended users. Be specific (e.g., 'family caregivers', 'spousal caregivers', 'people with early-stage Alzheimer's', 'healthcare professionals', 'veterans'). Look for 'designed for', 'who should attend', 'serves'."
    )

    cost_details: Optional[
        Literal[
            "Free or low-cost",
            "Available with an out-of-pocket fee",
            "Covered by some insurance",
        ]
    ] = Field(
        None,
        description="Cost information. Look for 'Free', 'No cost', 'Fee:', 'Cost:', 'Price:', '$[amount]', 'Accepts [Insurance Name]', 'Medicare/Medicaid', 'Sliding scale'. Choose the best fit category."
    )

    eligibility_criteria: Optional[str] = Field(
        None,
        description="Specific requirements to access this resource. Look for sections like 'Eligibility', 'Requirements', 'Who qualifies', 'How to Apply'. Examples: 'Must be a resident of X county', 'Diagnosis of Y required', 'Must be unpaid caregiver'."
    )
    languages: Optional[List[str]] = Field(
        None,
        description="List languages the service is offered in besides English, if mentioned. Look for 'Languages offered:', 'Servicios en Español', 'Bilingual staff', 'Interpretation available'."
    )
    accessibility_features: Optional[List[str]] = Field(
        None,
        description="Accessibility information. Look for 'Wheelchair accessible', 'Ramp access', 'Hearing loop', 'Large print materials', 'Transportation provided', 'ASL interpretation'."
    )
    resource_format: Optional[str] = Field(
        None,
        description="Specific delivery format/method (e.g., 'Support Group', 'Workshop', 'Helpline', 'In-person Consultation', 'Online Course', 'PDF Download', 'Respite Service', 'Assessment'). More specific than 'location'."
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
    ] = Field(
        None,
        description="List specific dementia types supported or focused on, if explicitly mentioned (e.g., 'specializing in Alzheimer's', 'support for LBD caregivers')."
    )

    service_option: Optional[Literal["Live", "Asynchronous", "Zip code"]] = Field(
        None,
        description="Interaction model: 'Live' (real-time interaction like calls, live webinars, groups), 'Asynchronous' (on-demand like recorded webinars, guides, forums), 'Zip code' (primary interaction is searching a location-based directory)."
    )


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
