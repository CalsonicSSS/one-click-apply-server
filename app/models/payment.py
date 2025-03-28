
from pydantic import BaseModel

class CreateSessionRequest(BaseModel):
    browser_id: str
    package: str
