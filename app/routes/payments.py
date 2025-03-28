from fastapi import APIRouter, Request, HTTPException
from app.models.payment import CreateSessionRequest
from app.services.payments import create_checkout_session, handle_stripe_webhook

router = APIRouter(prefix="/payments", tags=["payments"])

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