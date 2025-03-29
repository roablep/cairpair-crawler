# config.py

RESOURCE_TYPE_CATEGORIES = {
    "Direct Care Services": [
        "Home Care Assistance",
        "Skilled Nursing Care",
        "Hospice Care",
        "Palliative Care",
        "Geriatric Care Management",
    ],
    "Support & Education": [
        "Caregiver Support Groups",
        "Dementia Education Programs",
        "Online Forums & Communities",
        "Counseling & Therapy (for caregivers)",
        "Wellness Programs (for caregivers)",
    ],
    "Financial & Legal": [
        "Financial Assistance Programs",
        "Legal Aid & Advice",
        "Benefits Counseling",
        "Estate Planning Resources",
    ],
    "Practical Assistance": [
        "Respite Care",
        "Adult Day Care",
        "Transportation Services",
        "Meal Delivery Services",
        "Assistive Technology Resources",
        "Home Modification Resources",
    ],
    "Social & Recreational": [
        "Activities for People with Dementia and Caregivers",
        "Social Clubs & Programs for Seniors",
        "Recreational Therapy",
    ],
    "Emergency & Safety": [
        "Dementia-Specific Emergency Resources",
        "Emergency Alert Systems",
        "Safety Assessment & Home Safety Resources",
    ],
    "Information & Referral": [
        "Resource Directories & Databases",
        "Helplines & Hotlines",
        "Information Websites & Portals",
    ],
    "Media & Content": [
        "Articles",
        "Blog Posts",
        "Videos",
        "Podcasts",
    ],
    "Organizations": [
        "Non-Profit Organization",
        "Government Agency",
    ],
    "Other": [
        "Other"
    ]
}

RESOURCE_TYPE_MAP = {
    # Direct Care
    "home care": "Home Care Assistance",
    "nursing": "Skilled Nursing Care",
    "hospice": "Hospice Care",
    "palliative": "Palliative Care",
    "geriatric": "Geriatric Care Management",

    # Support & Education
    "support group": "Caregiver Support Groups",
    "support groups": "Caregiver Support Groups",
    "education": "Dementia Education Programs",
    "online forum": "Online Forums & Communities",
    "forum": "Online Forums & Communities",
    "therapy": "Counseling & Therapy (for caregivers)",
    "counseling": "Counseling & Therapy (for caregivers)",
    "wellness": "Wellness Programs (for caregivers)",

    # Financial & Legal
    "financial help": "Financial Assistance Programs",
    "financial assistance": "Financial Assistance Programs",
    "legal aid": "Legal Aid & Advice",
    "legal advice": "Legal Aid & Advice",
    "benefits": "Benefits Counseling",
    "estate planning": "Estate Planning Resources",

    # Practical Assistance
    "respite": "Respite Care",
    "day care": "Adult Day Care",
    "transport": "Transportation Services",
    "meals": "Meal Delivery Services",
    "assistive tech": "Assistive Technology Resources",
    "home modification": "Home Modification Resources",

    # Social
    "activities": "Activities for People with Dementia and Caregivers",
    "social clubs": "Social Clubs & Programs for Seniors",
    "recreational": "Recreational Therapy",

    # Emergency
    "emergency": "Dementia-Specific Emergency Resources",
    "alert system": "Emergency Alert Systems",
    "safety": "Safety Assessment & Home Safety Resources",

    # Info & Referral
    "resource directory": "Resource Directories & Databases",
    "directory": "Resource Directories & Databases",
    "helpline": "Helplines & Hotlines",
    "hotline": "Helplines & Hotlines",
    "info site": "Information Websites & Portals",

    # Media & Content
    "article": "Articles",
    "blog": "Blog Posts",
    "video": "Videos",
    "podcast": "Podcasts",

    # Organization
    "nonprofit": "Non-Profit Organization",
    "ngo": "Non-Profit Organization",
    "government": "Government Agency",

    # Fallback
    "other": "Other"
}

ALL_STANDARD_RESOURCE_TYPES = [
    resource for category in RESOURCE_TYPE_CATEGORIES.values() for resource in category
]

REQUIRED_KEYS = [
    "name",
    "resource_type",
    "description",
    "source_url" # Automatically added during processing
]

CSS_SELECTOR = "body"
