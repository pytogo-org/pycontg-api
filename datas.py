import bcrypt
from fastapi import HTTPException
from config import supabase
import re




def get_sponsorteirs():
    """
    Fetch all sponsor tiers from the database.
    """
    response = supabase.table("sponsortiers").select("*").execute()
    data = response.data
    if len(data) == 0:
        print("No sponsor tiers found.")
        return []

    for tier in data:
        tier["amount_cfa"] = int(tier["amount_cfa"])
        tier["amount_usd"] = int(float(tier["amount_usd"]))
        tier["availability"] = int(tier["availability"])
    
    return data

def get_sponsortirtbytitle(title):
    """
    Fetch a specific sponsor tier by its title.
    """
    
    response = supabase.table("sponsortiers").select("*").eq("title", title).execute()
    data = response.data
    if len(data) == 0:
        print(f"No sponsor tier found with title: {title}")
        return None
    data[0]["amount_cfa"] = int(data[0]["amount_cfa"])
    data[0]["amount_usd"] = int(float(data[0]["amount_usd"]))
    data[0]["availability"] = int(data[0]["availability"])
    
    return data[0]

def get_something_email(table, email):
    """
    Fetch a specific entry by email from a given table.
    """
    response = supabase.table(table).select("*").eq("email", email).execute()
    data = response.data
    if len(data) == 0:
        print(f"No entry found with email: {email}")
        return None
    
    data[0]["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", email)
    
    if "phone" in data[0]:
        data[0]["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", data[0]["phone"])
    return data[0]

def get_something_by_field(table, field, value):
    """
    Fetch a specific entry by a given field and value from a specified table.
    """
    response = supabase.table(table).select("*").eq(field, value).execute()
    data = response.data
    if len(data) == 0:
        print(f"No entry found with {field}: {value}")
        return None
    for entry in data:
        if "email" in entry:
            entry["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", entry["email"])
        if "phone" in entry:
            entry["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", entry["phone"])
    return data

def get_something_by_email_firstname_lastname(table, email, firstname, lastname):
    """
    Fetch a specific entry by email, first name, and last name from a given table.
    """
    response = supabase.table(table).select("*").eq("email", email).eq("firstname", firstname).eq("lastname", lastname).execute()
    data = response.data
    if len(data) == 0:
        print(f"No entry found with email: {email}, firstname: {firstname}, lastname: {lastname}")
        return None
    data[0]["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", data[0]["email"])
    if "phone" in data[0]:
        data[0]["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", data[0]["phone"])
    return data[0]


def insert_something(table, data):
    """
    Insert a new entry into a specified table.
    """
    response = supabase.table(table).insert(data).execute()
    if response:
        print("Data inserted successfully.")
        return True
    else:
        print(f"Failed to insert data: {response.error}")
        return False

def update_something(table, id, data):
    """
    Update an existing entry in a specified table by its ID.
    """
    response = supabase.table(table).update(data).eq("id", id).execute()
    if response:
        return True
    else:
        
        return False

def get_everything(table):
    """
    Get everything in a particular table
    """
    response = supabase.table(table).select("*").execute()
    data = response.data
    if len(data) == 0:
        return False
    
    for entry in data:
        if "email" in entry:
            entry["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", entry["email"])
        if "phone" in entry:
            entry["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", entry["phone"])
    return data

def get_everything_where(table, field, value):
    """
    Get everything in a particular table where a specific field matches a value
    """
    response = supabase.table(table).select("*").eq(field, value).execute()
    data = response.data
    if len(data) == 0:
        return False
    for entry in data:
        if "email" in entry:
            entry["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", entry["email"])
        if "phone" in entry:
            entry["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", entry["phone"])
    
    return data

def get_something_where(table, field, value):
    """
    Get everything in a particular table where a specific field matches a value
    """
    response = supabase.table(table).select("*").eq(field, value).execute()
    data = response.data
    if len(data) == 0:
        return False
    if "email" in data[0]:
        data[0]["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", data[0]["email"])
    if "phone" in data[0]:
        data[0]["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", data[0]["phone"])
    if len(data) > 1:
        return {"message": "Multiple entries found, please refine your query"}
    return data[0]

def get_volunteers_inquiries_where_motivation_is_not_null(table="volunteerinquiry"):
    """
    Get all volunteer inquiries where motivation is not null
    """
    response = supabase.table(table).select("*").neq("motivation", "").execute()
    data = response.data
    if len(data) == 0:
        return False
    for entry in data:
        if "email" in entry:
            entry["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", entry["email"])
        if "phone" in entry:
            entry["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", entry["phone"])
    return data

def auth_user(email: str, password: str):
    """
    Authenticates a user with email and password.
    """

    response = (
        supabase.table("staff")
        .select("id", "email", "role", "fullname", "password")
        .eq("email", email)
        .execute()
    )

    if not response.data:
        return None
    data = response.data
    user = data[0]
    if not bcrypt.checkpw(
        password.encode("utf-8"), user.get("password").encode("utf-8")
    ):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password pass"
        )
    else:
        user_data = {
            "id": user.get("id"),
            "email": user.get("email"),
            "full_name": user.get("fullname", ""),
            "role": user.get("role", "staff"),
        }

    return user_data

# get everything in table multiple fields
def get_everything_where_multiple_fields(table, **kwargs):
    """
    Get everything in a particular table where multiple fields match their respective values.
    """
    query = supabase.table(table).select("*")
    for field, value in kwargs.items():
        query = query.eq(field, value)
    
    response = query.execute()
    data = response.data
    if len(data) == 0:
        return False
    
    for entry in data:
        if "email" in entry:
            entry["email"] = re.sub(r"(?<=.{2}).(?=.*)", "*", entry["email"])
        if "phone" in entry:
            entry["phone"] = re.sub(r"(?<=.{2}).(?=.*\d)", "*", entry["phone"])
    
    return data

def delete_something(table, id):
    """
    Delete an entry from a specified table by its ID.
    """
    response = supabase.table(table).delete().eq("id", id).execute()
    if response:
        return True
    else:
        return False


if __name__ == "__main__":
    data = get_everything_where_multiple_fields(
        "proposalreviews", proposal_id=5, reviewer_id=24
    )
    if data:
        print(data)
    else:
        print("No data found or an error occurred.")