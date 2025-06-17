import typing

if not hasattr(typing, "_ClassVar") and hasattr(typing, "ClassVar"):
    typing._ClassVar = typing.ClassVar


from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



from datas import (
    get_sponsorteirs,
    get_everything,
    get_everything_where,
    update_something,
    get_volunteers_inquiries_where_motivation_is_not_null,
)
from utils import authenticate_user, create_access_token, get_current_user


app = FastAPI(
    title="PyCon Togo API",
    description="API for PyCon Togo",
    version="1.0.0",
    contact={
        "name": "PyCon Togo",
        "url": "https://pycontg.pytogo.org/",
        "email": "contact@pytogo.org",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
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
        
        }

)

origins = [
    "https://pytogo.org",
    "https://www.pytogo.org",
    "https://pycontg.pytogo.org",
    "http://localhost",
    "http://127.0.0.1:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






@app.get("/favicon.ico")
def favicon():
    """
    Endpoint to serve the favicon.
    """
    return HTMLResponse(
        '<link rel="icon" href="https://www.pytogo.org/assets/images/favicon.png" type="image/x-icon">'
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



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
    print("Current User:", current_user)
    registration = get_everything_where("registrations", "id", UUID(id))
    print(UUID(id))
    if registration:
        return registration[0]
    else:
        return JSONResponse(content={"message": "No registration found."}, status_code=404)


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
    if current_user.get("role") not in ["Admin", "Registration-manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to check registrations")
    
    registration = get_everything_where("registrations", "id", UUID(id))
    
    if registration:
        
        if registration[0].get("checked", False):
            return JSONResponse(content={"message": "Registration already checked."}, status_code=200)
        else:
           checked=  update_something("registrations", registration[0]["id"], {"checked": True})
           if checked:
                return JSONResponse(content={"message": "Registration checked successfully."}, status_code=200)
           else:
                return JSONResponse(content={"message": "Failed to check registration."}, status_code=400)
      
    else:
        return JSONResponse(content={"message": "No registration found."}, status_code=404)


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
def api_volunteer_inquiries(motivation: bool = None):
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
    if motivation is not None:
        if motivation is True:
            inquiries = get_volunteers_inquiries_where_motivation_is_not_null(
                "volunteerinquiry"
            )
        elif motivation is False:
            inquiries = get_everything_where("volunteerinquiry", "motivation", "")
    else:
        inquiries = get_everything("volunteerinquiry")
    
    return inquiries

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
    inquiries = get_everything_where("volunteerinquiry", "status", "accepted")
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
    inquiries = get_everything_where("volunteerinquiry", "status", "waiting")
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
    inquiries = get_everything_where("volunteerinquiry", "status", "rejected")
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
    if current_user.get("role") not in ["Admin", "Registration-manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to view registrations")
    registrations = get_everything("registrations")
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
    if current_user.get("role") not in ["Admin", "Sponsor-manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to view sponsor inquiries")
    inquiries = get_everything("sponsorinquiry")
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
    return sponsors

@app.get("/api/proposalsinquiries")
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
    if current_user.get("role") not in ["Admin", "Program-manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to view proposals")
    proposals = get_everything("proposals")
    return proposals

@app.get("/api/proposals")
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
    return accepted_proposals

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
    return sponsors


@app.get("/api/volunteerinquiries/{id}")
def api_get_volunteer_inquiry(id: int, current_user: dict = Depends(get_current_user)):
    """
    API endpoint to update a volunteer inquiry by ID.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") not in ["Admin", "Volunteer-manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to view volunteer inquiries")
    volunteer = get_everything_where("volunteerinquiry", "id", id)
    if volunteer:
        return volunteer
    else:
        return JSONResponse(content={"message": "Not found."}, status_code=404)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
