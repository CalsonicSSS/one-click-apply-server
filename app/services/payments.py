# Payments removed — credits/payments are disabled for this stage of the app.
#
# These stubs keep the /payments routes importable and non-crashing so the already
# published Chrome extension doesn't error out if it ever hits them. No Stripe, no DB.


async def create_checkout_session(browser_id: str, package: str) -> dict:
    """Payments are disabled. Everything is free, so there's nothing to purchase."""
    return {"message": "Payments are disabled — all features are free to use. No purchase needed."}


async def handle_stripe_webhook(payload: bytes, signature: str) -> dict:
    """Payments are disabled — webhooks are ignored."""
    return {"status": "ignored", "detail": "payments disabled"}
