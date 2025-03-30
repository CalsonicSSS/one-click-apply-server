from pydantic import BaseModel

class User(BaseModel):
    browser_id: str
    credits: int