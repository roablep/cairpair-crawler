# model/other_models.py

from pydantic import BaseModel, Field
from typing import List, Literal

class RankedUrlList(BaseModel):
    ranked_urls: List[str] = Field(..., description="A list of URLs, ordered from most to least promising for finding detailed caregiver resource information (like support groups, financial aid, program details, contact info).")

TagType = Literal[
    "education",
    "preparation",
    "early_stages",
    "middle_stages",
    "late_stages",
    "early_onset",
    "health",
    "end_of_life",
    "difficult_conversations",
    "legal",
    "financial",
    "long_term_care",
    "social_support",
    "shared_stories",
    "safety",
    "health_insurance",
    "insurance",
    "mental_health",
    "self_care",
    "burnout",
    "care_coordination",
    "symptom_management",
    "behavior_management",
    "dementia_symptoms",
    "daily_care_activities",
    "tips_advice",
    "home_care",
    "adult_day_care",
    "training",
]

class TagOutput(BaseModel):
    tag: TagType
