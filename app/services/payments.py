import stripe
from fastapi import HTTPException
from app.config import get_settings
from app.db.database import update_user_credits
from app.constants import CREDITS_PACKAGES

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_checkout_session(browser_id: str, package: str) -> dict:
    """Create a Stripe checkout session for credit purchase."""
    if package not in CREDITS_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package selected")

    package_info = CREDITS_PACKAGES[package]
    price_amount = int(package_info["price"] * 100)  # Convert to cents
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{package} Credits Package",
                        "description": f"Purchase {package} credits for Resume Tailor Assistant"
                    },
                    "unit_amount": price_amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://your-extension-url/success",  # Update with actual URL
            cancel_url="https://your-extension-url/cancel",    # Update with actual URL
            metadata={
                "browser_id": browser_id,
                "package": package,
                "credits": str(package_info["credits"])
            },
        )
        return {"session_id": session.id, "url": session.url}
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_stripe_webhook(payload: bytes, signature: str) -> dict:
    """Handle Stripe webhook events."""
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        browser_id = session["metadata"]["browser_id"]
        credits = int(session["metadata"]["credits"])
        
        # Update user credits in database
        await update_user_credits(browser_id, credits)
        
    return {"status": "success"} 