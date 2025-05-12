from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

# from typing import Annotated

# from fastapi import Depends, FastAPI
# from fastapi.security import HTTPBasic, HTTPBasicCredentials


from datas import (
    get_sponsorteirs,
    get_everything,
    get_everything_where,
    update_something,
)


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


@app.get("/")
def read_root():
    """
    Root endpoint that returns a simple HTML message.
    """
    return HTMLResponse('<h1>print("Welcome to PyCon Togo\'s API")</h1>')

# security = HTTPBasic()

# costumize the documentation by adding a title and description


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
def api_volunteer_inquiries():
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
    inquiries = get_everything("volunteerinquiry")
    return inquiries

@app.get("/api/registrations")
def api_registrations():
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
    registrations = get_everything("registrations")
    return registrations

@app.get("/api/sponsorinquiries")
def api_sponsor_inquiries():
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
    inquiries = get_everything("sponsorinquiry")
    return inquiries

@app.get("/api/proposals")
def api_proposals():
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
    proposals = get_everything("proposals")
    return proposals

@app.get("/api/waitlist")
def api_waitlist():
    """
    API endpoint to get all waitlist inquiries.

    data schema:
    - email: str
    """
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
    return sponsors

# update sponsor inquiry
@app.put("/api/sponsorinquiries/{id}")
def api_update_sponsor_inquiry(id: int, data: dict):
    """
    API endpoint to update a sponsor inquiry by ID.

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
    updated = update_something("sponsorinquiry", id, data)
    if updated:
        return JSONResponse(content={"message": "Sponsor inquiry updated successfully."})
    else:
        return JSONResponse(content={"message": "Failed to update sponsor inquiry."}, status_code=400)

# update volunteer inquiry
@app.put("/api/volunteerinquiries/{id}")
def api_update_volunteer_inquiry(id: int, data: dict):
    """
    API endpoint to update a volunteer inquiry by ID.
    """
    updated = update_something("volunteerinquiry", id, data)
    if updated:
        return JSONResponse(content={"message": "Volunteer inquiry updated successfully."})
    else:
        return JSONResponse(content={"message": "Failed to update volunteer inquiry."}, status_code=400)
    
@app.put("/api/proposals/{id}")
def api_update_proposal(id: int, data: dict):
    """
    API endpoint to update a proposal by ID.

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
    updated = update_something("proposals", id, data)
    if updated:
        return JSONResponse(content={"message": "Proposal updated successfully."})
    else:
        return JSONResponse(content={"message": "Failed to update proposal."}, status_code=400)

# check registration
@app.put("/api/registrations/{id}")
def api_update_registration(id: int, data: dict):
    """
    API endpoint to update a registration by ID.

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
    updated = update_something("registrations", id, data)
    if updated:
        return JSONResponse(content={"message": "Registration updated successfully."})
    else:
        return JSONResponse(content={"message": "Failed to update registration."}, status_code=400)


@app.get("/api/volunteer/{email}")
def api_volunteer(email: str):
    """
    API endpoint to get a volunteer inquiry by email.

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
    volunteer = get_everything_where("volunteerinquiry", "email", email)
    if volunteer:
        return volunteer
    else:
        return JSONResponse(content={"message": "No volunteer inquiry found."}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
