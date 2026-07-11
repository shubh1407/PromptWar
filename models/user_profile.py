from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional

class UserProfile(BaseModel):
    name: str = Field(default="", min_length=2, description="Your full name")
    city: str = Field(default="", min_length=2, description="City of residence")
    family_members: int = Field(default=1, ge=1, description="Total number of family members in your household")
    children: int = Field(default=0, ge=0, description="Number of children in the household")
    senior_citizens: int = Field(default=0, ge=0, description="Number of senior citizens in the household")
    pets: bool = Field(default=False, description="Do you have pets?")
    medical_conditions: str = Field(default="", description="Any medical conditions or regular medicines needed")

    @field_validator("children")
    @classmethod
    def validate_children(cls, v: int, info: ValidationInfo) -> int:
        family = info.data.get("family_members", 1)
        if v >= family:
            raise ValueError("Number of children cannot be equal to or exceed total family members.")
        return v

    @field_validator("senior_citizens")
    @classmethod
    def validate_seniors(cls, v: int, info: ValidationInfo) -> int:
        family = info.data.get("family_members", 1)
        children = info.data.get("children", 0)
        # We need to make sure children + senior_citizens doesn't exceed total family members.
        if v + children >= family:
            raise ValueError("The sum of children and senior citizens must be less than the total family members.")
        return v
