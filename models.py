from pydantic import BaseModel

class CheckInUpdate(BaseModel):
    isChecked: bool
