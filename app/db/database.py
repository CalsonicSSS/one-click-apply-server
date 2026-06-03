# Database layer removed — credits/payments are disabled for this stage of the app.
#
# These are no-op stubs that preserve the exact import surface the routes/services
# already depend on, so nothing else has to change and the already-published Chrome
# extension keeps working. There is no MongoDB connection anymore (that SRV-record
# lookup at client init was what was crashing the deploy).

from app.models.user import User

# A generous fixed balance so the existing frontend always shows plenty of credits
# and never blocks generation.
_UNLIMITED_CREDITS = 999999


async def init_db():
    print("init_db (no-op: database disabled)")


async def close_db_connection():
    print("close_db (no-op: database disabled)")


async def get_or_create_user(browser_id: str) -> User:
    return User(browser_id=browser_id, credits=_UNLIMITED_CREDITS)


async def check_user_credits(browser_id: str) -> bool:
    return True


async def consume_credit(browser_id: str) -> bool:
    return True


async def update_user_credits(browser_id: str, credits_to_add: int) -> User:
    return User(browser_id=browser_id, credits=_UNLIMITED_CREDITS)
