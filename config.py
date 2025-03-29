# config.py

POSSIBLE_RESOURCE_TYPES = [
    # Direct Care Services
    "Home Care Assistance", "Skilled Nursing Care", "Hospice Care", "Palliative Care", "Geriatric Care Management",
    # Support & Education
    "Caregiver Support Groups", "Dementia Education Programs", "Online Forums & Communities", "Counseling & Therapy (for caregivers)", "Wellness Programs (for caregivers)",
    # Financial & Legal
    "Financial Assistance Programs", "Legal Aid & Advice", "Benefits Counseling", "Estate Planning Resources",
    # Practical Assistance
    "Respite Care", "Adult Day Care", "Transportation Services", "Meal Delivery Services", "Assistive Technology Resources", "Home Modification Resources",
    # Social & Recreational
    "Activities for People with Dementia and Caregivers", "Social Clubs & Programs for Seniors", "Recreational Therapy",
    # Emergency & Safety
    "Dementia-Specific Emergency Resources", "Emergency Alert Systems", "Safety Assessment & Home Safety Resources",
    # Information & Referral
    "Resource Directories & Databases", "Helplines & Hotlines", "Information Websites & Portals",
    # General/Other (fallback)
    "Other"
]

REQUIRED_KEYS = [
    "name",
    "resource_type",
    "description",
    "source_url" # Automatically added during processing
]

CSS_SELECTOR = "body"
