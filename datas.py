from config import supabase


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
        print("Data updated successfully.")
        return True
    else:
        print(f"Failed to update data: {response.error}")
        return False

def get_everything(table):
    """
    Get everything in a particular table
    """
    response = supabase.table(table).select("*").execute()
    data = response.data
    if len(data) == 0:
        return {"message": "No entries found"}
    return data

def get_everything_where(table, field, value):
    """
    Get everything in a particular table where a specific field matches a value
    """
    response = supabase.table(table).select("*").eq(field, value).execute()
    data = response.data
    if len(data) == 0:
        return {"message": "No entries found"}
    return data

