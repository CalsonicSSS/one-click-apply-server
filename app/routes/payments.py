from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from app.services.payments import create_checkout_session, handle_stripe_webhook
from app.db.database import get_or_create_user, consume_credit
from fastapi import Body

router = APIRouter()


class CreateSessionRequest(BaseModel):
    browser_id: str
    package: str


@router.post("/create-session")
async def create_session(request: CreateSessionRequest):
    """Create a Stripe checkout session for credit purchase."""
    return await create_checkout_session(request.browser_id, request.package)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
    return await handle_stripe_webhook(payload, signature)

@router.post("/credits/consume")
async def consume_credit_route(browser_id: str):
    """Consume one credit from user's account."""
    success = await consume_credit(browser_id)
    if not success:
        raise HTTPException(
            status_code=402,
            detail="Not enough credits. Please purchase more."
        )
    return {"status": "success"} 