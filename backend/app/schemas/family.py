from pydantic import BaseModel, Field
from datetime import date


class FamilyMemberCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    relationship: str = Field(pattern="^(spouse|child|parent|sibling|other)$")
    date_of_birth: date | None = None
    nationality: str | None = None
    emirates_id_number: str | None = None


class FamilyMemberUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    relationship: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    emirates_id_number: str | None = None
    avatar_url: str | None = None


class FamilyMemberResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    relationship: str
    date_of_birth: str | None = None
    nationality: str | None = None
    emirates_id_number: str | None = None
    avatar_url: str | None = None
    created_at: str
