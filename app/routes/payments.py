from fastapi import APIRouter, Request, HTTPException
from app.models.payment import CreateSessionRequest
from app.services.payments import create_checkout_session, handle_stripe_webhook
from fastapi.responses import HTMLResponse

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


@router.get("/success", response_class=HTMLResponse)
async def payment_success(browser_id: str):
    """Payment success page with extension messaging."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Successful | One-Click Craft</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f7f9fc;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                color: #333;
            }}
            .container {{
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
                padding: 40px;
                text-align: center;
                max-width: 480px;
                width: 90%;
            }}
            .success-icon-circle {{
                width: 80px;
                height: 80px;
                background-color: #e6f7e9;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 24px;
            }}
            .success-icon {{
                color: #4CAF50;
                font-size: 40px;
                font-weight: bold;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 16px;
                font-size: 28px;
            }}
            p {{
                color: #7f8c8d;
                line-height: 1.6;
                margin-bottom: 24px;
                font-size: 16px;
            }}
            .button {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 14px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                border-radius: 50px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            }}
            .button:hover {{
                background-color: #43a047;
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
            }}
            .credits-info {{
                background-color: #f1f8fe;
                border-radius: 8px;
                padding: 16px;
                margin: 24px 0;
                border-left: 4px solid #3498db;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon-circle">
                <div class="success-icon">✓</div>
            </div>
            <h1>Payment Successful!</h1>
            <div class="credits-info">
                <p>Your credits have been added to your account and are ready to use.</p>
            </div>
            <p>You can close this window and return to One-Click Craft to continue crafting your perfect job application.</p>
            <button class="button" onclick="window.close()">Close Window</button>
        </div>
        <script>
            // This script communicates with the One-Click Craft extension
            function notifyExtension() {{
                // Your actual extension ID (NOT the browser_id)
                const EXTENSION_ID = "cgondpiegapndmcmlmgcobkedkgabbli";
                
                try {{
                    // Send a message to your extension with the browser_id
                    chrome.runtime.sendMessage(EXTENSION_ID, {{ 
                        action: "refreshCredits", 
                        browserId: "{browser_id}" 
                    }}, function(response) {{
                        if (response && response.success) {{
                            console.log("Successfully notified extension");
                        }}
                    }});
                }} catch (e) {{
                    console.log("Extension communication failed, but webhook will still update credits", e);
                }}
            }}
            
            // Try to notify extension after a brief delay
            setTimeout(notifyExtension, 300);
        </script>
    </body>
    </html>
    """
    return html_content


@router.get("/cancel", response_class=HTMLResponse)
async def payment_cancel():
    """Payment cancelled page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Cancelled | One-Click Craft</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                padding: 40px;
                text-align: center;
                max-width: 500px;
            }
            .cancel-icon {
                color: #FF9800;
                font-size: 64px;
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
                margin-bottom: 16px;
            }
            p {
                color: #666;
                line-height: 1.5;
                margin-bottom: 24px;
            }
            .button {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="cancel-icon">✕</div>
            <h1>Payment Cancelled</h1>
            <p>Your payment was not completed. You have not been charged.</p>
            <p>You can close this window and return to using the extension.</p>
            <button class="button" onclick="window.close()">Close Window</button>
        </div>
    </body>
    </html>
    """
    return html_content
