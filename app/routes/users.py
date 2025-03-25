from fastapi import APIRouter
from app.db.database import get_or_create_user
from fastapi import Query

router = APIRouter()

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/get-or-create")
async def get_or_create_user_route(  browser_id: str = Query(...)):
    print("get_or_create_user_route reached")
    print(browser_id)
    """Get or create a user with the given browser_id."""
    user = await get_or_create_user(browser_id)
    return user
