from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class CheckInUpdate(BaseModel):
    isChecked: bool

class StaffMobel(BaseModel):
    fullname: str
    email: str
    password: str
    role: str

class StaffUpdate(BaseModel):
    fullname: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None

class StaffLogin(BaseModel):
    email: str
    password: str

class RegistrationInquiry(BaseModel):
    id: UUID = Field(
        str(uuid4()),title="ID", description="Unique identifier for the registration inquiry",
    )
    fullName: str = Field(
        ..., title="First Name", description="First name of the person registering"
    )
    email: str = Field(
        ..., title="Email", description="Email address of the person registering"
    )
    phone: str = Field(
        "90000000", title="Phone", description="Phone number of the person registering"
    )
    organization: str = Field(
        None, title="Last Name", description="Last name of the person registering"
    )
    country: str = Field(
        "Togo",
        title="Country/City",
        description="Country or city of the person registering",
    )
    tshirtsize: str = Field(
        None, title="T-shirt Size", description="T-shirt size of the person registering"
    )
    dietaryrestrictions: str = Field(
        None, title="Message", description="Message from the registrant"
    )
    newsletter: bool = Field(
        True, title="Newsletter", description="Subscribe to the newsletter"
    )
    codeofconduct: bool = Field(
        True, title="Code of Conduct", description="Agree to the code of conduct"
    )
    checked: bool = Field(
        False, title="Checked", description="Whether the registration is checked"
    )


class DeleteModel(BaseModel):
    id: int = Field(
        ..., title="ID", description="Unique identifier for the entry to be deleted"
    )
    table: str = Field(
        ..., title="Table", description="Name of the table from which to delete the entry"
    )


class ProposalReviewModdel(BaseModel):
    reviewer_id: int = Field(..., title="REVIEWER_ID")
    reviewer: str = Field(..., title="Reviewer Fullname")
    proposal_id: int = Field(..., title="Proposal ID")
    rate: int = Field(..., title="Rate")
    comment: str = Field(..., title="Comment")
