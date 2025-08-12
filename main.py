import os
import typing

from utils.send_tickets import send_ticket_email

if not hasattr(typing, "_ClassVar") and hasattr(typing, "ClassVar"):
    typing._ClassVar = typing.ClassVar


from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from uuid import UUID, uuid4
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from datas import (
    delete_something,
    get_everything_where_multiple_fields,
    get_something_where_two_fields,
    get_sponsorteirs,
    get_everything,
    get_everything_where,
    insert_something,
    update_something,
    get_volunteers_inquiries_where_motivation_is_not_null,
)
from utils.auths import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    _sorted
)
from models import (
    CheckInUpdate,
    RegistrationInquiry,
    StaffModel,
    ProposalReviewModel,
    UpdateSpeakerModel,
)

load_dotenv()

app = FastAPI(
    title="PyCon Togo API",
    description="API for PyCon Togo",
    version="1.1.3",
    contact={
        "name": "PyCon Togo",
        "url": "https://pycontg.pytogo.org/",
        "email": "contact@pytogo.org",
    },
    license_info={
        "name": "Apache 2.0 License",
        "url": "https://opensource.org/licenses/Apache-2.0",
    },
    openapi_tags=[
        {
            "name": "sponsor",
            "description": "Sponsor related operations",
        },
        {
            "name": "volunteer",
            "description": "Volunteer related operations",
        },
        {
            "name": "registration",
            "description": "Registration related operations",
        },
    ],
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": -1,
        "defaultModelRendering": "model",
        "defaultModelsTabEnabled": False,
        "defaultModelTabEnabled": False,
    },
)

origins = os.getenv("ALLOWED_ORIGINS ", "*")




app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPONSOR_ORDER = {
    "headline": 1,
    "gold": 2,
    "silver": 3,
    "bronze": 4,
    "costum": 5,
    "educational": 6,
    "media": 7
}
SPEAKER_ORDER = {
    "Serge": 1,
    "Ibi": 2,
    "Zokora Elvis": 3,
    "Jacobs": 4,
    "Basile": 8,   
}
PROPOSAL_RATE = {
    4: 1,
    3: 2,
    2: 3,
    1: 4,
}
@app.get("/favicon.ico")
def favicon():
    """
    Endpoint to serve the favicon.
    """
    return HTMLResponse(
        '<link rel="icon" href="https://www.pytogo.org/assets/images/favicon.png" type="image/x-icon">'
    )



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
STAFF_SECRET_KEY = os.getenv("STAFF_SECRET_KEY")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = await authenticate_user(form_data.username, form_data.password)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={
            "sub": form_data.username,
            "user_id": user_data["id"],
            "full_name": user_data["full_name"],
            "role": user_data["role"],
        }
    )
    if not access_token:
        raise HTTPException(status_code=500, detail="Could not create access token")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
def read_root():
    """
    Root endpoint that returns a simple HTML message.
    """
    return HTMLResponse('<h1>print("Welcome to PyCon Togo\'s API")</h1>')


@app.get("/api/registration/{id}")
def api_registration(id: str, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get a registration by UUID.

    data schema:
    - id: UUID
    - fullName: str
    - email: str
    - phone: str
    - organization: str
    - country: str
    - tshirtsize: str
    - dietaryrestrictions: str
    - newsletter: bool
    - codeofconduct: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Registration-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view registrations"
        )
    try:
        uuid_obj = UUID(id, version=4)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    registration = get_everything_where("registrations", "id", str(uuid_obj))
    if registration:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if current_user.get("role") not in ["Admin", "Registration-manager"]:
            raise HTTPException(
                status_code=403, detail="Not authorized to view registrations"
            )

        if registration:
            return registration[0]
    else:
        return JSONResponse(
            content={"message": "No registration found."}, status_code=404
        )


@app.put("/api/checkregistration/{id}")
def api_check_registration(id: str, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to check a registration by UUID.

    data schema:
    - fullName: str
    - email: str
    - phone: str
    - organization: str
    - country: str
    - tshirtsize: str
    - dietaryrestrictions: str
    - newsletter: bool
    - codeofconduct: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.get("role") not in ["Admin", "Registration-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to check registrations"
        )

    try:
        uuid_obj = UUID(id, version=4)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    registration = get_everything_where("registrations", "id", str(uuid_obj))

    if registration:
        if registration[0].get("checked", False):
            return JSONResponse(
                content={"message": "Registration already checked."}, status_code=200
            )
          
        else:
            checked = update_something(
                "registrations", registration[0]["id"], {"checked": True}
            )
            if checked:
                return JSONResponse(
                    content={"message": "Registration checked successfully."},
                    status_code=200,
                )
            else:
                return JSONResponse(
                    content={"message": "Failed to check registration."},
                    status_code=400,
                )


    else:
        return JSONResponse(
            content={"message": "No registration found."}, status_code=404
        )



@app.put("/api/checkin/{id}")
def api_check_in(
    id: str, current_user: dict = Depends(get_current_user)
):
    """
    API endpoint to check a registration by UUID.

    data schema:
    - fullName: str
    - email: str
    - phone: str
    - organization: str
    - country: str
    - tshirtsize: str
    - dietaryrestrictions: str
    - newsletter: bool
    - codeofconduct: bool
    """
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated or not a staff member")
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to check registrations"
        )
    if current_user.get("role") not in ["Admin", "Registration-manager"]:
        raise HTTPException(
            status_code=403, detail="Not authorized to check registrations"
        )

    try:
        uuid_obj = UUID(id, version=4)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    registration = get_everything_where("registrations", "id", str(uuid_obj))

    if registration:
        if registration[0].get("checked", False):
            return JSONResponse(
                content={"message": "Registration already checked."}, status_code=200
            )
        else:
            checked = update_something(
                "registrations", registration[0]["id"], {"checked": True}
            )
            if checked:
                return JSONResponse(
                    content={"message": "Registration checked successfully."},
                    status_code=200,
                )
            else:
                raise JSONResponse(
                    content={"message": "Failed to check registration."},
                    status_code=400,
                )

    else:
        return JSONResponse(
            content={"message": "No registration found."}, status_code=404
        )
    


@app.put("/api/foodcheck/{id}")
def api_food_check(
    id: str, current_user: dict = Depends(get_current_user)
):
    """API endpoint to check food status of a registration by UUID.

    data schema:
    - fullName: str
    - email: str
    - phone: str
    - organization: str
    - country: str
    - tshirtsize: str
    - dietaryrestrictions: str
    - newsletter: bool
    - codeofconduct: bool
    """
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated or not a staff member")
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to check registrations"
        )
    #if current_user.get("role") not in ["Admin", "Registration-manager"]:
        #raise HTTPException(
        #    status_code=403, detail="Not authorized to check registrations"
        #)

    try:
        uuid_obj = UUID(id, version=4)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    registration = get_everything_where("registrations", "id", str(uuid_obj))

    if registration:
        if registration[0].get("foodchecked", False):
            return JSONResponse(
                content={"message": "NO: This Attendee has already taken."}, status_code=200
            )
        else:
            checked = update_something(
                "registrations", registration[0]["id"], {"foodchecked": True}
            )
            if checked:
                return JSONResponse(
                    content={"message": "YES: This Attendee can take food."},
                    status_code=200,
                )
            else:
                raise JSONResponse(
                    content={"message": " SHUUUT Failed to check food status."},
                    status_code=400,
                )

    else:
        return JSONResponse(
            content={"message": "No registration found."}, status_code=404
        )


@app.put("/api/registrations/{id}/checkin")
def api_check_in_update(
    id: str, check_in_update: CheckInUpdate, current_user: dict = Depends(get_current_user)
):
    """
    API endpoint to update check-in status of a registration by UUID.

    data schema:
    - isChecked: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated or not a staff member")
    
    if current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to update check-in status"
        )
    
    if current_user.get("role") not in ["Admin", "Registration-manager"]:
        raise HTTPException(
            status_code=403, detail="Not authorized to update check-in status"
        )

    try:
        uuid_obj = UUID(id, version=4)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    registration = get_everything_where("registrations", "id", str(uuid_obj))

    if registration:
        updated = update_something(
            "registrations", registration[0]["id"], {"checked": check_in_update.isChecked}
        )
        if updated:
            return JSONResponse(
                content={"message": "Check-in status updated successfully."},
                status_code=200,
            )
        else:
            raise JSONResponse(
                content={"message": "Failed to update check-in status."},
                status_code=400,
            )
    
    else:
        return JSONResponse(
            content={"message": "No registration found."}, status_code=404
        )

@app.get("/api/staff")
def get_staff(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get staff members.

    data schema:
    - full_name: str
    - email: str
    - role: str
    - phone: str
    - country: str
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.get("role") not in ["Admin"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to view staff")

    staff_members = get_everything("staff")
    if not staff_members:
        return JSONResponse(
            content={"message": "No staff members found."}, status_code=404
        )

    return staff_members


@app.get("/api/sponsor-tiers")
def api_sponsor_tiers():
    """
    API endpoint to get all sponsor tiers.

    data schema:
    - name: str
    - title: str
    - availability: int
    - available: int
    - amount_cfa: int
    - amount_usd: float
    - advantages: List[str]
    """
    tiers = get_sponsorteirs()
    return tiers


@app.get("/api/volunteerinquiries")
def api_volunteer_inquiries(
    motivation: bool = None, current_user: dict = Depends(get_current_user)
):
    """
    API endpoint to get all volunteer inquiries.

    data schema:
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - country_city: str
    - motivation: str
    - availability_before: bool
    - availability_during: bool
    - availability_after: bool
    - accepted: bool
    - experience: str
    - registration: bool
    - technical: bool
    - logistic: bool
    - social: bool
    - photography: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )

    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if current_user.get("role") not in ["Admin", "Volunteer-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view volunteer inquiries"
        )
    if motivation is not None:
        if motivation is True:
            inquiries = get_volunteers_inquiries_where_motivation_is_not_null(
                "volunteerinquiry"
            )
            if not inquiries:
                return JSONResponse(
                    content={
                        "message": "No volunteer inquiries with motivation found."
                    },
                    status_code=404,
                )

        elif motivation is False:
            inquiries = get_everything_where("volunteerinquiry", "motivation", "")
    else:
        inquiries = get_everything("volunteerinquiry")

    if not inquiries:
        return JSONResponse(
            content={"message": "No volunteer inquiries found."}, status_code=404
        )

    return inquiries


@app.post("/api/review/{id}")
def review_proposal(id: int, proposal: ProposalReviewModel, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to review proposal
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not proposal.reviewer_id:
        raise HTTPException(status_code=400, detail="Reviewer ID is required")
    if current_user.get("role") not in ["Admin", "Program-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to review")
    if current_user.get("user_id") != proposal.reviewer_id and current_user.get("full_name") != proposal.reviewer:
        raise HTTPException(
            status_code=403, detail="Not authorized to review this proposal"
        )
    
    if (id != proposal.proposal_id):
        raise HTTPException(
            status_code=400, detail="Proposal ID in URL does not match proposal ID in body"
        )
    exist = get_everything_where_multiple_fields(
        "proposalreviews", proposal_id=proposal.proposal_id, reviewer_id=proposal.reviewer_id
    )
    if exist:
        raise HTTPException(
            status_code=400, detail="Proposal already reviewed by this reviewer"
        )
    reviewed = insert_something("proposalreviews", proposal.dict())
    if not reviewed:
        raise HTTPException(status_code=500, detail="Failed to review the proposal")

    return JSONResponse(
        content={"message": "Proposal reviewed successfully."},
        status_code=201,
    )
    
@app.delete("/api/{itemType}/{itemId}")
def api_delete(itemType, itemId, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to delete a staff member by ID.
    """

    if itemType == "registrations":
        id = UUID(itemId, version=4)
    else:
        id = int(itemId)

    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") != "Admin" or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to delete staff")

    deleted = delete_something(itemType,id)
    if deleted:
        return JSONResponse(
            content={"message": f"{itemType} member deleted successfully."},
            status_code=200,
        )
    else:
        return JSONResponse(
            content={"message": "Failed to delete {itemType} member."}, status_code=400
        )


# accepted volunteer inquiries
@app.get("/api/volunteeraccepted")
def api_volunteer_accepted(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all accepted volunteer inquiries.

    data schema:
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - country_city: str
    - motivation: str
    - availability_before: bool
    - availability_during: bool
    - availability_after: bool
    - accepted: bool
    - experience: str
    - registration: bool
    - technical: bool
    - logistic: bool
    - social: bool
    - photography: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Volunteer-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view accepted volunteer inquiries"
        )
    inquiries = get_everything_where("volunteerinquiry", "status", "accepted")
    if not inquiries:
        return JSONResponse(
            content={"message": "No accepted volunteer inquiries found."},
            status_code=404,
        )
    if current_user.get("role") not in ["Admin", "Volunteer-manager"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view accepted volunteer inquiries",
        )

    return inquiries


@app.get("/api/volunteerwaiting")
def api_volunteer_waiting(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all accepted volunteer inquiries.

    data schema:
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - country_city: str
    - motivation: str
    - availability_before: bool
    - availability_during: bool
    - availability_after: bool
    - accepted: bool
    - experience: str
    - registration: bool
    - technical: bool
    - logistic: bool
    - social: bool
    - photography: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Volunteer-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view waiting volunteer inquiries"
        )
    inquiries = get_everything_where("volunteerinquiry", "status", "waiting")
    if not inquiries:
        return JSONResponse(
            content={"message": "No volunteer inquiries found."}, status_code=404
        )

    return inquiries


@app.get("/api/volunteerrejected")
def api_volunteer_rejected(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all accepted volunteer inquiries.

    data schema:
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - country_city: str
    - motivation: str
    - availability_before: bool
    - availability_during: bool
    - availability_after: bool
    - accepted: bool
    - experience: str
    - registration: bool
    - technical: bool
    - logistic: bool
    - social: bool
    - photography: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Volunteer-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view rejected volunteer inquiries"
        )
    inquiries = get_everything_where("volunteerinquiry", "status", "rejected")
    if not inquiries:
        return JSONResponse(
            content={"message": "No volunteer inquiries found."}, status_code=404
        )
    if current_user.get("role") not in ["Admin", "Volunteer-manager"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view rejected volunteer inquiries",
        )

    return inquiries


@app.get("/api/registrations")
def api_registrations(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all registrations.

    data schema:
    - fullName: str
    - email: str
    - phone: str
    - organization: str
    - country: str
    - tshirtsize: str
    - dietaryrestrictions: str
    - newsletter: bool
    - codeofconduct: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Registration-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view registrations"
        )
    registrations = get_everything("registrations")
    if not registrations:
        return JSONResponse(
            content={"message": "No registrations found."}, status_code=404
        )

    return registrations


@app.get("/api/sponsorinquiries")
def api_sponsor_inquiries(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all sponsor inquiries.

    data schema:
    - company: str
    - email: str
    - website: str
    - contact: str
    - title: str
    - phone: str
    - level: str
    - message: str
    - paid: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Sponsors-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view sponsor inquiries"
        )
    inquiries = get_everything("sponsorinquiry")
    if not inquiries:
        return JSONResponse(
            content={"message": "No sponsor inquiries found."}, status_code=404
        )

    return inquiries


@app.get("/api/sponsorspaid")
def api_sponsors_paid():
    """
    API endpoint to get all sponsors who have paid.

    data schema:
    - company: str
    - email: str
    - website: str
    - contact: str
    - title: str
    - phone: str
    - level: str
    - message: str
    - paid: bool
    """
    sponsors = get_everything_where("sponsorinquiry", "paid", True)
    if not sponsors:
        return JSONResponse(content={"message": "No sponsors found."}, status_code=404)
    return sponsors


@app.get("/api/proposals")
def api_proposals(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all proposals.

    data schema:
    - format: str
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - title: str
    - level: str
    - talk_abstract: str
    - talk_outline: str
    - bio: str
    - needs: bool
    - technical_needs: str
    - accepted: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")


    if current_user.get("role") not in ["Admin", "Program-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to view proposals")
    proposals = get_everything("proposals")
    if not proposals:
        return JSONResponse(content={"message": "No proposals found."}, status_code=404)
    return proposals

@app.put("/api/proposals/{id}/accept")
def api_accept_proposal(id: int, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to accept a proposal by ID.

    data schema:
    - accepted: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.get("role") not in ["Admin"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to accept proposals")
    
    proposal = get_everything_where("proposals", "id", id)
    if not proposal:
        return JSONResponse(content={"message": "Proposal not found."}, status_code=404)
    
    updated = update_something("proposals", id, {"accepted": True, "status": "accepted"})
    if updated:
        return JSONResponse(content={"message": "Proposal accepted successfully."}, status_code=200)
    
    return JSONResponse(content={"message": "Failed to accept proposal."}, status_code=400)

@app.put("/api/proposals/{id}/reject")
def api_reject_proposal(id: int, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to reject a proposal by ID.
    data schema:
    - accepted: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.get("role") not in ["Admin"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to reject proposals")
    
    proposal = get_everything_where("proposals", "id", id)
    if not proposal:
        return JSONResponse(content={"message": "Proposal not found."}, status_code=404)
    
    updated = update_something("proposals", id, {"accepted": False, "status": "rejected"})
    if updated:
        return JSONResponse(content={"message": "Proposal rejected successfully."}, status_code=200)
    
    return JSONResponse(content={"message": "Failed to reject proposal."}, status_code=400)


@app.get("/api/proposalsreconsideration")
def api_proposals_reconsideration(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all proposals under reconsideration.

    data schema:
    - format: str
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - title: str
    - level: str
    - talk_abstract: str
    - talk_outline: str
    - bio: str
    - needs: bool
    - technical_needs: str
    - accepted: bool
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if current_user.get("role") not in ["Admin", "Program-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to view proposals")
    proposals = get_everything("temp_speakers")
    sorted_proposals = _sorted(proposals, SPEAKER_ORDER, "rate")
    if not proposals:
        return JSONResponse(content={"message": "No proposals found."}, status_code=404)
    
    return sorted_proposals 

@app.get("/api/speakers")
def api_proposals_accepted():
    """
    API endpoint to get all accepted proposals.

    data schema:
    - format: str
    - first_name: str
    - last_name: str
    - email: str
    - phone: str
    - title: str
    - level: str
    - talk_abstract: str
    - talk_outline: str
    - bio: str
    - needs: bool
    - technical_needs: str
    - accepted: bool
    """
    accepted_proposals = get_everything_where("proposals", "accepted", True)
    if not accepted_proposals:
        return JSONResponse(
            content={"message": "No accepted proposals found."}, status_code=404
        )
    sorted_proposals = _sorted(accepted_proposals, SPEAKER_ORDER,"first_name")
    return sorted_proposals

@app.get("/api/propreviews")
def api_proposal_reviews(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all proposal reviews.

    data schema:
    - proposal_id: int
    - reviewer_id: int
    - reviewer: str
    - rating: int
    - comment: str
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Program-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to view proposals")
    if current_user.get("role") not in ["Admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view proposal reviews")
    
    reviews = get_everything("proposalreviews")
    if not reviews:
        return JSONResponse(content={"message": "No proposal reviews found."}, status_code=404)
    
    return reviews



@app.get("/api/waitlist")
def api_waitlist(current_user: dict = Depends(get_current_user)):
    """
    API endpoint to get all waitlist inquiries.

    data schema:
    - email: str
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    inquiries = get_everything("waitlist")
    if not inquiries:
        return JSONResponse(
            content={"message": "No waitlist inquiries found."}, status_code=404
        )
    return inquiries


# get sponsors who has paid
@app.get("/api/sponsors")
def api_sponsors():
    """
    API endpoint to get all sponsors who have paid.

    data schema:
    - company: str
    - email: str
    - website: str
    - contact: str
    - title: str
    - phone: str
    - level: str
    - message: str
    - paid: bool
    - accepted: bool
    """
    sponsors = get_everything_where("sponsorinquiry", "paid", True)
    if not sponsors:
        return JSONResponse(content={"message": "No sponsors found."}, status_code=404)
    sponsors_sorted = _sorted(
            sponsors,
            SPONSOR_ORDER,
            "level"
        )
    return sponsors_sorted


@app.get("/api/volunteerinquiries/{id}")
def api_get_volunteer_inquiry(id: int, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to update a volunteer inquiry by ID.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Volunteer-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view volunteer inquiries"
        )
    volunteer = get_everything_where("volunteerinquiry", "id", id)
    if volunteer:
        return volunteer
    else:
        return JSONResponse(content={"message": "Not found."}, status_code=404)


@app.post("/api/staff")
def api_add_staff(staff: StaffModel, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to add a new staff member.

    data schema:
    - fullname: str
    - email: str
    - password: str
    - role: str
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") != "Admin" or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(status_code=403, detail="Not authorized to add staff")

    staff_existing = get_everything_where("staff", "email", staff.email)
    if staff_existing:
        raise HTTPException(
            status_code=400, detail="Staff member with this email already exists"
        )
    hash_pass = hash_password(staff.password)

    added = insert_something(
        "staff",
        {
            "fullname": staff.fullname,
            "email": staff.email,
            "password": hash_pass,
            "role": staff.role,
        },
    )
    if not added:
        raise HTTPException(status_code=500, detail="Failed to add staff member")
    return JSONResponse(
        content={"message": "Staff member added successfully."}, status_code=201
    )


@app.post("/api/registrations")
def api_register_attendee(
    registration: RegistrationInquiry, current_user: dict = Depends(get_current_user)
):
    """
    API endpoint to register an attendee.

    data schema:
    - id: UUID
    - fullName: str
    - email: str
    - phone: str
    - organization: str
    - country: str
    - tshirtsize: str
    - dietaryrestrictions: str
    - newsletter: bool
    - codeofconduct: bool
    """
    
    # genrate a UUID for the registration
    _id = str(uuid4())
    print("Generated ID:", _id)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    staff = get_something_where_two_fields(
        "staff", "email", current_user.get("email"), "staff_secret_key", STAFF_SECRET_KEY
    )
    if not staff:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Registration-manager"] or current_user.get("full_name") != staff[0].get("fullname"):
        raise HTTPException(
            status_code=403, detail="Not authorized to register attendees"
        )
    

    existing_registration = get_everything_where(
        "registrations", "email", registration.email
    )

    if existing_registration:
        raise HTTPException(
            status_code=400, detail="An attendee with this email already exists"
        )

    registration_data = {
        "id": _id,
        "fullName": registration.fullName,
        "email": registration.email,
        "phone": registration.phone,
        "organization": registration.organization,
        "country": registration.country,
        "tshirtsize": registration.tshirtsize,
        "dietaryrestrictions": registration.dietaryrestrictions,
        "newsletter": registration.newsletter,
        "codeofconduct": registration.codeofconduct,
        "checked": registration.checked,
    }

    added = insert_something("registrations", registration_data)

    if not added:
        raise HTTPException(status_code=500, detail="Failed to register attendee")
    try:
        send_ticket_email(
            registration.fullName,
            registration.email,
            registration_data["id"],
        )
        return JSONResponse(
        content={"message": "Attendee registered successfully.", "id": registration_data["id"]},
        status_code=201,
    )
    except Exception as e:
        print(f"Failed to send ticket email: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to send ticket email"
        )





@app.patch("/api/speakers/{speaker_id}")
async def update_speaker(speaker_id: int, update: UpdateSpeakerModel):
    update_data = update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour.")

    # Simule une mise à jour en base de données
    print(f"Updating speaker {speaker_id} with: {update_data}")

    return {"speaker_id": speaker_id, "updated": update_data}


connected_clients: typing.List[WebSocket] = []


@app.websocket("/ws/checkin")
async def websocket_checkin(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # optionnel: filtrer ou valider les données reçues
            # puis broadcaster à tous les autres
            for client in connected_clients:
                if client != websocket:
                    await client.send_json(data)

    except WebSocketDisconnect:
        connected_clients.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
