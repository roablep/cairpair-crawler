# model/resource_provider.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ResourceProvider(BaseModel):
    """
    A provider of resources, including the name and a list of resources.
    """
    model_config = ConfigDict(extra='allow')

    provider_name: Optional[str] = Field(
        None, description="The official name of the resource or service provider."
    )
    resource_category: Optional[str] = Field(
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
    address: Optional[str] = Field(
        None, description="Full address of the resources headquarters, if available. e.g. 123 N Walker St, Arlington VA, 22207"
    )
    # Contact Info
    contact_phone: Optional[str] = Field(None, description="Contact phone number.")
    contact_email: Optional[str] = Field(None, description="Contact email address.")
    website: Optional[str] = Field(None, description="Primary website for the resource.")
    resources: list[Optional[dict]] = []

class ResourceProviderforLLM(BaseModel):
    """
    A provider of resources, including the name and a list of resources.
    """
    model_config = ConfigDict(extra='allow')

    provider_name: Optional[str] = Field(
        None, description="The official name of the resource or service provider."
    )
    resource_category: Optional[str] = Field(
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
    address: Optional[str] = Field(
        None, description="Full address of the resources headquarters, if available. e.g. 123 N Walker St, Arlington VA, 22207"
    )
    # Contact Info
    contact_phone: Optional[str] = Field(None, description="Contact phone number.")
    contact_email: Optional[str] = Field(None, description="Contact email address.")
    website: Optional[str] = Field(None, description="Primary website for the resource.")