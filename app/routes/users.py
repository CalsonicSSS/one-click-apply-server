from fastapi import APIRouter
from app.db.database import get_or_create_user
from fastapi import Query

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/get-or-create")
async def get_or_create_user_route(browser_id: str = Query(...)):
    print("/get-or-create user endpoint reached")
    user = await get_or_create_user(browser_id)
    return user
